from fastapi import FastAPI, Request
from fastapi.responses import FileResponse,RedirectResponse
from typing import Optional
from jmcomic import download_album as download
from jmcomic import create_option_by_str as read_jm_option
from jmcomic import JmOption ,MissingAlbumPhotoException,JsonResolveFailException,RequestRetryAllFailException,JmcomicException
from os.path import exists,join
from os import makedirs
from yaml import safe_load
from sys import exit
from collections import namedtuple

client = JmOption.default().new_jm_client()
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
app = FastAPI()
type_list = ["pdf", "zip"] 

try:
    # 检查配置文件是否存在
    if not exists("config.yml"):  
        exit("缺失程序配置")  
        # 读取配置文件
    with open("config.yml", 'r', encoding='utf-8') as temp:
        Config = namedtuple('Config', ['main', 'jm']) 
        file:dict = safe_load(temp)
        main:dict = file.get("main")
        jm:dict = file.get("jm")
        config = Config(main=main, jm=jm)
    # 读取配置到变量
    temp_output = config.main['temp_output']  
    temp_image = config.main['temp_image']  
    port = config.main['port']  
    host = config.main['host']  
    if config.main['jm_config']:
        # 使用外置配置
        jm_option = read_jm_option(str(config.jm))
    else:
        # 使用内置配置
        jm_config['dir_rule']['base_dir'] = config.main['temp_image']
        jm_config['plugins']['after_album'][0]['kwargs']['pdf_dir'] = config.main['temp_output']
        jm_config['plugins']['after_album'][1]['kwargs']['zip_dir'] = config.main['temp_output']
        jm_option = read_jm_option(str(jm_config))
    # 检查输出和缓存是否存在
    if not exists(temp_output): 
        makedirs(temp_output)  
    if not exists(temp_image):  
        makedirs(temp_image) 
# 报错处理
except Exception as e:   
    exit(f'"导入程序配置发生报错,请检查配置\n{e}"')  

@app.get("/jm_download")
def jm_download(request: Request, direct: Optional[str], id: Optional[int], type: Optional[str], name: Optional[str]):
    if type in type_list:
        try:
            download(id, jm_option)
            return direct_if(direct=direct, id=id, type=type, name=name, request=request)
        except MissingAlbumPhotoException as e:
            return {"code": 404, "data":{"msg": f'id={e.error_jmid}的本子不存在', "log": f'id={e.error_jmid}的本子不存在'}}
        except JsonResolveFailException as e:
            resp = e.resp
            return {"code": 500, "data":{"msg": "解析json失败", "log": f'resp.text: {resp.text}, resp.status_code: {resp.status_code}'}}
        except RequestRetryAllFailException as e:
            return {"code": 500, "data":{"msg": "请求失败，重试次数耗尽", "log": "请求失败，重试次数耗尽"}}
        except JmcomicException as e:
            return {"code": 500, "data":{"msg": "jmcomic遇到异常", "log": f"jmcomic遇到异常: {e}"}}
    else:
        return {"code": 400, "data":{"msg": "不支持此格式或输入错误", "log": "不支持此格式或输入错误"}}

# 判定是否直接返回文件   
def direct_if(request:Request,direct:Optional[str],id:Optional[int],type:Optional[str],name:Optional[str]):
    file_url = request.url_for("jm_file",file_name=name) 
    try:
        if direct == "False": 
            return {"code": 200,"data":{"id":id,"type":f"{type}","url": f"{file_url}"}}
        elif direct or direct == None:
            return RedirectResponse(f"{file_url}")
    except Exception as e:
        return {"code": 500, "data":{"msg": "发生错误请联系管理员", "log": f"错误:{e} in function direct_if with name={name}"}}

# 跳转到文档
@app.get("/")
def to_docs(request:Request):
    url = request.url_for("to_docs")
    return RedirectResponse(f"{url}docs")

# 文件服务
@app.get("/jm_file/{file_name}")
def jm_file(file_name: str):
    try:
        # 返回文件
        path = join(temp_output, file_name)
        return FileResponse(path=path)
    # 报错处理
    except Exception as e:
        return {"code": 500, "data":{"msg": "发生错误请联系管理员", "log": f"错误:{e} in function jm_file with name={file_name}"}}

# 下载本子
@app.get("/jm_api")
def jm_api(id: int, request: Request, direct: Optional[str] = "False", type: Optional[str] = "pdf"):
    """
    下面的文字是Copilot生成的,我也不知道是什么意思
    Endpoint to download a comic by its ID.

    Args:
        id (int): The ID of the comic to download.
        request (Request): The request object.
        direct (Optional[str], optional): Whether to directly return the file. Defaults to "False".
        type (Optional[str], optional): The type of file to download (pdf or zip). Defaults to "pdf".

    Returns:
        JSON response or RedirectResponse: The response object.
    """
    try:
        # 本子名称，本地路径，判定是否存在缓存
        file_name = f"{id}.{type}"
        path = join(temp_output, file_name)
        if exists(path):  
            return direct_if(direct=direct,id=id,type=type,name=file_name,request=request)
        else:
            return jm_download(direct=direct, id=id, type=type, name=file_name, request=request)
    # 报错处理
    except Exception as e:
        return {"code": 500, "data":{"msg": "发生错误请联系管理员", "log": f"错误:{e}"}}
    
# 程序入口
if __name__ == '__main__':
    from uvicorn import run
    run(app, host=host, port=port)
