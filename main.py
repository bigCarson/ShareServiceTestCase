'''
Author: bigCarson carson.li@cubewise.com
Date: 2024-01-03 19:51:20
LastEditors: carson.li@cubewise
LastEditTime: 2024-01-11 11:35:51
FilePath: /shareService 2/main.py
Description: 

Copyright (c) 2024 by carson.li@cubewise, All Rights Reserved. 
'''
import pytest
import os
import sys

class ExecutionMain:

    def smoking(self):

        pass
    
if __name__ == '__main__':

    import uuid

    test_id = str(uuid.uuid1())
    
    report_path = f'--html=report/{test_id}/{test_id}.html'

    pytest.main(['-v','./test_case.py', report_path])