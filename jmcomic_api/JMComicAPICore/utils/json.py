from typing import Union, Dict, Any

def _Dict(type: str,status:str,code:int,data:Union[Dict,Any]):
    return {'type':type,'status':status,'code':code,'data':data}

class Ok:
    """处理 成功响应 的类"""

    @staticmethod
    def json(type:str,data: Union[Dict, any]):
        """
        返回 字典 格式。
        """
        return _Dict(type=type,status='OK',code=200,data=data)

    @staticmethod
    def file(path: str,file_name: str=None,file_type: str=None):
        """
        返回 文件 格式。
        """
        return Ok.json(type='file',data={'path':path,'file_name':file_name,'file_type':file_type})

    @staticmethod
    def redirect(url: str):
        """
        返回 重定向 格式。
        """
        return Ok.json(type='redirect',data={'url':url})

    @staticmethod
    def jm_json(jm_id: int, file_type: str, file_url: str):
        """
        返回 Jm 的 JSON 格式。
        """
        file_name = f"{jm_id}.{file_type}"
        data = {
            "jm_id": jm_id,
            "file_type": file_type,
            "file_name": file_name,
            "file_url": file_url
        }
        return Ok.json(type='json', data=data)
