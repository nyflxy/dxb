# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-07-14
#
from dxb.handler import APIHandler,TokenAPIHandler
import libs.utils as utils

class MainHandler(APIHandler):
    #获取文件列表
    def get(self):
        result = utils.init_response_data()
        try:
            result['data']= "Api home page"
            result['version']= "v0.1.0"
            result['pack_date']= "2016-08-24"
            result['update_msg']= u"1.First Commit"
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

class MainTestHandler(APIHandler):
    #获取文件列表
    def get(self):
        result = utils.init_response_data()
        try:
            res = ''
            result['data']= res
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

handlers = [(r'/api/main/test', MainTestHandler),
            (r'/api/main', MainHandler),

            ]