# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-07
#

import pdb
from dxb.handler import APIHandler, RetrieveUpdateDestroyAPIHandler, ListAPIHandler, DestroyAPIHandler
from vendor.wxpay.wxpay import JsApi_pub,Wxinfo_pub
import libs.utils as utils
import libs.modellib as model

class OrderListHandler(APIHandler):
    _model = 'order.OrderModel'

    def get(self):
        try:
            result = utils.init_response_data()
            page_size = self.get_argument("page_size",10)
            page = self.get_argument("page",1)
            length = self.coll.find().count()
            user_id = self.get_argument("user_id")
            pager = utils.count_page(length,page,int(page_size))
            order_list = self.coll.find({"user_id":utils.create_objectid(user_id)}).limit(pager['page_size']).skip(pager['skip']).sort("pay_time",-1)
            if order_list is None:
                raise ValueError(u"无订单！")
            result["data"] = utils.dump(order_list)

            result["pager"]=pager
        except Exception,e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

class OrdersHandler(RetrieveUpdateDestroyAPIHandler):
    _model = "order.OrderModel"

    #生成订单
    def post(self):
        result = utils.init_response_data()
        try:
            request = self.request
            self.model.set_request(request)
            result['data'] = self.model.to_pay()
        except Exception as e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)


class OrderAdminListHandler(ListAPIHandler):
    _model = 'order.OrderModel'
    _serializer = "order.OrderSerializer"
    mg_query_params = {}
    mg_sort_params = {}

    def get(self):
        result = utils.init_response_data()
        try:
            order_id = self.get_argument("order_id","")
            mobile = self.get_argument("mobile","")
            pay_type = self.get_argument("pay_type","")
            order_status = self.get_argument("order_status","")
            if order_id != "":
                self.mg_query_params.update({
                    "order_id":{"$regex":order_id},
                })
            if mobile != "":
                self.mg_query_params.update({
                    "mobile": {"$regex": mobile},
                })
            if pay_type != "":
                self.mg_query_params.update({
                    "pay_type.value":int(pay_type) ,
                })
            if order_status != "":
                self.mg_query_params.update({
                    "order_status.value": int(order_status),
                })
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        ListAPIHandler.get(self)

class OrderDestroyAPIHandler(DestroyAPIHandler):
    _model = "enterprise.EnterpriseModel"
    mp_require_params = ["id"]  # put 方法必要参数
    mp_update_params = ["id"]  # put 方法允许参数


handlers = [(r"/api/order", OrdersHandler),
            (r"/api/order/list", OrderListHandler),
            (r"/api/order/admin/list", OrderAdminListHandler),
            (r"/api/order/delete", OrderDestroyAPIHandler),
            ]