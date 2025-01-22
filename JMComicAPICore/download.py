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
from .utils import error_json, ok_json, temp_if, Config

async def direct_if(
    request: Request,
    jm_id: Optional[int] = None,
    direct: Literal["true", "false"] = "false",
    album: Optional[JmAlbumDetail] = None,
    dler: Optional[JmDownloader] = None,
    file_name: Optional[str] = None,
    file_type: Optional[str] = None
):
    """
    根据 direct 参数判断是否直接返回文件下载链接或者 JSON 响应。

    参数:
    - jm_id (int): 文件的 JM ID。
    - file_type (str): 文件类型（如 'mp4', 'pdf' 等）。
    - request (Request): FastAPI 的请求对象，用于生成文件 URL。
    - direct (Literal["true", "false"]): 控制返回行为，如果是 "false" 返回 JSON 响应，"true" 返回重定向（默认值为 "false"）。
    - album (JmAlbumDetail): 如果提供了 album，则使用 album 的 jm_id。
    - dler (JmDownloader): 下载器实例，用于调试或处理下载。
    - file_name (str): 文件名。
    - file_type (str): 文件类型。

    返回:
    - JSON 响应或重定向响应：根据 direct 参数返回不同的结果。

    异常:
    - 如果 direct 参数值无效，返回 404 错误。
    - 如果发生未知错误，返回 500 错误。
    """
    
    # 回调支持,暂时没写好
    if not jm_id:
        if album:
            jm_id = album.album_id
        else:
            return error_json.not_found(msg="没有提供jm_id", log="Missing jm_id.")
    
    if not file_name:
        if jm_id and file_type:
            file_name = f"{jm_id}.{file_type}"
        else:
            return error_json.not_found(msg="没有提供file_type", log="用户没有提供 file_type")

    # 回调调试
    if dler:
        print(f"JmDownloader instance: {dler}")

    # 获取文件 URL
    try:
        # 使用 FastAPI 的 url_for 动态生成文件的 URL
        file_url = request.url_for("jm_file", file_name=file_name)._url  # _url 在这里是获取最终的 URL
        
        # 根据 direct 参数选择响应
        if direct == "false":
            # 返回带有文件 URL 的 JSON 响应
            return ok_json.jm_json(jm_id=jm_id, file_type=file_type, file_url=file_url)

        elif direct == "true":
            # 执行重定向
            return ok_json.redirect(file_url)

        else:
            # 返回 404 错误
            return error_json.not_found(msg="无效的 direct 参数值", log=f"Invalid 'direct' parameter value: {direct}")

    except Exception as e:
        # 捕获其他异常并返回 500 错误
        return error_json.unknown_error(log=f"Unexpected error: {str(e)}")

async def jm_download(
    jm_id: int, 
    file_type: str, 
    request: Request, 
    config_path: str, 
    direct: Literal["true", "false"] = "false"
):
    """处理下载逻辑"""

    # 加载配置
    config = Config(config_path=config_path)
    file_name = f"{jm_id}.{file_type}"
    if temp_if([file_name],config_path)[file_name]:
        return await direct_if(jm_id=jm_id,file_type=file_type, request=request, direct=direct)
    # 检查文件格式是否受支持
    if file_type not in config.supported_formats:
        return error_json.not_found(
            msg="不支持的格式或输入错误", 
            log="请求的格式不在支持的格式列表中"
        )

    try:
        download(jm_id, config.jm_config)
                
        return await direct_if(jm_id=jm_id,file_type=file_type, request=request, direct=direct)

    except MissingAlbumPhotoException as e:
        return error_json.not_found(
            msg=f"本子不存在: {e.error_jmid}",
            log=f"ID:{e.error_jmid}, Msg:{e.msg}"
        )

    except JsonResolveFailException as e:
        return error_json(
            code=500, 
            msg="解析 JSON 失败", 
            log=f"Msg:{e.resp.text}, URL: {e.resp.url}"
        )

    except RequestRetryAllFailException as e:
        return error_json(
            code=500, 
            msg="请求失败，重试耗尽", 
            log=f"Msg:{e}, URL: {e.url}"
        )

    except JmcomicException as e:
        return error_json(
            code=500, 
            msg="Jmcomic 库遇到异常", 
            log=f"Msg:{e}, Detail: {str(e)}"
        )

    except Exception as e:
        return error_json.unknown_error(
            log=f"Jmcomic 库遇到未知异常, Msg:{e}"
        )
