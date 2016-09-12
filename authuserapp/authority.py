# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-07-18
"""

import pdb
import tornado
import renren.model.model as model
import renren.consts as consts
import renren.libs.utils as utils
from bson.son import SON
from tornado.web import RequestHandler as BaseRequestHandler, HTTPError

class AuthorityModel(model.BaseModel,model.Singleton):
    __name = "renren.authority"
    help = "用户权限管理"

    def __init__(self):
        model.BaseModel.__init__(self,AuthorityModel.__name)
        self.api_scope_dict = {
            "/api/user":{"GET":["font-api"]},
            "/api/user/person/auth/info":{"GET":["font-api"]},
        }

    def process(self,request,access):
        request_path = request.path
        request_method = request.method

        scopes = access["scopes"]
        api_scopes = self.get_api_scopes(request_path,request_method)
        if len(api_scopes) == 0:#未设置权限 默认公开访问
            return
        if len(list(set(scopes))) + len(list(set(api_scopes))) > len(list(set(scopes+api_scopes))) :
            return
        else:
            raise Exception("访问受限")

    def get_api_scopes(self,request_path,request_method):
        api_scopes = []
        try:
            api_scopes = self.api_scope_dict[request_path][request_method]
        except Exception as e:
            pass
        return api_scopes

authority = AuthorityModel()