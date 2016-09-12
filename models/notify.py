# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-08
#

import libs.modellib as model

class NotifyModel(model.BaseModel):
    __name = "dxb.notify"

    def __init__(self):
        model.BaseModel.__init__(self,NotifyModel.__name)

    #回调操作相关
    def generate_notify_operate(self,order):
        order_model = model.BaseModel.get_model("order.OrderModel")
        #更新订单
        order_model.coll.save(order)
        return


