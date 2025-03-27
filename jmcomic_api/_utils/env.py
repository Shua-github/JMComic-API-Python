import os
from jmcomic import create_option_by_str

def get_dev_mode() -> bool:
    """
    获取是否为开发模式
    """
    return os.getenv('DEV','').lower() == 'true'  

dev_mode = get_dev_mode()  

JM_CONFIG = '''
client:
  impl: api
'''

JM_CONFIG = create_option_by_str(JM_CONFIG)