'''
Author: bigCarson carson.li@cubewise.com
Date: 2024-01-10 13:52:16
LastEditors: carson.li@cubewise
LastEditTime: 2024-01-10 17:29:55
FilePath: /shareService 2/src/utils.py
Description: 

Copyright (c) 2024 by carson.li@cubewise, All Rights Reserved. 
'''
import os
import yaml
import pytest_html
from TM1py.Services import TM1Service
import configparser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
conf_file_path = os.path.join(BASE_DIR, 'conf.ini')
conf = configparser.ConfigParser()
conf.read(conf_file_path)

def read_conf_from_yaml(section, event):

    with open(conf_file_path, 'r', encoding='utf-8') as yaml_file:
        content = yaml.safe_load(yaml_file)

        return content.get(section).get(event)
    
target_tm1 = TM1Service(**conf['target'])

        # assert subset
target_dimension_subset = target_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
assert target_dimension_subset == source_dimension_subset

for _target_subset_item in target_dimension_subset:
    assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item)