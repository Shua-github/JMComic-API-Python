from .file import file_if,file_path_join
from .config import Config
def temp_if(file_name,config_path):
    config = Config(config_path=config_path)
    file_path = file_path_join([config.temp_output,file_name])
    if file_if(file_path=file_path):
        return True
    return False
