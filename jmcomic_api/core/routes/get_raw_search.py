from fastapi import Query
from fastapi.responses import JSONResponse
from typing import Literal, List, Dict
from jmcomic_api._utils.other import get_object_members
from jmcomic_api.models.core.route import Route
from jmcomic import create_option_by_str


class GetRawSearch(Route):
    def __init__(self):
        self.method = ["GET"]
        self.path = "/get/raw/search"

    def config(self, jm_config):
        self.client = create_option_by_str(str(jm_config)).build_jm_client()

    async def route_def(
        self,
        page: int = Query(1, title="页码", description="页码"),
        text: str = Query(..., title="需要搜索的内容", description="需要搜索的内容"),
        types: List[Literal["site", "tags", "author", "work"]] = Query(
            ..., title="需要的数据列表", description="需要的数据列表"
        ),
    ) -> JSONResponse:
        search_methods = {
            "site": self.client.search_site,
            "tags": self.client.search_tag,
            "author": self.client.search_author,
            "work": self.client.search_work,
        }

        return_data: Dict = {
            "code": 200,
            "status": "OK",
            "data": {"raw_results": {}},
        }

        for t in types:
            if t in search_methods:
                return_data["data"]["raw_results"][t] = get_object_members(
                    search_methods[t](search_query=text, page=page)
                )

        return JSONResponse(content=return_data)
