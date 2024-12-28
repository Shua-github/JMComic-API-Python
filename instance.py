from fastapi import APIRouter
from fastapi import Request, Query
from fastapi.responses import FileResponse, RedirectResponse
from os.path import exists, join

# 模拟 jmcomic 的部分功能
from jmcomic import (
    download_album as download,
    MissingAlbumPhotoException,
    JsonResolveFailException,
    RequestRetryAllFailException,
    JmcomicException,
)

router = APIRouter()

def getRouter(jm_option: dict, temp_output: str, temp_image: str, type_list: list):
    @router.get("/direct_if")
    async def direct_if(
        request: Request,
        direct: str = Query("False", description="是否直接下载"),
        id: int = Query(..., description="本子 ID"),
        type: str = Query("pdf", description="文件类型"),
        name: str = Query(..., description="文件名")
    ):
        file_url = await jm_file(request, name)
        try:
            if direct == "False":
                return {"code": 200, "data": {"id": id, "type": type, "url": file_url}}
            elif direct or direct is None:
                return RedirectResponse(file_url)
        except Exception as e:
            return {"code": 500, "data": {"msg": "发生错误，请联系管理员", "log": f"错误:{e}"}}

    @router.get("/jm_download")
    async def jm_download(
        request: Request,
        direct: str = Query("False", description="是否直接下载"),
        id: int = Query(..., description="本子 ID"),
        type: str = Query("pdf", description="文件类型"),
        name: str = Query(..., description="文件名")
    ):
        if type in type_list:
            try:
                download(id, jm_option)
                return await direct_if(request, direct, id, type, name)
            except MissingAlbumPhotoException as e:
                return {"code": 404, "data": {"msg": f"本子不存在: {e.error_jmid}", "log": str(e)}}
            except JsonResolveFailException as e:
                return {"code": 500, "data": {"msg": "解析 JSON 失败", "log": f"{e.resp.text}"}}
            except RequestRetryAllFailException:
                return {"code": 500, "data": {"msg": "请求失败，重试耗尽"}}
            except JmcomicException as e:
                return {"code": 500, "data": {"msg": "Jmcomic 遇到异常", "log": str(e)}}
        else:
            return {"code": 400, "data": {"msg": "不支持的格式或输入错误"}}

    @router.get("/jm_file")
    async def jm_file(self, file_name: str):
        try:
            path = join(temp_output, file_name)
            return FileResponse(path=path)
        except Exception as e:
            return {"code": 500, "data": {"msg": "文件服务出错", "log": str(e)}}

    @router.get("/jm_api")
    async def jm_api(
        request: Request,
        id: int = Query(..., description="本子 ID"),
        direct: str = Query("False", description="是否直接下载"),
        type: str = Query("pdf", description="文件类型")
    ):
        file_name = f"{id}.{type}"
        path = join(temp_output, file_name)
        if exists(path):
            return await direct_if(request, direct, id, type, file_name)
        else:
            return await jm_download(request, direct, id, type, file_name)
    return router