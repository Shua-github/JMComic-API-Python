from typing import List, Tuple, Type, Union
from jmcomic import (
    JmHtmlClient,
    JmApiClient,
    JmAlbumDetail,
    JmImageDetail,
)


def get_album_images(
    jm_album_id: int,
    client: Union[Type[JmHtmlClient], Type[JmApiClient]],
) -> Tuple[JmAlbumDetail, List[List[JmImageDetail]]]:
    """
    获取本子信息和图片列表，不进行下载。
    """
    album = client.get_album_detail(jm_album_id)  # 获取专辑详细信息

    image_data_list = []
    for photo in album:
        client.check_photo(photo)  # 检查每张照片
        image_data = [image for image in photo]  # 获取每张照片中的所有图片
        image_data_list.append(image_data)

    return album, image_data_list
