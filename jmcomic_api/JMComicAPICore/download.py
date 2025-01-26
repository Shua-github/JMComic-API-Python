from fastapi import Request
from typing import Literal, Optional
from jmcomic.api import JmDownloader, JmAlbumDetail
from jmcomic import download_album as download
from jmcomic import (
    MissingAlbumPhotoException,
    JsonResolveFailException,
    RequestRetryAllFailException,
    JmcomicException,
)
from jmcomic.jm_entity import JmAlbumDetail
from jmcomic.jm_downloader import JmDownloader
from .utils import ok_json, temp_if, Config, CustomError

async def direct_if(
    request: Request,
    jm_id: Optional[int] = None,
    direct: Literal["true", "false"] = "false",
    album: Optional[JmAlbumDetail] = None,
    dler: Optional[JmDownloader] = None,
    file_name: Optional[str] = None,
    file_type: Optional[str] = None
):
    # 检查 jm_id 和 file_name
    if not jm_id:
        if album:
            jm_id = album.album_id
        else:
            raise CustomError.not_found(msg="没有提供 jm_id", log="用户没有提供 jm_id")

    if not file_name:
        if jm_id and file_type:
            file_name = f"{jm_id}.{file_type}"
        else:
            raise CustomError.not_found(msg="没有提供 file_type", log="用户没有提供 file_type")
        
    # 回调调试
    if dler:
        print(f"JmDownloader instance: {dler}")

    # 获取文件 URL
    try:
        file_url = str(request.url_for("jm_file", file_name=file_name)._url)
    except Exception as e:
        raise CustomError.unknown_error(log=f"生成文件 URL 失败: {str(e)}")

    # 根据 direct 参数选择响应
    if direct == "false":
        return ok_json.jm_json(jm_id=jm_id, file_type=file_type, file_url=file_url)
    elif direct == "true":
        return ok_json.redirect(file_url)
    else:
        raise CustomError.not_found(msg="无效的 direct 参数值", log=f"Invalid 'direct' parameter value: {direct}")

async def jm_download(
    jm_id: int, 
    file_type: str, 
    request: Request, 
    config_path: str, 
    direct: Literal["true", "false"] = "false"
):
    # 加载配置
    config = Config(config_path=config_path)
    file_name = f"{jm_id}.{file_type}"

    # 检查文件是否已存在
    if temp_if([file_name], config_path)[file_name]:
        return await direct_if(jm_id=jm_id, file_type=file_type, request=request, direct=direct)

    # 检查文件格式是否受支持
    if file_type not in config.supported_formats:
        raise CustomError.not_found(
            msg="不支持的格式或输入错误", 
            log="请求的格式不在支持的格式列表中"
        )

    try:
        download(jm_id, config.jm_config)
        return await direct_if(jm_id=jm_id, file_type=file_type, request=request, direct=direct)

    except MissingAlbumPhotoException as e:
        raise CustomError.not_found(
            msg=f"本子不存在: {e.error_jmid}",
            log=f"ID:{e.error_jmid}, Msg:{e.msg}"
        )

    except JsonResolveFailException as e:
        raise CustomError._raise_error(
            code=500, 
            msg="解析 JSON 失败", 
            log=f"Msg:{e.resp.text}, URL: {e.resp.url}"
        )

    except RequestRetryAllFailException as e:
        raise CustomError._raise_error(
            code=500, 
            msg="请求失败，重试耗尽", 
            log=f"Msg:{e}, URL: {e.url}"
        )

    except JmcomicException as e:
        raise CustomError._raise_error(
            code=500, 
            msg="Jmcomic 库遇到异常", 
            log=f"Msg:{e}, Detail: {str(e)}"
        )

    except Exception as e:
        raise CustomError.unknown_error(
            log=f"Jmcomic 库遇到未知异常, Msg:{e}"
        )
