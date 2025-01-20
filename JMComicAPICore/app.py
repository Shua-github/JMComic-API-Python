from fastapi import FastAPI, Request
from typing import Literal
import inspect
import uvicorn

from . import file_service, downloader
from .utils import direct_if, temp_if

class FastAPI_app:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.app = FastAPI()
        # 绑定路由
        self._bind_routes()

    async def jm_file(self, file_name: str):
        return await file_service.jm_file(file_name=file_name, config_path=self.config_path)

    async def jm_api(self, jm_id: int, file_type: Literal["pdf", "zip"], request: Request, direct: Literal["true", "false"] = "false"):
        file_name = f"{jm_id}.{file_type}"
        if temp_if(config_path=self.config_path, file_name=file_name):
            return await direct_if(jm_id=jm_id, file_type=file_type, request=request)
        return await downloader.jm_download(jm_id, file_type, request=request, config_path=self.config_path, direct=direct)

    def _bind_routes(self):
        # 自动绑定类方法作为路由
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_"):  # 跳过以 "_" 开头的方法
                continue
            elif name.endswith("file"):
                route_path = f"/{name}/{{file_name}}"
            else:
                route_path = f"/{name}"
            
            self.app.add_api_route(
                route_path,
                method,
                methods=["GET", "POST"]
            )

    def _run(self, host: str, port: int):
        # 启动 FastAPI 应用
        uvicorn.run(self.app, host=host, port=port)
