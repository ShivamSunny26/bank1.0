create database if not exists bankdb;

use bankdb;

create table users (
    id int auto_increment primary key,
    username varchar(100) not null,
    account_no varchar(20) not null unique,
    password varchar(255) not null,
    balance decimal(10, 2) default 0.00

);

create table transactions(
    id int auto_increment primary key,
    from_account varchar(20),
    to_account varchar(20),
    amount decimal(10, 2),
    timestamp timestamp default current_timestamp
);

alter table transactions
add column transaction_id varchar(100) unique after id;

alter table transactions
add column status varchar(20) after amount;
create table services (
    id int auto_increment primary key,
    account_no varchar(20), 
    service_type varchar(50),
    details text,
    amount decimal(10,2),
    timestamp timestamp default current_timestamp
);

select * from users 
limit 6;