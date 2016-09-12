# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

from dxb import status

status.ORDER_STATUS = [
    ('waiting',0,u'待支付'),
    ('service',1,u'服务中'),
    ('complete',2,u'已完成'),
    ('cancel',3,u'已取消'),
]

status.SHIPPING_STATUS = [
    ('waiting',0,u'未发货'),
    ('service',10,u'运输中'),
    ('complete',20,u'已完成'),
    ('cancel',30,u'已取消'),
]

status.PAY_STATUS = [
    ('waiting',0,u'等待支付'),
    ('payed',1,u'已支付'),
    ('partly',2,u'部分支付'),
]

status.PAY_TYPE = [
    ('waiting','waiting',u'暂未支付'),
    ('wxpay','wxpay',u'微信支付'),
    ('alipay','alipay',u'支付宝支付'),
    ('wx_wap','wx_wap',u'微信网页支付'),
]
