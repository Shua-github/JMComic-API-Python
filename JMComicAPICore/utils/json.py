from typing import Union, Dict
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse

class error:
    def __init__(self, status: Union[str], msg: str, log: str, code: int):
        # 调用 _error 而不传递 status
        self._error(status, msg, log, code)

    @staticmethod
    def json(status: Union[str], code: int, data: Union[Dict, any]):
        # 使用 staticmethod 装饰器避免不必要的 self 参数
        return JSONResponse(content={"status": status, "code": code, "data": data}, status_code=code)
    @staticmethod
    def _error(msg: str, log: str, code: int):
        # 调用 json 方法时不需要传递 status
        return error.json(status="Internal Server Error", code=code, data={"msg": msg, "log": log})

    @staticmethod
    def request_error_404(msg: str, log: str):
        # 错误 404 请求
        return error.json(status="Not Found", code=404, data={"msg": msg, "log": log})

    @staticmethod
    def _error_unknown(log):
        # 未知错误
        return error._error(msg="发生未知错误。", log=log, code=500)


class ok:
    def __init__(self, data: Union[Dict, str]):
        # 调用 json 方法
        self.json(data)

    @staticmethod
    def json(data: Union[Dict, any]):
        # OK 返回
        return JSONResponse(content={"status": "OK", "code": 200, "data": data}, status_code=200)

    @staticmethod
    def file(path: Union[str, "r'path/to/file_name'"]):
        # 文件响应
        return FileResponse(path=path)

    @staticmethod
    def direct(url: Union[str]):
        # 重定向响应
        return RedirectResponse(url=url)
    
    @staticmethod
    def jm_json(jm_id: Union[int, str], file_type: Union[str], file_url: Union[str]):
        # 提供Jm格式的 JSON 响应
        file_name = f"{jm_id}.{file_type}"
        return ok.json(data={"id": jm_id, "file_type": file_type, "file_name": file_name, "file_url": file_url})