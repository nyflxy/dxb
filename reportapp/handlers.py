#coding=utf-8

import json, pdb ,os
import time
import datetime
import tornado
from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler,ReportHandler
import dxb.libs.utils as utils
import dxb.libs.modellib as model
import dxb.libs.reportlib as reportlib
import authuserapp.models as authuser_models

class OrderReportHandler(ReportHandler):
    _model = "order.OrderModel" #导出表名
    mg_query_params = {}  # get 方法查询参数
    mg_sort_params = {}  # get 方法排序字段
    namelist = [u'序号']  # 报表表头
    column_list = []  # 报表表头字段
    report_name = "订单报表"  # 报表名

    def get(self):
        try:
            order_id = self.get_argument("order_id", "")
            mobile = self.get_argument("mobile", "")
            pay_type = self.get_argument("pay_type", "")
            order_status = self.get_argument("order_status", "")
            if order_id != "":
                self.mg_query_params.update({
                    "order_id": {"$regex": order_id},
                })
            if mobile != "":
                self.mg_query_params.update({
                    "mobile": {"$regex": mobile},
                })
            if pay_type != "":
                self.mg_query_params.update({
                    "pay_type.value": int(pay_type),
                })
            if order_status != "":
                self.mg_query_params.update({
                    "order_status.value": int(order_status),
                })
            self.namelist = [u'序号', u'订单号', u'产品名称', u'消费类型', u'手机号', u'订单状态', u'支付类型', u'订单总金额', u'下单时间']
            self.column_list = ["order_id","good_name","good_type","mobile","order_status_desc","pay_status_desc","should_pay","add_time"]
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return
        ReportHandler.get(self)

class UserReportHandler(ReportHandler):
    model = authuser_models.AuthUserModel() #导出表名
    report_name = "用户报表"  # 报表名

handlers = [
    (r"/api/report/order", OrderReportHandler),
    (r"/api/report/user", UserReportHandler),
]
