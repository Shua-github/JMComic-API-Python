from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import RedirectResponse
from jmcomic_api._utils.env import dev_mode
from jmcomic_api._utils.exception import (
    add_exception_handler,
)
from typing import Callable
import uuid
from fastapi.routing import APIRoute

app = FastAPI(debug=dev_mode)
app = add_exception_handler(app=app)


def add_temporary_route(path: str, route_func: Callable):
    """
    添加一个临时路由（自动删除且不在文档显示）
    """
    endpoint_name = f"temporary_route_{uuid.uuid4().hex}"
    temporary_router = APIRouter()

    # 关键修改：添加 include_in_schema=False
    @temporary_router.get(path, name=endpoint_name, include_in_schema=False)
    async def temporary_route(request: Request):
        response = await route_func()

        # 删除路由的逻辑保持不变
        routes_to_remove = [
            route
            for route in app.router.routes
            if isinstance(route, APIRoute) and route.name == endpoint_name
        ]
        for route in routes_to_remove:
            app.router.routes.remove(route)

        return response

    app.include_router(temporary_router)


async def root():
    return RedirectResponse(url="/docs")


app.add_api_route("/", root)
