#!/usr/bin/env python
#-*- coding:utf-8 -*-
import logging
import os
import time

class Logger(object):
	def __init__(self,log_dir,log_name):
		#创建日志目录
		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
			
		#给日志文件加上时间戳
		log_file_path = os.path.join(log_dir,log_name) + '_' + time.strftime('%Y-%m-%d_%H%M%S',time.localtime(time.time())) + '.log'
		
		#配置日志级别
		logger = logging.getLogger()
		logger.setLevel(logging.DEBUG)
		
		#配置输出到控制台
		handler = logging.StreamHandler()
		formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		
		#配置输出到文件
		handler = logging.FileHandler(log_file_path)
		formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)