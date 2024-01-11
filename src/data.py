import os
import sys
from TM1py.Services import TM1Service
from TM1py.Objects import Dimension, Element, ElementAttribute, Hierarchy, Subset, Cube, NativeView
import configparser
import yaml
import datetime
import time

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.append(BASE_DIR)
conf_file_path = os.path.join(BASE_DIR, 'conf.ini')
test_data_yaml_file = os.path.join(BASE_DIR, 'doc/testData.yaml')

class TestingData:
    
    def __init__(self) -> None:
        conf = configparser.ConfigParser()
        conf.read(conf_file_path)
        
        self.source_tm1 = TM1Service(**conf['source'])
        self.target_tm1 = TM1Service(**conf['target'])
        self.share_service_tm1 = TM1Service(**conf['share_service'])
        self.source_instance_name = conf['info']['source_instance']
        self.target_instance_name = conf['info']['target_instance']
        self.job_id = conf['info']['share_service_job_id']
        self.job_name = conf['info']['share_service_job_id']

    def create_test_data(self) -> None:
        
        # create_share_service_job
        self.create_share_service_job()

        data_list:list = []

        with open(test_data_yaml_file, 'r', encoding='utf-8') as data_yaml:
            data_list = yaml.safe_load(data_yaml)

        metarical_dimension = []

        for data_item in data_list:
            if data_item.get('Type') == 'create_dimension':
                getattr(TestingData, data_item.get('Type'))(self.source_tm1, data_item)
                metarical_dimension.append(data_item.get('Dimension'))
        
        # update source materials in share service
        _process_name = "Sys.Sync.Dim.Sys TM1 Object.Update.Caller"
        _parameter = {
            'Parameters':[
                {
                    'Name':'pInstance',
                    'Value':'TEST_SOURCE_INSTANCE',
                },
                {
                    'Name':'pObjectType',
                    'Value':'All Types'
                }
            ]
        }
        self.share_service_tm1.processes.execute(_process_name, _parameter)
        
        time.sleep(30)
        
        # insert data to share service db
        self.insert_dimension_materials()
        
    def delete_test_data(self) -> None:
        data = None
        with open(os.path.join(BASE_DIR, 'doc/ShareServiceMaterials.yaml'), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # delete cube first
        cube_list = []
        for item in data:
            if item.get('Sync Type') == 'Cube': cube_list.append(item.get('Name'))
            
        for _ in cube_list:
            try:
                self.source_tm1.cubes.delete(cube_name=item.get('Name'))
            except:
                pass
            try:
                self.target_tm1.cubes.delete(cube_name=item.get('Name'))
            except:
                pass
        
        # delete dimension
        for item in data:
            if item.get('Sync Type') == 'Dimension':
                try:
                    self.source_tm1.dimensions.delete(dimension_name=item.get('Name'))
                except:
                    pass
                try:
                    self.target_tm1.dimensions.delete(dimension_name=item.get('Name'))
                except:
                    pass
        # delete job
        _process_name = "Sys.Sync.Dim.Sys Sync Job.Add"
        _parameter = {
            'Parameters':[
                {
                    'Name':'pJobID',
                    'Value':self.job_id,
                },
                {
                    'Name':'pSyncJob',
                    'Value':self.job_id,
                },
                {
                    'Name':'pMode',
                    'Value':'2',
                }
            ]
        }
        self.share_service_tm1.processes.execute(_process_name, _parameter)
        
    def create_share_service_job(self):

        _process_name = "Sys.Sync.Dim.Sys Sync Job.Add"
        _parameter = {
            'Parameters':[
                {
                    'Name':'pJobID',
                    'Value':self.job_id,
                },
                {
                    'Name':'pSyncJob',
                    'Value':self.job_id,
                },
                {
                    'Name':'pMode',
                    'Value':'1',
                }
            ]
        }
        self.share_service_tm1.processes.execute(_process_name, _parameter)
    
        cellset = {}
    
        cellset[(self.job_id, 'SOURCE TM1 SERVER')] = self.source_instance_name
    
        self.share_service_tm1.cells.write_values('}ElementAttributes_Sys Sync Job', cellset)
    
        cellset = {}
    
        cellset[(self.target_instance_name, f'{self.job_id} - {self.job_name}', 'Selected')] = 1
    
        self.share_service_tm1.cells.write_values('Sys Sync Definition Target Instance', cellset)
        
        job_status = False

        while not job_status:
        
            try:
                assert self.share_service_tm1.elements.execute_set_mdx('{[Sys Sync Job].[Sys Sync Job].[%s]}' % self.job_id) != []
                job_status = True
            except AssertionError:
                time.sleep(0.5)
        

    def execute_job(self):
        
        _process_name = "Sys.Sync.Generate Sync Job.Caller"
        _parameter = {
            'Parameters':[
                {
                    'Name':'pSyncJob',
                    'Value':self.job_id,
                },
                {
                    'Name':'pClientExecute',
                    'Value':"cubewise.com/Carson Li",
                },
                {
                    'Name': 'pParallelCount',
                    'Value': ''
                }
                ]

        }
        self.share_service_tm1.processes.execute(_process_name, _parameter)
        
    
    def run_sync_job(self):
        
        self.share_service_tm1.processes.execute(
            "Sys.sync.Dim.Sys TM1 Object.Update.Caller",
            {
                'Parameters':[
                    {
                        'Name':'pInstance',
                        'Value':'TEST_SOURCE_INSTANCE'
                    },
                    {
                        'Name':'pObjectType',
                        'Value':'All Types'
                    }
                ]
            }
        )

    @staticmethod
    def create_dimension(tm1_object:object, data:dict=None):

        dimension = data.get('Dimension')
        # Define elements
        elements = [Element(name=_.split('@')[0], element_type=_.split('@')[1]) for _ in data.get('Element').split(',') if data.get('Element') != '']
        # Define element edges
        edges = {}
        for _ in data.get('Edge').split(','): edges[(_.split('@')[0], _.split('@')[1])] = 1
        # Define Attribute
        element_attribute = [ElementAttribute(name=_.split('@')[0],attribute_type=_.split('@')[1]) for _ in data.get('Attribute').split(',')]
        # Create dimension 
        tm1_object.dimensions.create(
            Dimension(
                name=dimension,
                hierarchies=[
                    Hierarchy(
                        name=dimension, 
                        dimension_name=dimension, 
                        elements=elements, 
                        edges=edges, 
                        element_attributes=element_attribute
                    )
                ]
            )
        )

        # Create Subset
        for _ in data.get('Subset'):
            tm1_object.subsets.create(
                subset=Subset(
                    dimension_name=dimension,
                    subset_name=_.get('Name'),
                    alias=_.get('Alias'),
                    elements=[item for item in _.get('Element').split(',')]
                ),
                private=_.get('Private')
            )
        
        # Update Attribute content
        Attribute_Cube_Name = '}ElementAttributes_' + dimension
        cellset = {}
        for _ in data.get('AttributeContent').split(','):
            cellset[(_.split('=')[0].split('@')[0], _.split('=')[0].split('@')[1])] = int(_.split('=')[1]) if _.split('=')[1].isdigit() else _.split('=')[1]
            
        tm1_object.cubes.cells.write_values(Attribute_Cube_Name, cellset)
    
    def insert_dimension_materials(self):
        
        data = None
        with open(os.path.join(BASE_DIR, 'doc/ShareServiceMaterials.yaml'), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        dimension_cellset = {}
        cube_cellset = {}

        for item in data:
            if item.get('Sync Type') == 'Dimension':
                dimension_cellset[(self.target_instance_name, self.job_id, item.get('Name'), 'SYNC MODE')] = item.get('Sync Mode')

            if 'Attribute Name' in item:
                dimension_cellset[(self.target_instance_name, self.job_id, item.get('Name'),'ATTRIBUTE NAME')] = item.get('Attribute Name')
            
            if 'Subset Name' in item:
                dimension_cellset[(self.target_instance_name, self.job_id, item.get('Name'),'SUBSET NAME')] = item.get('Subset Name')
                
            if 'Sync Elements In Subset' in item:
                dimension_cellset[(self.target_instance_name, self.job_id, item.get('Name'),'SYNC ELEMENTS IN SUBSET')] = 'Y'
            elif item.get('Sync Type') == 'Cube':
                pass

        self.share_service_tm1.cells.write_values('Sys Sync Definition Dimension', dimension_cellset)