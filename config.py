from yaml import safe_load
from collections import namedtuple
from os.path import exists
from os import makedirs
from jmcomic import create_option_by_str as read_jm_option

# 内置 jm 配置
default_jm_config = {
    "dir_rule": {"base_dir": ""},
    "download": {"image": {"decode": True, "suffix": ".jpg"}},
    "log": True,
    "plugins": {
        "after_album": [
            {"plugin": "img2pdf", "kwargs": {"pdf_dir": "", "filename_rule": "Aid"}},
            {"plugin": "zip", "kwargs": {"level": "album", "filename_rule": "Aid", "zip_dir": "", "delete_original_file": True}}
        ]
    },
    "version": "2.1"
}

# 读取 YAML 配置文件
def open_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return safe_load(file)  # 这里返回的是已经解析过的字典
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {file_path}")
    except Exception as e:
        raise RuntimeError(f"读取配置文件时发生错误: {e}")

def read_config():
    try:
        file = open_config("config.yml")

        # 定义命名元组以存储配置
        NetConfig = namedtuple("NetConfig", ["port", "host"])
        TempConfig = namedtuple("TempConfig", ["image", "output"])
        MainConfig = namedtuple("MainConfig", ["net", "temp", "jm"])

        # 解析网络和临时配置
        net_config = NetConfig(port=file["app"]["port"], host=file["app"]["host"])
        temp_config = TempConfig(image=file["app"]["temp_image"], output=file["app"]["temp_output"])

        # 配置 jmcomic
        jm = file["jm"]
        if file["app"]["jm_switch"]:
            jm_config = read_jm_option(jm)
        else:
            custom_jm_config = default_jm_config.copy()
            custom_jm_config["dir_rule"]["base_dir"] = temp_config.image
            custom_jm_config["plugins"]["after_album"][0]["kwargs"]["pdf_dir"] = temp_config.output
            custom_jm_config["plugins"]["after_album"][1]["kwargs"]["zip_dir"] = temp_config.output
            jm_config = read_jm_option(str(custom_jm_config))

        # 确保必要的目录存在
        if not exists(temp_config.output):
            makedirs(temp_config.output)
        if not exists(temp_config.image):
            makedirs(temp_config.image)

        return MainConfig(net=net_config, temp=temp_config, jm=jm_config)
    except KeyError as e:
        raise KeyError(f"配置文件缺少必要的字段: {e}")
    except Exception as e:
        raise RuntimeError(f"读取配置时发生错误: {e}")