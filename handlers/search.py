# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-18
"""

import json,pdb
import oauth2
import datetime
import tornado
import urllib
from dxb.handler import TokenAPIHandler
from dxb.handler import APIHandler
import libs.utils as utils
import models.search as search

class SearchListCreateHandler(APIHandler):
    model = search.SearchModel()
    def get(self):
        result = utils.init_response_data()
        try:
            page = self.get_argument("page",1)
            page_size = self.get_argument("page_size",4)
            query_params = {
                "len":{"$lte":4},
            }
            sort_params = {
                "count":-1,
            }
            datas,pager = SearchListCreateHandler.model.search_list(page,page_size,sort_params=sort_params,query_params=query_params)
        except Exception,e:
            result = utils.reset_response_data(0, str(e))
            return result

        result["data"] = datas
        result["pager"] = pager
        self.finish(result)

    def post(self):
        result = utils.init_response_data()
        try:
            keyword = self.get_argument("keyword")
            SearchListCreateHandler.model.create(keyword=keyword)
        except Exception,e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)


handlers = [
    (r"/api/search/list", SearchListCreateHandler),
]
