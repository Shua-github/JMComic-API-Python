import argparse
import os
import shutil
from pathlib import Path
from yaml import safe_load, dump
from importlib.resources import files  # 替换 pkg_resources
from .JMComicAPICore import run
import platform


class Config:
    def __init__(self, host, port, core_path):
        self.host = host
        self.port = port
        self.core_path = core_path

    @classmethod
    def from_dict(cls, config_dict: dict):
        """从字典创建 Config 实例"""
        server_config: dict = config_dict.get('net')
        host = server_config.get('host')
        port = server_config.get('port')
        core_path = config_dict.get('core_config_path')
        return cls(host, port, core_path)

class ConfigManager:
    @staticmethod
    def get_default_dir():
        system = platform.system()
        if system == 'Windows':
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / 'jmcomic_api'
            else:
                # Fallback for Windows without APPDATA (unlikely)
                return Path.home() / 'AppData' / 'Roaming' / 'jmcomic_api'
        else:
            # Linux, macOS, etc.
            return Path.home() / '.config' / 'jmcomic_api'
        
    DEFAULT_DIR = get_default_dir()
    CONFIG_FILES = ['RunConfig.yml', 'CoreConfig.yml']

    def __init__(self):
        self.args = self._parse_args()
        self.config_path = self._get_config_path()
        self._ensure_configs_exist()
        self.config = self._read_config()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="JMComic API 配置管理器")
        parser.add_argument('-c', '--config', action='store_true', help='自定义配置文件路径')

        return parser.parse_args()

    def _get_config_path(self):
        if self.args.config:
            return Path(self.args.config)
        return self.DEFAULT_DIR / 'RunConfig.yml'

    def _ensure_configs_exist(self):
        """确保所有配置文件存在"""
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        for file in self.CONFIG_FILES:
            target_path = config_dir / file
            if not target_path.exists():
                self._copy_config_from_package(file, target_path)

    def _copy_config_from_package(self, filename: str, target_path: Path):
        """从包内拷贝默认配置文件"""
        try:
            # 使用 importlib.resources 替换 pkg_resources
            source_path = files("jmcomic_api.data").joinpath(filename)
            shutil.copy(source_path, str(target_path))

            if filename == 'RunConfig.yml':
                self._update_core_config_path(target_path)
            elif filename == 'CoreConfig.yml':
                self._update_temp_paths(target_path)

        except Exception as e:
            raise RuntimeError(f"无法拷贝配置文件 {filename}: {str(e)}")

    def _update_core_config_path(self, run_config_path: Path):
        """更新 RunConfig.yml 中的 core_config_path 字段"""
        try:
            core_config_path = run_config_path.parent / 'CoreConfig.yml'
            with open(run_config_path, 'r',encoding="utf-8") as f:
                config = safe_load(f)

            config['core_config_path'] = str(core_config_path)
            with open(run_config_path, 'w',encoding="utf-8") as f:
                dump(config, f)

        except Exception as e:
            raise RuntimeError(f"更新 RunConfig.yml 的 core_config_path 失败: {str(e)}")

    def _update_temp_paths(self, core_config_path: Path):
        """更新 CoreConfig.yml 中的 temp_output 和 temp_image 路径"""
        try:
            # 读取配置文件，确保使用 UTF-8 编码
            with open(core_config_path, 'r', encoding='utf-8') as f:
                config = safe_load(f)

            # 确保 'core' 部分存在
            if 'core' not in config:
                config['core'] = {}

            # 更新 temp_output 和 temp_image 路径
            config['core']['temp_output'] = str(self.DEFAULT_DIR / 'temp_output')
            config['core']['temp_image'] = str(self.DEFAULT_DIR / 'temp_image')

            # 写入配置文件，确保使用 UTF-8 编码
            with open(core_config_path, 'w', encoding='utf-8') as f:
                dump(config, f)
        except Exception as e:
            raise RuntimeError(f"更新 CoreConfig.yml 的 temp_output 和 temp_image 路径失败: {str(e)}")

    def _read_config(self):
        """读取并返回配置对象"""
        try:
            with open(self.config_path, 'r',encoding="utf-8") as f:
                config_dict = safe_load(f)

            core_config_path = Path(config_dict.get('core_config_path', ''))
            if not core_config_path.exists():
                raise FileNotFoundError(f"核心配置文件不存在: {core_config_path}")

            return Config.from_dict(config_dict)

        except Exception as e:
            raise RuntimeError(f"读取配置文件失败: {str(e)}")

if __name__ == '__main__':
    try:
        manager = ConfigManager()
        
        # 输出配置信息
        print(f"Host: {manager.config.host},Port: {manager.config.port},")
        print(f"RunConfig Path: {manager.config_path}")
        print(f"CoreConfig Path: {manager.config.core_path}")

        # 启动 JMComic API
        run(
            config_path=manager.config.core_path,
            host=manager.config.host,
            port=manager.config.port
        )
    except Exception as e:
        print(f"启动失败: {e}")
        exit(1)