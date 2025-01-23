from JMComicAPICore import run
from yaml import safe_load
class Config:
    def __init__(self, host, port, core_path):
        self.host = host
        self.port = port
        self.core_path = core_path

    @classmethod
    def from_dict(cls, config_dict:dict):
        """从字典创建 Config 实例"""
        server_config:dict = config_dict.get('net')
        host = server_config.get('host')
        port = server_config.get('port')
        core_path = config_dict.get('core_config_path')
        return cls(host, port, core_path)

# 读取 YAML 配置文件并返回 Config 实例
def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config_dict = safe_load(file)
        return Config.from_dict(config_dict)
    except FileNotFoundError:
        exit("配置文件丢失")

if __name__ == '__main__':
    config = read_config('RunConfig.yml')  # 加载配置文件
    run(config_path=config.core_path,host=config.host,port=config.port) # 启动服务器
