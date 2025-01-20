from fastapi.responses import RedirectResponse
from fastapi import Request
from typing import Literal

async def direct_if(jm_id: int, file_type: str, request: Request, direct: Literal["true", "false"] = "false"):
    """判断是否直接返回下载链接"""
    from . import ok_json, error_json  # 确保 ok_json 和 error_json 正确导入

    # 构建文件名和文件 URL
    file_name = f"{jm_id}.{file_type}"
    file_url = request.url_for("jm_file", file_name=file_name)  # 使用 FastAPI 的 url_for 动态生成文件的 URL

    try:
        # 如果 direct 为 "false"，返回带有文件 URL 的 JSON 响应
        if direct == "false":
            return ok_json.jm_json(jm_id=jm_id, file_type=file_type, file_url=file_url._url)

        # 如果 direct 为 "true"，执行重定向
        elif direct == "true":
            return ok_json.direct(file_url)

        # 默认行为：如果没有匹配的值，抛出异常或返回错误
        else:
            return error_json.request_error_404(msg="无效的 direct 参数值", log=f"Received direct={direct}")
    except Exception as e:
        # 捕获其他异常并返回 500 错误
        return error_json._error_unknown(log=f"Msg: {str(e)}")
