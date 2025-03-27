from fastapi import Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Literal, List, Dict
from jmcomic_api._libs import jm_api
from jmcomic_api._utils.env import JM_CONFIG
from jmcomic_api._utils.file import images_encrypted
from jmcomic_api.models.core.route import Route
import os
import base64

def fetch_images(jm_id: int, output_dir: str, img_format: str = 'PNG', no_cache: bool = False) -> List[str]:
    """
    下载本子
    """
    output_dir = os.path.join(output_dir, str(jm_id))
    
    client = JM_CONFIG.build_jm_client()
    
    # 检查是否存在文件夹
    if os.path.exists(output_dir) and not no_cache:
        image_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(f'.{img_format}')]
        if not os.listdir(output_dir):  # 再次确认文件夹为空
            os.rmdir(output_dir)  # 删除空文件夹
        else:
            return image_files
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取详情和图片数据列表
    album, image_data_list = jm_api.get_album_images(jm_id)
    
    images_path: List[str] = []
    
    for image_data in image_data_list:
        img_save_path = os.path.join(output_dir,f"{image_data.img_file_name}.{img_format.lower()}")
        client.download_by_image_detail(image_data, img_save_path, decode_image=True)
        images_path.append(img_save_path)
    
    return images_path

class GetFile(Route):
    def __init__(self):
        self.method = ['GET']
        self.path = '/get/file'
    
    def config(self,output_dir:str):
        self.output_dir = output_dir
        
    async def route_def(
        self,
        jm_id: int = Query(..., title='本子ID', description='本子ID'),
        file_type: Literal['pdf', 'zip'] = Query(..., title='文件格式', description='文件格式'),
        file_pwd: str = Query(None, title='文件密码', description='文件密码'),
        no_cache: Literal['true','false'] = Query('false', title='是否绕过缓存', description='是否绕过缓存'),
        return_method: Literal['from-data','base64'] = Query('base64', title='返回方式', description='返回方式'),
    ) -> JSONResponse:
        return_data: Dict = {
            'code': 200,
            'status': 'OK', 
            'data': {
                'jm_id': jm_id,
                'file_type': file_type,
                'file_pwd': file_pwd,
                'no_cache': no_cache,
                'file': None,
                }
            }

        if no_cache == 'false':
            no_cache = False
        elif no_cache == 'true':
            no_cache = True
        
        out_img_paths = fetch_images(jm_id=jm_id, output_dir=self.output_dir, no_cache=no_cache)

        if not out_img_paths:  # 检查 out_img_paths 是否为空
            raise ValueError("生成的图片路径列表为空，无法处理文件")
        
        encrypted_file = images_encrypted(image_paths=out_img_paths, password=file_pwd, out_file_format=file_type)
        encrypted_file.seek(0)  # 确保文件指针在开头
        
        if return_method == 'base64':
            return_data['data']['file'] = base64.b64encode(encrypted_file.read()).decode('utf-8')
        elif return_method == 'from-data':
            def file_iterator():
                while chunk := encrypted_file.read(1024 * 1024):  # 每次读取 1MB
                    yield chunk
            return StreamingResponse(file_iterator(), media_type="application/octet-stream", headers={
                "Content-Disposition": f"attachment; filename={jm_id}.{file_type}"
            })
        
        return JSONResponse(content=return_data)
