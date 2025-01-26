from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi import FastAPI, Request, Query
from typing import Literal
import inspect
import uvicorn
from . import download, file_service
from .utils import CustomError,CustomHTTPException,_Dict
def FastAPI_response_treat(data:_Dict):
    """
    返回 JSON 响应。

    参数:
    - data (dict): JSON 数据

    返回:
    - 响应对象
    """
    match data['type']:
        case 'json':
            return JSONResponse(status_code=data['code'],content=data)
        case 'file':
            return FileResponse(data['data']['path'])
        case 'redirect':
            return RedirectResponse(url=data['data']['url'])
        case _:
            raise CustomError.unknown_error(log="没有匹配到类型")
        
class FastAPI_App:
    def __init__(self, config_path: str):
        """
        初始化 FastAPI 应用实例，并绑定路由。

        参数:
        - config_path (str): 配置文件路径
        """
        self.config_path = config_path
        self.app = FastAPI()
        self._bind_routes()

    async def jm_file(self, file_name: str):
        """
        处理文件请求，通过文件服务返回文件。

        参数:
        - file_name (str): 文件名

        返回:
        - FileResponse: 文件响应
        """
        try:
            return FastAPI_response_treat(await file_service.jm_file(file_name=file_name, config_path=self.config_path))
        except CustomError as e:
            raise CustomHTTPException(e)


    async def jm_api(self, file_type: Literal["pdf", "zip"], request: Request, direct: Literal["true", "false"] = "false", jm_id: int = Query(...)):
        """
        下载 API，判断是否需要直接返回下载链接或通过下载器下载。

        参数:
        - jm_id (int, list): 漫画 ID 或 漫画 ID 列表
        - file_type (Literal["pdf", "zip"]): 文件类型
        - request (Request): FastAPI 请求对象
        - direct (Literal["true", "false"]): 是否直接返回下载链接

        返回:
        - Response: 下载链接或下载响应
        """
        try:
            # 使用 await 等待协程结果
            result = await download.jm_download(jm_id, file_type, request=request, config_path=self.config_path, direct=direct)
            # 将结果传递给 FastAPI_response_treat
            return FastAPI_response_treat(result)
        except CustomError as e:
            raise CustomHTTPException(e)

    def _bind_routes(self):
        """
        动态绑定类中的方法作为 FastAPI 路由，自动生成 API 路径。
        """
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_"):  # 跳过以 "_" 开头的方法
                continue

            # 根据方法名生成路由路径
            route_path = self._generate_route_path(name)
            
            # 绑定路由
            self.app.add_api_route(
                route_path,
                method,
                methods=["GET", "POST"]
            )

    def _generate_route_path(self, method_name: str) -> str:
        """
        根据方法名生成路由路径。

        参数:
        - method_name (str): 方法名

        返回:
        - str: 路由路径
        """
        if method_name.endswith("file"):
            # 对于文件相关的接口，使用带有文件名的路径
            return f"/{method_name}/{{file_name}}"
        return f"/{method_name}"

    def _run(self, host: str, port: int):
        """
        启动 FastAPI 应用。

        参数:
        - host (str): 服务器地址
        - port (int): 端口号
        """
        uvicorn.run(self.app, host=host, port=port)