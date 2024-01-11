import os
import pytest
import yaml
import datetime
import time
from src.target import *
import configparser
import datetime
import sys

conf = configparser.ConfigParser()
conf.read('conf.ini')

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)
from src.utils import wait_dimension_exit
from src.target import get_dimension_content

job_run_time = int(conf['info']['job_run_time'])
    
def test_update_source_object(share_service_tm1):

    update_source_metarial()
    
    dimension_status = False
    dimension_list = []
    cube_status = False
    cube_list = []

    test_data = None

    with open(os.path.join(BASE_DIR, 'doc/testData.yaml'), 'r', encoding='utf-8') as f:
        
        test_data = yaml.safe_load(f)

    for _ in test_data:
        if 'Dimension' in _: dimension_list.append(_.get('Dimension'))
        elif 'Cube' in _: cube_list.append(_.get('Cube'))

    while not dimension_status:
        dimension_num = 0
        cube_num = 0
        for _ in dimension_list:
            try:
                assert share_service_tm1.elements.execute_set_mdx('{[Sys TM1 Object Dimension].[Sys TM1 Object Dimension].[%s]}' % _) != []
                dimension_num += 1
            except AssertionError:
                time.sleep(0.5)
        if dimension_num == dimension_list.__len__():dimension_status = True


    while not cube_status:
        cube_num = 0
        for _ in cube_list:
            try:
                assert share_service_tm1.elements.execute_set_mdx('{[Sys TM1 Object Cube].[Sys TM1 Object Cube].[%s]}' % _) != []
                dimension_num += 1
            except AssertionError:
                time.sleep(0.5)
        if cube_num == cube_list.__len__():cube_status = True

    assert dimension_status == True
    assert cube_status == True
    
def test_update_testing_material():
    
    assert update_sync_list() == 1
        
def test_ShareServiceCase0001(target_tm1, source_tm1):

    dimension_name = 'ShareServiceCase0001'
    
    wait_dimension_exit(target_tm1, dimension_name)

    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset') == source_dimension_content.get('Dimension Subset')
    
    # assert attribute
    assert target_dimension_content.get('Attribute') == source_dimension_content.get('Attribute')

    # assert attribute content
    assert target_dimension_content.get('Attribute Content') == source_dimension_content.get('Attribute Content')
    
    # for _ in range(1, 6):
    #     assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
    #     assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short]' % (dimension_name, dimension_name))]['Value'] == f'ShortAliasItem{str(_)}'
    #     assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'
    #     assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]' % (dimension_name, dimension_name))]['Value'] == _

def test_ShareServiceCase0002(target_tm1, source_tm1):

    '''
    Case Name: Sync Dimension,with mode “Sync Full Element, attribute name and subset name are empty
    '''
    dimension_name = 'ShareServiceCase0002'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset') == []
    
    # assert attribute
    assert target_dimension_content.get('Attribute') == []
    

def test_ShareServiceCase0003(target_tm1, source_tm1):
    
    '''
    Sync Dimension,with mode “Sync Full Element, attribute name equal to "Name Long,String Name"
    '''
    dimension_name = 'ShareServiceCase0003'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
        # assert subset
    assert target_dimension_content.get('Dimension Subset') == []
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 2
    assert 'Name Long' in target_dimension_content.get('Attribute')
    assert 'String Name' in target_dimension_content.get('Attribute')
    
    attribute_content = target_dimension_content.get('Attribute Content')
    
    for _ in range(1, 6):
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'

def test_ShareServiceCase0004(target_tm1, source_tm1):
    
    '''
      Case Name: Sync Dimension,with mode “Sync Full Element, subset name equal to "PublicSubset,PublicSubset2"
    '''
    dimension_name = 'ShareServiceCase0004'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')

    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']

    assert target_dimension_content.get('Attribute') == []
        

def test_ShareServiceCase0005(target_tm1, source_tm1):
    
    '''
    Case Name: Sync Dimension,with mode “Sync Full Dimension”, attribute name equal to "Name Long,String Name", subset name equal to "PublicSubset,PublicSubset2"    
    '''
    dimension_name = 'ShareServiceCase0005'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
        
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2
    
    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']

    # assert attribute
    assert target_dimension_content.get('Attribute') == ['Name Long','String Name']
    
    # assert attribute content
    attribute_content = target_dimension_content.get('Attribute Content')
    
    for _ in range(1, 6):
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'


