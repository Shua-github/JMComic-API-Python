from os.path import exists, join

# 函数：检查文件是否存在
def file_if(file_path: str) -> bool:
    if exists(file_path):
        return True
    return False  # 如果文件不存在，则返回 False

# 函数：拼接路径
def file_path_join(path_list: list) -> str:
    return join(*path_list)