import platform
from typing import Optional, List, Dict
from pathlib import Path
import os
import yaml
from pydantic import BaseModel

def get_default_dir() -> Path:
    """获取默认配置文件目录"""
    system: str = platform.system()
    
    if system == 'Windows':
        appdata: Optional[str] = os.getenv('APPDATA')
        if appdata:
            return Path(appdata) / 'jmcomic_api'
        else:
            # Fallback for Windows without APPDATA (unlikely)
            return Path.home() / 'AppData' / 'Roaming' / 'jmcomic_api'
    else:
        # Linux, macOS, etc.
        config_dir = Path.home() / '.config' / 'jmcomic_api'
        config_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        return config_dir
    
class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 5000

class RouteConfig(BaseModel):
    GetFile: Optional[Dict[str, str]] = {"output_dir": f'{str(get_default_dir() / 'temp_output')}'}

class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    routes: List[RouteConfig] = [RouteConfig()]

def load_config() -> AppConfig:
    """加载配置文件，如果不存在则使用默认值并释放默认配置"""
    config_path = get_default_dir() / "config.yaml"
    print(f'Config.yml Path: {str(config_path)}')
    if not config_path.exists():
        default_config = AppConfig()
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config.model_dump(), f, allow_unicode=True)
        return default_config
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return AppConfig(**config_data)