'''
Author: bigCarson carson.li@cubewise.com
Date: 2024-01-10 13:29:08
LastEditors: carson.li@cubewise
LastEditTime: 2024-01-11 16:32:59
FilePath: /ShareServiceTestCase/conftest.py
Description: 

Copyright (c) 2024 by carson.li@cubewise, All Rights Reserved. 
'''
import pytest
from src.data import TestingData
import configparser
from TM1py.Services import TM1Service
import os
import yaml
conf = configparser.ConfigParser()
conf.read('conf.ini')
BASE_DIR = os.path.dirname(__file__)

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "smoke: mark a test as a smoke test."
    )
    config.option.html_report_title = config.getoption('--report_title')

def pytest_addoption(parser):
    
    # parser.addoption('--testId', action='store')
    parser.addoption("--report_title", action="store", default="Default Report Title", help="Custom title for the HTML report")

def pytest_sessionstart(session):
    # test SetUp
    TestingDataMain = TestingData()
    # create data
    TestingDataMain.create_test_data()
    # sync source instance object to share_service
    TestingDataMain.run_sync_job()
    # run job
    TestingDataMain.execute_job()
    # logout instance
    TestingDataMain.source_tm1.logout()
    TestingDataMain.target_tm1.logout()
    TestingDataMain.share_service_tm1.logout()

def pytest_sessionfinish(session, exitstatus):
    # test tearDown
    TestingDataMain = TestingData()
    TestingDataMain.delete_test_data()
    TestingDataMain.source_tm1.logout()
    TestingDataMain.target_tm1.logout()
    TestingDataMain.share_service_tm1.logout()

@pytest.fixture(scope="function")
def share_service_tm1():
    share_service_object = TM1Service(**conf['share_service'])
    yield share_service_object
    share_service_object.logout()

@pytest.fixture(scope="function")
def target_tm1():
    target_object = TM1Service(**conf['target'])
    yield target_object
    target_object.logout()

@pytest.fixture(scope="function")
def source_tm1():
    source_object = TM1Service(**conf['source'])
    yield source_object
    source_object.logout()

def pytest_html_report_title(report):

    report.title = report.config.option.html_report_title + ' Report'