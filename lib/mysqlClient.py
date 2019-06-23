#!/usr/bin/env python
#-*- coding:utf-8 -*-
import logging
import pymysql

class MysqlClient(object):

    def __init__(self,host,user,passwd,dbname):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.db = None

    def connect(self,):
        if self.db is None:
            self.db = pymysql.connect(host=self.host,user=self.user,password=self.passwd,db=self.dbname,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    def execute(self,sql):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            logging.error(e)

    def query(self,sql):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            logging.error(e)

    def close(self,):
        if self.db is not None:
            self.db.close()

if __name__ == '__main__':
    host = "localhost"
    user = "root"
    passwd = "test"
    dbname = "ftc_auto"
    
    mysql_client = MysqlClient(host,user,passwd,dbname)
    mysql_client.connect()
    sql = '''insert into tb_xpath(nick_name,xpath_value,os_type,el_type,page) values("第一个点","//android.widget.ImageView[@resource-id='cn.futu.trader:id/login_futu_logo' and @bounds='[422,277][658,605]']","android","android.widget.ImageView","登录页") where not exists (select * from tb_xpath where xpath_value = "//android.widget.ImageView[@resource-id='cn.futu.trader:id/login_futu_logo' and @bounds='[422,277][658,605]']")'''
    mysql_client.execute(sql)
    sql = '''select * from tb_xpath'''
    print(mysql_client.query(sql))
    mysql_client.close()