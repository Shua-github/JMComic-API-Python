from fastapi import Request 
from typing import Literal
from jmcomic import download_album as download
from .utils import error_json,direct_if,Config
from jmcomic import (
MissingAlbumPhotoException,
JsonResolveFailException,
RequestRetryAllFailException,
JmcomicException,
)
async def jm_download(jm_id: int, file_type:str, request:Request,config_path,direct:Literal["true","false"]="false",):
    """处理下载逻辑"""
    print(jm_id,file_type,direct)
    config = Config(config_path=config_path)
    if file_type in config.supported_formats:
        try:
            download(jm_id, config.jm_config)
            return await direct_if(jm_id, file_type, request , direct)
        except MissingAlbumPhotoException as e:
            return error_json.request_error_404(msg=f"本子不存在: {e.error_jmid}",log=f"ID:{e.error_jmid},Msg:{e.msg}")
        except JsonResolveFailException as e:
            return error_json(code=500,msg="解析 JSON 失败", log=f"Msg:{e.resp.text}")
        except RequestRetryAllFailException as e:
            return error_json(code=500,msg="请求失败，重试耗尽",log=f"Msg:{e}")
        except JmcomicException as e:
            return error_json(code=500,msg="Jmcomic库 遇到异常", log=f"Msg:{e}")
        except Exception as e:
            return error_json._error_unknown(log=f"Jmcomic库 遇到未知异常,Msg:{e}")
    else:
        return error_json.request_error_404(msg="不支持的格式或输入错误",log="")


