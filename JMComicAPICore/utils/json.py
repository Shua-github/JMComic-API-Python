from typing import Union, Dict, Any
from fastapi import HTTPException
from fastapi.responses import FileResponse,RedirectResponse,JSONResponse

class CustomHTTPException(HTTPException):
    def __init__(self, status: str, code: int, data: Union[Dict, Any]):
        # 构造基础 HTTPException
        self.status = status
        self.code = code
        self.detail = data
        super().__init__(status_code=self.code, detail=self._format_detail())

    def _format_detail(self):
        """
        格式化错误详情，符合你的要求
        """
        return {"status": self.status, "code": self.code, "data": self.detail}


class Error:
    """处理错误响应"""

    def __init__(self, msg: str = None, log: str = None, code: int = None):
        if all([msg, log, code]):
            self._raise_error(msg, log, code)

    @staticmethod
    def json(code: int, data: Union[Dict, any], status: str):
        """
        返回 自定义 格式的错误响应。
        """
        return CustomHTTPException(status=status, code=code, data=data)

    @staticmethod
    def _raise_error(msg: str, log: str, code: int):
        """
        服务器内部错误，包含错误消息和日志。
        """
        raise Error.json(
            code=code,
            data={"msg": msg, "log": log},
            status="Internal Server Error"
        )

    @staticmethod
    def not_found(msg: str, log: str):
        """
        返回 404 错误响应。
        """
        raise Error.json(
            code=404,
            data={"msg": msg, "log": log},
            status="Not Found"
        )

    @staticmethod
    def unknown_error(log: str):
        """
        返回未知错误的响应，状态码 500。
        """
        raise Error.json(
            code=500,
            data={"log": log},
            status="Unknown Error"
        )


class Ok:
    """处理 FastAPI 成功响应的类"""

    def __init__(self, data: Union[Dict, any]):
        """
        初始化并返回成功响应。
        """
        self.json(data)

    @staticmethod
    def json(data: Union[Dict, any]):
        """
        返回 JSON 格式的成功响应。
        """
        return JSONResponse(content={"status": "OK", "code": 200, "data": data}, status_code=200)

    @staticmethod
    def file(path: str):
        """
        返回文件响应。
        """
        return FileResponse(path=path)

    @staticmethod
    def redirect(url: str):
        """
        返回重定向响应。
        """
        return RedirectResponse(url=url)

    @staticmethod
    def jm_json(jm_id: Union[int, str], file_type: str, file_url: str):
        """
        返回 Jm 格式的 JSON 响应。
        """
        file_name = f"{jm_id}.{file_type}"
        return Ok.json(data={"jm_id": jm_id, "file_type": file_type, "file_name": file_name, "file_url": file_url})
