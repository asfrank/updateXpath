#!/usr/bin/env python
#-*- coding:utf-8 -*-
import logging
import os
import time
import datetime
import json
from flask import Flask, render_template, request, jsonify
from werkzeug import secure_filename
from lib.xpathUpdate import XpathUpdate

app = Flask(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))

'''
配置日志输出到控制台
'''
#1.日志级别
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#2.输出到控制台
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

'''
xpath更新工具WEB接口
'''
@app.route('/xpathupdate')
def xpathupdate():
    return render_template('xpathUpdate.html')
   
@app.route('/get_xpath', methods = ['GET', 'POST'])
def get_xpath():
   #时间戳
   timestamp = time.strftime('_%Y-%m-%d_%H%M%S',time.localtime(time.time()))
   #响应时返回的数据
   response_data = {"success":False,"data":{}}
   #处理POST请求
   if request.method == 'POST':
         if 'qqfile' in request.files:
            #获取上传文件
            upload_file = request.files['qqfile']
            #获取参数
            appium_url = request.form.get("appium_url").strip()
            desired_caps = json.loads(request.form.get("desired_caps").strip())
            #获取返回给客户端的文件
            data_dir = os.path.sep + "static" + os.path.sep +  "tmp" + os.path.sep
            upload_filename = upload_file.filename
            case_file = current_dir + data_dir + upload_filename
            upload_file.save(case_file)
            xpath_update_obj = XpathUpdate(desired_caps,appium_url,current_dir + data_dir)
            error_msg,xpath_file = xpath_update_obj.run(case_file)
            #封装响应数据
            if error_msg:
               response_data["success"] = False
               response_data["data"]["msg"] = error_msg
            else:
               response_data["success"] = True
               xpath_file_name = os.path.basename(xpath_file)
               xpath_file_url = data_dir + xpath_file_name
               response_data["data"]["xpath_file_name"] = xpath_file_name
               response_data["data"]["xpath_file_url"] = xpath_file_url

   return jsonify(response_data)

if __name__ == '__main__':
   app.run(host = "0.0.0.0", port = 80 ,debug = True)
   #app.run(host = "0.0.0.0", port = 9090 )
