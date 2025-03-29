from fastapi import Query, Request
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
)
from typing import Literal, Dict
from jmcomic_api._utils.file import (
    merge_images_to_file,
    encrypt_file,
    GetCacheFilePath,
)
from jmcomic_api._utils.env import IMG_FORMAT
from jmcomic_api.models.core.route import Route
from jmcomic_api.core.main import add_temporary_route
import os
import base64
from io import BytesIO


class GetFile(Route):
    def __init__(self):
        self.method = ["GET"]
        self.path = "/get/file"

    def config(self, output_dir: str):
        self.output_dir = output_dir

    async def route_def(
        self,
        request: Request,
        jm_id: int = Query(..., title="本子ID", description="本子ID"),
        file_type: Literal["pdf", "zip"] = Query(
            ..., title="文件格式", description="文件格式"
        ),
        file_pwd: str = Query(None, title="文件密码", description="文件密码"),
        return_method: Literal["from-data", "base64", "url"] = Query(
            "base64",
            title="返回方式",
            description="返回方式",
        ),
    ) -> JSONResponse:
        get_cache_path = GetCacheFilePath(self.output_dir, jm_id).get
        file_name = f"{jm_id}.{file_type}"
        return_data: Dict = {
            "code": 200,
            "status": "OK",
            "data": {
                "jm_id": jm_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_pwd": file_pwd,
                "file": None,
            },
        }

        img_dir = get_cache_path(IMG_FORMAT.lower())
        if not os.path.exists(img_dir) or not os.listdir(img_dir):
            return JSONResponse(
                content={
                    "code": 400,
                    "status": "error",
                    "data": {
                        "msg": "图片未下载",
                        "log": "图片未下载",
                    },
                },
                status_code=400,
            )

        out_img_paths = []  # 用于存储符合条件的图片路径

        # 获取每个章节的图片路径，按章节命名文件夹，避免文件名冲突
        for chapter_index, chapter_data in enumerate(os.listdir(img_dir)):
            chapter_path = os.path.join(img_dir, chapter_data)
            if os.path.isdir(chapter_path):
                chapter_name = chapter_data  # 章节名  # noqa: F841
                for f in os.listdir(chapter_path):
                    if f.endswith(f".{IMG_FORMAT.lower()}"):
                        full_path = os.path.join(chapter_path, f)
                        # 使用章节名加图片文件名来避免文件名冲突
                        out_img_paths.append(full_path)

        # 获取拼接过的zip或pdf
        file: BytesIO = merge_images_to_file(out_img_paths, file_type)

        # 获取路径
        file_dir: str = os.path.join(get_cache_path(file_type))
        file_path: str = os.path.join(file_dir, file_name)
        os.makedirs(file_dir, exist_ok=True)

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(file.getvalue())

        # 删除文件路径
        del file_path

        # 加密
        if file_pwd:
            file = encrypt_file(
                input_file=file,
                password=file_pwd,
                file_type=file_type,
            )

        # 返回流式
        async def return_streaming(file_name, file_type):
            def file_iterator():
                while chunk := file.read(1024 * 1024):
                    yield chunk

            return StreamingResponse(
                file_iterator(),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "X-File-Type": file_type,
                },
            )

        # 返回逻辑
        if return_method == "base64":
            return_data["data"]["file"] = base64.b64encode(file.read()).decode("utf-8")
        elif return_method == "from-data":
            return await return_streaming(file_name=file_name, file_type=file_type)
        elif return_method == "url":
            base_url = str(request.base_url._url).rstrip("/")
            url_path = f"/temp/{file_name}"

            def call_back():
                return return_streaming(file_name=file_name, file_type=file_type)

            add_temporary_route(url_path, call_back)
            return_data["data"]["file"] = f"{base_url}{url_path}"
        return JSONResponse(content=return_data)
