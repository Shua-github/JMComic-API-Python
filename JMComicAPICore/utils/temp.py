from .file import file_if, file_path_join
from .config import Config

def temp_if(file_names: list, config_path: str) -> dict:
    """
    判断本地是否缓存了指定的文件列表，并以字典形式返回每个文件的存在状态

    参数:
    - file_names (list): 要检查的文件名列表
    - config_path (str): 配置文件的路径，包含临时输出文件夹的路径

    返回:
    - dict: 键为文件名，值为布尔值，表示每个文件是否存在
    """
    # 创建 Config 实例，并传入配置路径
    config = Config(config_path=config_path)
    
    # 构造字典，键是文件名，值是文件是否存在的布尔值
    data = {}
    for file_name in file_names:
        try:
            file_path_join([config.temp_output, file_name])
        except FileNotFoundError:
            data[file_name] = False
        else:
            data[file_name] = True
    return data
