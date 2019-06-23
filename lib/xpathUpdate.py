#!/usr/bin/env python3

import logging
import sys
import os
import time
import xlrd
import xlsxwriter
import json
import lxml.etree
import shutil
import re
import hashlib
from appium import webdriver
from selenium.common.exceptions import WebDriverException
from .mysqlClient import MysqlClient
from .logger import Logger

class XpathUpdate(object):
    def __init__(self,desired_caps,url,tmp_file_dir):
        '''
        desired_caps：json格式的客户端信息
        url：appium服务地址
        '''
        self.desired_caps = desired_caps
        self.url = url
        self.tmp_file_path = tmp_file_dir
        self.db_client = MysqlClient(host="localhost",user="root",passwd="test",dbname="ftc_auto")
        
    def run(self,steps_excel_file):
        try:
            error_msg = None
            xpath_file = None
            
            #获取操作步骤列表
            steps = self.get_steps(steps_excel_file)
            logging.info("get steps from excel")
            
            if steps:
                #启动APP
                driver = webdriver.Remote(self.url, self.desired_caps)
                logging.info("launch app")
                
                #遍历操作步骤，并执行
                for step in steps:
                    #过滤空行
                    if len(step) < 7:
                        continue
                    
                    #给操作中各字段赋值
                    current_page_name = str(step[0]).strip()
                    result_page_name = str(step[1]).strip()
                    current_page_mark = str(step[2]).strip()
                    el_action = str(step[3]).strip()
                    el_value = str(step[4]).strip()
                    action_delay = int(str(step[5]).strip())
                    result_page_mark = str(step[6]).strip()
                    
                    #获取当前页元素标记的控件
                    current_el = self.get_el(driver,current_page_mark)
                    logging.info("locating elment: " + current_page_mark)
                    
                    if current_el:
                        #提取当前页面xpath值,并存放入数据库
                        self.save_xpath(driver.page_source,current_page_name)
                        logging.info("save xpath for current page:" + current_page_name)
                    
                        #按配置规则进行操作
                        if el_action == "点击":
                            #进行点击操作
                            current_el.click()
                            time.sleep(action_delay)
                            logging.info("delay " + str(action_delay) + " seconds for click")
                        elif el_action == "输入":
                            #进行输入操作
                            current_el.send_keys(el_value)
                        else:
                            #不操作
                            pass
                        logging.info("elment action...")
                        
                        if not result_page_mark == "不检查":
                            #获取结果页元素标记的控件
                            result_el = self.get_el(driver,result_page_mark)
                            logging.info("locating elment: " + result_page_mark)
                            if result_el:
                                #提取结果页面xpath值, 并存放入数据库
                                self.save_xpath(driver.page_source,result_page_name)
                                logging.info("save xpath for result page:" + result_page_name)
                        
                            else:
                                #没定位到结果页控件就退出
                                error_msg = "没找到结果页标记：" + result_page_mark
                                logging.error(error_msg)
                                logging.debug(driver.page_source)
                                break
                        
                    else:
                        #没定位到当前页控件就退出
                        error_msg = "没找到当前页标记：" + current_page_mark
                        logging.error(error_msg)
                        logging.debug(driver.page_source)
                        break

                #结束
                driver.quit()
                
                #装载xpath文件
                if not error_msg:
                    xpath_file = self.load_xpath();
    
            return error_msg,xpath_file
        
        except WebDriverException as e:
            logging.error(e)
            logging.error("An unknown server-side error occurred, please try again manual.")

    def get_xpaths(self,xml_source,filter_node_flag = False):
        '''
        获取xml中所有控件的xpath值
        xml_source：xml源
        filter_node_flag: 过滤节点标记，False表示不过滤，True表示过滤
        '''
        
        #返回结果
        el_xpath_list = []
        el_name_list = []
        el_type_list = []
        
        #去掉xml文件声明
        declaration_line = '<?xml version="1.0" encoding="UTF-8"?>'
        if declaration_line in xml_source:
            xml_source = xml_source.replace(declaration_line,'')
        tree = lxml.etree.fromstring(xml_source)
            
        #便历结点提取xpath数据
        for node in tree.iter():
            if not list(node):
                #iOS端数据
                if self.desired_caps["platformName"] == "ios":
                    tag_name = "name"
                    el_name = node.get(tag_name)
                    if not el_name:
                        tag_name = "value"
                        el_name = node.get(tag_name)
                        
                    if filter_node_flag is True and self.is_num_node(el_name):
                        continue
                    else:
                        el_type = node.tag
                        filter_type_list = ["XCUIElementTypeStaticText","XCUIElementTypeCell","XCUIElementTypeButton","XCUIElementTypeTextField","XCUIElementTypeSecureTextField"]
                        if filter_node_flag and el_type not in filter_type_list:
                            continue
                        else:
                            el_x = node.get("x")
                            el_y = node.get("y")
                            if el_name:
                                el_xpath = "//" + el_type + "[@" + tag_name + "='" + el_name + "' and @x='" + el_x + "' and @y='" + el_y + "']"
                                el_xpath_list.append(el_xpath)
                                el_name_list.append(el_name)
                                el_type_list.append(el_type)

                #Android端数据
                elif self.desired_caps["platformName"] == "Android":
                    el_name = node.get("text")
                    if filter_node_flag is True and self.is_num_node(el_name):
                        continue
                    else:
                        el_xpath = None
                        el_type = node.tag
                        el_resource_id = node.get("resource-id")
                        el_bounds = node.get("bounds")
                        
                        if el_name and el_resource_id:
                            el_xpath = "//" + el_type + "[@text='" + el_name + "' and @resource-id='" + el_resource_id + "' and @bounds='" + el_bounds + "']"
                        elif el_name:
                            el_xpath = "//" + el_type + "[@text='" + el_name + "' and @bounds='" + el_bounds + "']"
                        elif el_resource_id:
                            el_xpath = "//" + el_type + "[@resource-id='" + el_resource_id + "' and @bounds='" + el_bounds + "']"
                            
                        if el_xpath:
                            el_xpath_list.append(el_xpath)
                            el_name_list.append(el_name)
                            el_type_list.append(el_type)

        return el_name_list,el_xpath_list,el_type_list
    
    def is_num_node(self,text_value):
        '''检查节点元素的text属性值是否是纯数值，或百分比数值'''
        if text_value:
            #num_str_reg = '^[+-]{0,1}[0-9]+[.]{0,1}[0-9]*[%]{0,1}$'
            num_str_reg = '^.*[0-9]+.*$'
            if re.match(num_str_reg,text_value):
                return True
            else:
                return False
        else:
            return False
    
    def get_el(self,driver,el_mark,max_try_times=3):
        '''
        通过控件的标记，动态获取到控件
        '''
        try:
            el = None
            if el_mark.startswith("//"):
                el = driver.find_element_by_xpath(el_mark)
            else:
                for times in range(max_try_times):
                    page_source = driver.page_source
                    logging.debug(page_source)
                    name_list,xpath_list,type_list = self.get_xpaths(page_source)
                    for xpath in xpath_list:
                        if el_mark in xpath:
                            el = driver.find_element_by_xpath(xpath)
                            break
                    if el is None:
                        #尝试关闭广告弹窗后再试
                        self.close_popup_ad(driver)
                    else:
                        break
            return el
        except WebDriverException as e:
            logging.error(e)
            return None
        
    def close_popup_ad(self,driver,close_popup_ad_bt_list = ["close_popup_ad_view"]):
        '''
        关闭广告窗口
        '''
        name_list,xpath_list,type_list = self.get_xpaths(driver.page_source)
        for close_popup_ad in close_popup_ad_bt_list:
            for xpath in xpath_list:
                if close_popup_ad in xpath:
                    el = driver.find_element_by_xpath(xpath)
                    el.click()
                    time.sleep(4)
                    return True
        return False
                    
    def get_steps(self,steps_excel_file):
        '''
        从指定的excel文件中获取步骤操作列表
        '''
        steps = []
        data = xlrd.open_workbook(steps_excel_file)
        for table in data.sheets():
            for i in range(table.nrows):
                row = table.row_values(i)
                if len(row) >= 7 and row[0] != "#":
                    steps.append(row[1:])
        return steps
    
    def save_xpath(self,xml_source,page_name):
        page_md5sum = hashlib.md5(xml_source.encode('utf-8')).hexdigest()
        sql = '''select * from tb_filesum where filesum_value="''' + page_md5sum + '''"'''
        self.db_client.connect()
        if not self.db_client.query(sql):
            #保存xpath值
            el_name_list,el_xpath_list,el_type_list = self.get_xpaths(xml_source,filter_node_flag = True)
            for el_name,el_xpath,el_type in zip(el_name_list,el_xpath_list,el_type_list):
                sql = '''insert into tb_xpath(el_name,el_xpath,el_type,page_name,platform_name) select "''' + el_name + '","' + el_xpath + '","' + el_type + '","' + page_name + '","' + self.desired_caps["platformName"] + '''" from dual where not exists (select * from tb_xpath where el_xpath="''' + el_xpath + '''")'''
                self.db_client.execute(sql)
            #保存xml md5值
            sql = '''insert into tb_filesum(filesum_value) values("''' + page_md5sum + '''")'''
            self.db_client.execute(sql)
        else:
            pass
        
    def load_xpath(self,):
        '''
        从数据库中加载xpath数据到excel文件
        '''

        #文件名称
        timestamp = time.strftime('_%Y-%m-%d_%H%M%S',time.localtime(time.time()))
        xpath_file_name = self.tmp_file_path + self.desired_caps['platformName'] + "_xpath_" + timestamp + ".xlsx"
        
        #文件格式
        workbook = xlsxwriter.Workbook(xpath_file_name)
        worksheet = workbook.add_worksheet()

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()
        cell_format.set_align("left")
        cell_format.set_align('vcenter')
        cell_format.set_font_size(10)
        cell_format.set_border()
        
        #文件标题
        row_num = 0
        column_title = ["别名","定位方式","定位值","页面","节点类型"]
        worksheet.set_column(0,1,22)
        worksheet.set_column(1,2,8)
        worksheet.set_column(2,3,150)
        worksheet.set_column(3,4,12)
        worksheet.set_column(4,5,28)
        for column_num,column_value in zip(range(len(column_title)),column_title):
            worksheet.write(row_num,column_num,column_value,cell_format)
        row_num += 1
        
        #文件内容
        sql = '''select * from tb_xpath where platform_name="''' + self.desired_caps['platformName'] + '''"'''
        self.db_client.connect()
        data_list = self.db_client.query(sql)
        for xpath_data in data_list:
            row_data = [xpath_data['el_name'],"By.xpath",xpath_data['el_xpath'],xpath_data['page_name'],xpath_data['el_type']]
            for column_num,column_value in zip(range(len(row_data)),row_data):
                worksheet.write(row_num,column_num,column_value,cell_format) 
            row_num += 1
            
        #关闭写入
        workbook.close()
        
        return xpath_file_name
    
if __name__ == '__main__':
    pass
    
    
    