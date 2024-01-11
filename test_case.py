import os
import pytest
import yaml
import datetime
import time
from src.target import *
import configparser
import datetime

conf = configparser.ConfigParser()
conf.read('conf.ini')

BASE_DIR = os.path.dirname(__file__)
job_run_time = int(conf['info']['job_run_time'])

def test_create_job(share_service_tm1):

    job_id = create_job()

    current_time = datetime.datetime.now()

    job_status = False

    while (datetime.datetime.now() - current_time).seconds < 120:
        
        try:
            assert share_service_tm1.elements.execute_set_mdx('{[Sys Sync Job].[Sys Sync Job].[%s]}' % job_id) != []
            job_status = True
        except AssertionError:
            time.sleep(0.5)

    assert job_status == True

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
    '''
    Sync Dimension, with mode “Full Dimension”
    '''
    dimension_name = 'ShareServiceCase0001'
    
    exit_sign = False
    start_time = datetime.datetime.now()
    while not exit_sign:
        time.sleep(10)
        exit_sign = target_tm1.dimensions.exists(dimension_name=dimension_name)
        if (datetime.datetime.now() - start_time).seconds > job_run_time: raise RuntimeError(f"Job execute time more than {str(job_run_time)} second")


    # assert dimension
    target_dimension = target_tm1.dimensions.get(dimension_name)
    source_dimension = source_tm1.dimensions.get(dimension_name)
    assert target_dimension == source_dimension

    # assert dimension element
    target_dimension_elements = target_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements = source_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements == source_dimension_elements

    # assert dimension elements edges
    target_dimension_elements_edges = target_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements_edges = source_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements_edges == source_dimension_elements_edges

    # assert subset
    target_dimension_subset = target_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_subset = source_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_subset == source_dimension_subset
    for _target_subset_item, _source_subset_item in zip(target_dimension_subset, source_dimension_subset):
        assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item) == source_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_source_subset_item)
    
    
    # assert attribute
    target_dimension_attribute = target_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_attribute = source_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_attribute == source_dimension_attribute
 
    _mdx = '''
            SELECT
            {[}ElementAttributes_%s].[}ElementAttributes_%s].Members}
            ON COLUMNS ,
            {[%s].[%s].Members}
            ON ROWS
            FROM [}ElementAttributes_%s]
            ''' % (dimension_name, dimension_name, dimension_name, dimension_name, dimension_name)
            
    assert target_tm1.cells.execute_mdx(_mdx) == source_tm1.cells.execute_mdx(_mdx)
    
    _mdx = '''
            SELECT
            {[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long],[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short],[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri],[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]}
            ON COLUMNS ,
            {[%s].[%s].Members}
            ON ROWS
            FROM [}ElementAttributes_%s]
            ''' % (dimension_name, dimension_name, dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name)
    
    mdx_result = target_tm1.cells.execute_mdx(_mdx)
    
    for _ in range(1, 6):
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short]' % (dimension_name, dimension_name))]['Value'] == f'ShortAliasItem{str(_)}'
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]' % (dimension_name, dimension_name))]['Value'] == _


def test_ShareServiceCase0002(target_tm1, source_tm1):

    '''
    Case Name: Sync Dimension,with mode “Sync Full Dimension”, attribute name and subset name are empty
    '''
    dimension_name = 'ShareServiceCase0002'
    
    exit_sign = False
    start_time = datetime.datetime.now()
    while not exit_sign:
        time.sleep(10)
        exit_sign = target_tm1.dimensions.exists(dimension_name=dimension_name)
        if (datetime.datetime.now() - start_time).seconds > job_run_time: raise RuntimeError(f"Job execute time more than {str(job_run_time)} second")
        
    
        # assert dimension
    target_dimension = target_tm1.dimensions.get(dimension_name)
    source_dimension = source_tm1.dimensions.get(dimension_name)
    assert target_dimension == source_dimension
    
        # assert dimension element
    target_dimension_elements = target_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements = source_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements == source_dimension_elements
    
        # assert dimension elements edges
    target_dimension_elements_edges = target_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements_edges = source_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements_edges == source_dimension_elements_edges
    
        # assert subset
    target_dimension_subset = target_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_subset = source_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_subset == source_dimension_subset

    for _target_subset_item in target_dimension_subset:
        assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item)
    for _target_subset_item, _source_subset_item in zip(target_dimension_subset, source_dimension_subset):
        assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item) != source_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_source_subset_item)
    
    
        # assert attribute
    target_dimension_attribute = target_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_attribute = source_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_attribute == source_dimension_attribute
    
    _mdx = '''
        SELECT
        {[}ElementAttributes_%s].[}ElementAttributes_%s].Members}
        ON COLUMNS ,
        {[%s].[%s].Members}
        ON ROWS
        FROM [}ElementAttributes_%s]
        ''' % (dimension_name, dimension_name, dimension_name, dimension_name, dimension_name)
            
    assert target_tm1.cells.execute_mdx(_mdx) == source_tm1.cells.execute_mdx(_mdx)
    
    _mdx = '''
            SELECT
            {[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long],[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short],[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri],[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]}
            ON COLUMNS ,
            {[%s].[%s].Members}
            ON ROWS
            FROM [}ElementAttributes_%s]
            ''' % (dimension_name, dimension_name, dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name)
    
    mdx_result = target_tm1.cells.execute_mdx(_mdx)
    for _ in range(1, 6):
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]' % (dimension_name, dimension_name))]['Value'] == ''


