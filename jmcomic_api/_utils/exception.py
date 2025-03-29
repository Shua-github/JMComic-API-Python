from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jmcomic.jm_exception import JmcomicException


def add_exception_handler(app: FastAPI):
    @app.exception_handler(JmcomicException)
    async def jmcomic_exception_handler(
        request: Request, exc: JmcomicException
    ) -> FastAPI:
        """
        全局异常处理器，用于捕获 JmcomicException 及其子类。
        """
        response_data = {
            "status": "error",
            "code": 400,
            "data": {
                "msg": str(exc),  # 异常消息
                "log": str(
                    exc.context if hasattr(exc, "context") else {}
                ),  # 异常上下文，默认空字典
            },
        }
        return JSONResponse(content=response_data, status_code=400)

    return app
