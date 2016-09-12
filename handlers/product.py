# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-01-09
#

from dxb.handler import APIHandler
from libs import utils

class ProductHandler(APIHandler):
    _model = 'product.ProductModel'

    def get(self):
        result = utils.init_response_data()
        try:
            product_id = self.get_argument("product_id","")
            product = self.coll.find_one({"_id":utils.create_objectid(product_id)})
            result["data"] = utils.dump(product)
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

    def put(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

class ProductListHandler(APIHandler):
    _model = 'product.ProductModel'

    def get(self):
        result = utils.init_response_data()
        query_list = {}
        try:
            page = self.get_argument("page",1)
            page_size = self.get_argument("page_size",15)
            type = self.get_argument("type",None)
            if type is not None:
                query_list['type'] = type
            query_list['enable_flag'] = 1
            result["data"],result["pager"] = self.model.list(query_list,page,page_size)
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

class ProductShowHandler(APIHandler):
    _model = 'product.ProductModel'

    def get(self):
        result = utils.init_response_data()
        try:
            show_code = self.get_argument("show_code","")
            result["data"] = self.model.get_show_products(show_code)
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)


handlers = [
            (r"/api/product/list", ProductListHandler),
            (r"/api/product", ProductHandler),
            (r"/api/product/show", ProductShowHandler),
            ]