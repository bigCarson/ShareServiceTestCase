import os
import sys
import configparser
import yaml
conf = configparser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
conf.read(os.path.join(BASE_DIR, 'conf.ini'))
ShareServiceMaterials_path = os.path.join(BASE_DIR, 'doc/ShareServiceMaterials.yaml')
from TM1py.Services import TM1Service

def create_job():

    job_id = conf['info']['share_service_job_id']
    job_name = conf['info']['share_service_job_id']
    source_instance_name = conf['info']['source_instance']
    target_instance_name = conf['info']['target_instance']
    share_service_tm1 = TM1Service(**conf['share_service'])

    _process_name = "Sys.Sync.Dim.Sys Sync Job.Add"
    _parameter = {
        'Parameters':[
            {
                'Name':'pJobID',
                'Value':job_id,
            },
            {
                'Name':'pSyncJob',
                'Value':job_id,
            },
            {
                'Name':'pMode',
                'Value':'1',
            }
        ]
    }
    share_service_tm1.processes.execute(_process_name, _parameter)

    cellset = {}

    cellset[(job_id, 'SOURCE TM1 SERVER')] = source_instance_name

    share_service_tm1.cells.write_values('}ElementAttributes_Sys Sync Job', cellset)

    cellset = {}

    cellset[(target_instance_name, f'{job_id} - {job_name}', 'Selected')] = 1

    share_service_tm1.cells.write_values('Sys Sync Definition Target Instance', cellset)

    share_service_tm1.logout()

    return job_id


def update_source_metarial():

    share_service_tm1 = TM1Service(**conf['share_service'])

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

    share_service_tm1.processes.execute(_process_name, _parameter)
    share_service_tm1.logout()
    
def update_sync_list():
    
    target_instance = conf['info']['target_instance']
    _test_job_id = conf['info']['share_service_job_id']

    # dimension
    materials = None
    share_service_tm1 = TM1Service(**conf['share_service'])
    with open(ShareServiceMaterials_path, "r", encoding='utf-8') as f:
        materials = yaml.safe_load(f.read())
    
    cellset = {}
    for _ in materials:
        if _.get('Sync Type') == 'Dimension':
            cellset[(target_instance, _test_job_id, _.get('Name'), 'SYNC MODE')] = _.get('Sync Mode')
            
            if 'Attribute Name' in _:
                cellset[(target_instance, _test_job_id, _.get('Name'),'ATTRIBUTE NAME')] = _.get('Attribute Name')
            
            if 'Subset Name' in _:
                cellset[(target_instance, _test_job_id, _.get('Name'),'SUBSET NAME')] = _.get('Subset Name')
                
            if 'Sync Elements In Subset' in _:
                cellset[(target_instance, _test_job_id, _.get('Name'),'SYNC ELEMENTS IN SUBSET')] = 'Y'
                
    share_service_tm1.cells.write_values('Sys Sync Definition Dimension', cellset)
    
    # logout
    share_service_tm1.logout()
    
    return 1




        