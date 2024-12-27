from fastapi import FastAPI, APIRouter
from typing import Callable
import inspect


# 定义一个类，包含多个方法
class MyClass:
    async def hello(self):
        return {"message": "Hello, world!"}

    async def goodbye(self):
        return {"message": "Goodbye, world!"}
    async def goodbye1(self):
        return {"message": "Goodbye, world1!"}

# 自动将类中的方法加载为路由
def load_routes_from_class(router: APIRouter, instance: object):
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        # 确保只加载以方法名为路径的路由
        if not name.startswith("_"):  # 排除特殊方法
            router.add_api_route(f"/{name}", method, methods=["GET"])

# 创建 FastAPI 应用和路由器
app = FastAPI()
router = APIRouter()

# 实例化类并加载方法为路由
my_class_instance = MyClass()
load_routes_from_class(router, my_class_instance)

# 将路由器添加到应用中
app.include_router(router)

if __name__ == '__main__':
    from uvicorn import run
    run(app, host='127.0.0.1', port=7000)
