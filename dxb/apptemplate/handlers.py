#coding=utf-8

from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.modellib as model

# class TempAPIHandler(ListCreateAPIHandler):
#     _model = "enterprise.EnterpriseModel"
#     query_params  = {}
#     mg_extra_params = ["count"]
#
#     def get(self):
#         pass