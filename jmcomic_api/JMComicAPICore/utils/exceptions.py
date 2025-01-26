from inspect import stack

class CustomError(Exception):
    """自定义异常类，用于处理错误响应并返回详细的异常信息"""
    
    def __init__(self, msg: str, code: int, log: str, status: str):
        # 直接在 __init__ 中获取调用模块的名称
        module_name = stack()[2].function
        super().__init__(msg)  # 调用父类构造函数
        self.code = code
        self.msg = msg
        self.status = status
        self.module_name = module_name
        self.log = log

    @staticmethod
    def json(code: int, status: str, msg: str, log: str):
        """返回自定义格式的错误响应对象"""
        return CustomError(msg=msg, code=code, log=log, status=status)

    @staticmethod
    def _raise_error(msg: str, log: str, code: int):
        """内部错误，返回错误对象"""
        return CustomError(
            msg=msg,
            code=code,
            log=log,
            status='Internal Server Error'
        )

    @staticmethod
    def not_found(msg: str, log: str):
        """返回404错误响应对象"""
        return CustomError(
            code=404,
            msg=msg,
            log=log,
            status="Not Found"
        )

    @staticmethod
    def unknown_error(log: str):
        """返回500未知错误的响应对象"""
        return CustomError(
            code=500,
            msg="Unknown Error",
            log=log,
            status="Unknown Error"
        )

    def to_dict(self):
        """将异常信息转换为字典格式，方便其他框架使用"""
        return {
            "code": self.code,
            "msg": self.msg,
            "log": self.log,
            "status": self.status,
            "module_name": self.module_name
        }


# FastAPI 专用的异常类
from fastapi import HTTPException

class CustomHTTPException(HTTPException):
    """FastAPI 专用的异常类，继承自 HTTPException"""
    
    def __init__(self, custom_error: CustomError):
        self.status_code = custom_error.code
        self.code = custom_error.code
        self.msg = custom_error.msg
        self.log = custom_error.log
        super().__init__(status_code=self.status_code, detail=self._format_detail())

    def _format_detail(self):
        return {
            "data": {
                "msg": self.msg,
                "log": self.log,
            }
        }