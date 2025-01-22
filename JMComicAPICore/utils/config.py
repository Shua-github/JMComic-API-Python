from yaml import safe_load
from .file import file_if
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
        """
        初始化 Config 类，读取配置文件并初始化配置参数。

        参数:
        - config_path (str): 配置文件的路径
        """
        self.config_path = config_path
        self.config = self._read_config(config_path=config_path)  # 调用读取配置文件的方法

    @staticmethod
    def open_config(config_path: str):
        """
        打开并读取 YAML 配置文件。

        参数:
        - config_path (str): 配置文件路径

        返回:
        - dict: 解析后的配置字典
        """
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return safe_load(file)  # 返回解析后的字典
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        except Exception as e:
            raise RuntimeError(f"读取配置文件时发生错误: {e}")

    def _create_directory(self, directory: str):
        """
        确保目录存在，如果不存在则创建。

        参数:
        - directory (str): 目录路径
        """
        if not file_if(directory):
            makedirs(directory)

    def _read_config(self, config_path: str):
        """
        读取并解析配置文件内容。

        参数:
        - config_path (str): 配置文件路径

        返回:
        - dict: 配置字典

        异常：
        - KeyError: 如果配置文件缺少必需的字段
        - RuntimeError: 其他错误
        """
        try:
            # 读取配置文件
            file = self.open_config(config_path)

            # 从配置中提取临时路径配置
            self.temp_image = file["core"]["temp_image"]
            self.temp_output = file["core"]["temp_output"]

            # 配置 jmcomic
            jm = file["jm"]
            if file["core"]["jm_switch"]:
                # 如果启用 jm_switch，读取 jmcomic 配置
                jm_config = read_jm_option(jm)
            else:
                # 如果禁用 jm_switch，使用默认配置并合并
                custom_jm_config = default_jm_config.copy()
                custom_jm_config["dir_rule"]["base_dir"] = self.temp_image
                custom_jm_config["plugins"]["after_album"][0]["kwargs"]["pdf_dir"] = self.temp_output
                custom_jm_config["plugins"]["after_album"][1]["kwargs"]["zip_dir"] = self.temp_output
                jm_config = read_jm_option(str(custom_jm_config))

            # 确保必要的目录存在
            self._create_directory(self.temp_output)
            self._create_directory(self.temp_image)

            # 保存最终的 jm 配置和支持的文件格式
            self.jm_config = jm_config
            self.supported_formats = file["core"]["supported_formats"]

        except KeyError as e:
            raise KeyError(f"配置文件缺少必要的字段: {e}")
        except Exception as e:
            raise RuntimeError(f"读取配置时发生错误: {e}")
