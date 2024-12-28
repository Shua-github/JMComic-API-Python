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

class instance:
    def __init__(self, jm_option: dict, temp_output: str, temp_image: str, type_list: list):
        self.jm_option = jm_option  # 通过初始化时传入，不通过查询参数
        self.temp_output = temp_output
        self.temp_image = temp_image
        self.type_list = type_list

    async def direct_if(
        self,
        request: Request,
        direct: str = Query("False", description="是否直接下载"),
        id: int = Query(..., description="本子 ID"),
        type: str = Query("pdf", description="文件类型"),
        name: str = Query(..., description="文件名")
    ):
        file_url = request.url_for("jm_file", file_name=str(name))
        try:
            if direct == "False":
                return {"code": 200, "data": {"id": id, "type": type, "url": file_url}}
            elif direct or direct is None:
                return RedirectResponse(file_url)
        except Exception as e:
            return {"code": 500, "data": {"msg": "发生错误，请联系管理员", "log": f"错误:{e}"}}

    async def jm_download(
        self,
        request: Request,
        direct: str = Query("False", description="是否直接下载"),
        id: int = Query(..., description="本子 ID"),
        type: str = Query("pdf", description="文件类型"),
        name: str = Query(..., description="文件名")
    ):
        if type in self.type_list:
            try:
                download(id, self.jm_option)
                return await self.direct_if(request, direct, id, type, name)
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

    async def jm_file(self, file_name: str):
        try:
            path = join(self.temp_output, file_name)
            return FileResponse(path=path)
        except Exception as e:
            return {"code": 500, "data": {"msg": "文件服务出错", "log": str(e)}}

    async def jm_api(
        self,
        request: Request,
        id: int = Query(..., description="本子 ID"),
        direct: str = Query("False", description="是否直接下载"),
        type: str = Query("pdf", description="文件类型")
    ):
        file_name = f"{id}.{type}"
        path = join(self.temp_output, file_name)
        if exists(path):
            return await self.direct_if(request, direct, id, type, file_name)
        else:
            return await self.jm_download(request, direct, id, type, file_name)