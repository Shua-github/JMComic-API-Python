import os


def get_dev_mode() -> bool:
    """
    获取是否为开发模式
    """
    return os.getenv("DEV", "").lower() == "true"


dev_mode = get_dev_mode()

IMG_FORMAT = "PNG"
