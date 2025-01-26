from .utils import ok_json, Config, file_path_join,CustomError
async def jm_file(file_name: str, config_path: str):
    """提供文件"""
    config = Config(config_path=config_path)

    try:
        # 拼接路径,构造JSON
        path = file_path_join([config.temp_output, file_name])
        return ok_json.file(path=path)
    
    except FileNotFoundError as e:
        # 文件未找到，返回 404 错误
        raise CustomError.not_found(
            msg="文件未找到",
            log=f"未找到文件: {file_name}, Msg: {str(e)}"
        )
    
    except Exception as e:
        # 其他未知错误
        raise CustomError.unknown_error(
            log=f"未知错误: {str(e)}"
        )
