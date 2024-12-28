from fastapi import FastAPI
import inspect
from config import read_config
from instance import instance

type_list = ["pdf", "zip"]
app = FastAPI()

# 动态绑定类方法为路由
def bind_routes_from_class(app: FastAPI, instance):
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        if name.endswith("file"):
            route_path = f"/{name}/{{file_name}}"
        else:
            route_path = f"/{name}"
        app.add_api_route(route_path, method, methods=["GET", "POST"], name=name)

if __name__ == "__main__":
    try:
        config = read_config() 
        jm_api_instance = instance(config.jm, config.temp.output, config.temp.image, type_list)
        bind_routes_from_class(app, jm_api_instance)
        from uvicorn import run
        run(app, host=config.net.host, port=config.net.port)
    except Exception as e:
        print(f"启动服务时发生错误: {e}")
        exit(1)