def test_ShareServiceCase0003(target_tm1, source_tm1):
    
    '''
    Sync Dimension,with mode “Sync Full Dimension”, attribute name equal to "Name Long,String Name"
    '''
    dimension_name = 'ShareServiceCase0003'
    
    exit_sign = False
    start_time = datetime.datetime.now()
    while not exit_sign:
        time.sleep(10)
        exit_sign = target_tm1.dimensions.exists(dimension_name=dimension_name)
        if (datetime.datetime.now() - start_time).seconds > job_run_time: raise RuntimeError(f"Job execute time more than {str(job_run_time)} second")
        
        # assert dimension
    target_dimension = target_tm1.dimensions.get(dimension_name)
    source_dimension = source_tm1.dimensions.get(dimension_name)
    assert target_dimension == source_dimension
    
        # assert dimension element
    target_dimension_elements = target_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements = source_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements == source_dimension_elements
    
        # assert dimension elements edges
    target_dimension_elements_edges = target_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements_edges = source_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements_edges == source_dimension_elements_edges
    
        # assert subset
    target_dimension_subset = target_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_subset = source_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_subset == source_dimension_subset
    for _target_subset_item, _source_subset_item in zip(target_dimension_subset, source_dimension_subset):
        assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item) != source_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_source_subset_item)
    
        # assert attribute
    target_dimension_attribute = target_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_attribute = source_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_attribute == source_dimension_attribute
    
    _mdx = '''
        SELECT
        {[}ElementAttributes_%s].[}ElementAttributes_%s].Members}
        ON COLUMNS ,
        {[%s].[%s].Members}
        ON ROWS
        FROM [}ElementAttributes_%s]
        ''' % (dimension_name, dimension_name, dimension_name, dimension_name, dimension_name)
            
    assert target_tm1.cells.execute_mdx(_mdx) == source_tm1.cells.execute_mdx(_mdx)
    
    _mdx = '''
            SELECT
            {[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long],[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short],[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri],[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]}
            ON COLUMNS ,
            {[%s].[%s].Members}
            ON ROWS
            FROM [}ElementAttributes_%s]
            ''' % (dimension_name, dimension_name, dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name)
    
    mdx_result = target_tm1.cells.execute_mdx(_mdx)
    for _ in range(1, 6):
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == f'LongAliasItem{str(_)}'
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == f'String AttriItem{str(_)}'
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]' % (dimension_name, dimension_name))]['Value'] == ''

def test_ShareServiceCase0004(target_tm1, source_tm1):
    
    '''
      Case Name: Sync Dimension,with mode “Sync Full Dimension”, subset name equal to "PublicSubset,PublicSubset2"
    '''
    dimension_name = 'ShareServiceCase0004'
    
    exit_sign = False
    start_time = datetime.datetime.now()
    while not exit_sign:
        time.sleep(10)
        exit_sign = target_tm1.dimensions.exists(dimension_name=dimension_name)
        if (datetime.datetime.now() - start_time).seconds > job_run_time: raise RuntimeError(f"Job execute time more than {str(job_run_time)} second")

        # assert dimension
    target_dimension = target_tm1.dimensions.get(dimension_name)
    source_dimension = source_tm1.dimensions.get(dimension_name)
    assert target_dimension == source_dimension
    
        # assert dimension element
    target_dimension_elements = target_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements = source_tm1.elements.get_elements(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements == source_dimension_elements
    
        # assert dimension elements edges
    target_dimension_elements_edges = target_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_elements_edges = source_tm1.elements.get_edges(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_elements_edges == source_dimension_elements_edges
    
        # assert subset
    target_dimension_subset = target_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_subset = source_tm1.subsets.get_all_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_subset == source_dimension_subset
    for _target_subset_item, _source_subset_item in zip(target_dimension_subset, source_dimension_subset):
        assert target_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_target_subset_item) == source_tm1.subsets.get_element_names(dimension_name=dimension_name, hierarchy_name=dimension_name, subset_name=_source_subset_item)
    
        # assert attribute
    target_dimension_attribute = target_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    source_dimension_attribute = source_tm1.elements.get_element_attribute_names(dimension_name=dimension_name, hierarchy_name=dimension_name)
    assert target_dimension_attribute == source_dimension_attribute
    
    _mdx = '''
        SELECT
        {[}ElementAttributes_%s].[}ElementAttributes_%s].Members}
        ON COLUMNS ,
        {[%s].[%s].Members}
        ON ROWS
        FROM [}ElementAttributes_%s]
        ''' % (dimension_name, dimension_name, dimension_name, dimension_name, dimension_name)
            
    assert target_tm1.cells.execute_mdx(_mdx) == source_tm1.cells.execute_mdx(_mdx)
    
    _mdx = '''
            SELECT
            {[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long],[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short],[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri],[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]}
            ON COLUMNS ,
            {[%s].[%s].Members}
            ON ROWS
            FROM [}ElementAttributes_%s]
            ''' % (dimension_name, dimension_name, dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name,dimension_name)
    
    mdx_result = target_tm1.cells.execute_mdx(_mdx)
    for _ in range(1, 6):
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Long]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Name Short]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[String Attri]' % (dimension_name, dimension_name))]['Value'] == ''
        assert mdx_result[(f'[{dimension_name}].[{dimension_name}].[Item{str(_)}]', '[}ElementAttributes_%s].[}ElementAttributes_%s].[Numeric Attri]' % (dimension_name, dimension_name))]['Value'] == ''