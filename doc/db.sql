create table tb_xpath
(
    id int primary key auto_increment,
    el_name varchar(255),
    el_xpath varchar(255) not null unique,
    el_type varchar(50) not null,
    page_name varchar(50),
    platform_name varchar(20) not null
);

create table tb_filesum
(
    id int primary key auto_increment,
    filesum_value varchar(255) not null unique
);