def test_ShareServiceCase0006(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'FULL ELEMENT WITH ATTRS', empty subset name
    '''
    dimension_name = 'ShareServiceCase0006'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
        
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 0
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 4
    assert 'Name Long' in target_dimension_content.get('Attribute')
    assert 'Name Short' in target_dimension_content.get('Attribute')
    assert 'String Name' in target_dimension_content.get('Attribute')
    assert 'Numeric Attri' in target_dimension_content.get('Attribute')
    
    # assert attribute content
    assert target_dimension_content.get('Attribute Content') == source_dimension_content.get('Attribute Content')
    
def test_ShareServiceCase0007(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'FULL ELEMENT WITH ATTRS', with subset name "PublicSubset,PublicSubset2"
    '''
    dimension_name = 'ShareServiceCase0007'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)

    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2
    
    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 4
    assert 'Name Long' in target_dimension_content.get('Attribute')
    assert 'Name Short' in target_dimension_content.get('Attribute')
    assert 'String Name' in target_dimension_content.get('Attribute')
    assert 'Numeric Attri' in target_dimension_content.get('Attribute')
    
    # assert attribute content
    assert target_dimension_content.get('Attribute Content') == source_dimension_content.get('Attribute Content')

def test_ShareServiceCase0008(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'SYNC FULL ATTRS' and empty SUBSET NAME

    '''
    dimension_name = 'ShareServiceCase0008'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')

    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 0
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 4
    assert 'Name Long' in target_dimension_content.get('Attribute')
    assert 'Name Short' in target_dimension_content.get('Attribute')
    assert 'String Name' in target_dimension_content.get('Attribute')
    assert 'Numeric Attri' in target_dimension_content.get('Attribute')
    
    # assert attribute content
    assert target_dimension_content.get('Attribute Content') == source_dimension_content.get('Attribute Content')

def test_ShareServiceCase0009(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'ALL PUBLIC SUBSETS' and empty ATTRIBUTE NAME

    '''
    dimension_name = 'ShareServiceCase0009'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
        # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2
    
    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset1':
            assert _.get('Element') == ['Item1','Item3']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']

    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 0

def test_ShareServiceCase0010(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'ALL PUBLIC SUBSETS', with attribute name 'Name Long,String Name'

    '''
    dimension_name = 'ShareServiceCase0010'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
        # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 3
    
    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset1':
            assert _.get('Element') == ['Item1','Item3']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']

    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 2
    
    # assert attribute content
    attribute_content = target_dimension_content.get('Attribute Content')
    
    for _ in range(1, 6):
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'

def test_ShareServiceCase0011(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'USER DEFINE', with attribute name 'Name Long,String Name' subset name "PublicSubset,PublicSubset2"

    '''
    dimension_name = 'ShareServiceCase0011'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
        # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2

    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']

    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 2
    
    # assert attribute content
    attribute_content = target_dimension_content.get('Attribute Content')
    
    for _ in range(1, 6):
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'

def test_ShareServiceCase0012(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'USER DEFINE', with attribute name 'Name Long,String Name'

    '''
    dimension_name = 'ShareServiceCase0012'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 0
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 2
    
    # assert attribute content
    attribute_content = target_dimension_content.get('Attribute Content')
    
    for _ in range(1, 6):
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert attribute_content[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'

def test_ShareServiceCase0013(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'USER DEFINE', with SUBSET NAME "PublicSubset,PublicSubset2"

    '''
    dimension_name = 'ShareServiceCase0013'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)

    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 2

    # assert subset element
    for _ in target_dimension_content.get('Dimension Subset'):
        if _.get('Name') == 'PublicSubset':
            assert _.get('Element') == ['Item1','Item2']
        if _.get('Name') == 'PublicSubset2':
            assert _.get('Element') == ['Item1','Item4']
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 0

def test_ShareServiceCase0014(target_tm1, source_tm1):
    '''
    Case Name: Sync Dimension, with mode 'USER DEFINE'

    '''
    dimension_name = 'ShareServiceCase0014'
    
    wait_dimension_exit(target_tm1, dimension_name)
    
    target_dimension_content = get_dimension_content(target_tm1, dimension_name)
    source_dimension_content = get_dimension_content(source_tm1, dimension_name)
    # assert dimension
    assert target_dimension_content.get('Full Dimension') == source_dimension_content.get('Full Dimension')
    
    # asssert dimension elements
    assert target_dimension_content.get('Dimension Element') == source_dimension_content.get('Dimension Element')
    
    # assert Dimension Edges
    assert target_dimension_content.get('Dimension Edges') == source_dimension_content.get('Dimension Edges')
    
    # assert subset
    assert target_dimension_content.get('Dimension Subset').__len__() == 0
    
    # assert attribute
    assert target_dimension_content.get('Attribute').__len__() == 0