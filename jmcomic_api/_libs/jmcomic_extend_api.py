from typing import List, Tuple
from jmcomic import *

def get_album_images(jm_album_id: int, option=None) -> Tuple[JmAlbumDetail, List[JmImageDetail]]:
    """
    获取本子信息和图片列表，不进行下载。
    """
    
    if option is None:
        option = JmModuleConfig.option_class().default()

    client = option.build_jm_client()
    album = client.get_album_detail(jm_album_id)

    image_data_list = []
    for photo in album:
        client.check_photo(photo)
        for image in photo:
            image_data_list.append(image)
    
    return album, image_data_list