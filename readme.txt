一、运行环境
1.安装python 3.6.8，安装pip
2.安装mysql 5.6

二、安装所需要第三方库
1.直接在工具根目录执行命令：pip3 install -r requirements.txt

三、数据库相关配置
1.设置数据库root账号密码为test
2.创建数据库：create database ftc_atuo;
3.创建表tb_xpath和tb_filesum:
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

四、启动工具
1.在工具根目录执行命令：python3 application.py

五、搭建测试环境
1.启动appium服务
2.启动模拟器或真机

六、访问工具web接口URL
http://localhost/xpathupdate

1.在把web接口中默认appium和模拟器配置修改为你自己搭建的测试环境中的配置
2.上传写好的APP路径页面excel格式文件即可开始运行




