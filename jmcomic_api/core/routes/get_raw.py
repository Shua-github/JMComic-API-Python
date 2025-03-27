from fastapi import Query
from fastapi.responses import JSONResponse
from typing import Literal, List, Dict
from jmcomic_api._libs import jm_api
from jmcomic_api._utils.other import get_object_members
from jmcomic_api.models.core.route import Route

class GetRaw(Route):
    
    def __init__(self):
        self.method = ['GET']
        self.path = '/get/raw'
        
    async def route_def(
        self,
        jm_id: int = Query(..., title='本子ID', description='本子ID'),
        types: List[Literal['info', 'img_url_list']] = Query(..., title='需要的数据列表', description='需要的数据列表')
    ) -> JSONResponse:
        return_data: Dict = {'code': 200, 'status': 'OK', 'data': {}}

        album, img_list = jm_api.get_album_images(jm_id)

        if 'info' in types:
            return_data['data']['raw_info'] = get_object_members(album)

        if 'img_url_list' in types:
            return_data['data']['raw_img_url_list'] = get_object_members(img_list)

        return JSONResponse(content=return_data)
