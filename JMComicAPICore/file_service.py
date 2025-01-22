from .utils import ok_json, error_json, Config, file_path_join,file_if

async def jm_file(file_name: str, config_path: str):
    """提供文件"""
    config = Config(config_path=config_path)



    try:
        # 拼接路径,构造JSON
        path = file_path_join([config.temp_output, file_name])
        return ok_json.file(path=path)
    
    except FileNotFoundError as e:
        # 文件未找到，返回 404 错误
        return error_json.not_found(
            msg="文件不存在", 
            log=f"文件 {file_name} 不存在，Msg: {str(e)}"
        )
    
    except Exception as e:
        # 其他未知错误
        return error_json.unknown_error(
            log=f"文件服务 遇到未知异常，文件名: {file_name}, Msg: {str(e)}"
        )
