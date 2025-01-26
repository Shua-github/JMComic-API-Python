from os.path import exists, join
from typing import List

def file_if(file_path: str) -> bool:
    """判断指定路径的文件是否存在。

    参数:
    - file_path (str): 文件路径。

    返回:
    - bool: 如果文件存在，返回 True；否则返回 False。
    """
    return exists(file_path)

def file_path_join(path_list: List[str]) -> str:
    """将路径列表按顺序拼接成完整路径，并检查文件是否存在。

    参数:
    - path_list (List[str]): 路径组件列表。

    返回:
    - str: 拼接后的完整路径。。
    """
    full_path = join(*path_list)
    if not exists(full_path):
        raise FileNotFoundError(f"The file at path '{full_path}' does not exist.")
    return full_path

def combine_files(input_paths: List[str], output_path: str) -> bool:
    """将多个文件拼接到一个目标文件中。

    参数:
    - input_paths (List[str]): 输入文件路径列表。
    - output_path (str): 目标文件路径。

    返回:
    - bool: 如果操作成功，返回 True。

    异常:
    - FileExistsError: 如果目标文件已经存在，会抛出此错误。
    """
    # 检查目标文件是否已经存在
    if file_if(output_path):
        raise FileExistsError(f"文件 {output_path} 已经存在")
    
    # 打开目标文件，使用二进制写入模式 ('wb')
    with open(output_path, 'wb') as dest:
        for file in input_paths:
            # 逐个读取输入文件并写入目标文件
            with open(file, 'rb') as src:
                while chunk := src.read(1024):  # 每次读取 1024 字节
                    dest.write(chunk)
    
    return True
