from jmcomic_api.models.config import load_config
from jmcomic_api.core.main import app
from uvicorn import run
from jmcomic_api._utils.env import dev_mode
from jmcomic_api.models.core.route import Route
from jmcomic_api.core.routes import __all__ as all_routes

RELOAD_DIR = "./jmcomic_api"

def main():
    # dev启用热重载
    if dev_mode:
        import jurigged
        
        jurigged.watch(
            pattern=RELOAD_DIR,
        )
    
    config = load_config()
    configured_routes = {route_name: route_params for route_config in config.routes for route_name, route_params in route_config.model_dump().items()}
    
    # 配置路由
    for route_class in all_routes:
        route_name = route_class.__name__
        route_instance: Route = route_class()
        
        # 如果路由需要配置且在配置文件中定义，则调用 config 方法
        if route_name in configured_routes:
            route_params = configured_routes[route_name]
            if hasattr(route_instance, "config") and callable(route_instance.config):
                route_instance.config(**route_params)
        
        # 添加路由到 FastAPI 应用
        app.add_api_route(route_instance.path, route_instance.route_def, methods=route_instance.method)
        
    server_config = config.server
    run(app=app, host=server_config.host, port=server_config.port)