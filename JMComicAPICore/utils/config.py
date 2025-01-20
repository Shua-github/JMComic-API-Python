from yaml import safe_load
from os.path import exists
from os import makedirs
from jmcomic import create_option_by_str as read_jm_option
from typing import Union

# 默认 jm 配置
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

class Config:
    def __init__(self, config_path: str):
        """构造函数，读取配置文件并初始化配置"""
        self.config_path = config_path
        self.config = self._read_config(config_path=config_path)  # 将返回的配置保存为实例变量

    @staticmethod
    def open_config(config_path: str):
        """打开yaml配置文件并返回字典"""
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return safe_load(file)  # 这里返回的是已经解析过的字典
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        except Exception as e:
            raise RuntimeError(f"读取配置文件时发生错误: {e}")

    def _read_config(self, config_path: str):
        """读取并解析配置文件"""
        try:
            # 读取配置文件内容
            file = self.open_config(config_path)

            # 临时配置，存储临时文件路径
            self.temp_image = file["core"]["temp_image"]  # 确保这里读取正确
            self.temp_output = file["core"]["temp_output"]  # 确保这里读取正确

            # 配置 jmcomic
            jm = file["jm"]
            if file["core"]["jm_switch"]:
                jm_config = read_jm_option(jm)  # 根据配置调用 jmcomic 配置
            else:
                # 如果未开启 jm_switch, 使用默认的配置并合并
                custom_jm_config = default_jm_config.copy()
                custom_jm_config["dir_rule"]["base_dir"] = self.temp_image
                custom_jm_config["plugins"]["after_album"][0]["kwargs"]["pdf_dir"] = self.temp_output
                custom_jm_config["plugins"]["after_album"][1]["kwargs"]["zip_dir"] = self.temp_output
                jm_config = read_jm_option(str(custom_jm_config))

            # 确保必要的目录存在
            if not exists(self.temp_output):
                makedirs(self.temp_output)
            if not exists(self.temp_image):
                makedirs(self.temp_image)

            # 保存并返回配置
            self.jm_config = jm_config
            self.supported_formats = file["core"]["supported_formats"]

        except KeyError as e:
            raise KeyError(f"配置文件缺少必要的字段: {e}")
        except Exception as e:
            raise RuntimeError(f"读取配置时发生错误: {e}")
