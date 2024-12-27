from fastapi import FastAPI, Request
from jmcomic import create_option_by_str as read_jm_option
from os.path import exists
from os import makedirs
import inspect
from instance import instance

jm_config = {
    'dir_rule': {'base_dir': ''},
    'download': {'image': {'decode': True, 'suffix': '.jpg'}},
    'log': True,
    'plugins': {
        'after_album': [
            {'plugin': 'img2pdf', 'kwargs': {'pdf_dir': '', 'filename_rule': 'Aid'}},
            {'plugin': 'zip', 'kwargs': {'level': 'album', 'filename_rule': 'Aid', 'zip_dir': '', 'delete_original_file': True}}
        ]
    },
    'version': '2.1'
}

type_list = ["pdf", "zip"] 
app = FastAPI()
# 动态绑定类方法为路由
def bind_routes_from_class(app, instance):
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        if not name.startswith("_"):
            async def route_func(request,_method=method,**kwargs, ):
                return await _method(instance, request=request, **kwargs)

            app.add_api_route(f"/{name}", route_func, methods=["GET", "POST"])



# -----------------配置-----------------
from yaml import safe_load
from sys import exit
from collections import namedtuple
try:
    if not exists("config.yml"):  
        exit("缺失程序配置")  
    with open("config.yml", 'r', encoding='utf-8') as temp:
        Config = namedtuple('Config', ['main', 'jm']) 
        file: dict = safe_load(temp)
        main: dict = file.get("app")
        jm: dict = file.get("jm")
        config = Config(main=main, jm=jm)

    temp_output = config.main['temp_output']  
    temp_image = config.main['temp_image']  
    port = config.main['port']  
    host = config.main['host']  
    if config.main['jm_config']:
        jm_option = read_jm_option(str(config.jm))
    else:
        jm_config['dir_rule']['base_dir'] = config.main['temp_image']
        jm_config['plugins']['after_album'][0]['kwargs']['pdf_dir'] = config.main['temp_output']
        jm_config['plugins']['after_album'][1]['kwargs']['zip_dir'] = config.main['temp_output']
        jm_option = read_jm_option(str(jm_config))
    if not exists(temp_output): 
        makedirs(temp_output)  
    if not exists(temp_image):  
        makedirs(temp_image) 
except Exception as e:   
    exit(f'"导入程序配置发生报错,请检查配置\n{e}"')  
# -----------------配置-----------------

if __name__ == '__main__':
    bind_routes_from_class(app, instance(jm_option, temp_output, temp_image, type_list))
    from uvicorn import run
    run(app, host=host, port=port)
