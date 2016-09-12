# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-01-09
#

from dxb import status
from dxb.handler import APIHandler
import libs.utils as utils
import libs.modellib as model
from vendor.wxpay import wxpay


class WxpayNotifyHandler(APIHandler):

    def get(self):
        self.finish({"data":"WxpayNotifyHandler"})

    def post(self):
        order_model = BaseModel.get_model("order.OrderModel")
        notify_model = BaseModel.get_model("notify.NotifyModel")
        result = utils.init_response_data()
        try:
            wx_server = wxpay.Wxpay_server_pub()
            wx_server.saveData(self.request.body)
            data = wx_server.getData()
            if not wx_server.checkSign():
                raise ValueError(u"签名错误")
            else:
                if data['result_code'] == 'SUCCESS':
                    order_id = data['out_trade_no'].split('_')[0]
                    order = order_model.coll.find_one({"order_id":order_id})
                    if order is None:
                        raise ValueError(u"订单不存在")
                    if order['receive_wx_notify'] == 1:
                        return
                    money_paid = int(data['cash_fee'])*0.01

                    if data['trade_type'] == 'JSAPI':
                        pay_type = status.PAY_TYPE_WX_WAP
                    else:
                        pay_type = status.PAY_TYPE_WXPAY

                    order['order_status'] = status.ORDER_STATUS_SERVICE
                    order['pay_status'] = status.PAY_STATUS_PAYED
                    order['pay_type'] = pay_type
                    order['pay_time'] = utils.get_now()
                    order['money_paid'] = money_paid
                    order['receive_wx_notify'] = 1

                    notify_model.generate_notify_operate(order)
                else:
                    raise ValueError(u"支付失败")
        except StandardError,e:
            result = utils.reset_response_data(0,unicode(e))
            print unicode(e)
            utils.write_log('wxpay',u"支付失败↓")
            utils.write_log('wxpay',unicode(e))
            utils.write_log('wxpay',self.request.body)
            utils.write_log('wxpay',u"支付失败↑")
        self.finish(result)

handlers = [(r"/api/notify/wxpay", WxpayNotifyHandler)
            ]
