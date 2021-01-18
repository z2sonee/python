create table member(
    mem_id int not null auto_increment,
    mem_name varchar(20),
    mem_email varchar(40),
    mem_pwd varchar(20),
    mem_address varchar(40),
    mem_phonenum varchar(30),
    mem_created_date datetime,
    primary key(mem_id)
) default charset=utf8;

create table product(
    prod_id int not null auto_increment,
    prod_name varchar(30),
    prod_company varchar(20),
    prod_color varchar(20),
    prod_volume varchar(20),
    prod_price varchar(20),
    prod_qty varchar(20),
    prod_created_date datetime,
    primary key(prod_id)
) default charset=utf8;

create table order_mng(
    order_id int not null auto_increment,
    order_qty varchar(20),
    order_price varchar(20),
    order_created_date datetime,
    mem_id int,
    prod_id int,
    primary key(order_id)
) default charset=utf8;

create table shopbasket(
    sb_id int not null auto_increment,
    sb_qty varchar(20),
    sb_price varchar(20),
    sb_created_date datetime,
    mem_id int,
    prod_id int,
    primary key(sb_id)
) default charset=utf8;

alter table order_mng add constraint foreign key(mem_id) references member(mem_id) on delete cascade on update cascade;
alter table order_mng add constraint foreign key(prod_id) references product(prod_id) on delete cascade on update cascade;

alter table shopbasket add constraint foreign key(mem_id) references member(mem_id) on delete cascade on update cascade;
alter table shopbasket add constraint foreign key(prod_id) references product(prod_id) on delete cascade on update cascade;

insert into member(mem_name, mem_email, mem_pwd, mem_address, mem_phonenum, mem_created_date) VALUES('Admin', 'admin', 'admin1234', 'admin_address', '010-5555-5555', NOW());
insert into member(mem_name, mem_email, mem_pwd, mem_address, mem_phonenum, mem_created_date) VALUES('곽지선', 'jiseon@test.com', '1234', '경기도 동두천시', '010-1212-3434', NOW());
insert into member(mem_name, mem_email, mem_pwd, mem_address, mem_phonenum, mem_created_date) VALUES('라이언', 'lian@test.com', '1111', '제주시 애월읍', '010-1111-3434', NOW());
insert into member(mem_name, mem_email, mem_pwd, mem_address, mem_phonenum, mem_created_date) VALUES('어피치', 'apeach@test.com', '2222', '경기도 양주시', '010-3333-3434', NOW());

insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('iPhone 12 mini', 'Apple', 'Black', '128GB', 102, 50, NOW());
insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('iPhone 11 pro', 'Apple', 'Gold', '256GB', 90, 100, NOW());
insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('iPhone XR', 'Apple', 'White', '64GB', 80, 200, NOW());
insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('Galaxy S9', 'Samsung', 'Violet', '64GB', 70, 120, NOW());
insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('Galaxy S20', 'Samsung', 'Gold', '256GB', 120, 300, NOW());
insert into product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES('Galaxy Note 10', 'Samsung', 'White', '128GB', 30, 88, NOW());
