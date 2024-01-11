'''
Author: bigCarson carson.li@cubewise.com
Date: 2024-01-10 13:52:16
LastEditors: carson.li@cubewise
LastEditTime: 2024-01-11 22:30:42
FilePath: /ShareServiceTestCase/src/utils.py
Description: 

Copyright (c) 2024 by carson.li@cubewise, All Rights Reserved. 
'''
import os
import yaml
import pytest_html
from TM1py.Services import TM1Service
import configparser
import datetime
import time

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
conf_file_path = os.path.join(BASE_DIR, 'conf.ini')
conf = configparser.ConfigParser()
conf.read(conf_file_path)

def read_conf_from_yaml(section, event):

    with open(conf_file_path, 'r', encoding='utf-8') as yaml_file:
        content = yaml.safe_load(yaml_file)

        return content.get(section).get(event)
    
def wait_dimension_exit(tm1,dimension):
    
    job_run_time = int(conf['info']['job_run_time'])
    exit_sign = False
    start_time = datetime.datetime.now()
    while not exit_sign:
        exit_sign = tm1.dimensions.exists(dimension_name=dimension)
        if (datetime.datetime.now() - start_time).seconds > job_run_time: raise RuntimeError(f"Job execute time more than {str(job_run_time)} second")
        time.sleep(1)