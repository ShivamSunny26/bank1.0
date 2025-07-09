from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = "bank_secret_key"

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_no = request.form['account_no']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE account_no=%s AND password=%s", (account_no, password))

        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user']= user
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    return render_template('login2.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['user'])


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if 'user' not in session:
        return redirect('/')

    txn_id = ""
    message = ""
    show_result = False


    if request.method == 'POST':
        from_acc = session['user']['account_no']
        to_acc = request.form['to_account']
        amount = float(request.form['amount'])
        txn_id = str(uuid.uuid4())

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Check if destination account exists and not same as sender
        cursor.execute("SELECT * FROM users WHERE account_no = %s", (to_acc,))
        to_user = cursor.fetchone()

        if to_user and from_acc != to_acc:
            cursor.execute("SELECT balance FROM users WHERE account_no = %s", (from_acc,))
            balance = cursor.fetchone()['balance']

            if balance >= amount:
                # Successful transaction
                cursor.execute("UPDATE users SET balance = balance - %s WHERE account_no = %s", (amount, from_acc))
                cursor.execute("UPDATE users SET balance = balance + %s WHERE account_no = %s", (amount, to_acc))
            
                message = f"✅ Transaction Successful! Transaction ID: {txn_id}"
            else:
                
                amount = 0  # nothing deducted
                message = f"❌ Transaction Failed (Insufficient Balance). Transaction ID: {txn_id}"
        else:
            
            amount = 0  # nothing deducted
            message = f"❌ Transaction Failed (Invalid Account). Transaction ID: {txn_id}"

        # Save the transaction with status
        cursor.execute("""
            INSERT INTO transactions (transaction_id, from_account, to_account, amount)
            VALUES (%s, %s, %s, %s)
        """, (txn_id, from_acc, to_acc, amount))

        conn.commit()
        cursor.close()
        conn.close()

    return render_template('transaction2.html', message=message)



@app.route('/passbook')
def passbook():
    if 'user' not in session:
        return redirect('/')

    acc = session['user']['account_no']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE from_account=%s OR to_account=%s ORDER BY timestamp DESC", (acc, acc))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('passbook.html', transactions=transactions, user_acc=acc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
