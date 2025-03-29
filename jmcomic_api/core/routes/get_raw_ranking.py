from fastapi import Query
from fastapi.responses import JSONResponse
from typing import Literal, List, Dict
from jmcomic_api._utils.other import get_object_members
from jmcomic_api.models.core.route import Route
from jmcomic import create_option_by_str


class GetRawRanking(Route):
    def __init__(self):
        self.method = ["GET"]
        self.path = "/get/raw/ranking"

    def config(self, jm_config):
        self.client = create_option_by_str(str(jm_config)).build_jm_client()

    async def route_def(
        self,
        page: int = Query(1, title="页码", description="页码"),
        types: List[Literal['day','week','month']] = Query(
            ..., title="需要的数据列表", description="需要的数据列表"
        ),
    ) -> JSONResponse:
        search_methods = {
            "day": self.client.day_ranking, # 日
            "week": self.client.week_ranking, # 周
            "month": self.client.month_ranking, # 月
        }

        return_data: Dict = {
            "code": 200,
            "status": "OK",
            "data": {"raw_results": {}},
        }

        for t in types:
            if t in search_methods:
                return_data["data"]["raw_results"][t] = get_object_members(
                    search_methods[t](page=page)
                )

        return JSONResponse(content=return_data)
