from .utils import ok_json,error_json,Config,file_path_join
async def jm_file(file_name: str, config_path:str):
    """提供文件"""
    config = Config(config_path=config_path)
    try:
        path = file_path_join([config.temp_output, file_name])
        return ok_json.file(path=path)
    except FileNotFoundError as e:
        return error_json.request_error_404(msg="文件不存在",log=str(e))
    except Exception as e:
        return error_json._error_unknown(log=f"文件服务 遇到未知异常,Msg:{e}")
