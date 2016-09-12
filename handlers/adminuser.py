# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-22
"""

import json,pdb
import oauth2
import datetime
import tornado
import urllib
from dxb.handler import APIHandler,TokenAPIHandler,ListCreateAPIHandler,RetrieveUpdateDestroyAPIHandler
import libs.utils as utils

class AdminUserListCreateHandler(ListCreateAPIHandler):
    _model = "adminuser.AdminUserModel"
    _serializer = "adminuser.AdminUserSerializer"
    mg_require_params = [] # get 方法必要参数
    mg_default_params = {} # get 方法默认参数
    mg_query_params = {}
    mp_require_params = ["username","type"] #post 方法必要参数
    mp_default_params = dict( #post 方法默认参数
        phone = "",
        login_time = "",
        status = 1,
    )
    query_params = ["username"]
    mg_extra_params = []  # 返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        try:
            page = self.get_argument("page", 1)
            page_size = self.get_argument("page_size", 10)
            username = self.get_argument("username","")
            phone = self.get_argument("phone","")
            type = self.get_argument("type","all")
            l_query_params = {}
            if username != "":
                l_query_params.update({"username": {"$regex":username}})
            if phone != "":
                l_query_params.update({"phone": {"$regex": phone}})
            if type != "all" and type.isdigit():
                l_query_params.update({"type": int(type)})
            self.request.arguments = {"page": [unicode(page)], "page_size": [unicode(page_size)],
                                      "query_params": [json.dumps(l_query_params)]}
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        ListCreateAPIHandler.get(self)


class AdminUserRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    _model = "adminuser.AdminUserModel"
    mp_require_params = ["id"]  # put 方法必要参数
    mp_update_params = ["id","phone","type","status"] # put 方法允许参数
    mg_extra_params = []  # 返回数据额外字段

class AdminUserInitHandler(AdminUserListCreateHandler):
    _model = "adminuser.AdminUserModel"
    mp_update_or_raise = "raise"
    mp_default_params = {
        "type": "10",
    }

    def post(self):
        result = utils.init_response_data()
        try:
            self.mp_require_params = ["username","password"]
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        AdminUserListCreateHandler.post(self)

class AdminUserAddHandler(AdminUserListCreateHandler):
    _model = "adminuser.AdminUserModel"
    mp_update_or_raise = "raise"

    def post(self):
        result = utils.init_response_data()
        try:
            self.mp_require_params.extend(["password"])
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        AdminUserListCreateHandler.post(self)

handlers = [
    (r"/api/adminuser/list", AdminUserListCreateHandler),
    (r"/api/adminuser", AdminUserRetrieveUpdateDestroyHandler),
    (r"/api/adminuser/init", AdminUserInitHandler),
    (r"/api/adminuser/add", AdminUserAddHandler),
]