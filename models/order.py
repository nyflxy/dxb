# -*- coding: utf-8 -*-

"""
    alter by: daemon wnag
    alter on 2016-07-14
"""
import libs.modellib as model
import libs.utils as utils
import json
import types
import random
import time
from libs.hash import sign_encode
from vendor.wxpay import wxpay
from dxb import status
from libs.utils import options
import pdb


class OrderModel(model.BaseModel,model.Singleton):
    __name = "dxb.order"

    def __init__(self):
        model.BaseModel.__init__(self,OrderModel.__name)

    #安全验证
    def _vaildate(self):
        from_sign = self.get_argument("sign")
        if self.get_argument("timestamp") is None:
            raise ValueError(u"缺失时间戳")

        if from_sign is None:
            raise ValueError(u"缺失签名")

        sign = sign_encode(self._request.body)
        if from_sign != sign or sign == 0:
            print from_sign,sign
            raise ValueError(u"签名错误")

    #创建订单商品
    def _create_order_goods(self):
        _carts = self.get_argument("carts")
        carts = []
        if (type(_carts) == types.UnicodeType or type(_carts) == types.StringType) and _carts is not None and _carts != '':
            carts = json.loads(_carts)
        elif type(_carts) == types.ListType:
            carts = _carts
        if len(carts) == 0:
            raise ValueError(u"没有购买商品")

        order_goods = []
        for c in carts:
            num = c.get('num',0)
            goods_id = c['_id']
            product_model = model.BaseModel.get_model("product.ProductModel")
            product = product_model.get_coll().find_one({"_id":utils.create_objectid(goods_id),"on_sale_flag":1,"enable_flag":1})
            if product is None:
                raise ValueError(u"该商品不存在或者已下架")
            product['num'] = num
            order_goods.append(utils.dump(product))

        return order_goods

    #计算金额
    def _count_amount(self,order_goods,discount=0):
        promotion_id = self.get_argument("promotion_id")
        goods_amount = 0
        for g in order_goods:
            goods_amount += g['price'] * g['num']
        if promotion_id is not None:
            discount += 0
        should_pay = goods_amount - discount
        return goods_amount,should_pay,discount

    #获取地址
    def _get_address(self):
        address_id = self.get_argument("address_id")
        if address_id is None:
            res = None
        else:
            res = None
        return res

    #获取用户信息
    def _get_user(self):
        user_model = model.BaseModel.get_model("user.UserModel")
        user_id = self.get_argument("user_id")
        if not user_model.is_exist(user_id):
            raise ValueError(u"该用户不存在")
        user = user_model.get_coll().find_one({"_id":utils.create_objectid(user_id)})
        return user

    #生成订单号
    def _generate_orderid(self):
        origin_code = self.get_argument("origin_code")
        mobile_type = self.get_argument("mobile_type")
        if origin_code is None:
            raise ValueError(u"来源为空")
        else:
            order_id = mobile_type+time.strftime('%Y%m%d%M%S',time.localtime())+unicode(random.randint(0,999)).zfill(3)
            return order_id

    #获取企业相关信息
    def _get_enterprise(self):
        ent_model= model.BaseModel.get_model("enterprise.EnterpriseModel")
        enterprise_id = self.get_argument("enterprise_id")
        ent = ent_model.get_coll().find_one({"_id":utils.create_objectid(enterprise_id)})
        if ent is None:
            raise ValueError(u"该企业不存在")
        return ent

    #生成订单
    def create(self):
        user = self._get_user()
        order_goods = self._create_order_goods()
        order_address = self._get_address()
        order_id = self._generate_orderid()
        ent=self._get_enterprise()

        contact_name = self.get_argument("contact_name")
        mobile = self.get_argument("mobile")
        email = self.get_argument("email")

        if contact_name is None:
            raise ValueError(u"联系人为空")
        if mobile is None:
            raise ValueError(u"联系电话为空")
        if email is None:
            raise ValueError(u"接收邮箱为空")

        if utils.check_mobile(mobile) == False:
            raise ValueError(u"手机格式有误")
        if utils.check_email(email) == False:
            raise ValueError(u"接收邮箱有误")

        goods_amount,should_pay,discount = self._count_amount(order_goods)

        order = {
                "order_id":"DD"+user['uid']+order_id,
                "user_id":user['_id'],
                "address_id":self.get_argument("address_id"),
                "order_status":status.ORDER_STATUS_WAITING,
                "shipping_status":status.SHIPPING_STATUS_WAITING,
                "shipping_fee":0,
                "pay_status":status.PAY_STATUS_WAITING,
                "contact_name":contact_name,
                "mobile":mobile,
                "email":email,
                "remark":self.get_argument("remark",""),
                "pay_type":status.PAY_TYPE_WAITING,
                "goods_amount":round(goods_amount,2),
                "should_pay":round(should_pay,2),
                "money_paid":0,
                "discount":round(discount,2),
                "add_time":utils.get_now(),
                "pay_time":None,
                "origin_code":self.get_argument("origin_code"),
                "receive_wx_notify":0,
                "edit_times":0,
                "order_goods":order_goods,
                "order_address":order_address,
                "delivery_time":self.get_argument("delivery_time","即时发货"),
                "promotion_id":self.get_argument("promotion_id"),
                "enterprise":{
                    "ent_id":utils.objectid_str(ent['_id']),
                    "entname":ent['entname'],
                    "regno":ent['regno'],
                    "frname":ent['frname'],
                    "dom":ent['dom']
                    }
                }

        self.coll.save(order)
        return order

    def to_pay(self):
        self._vaildate()
        order_id = self.get_argument("order_id")
        if order_id is None:
            order = self.create()
        else:
            order = self.coll.find_one({"order_id":self.get_argument("order_id")})
            if order is None:
                raise ValueError(u"该订单不能去支付")

        return self.pay(order)

    def pay(self,order):
        pay_type = self.get_argument("pay_type")
        if pay_type is None:
            raise ValueError(u"支付方式为空")

        #微信网页支付
        if pay_type == status.PAY_TYPE_WX_WAP['value']:
            openid = self.get_argument("openid")
            if openid is None:
                raise ValueError(u"用户openid为空")

            order_pub = wxpay.UnifiedOrder_pub()
            order_pub.setParameter("out_trade_no",order['order_id'] + '_' + unicode(random.randint(0,9999)).zfill(4))
            order_pub.setParameter("body","东信宝尽调报告")
            order_pub.setParameter("total_fee","%s"%int(100*order['should_pay']))
            order_pub.setParameter("notify_url","%s/notify/wxpay"%options.home_url)
            order_pub.setParameter("trade_type","JSAPI")
            order_pub.setParameter("openid",openid)
            print order_pub.parameters

            return order_pub.getResult()
        else:
            raise ValueError(u"暂不支持这种支付方式")

    def get_good_name(self,obj):
        goods =  obj["order_goods"]
        if len(goods) and goods[0].has_key("show_name"):
            good_name = goods[0]["show_name"]
        else:
            good_name = ""
        return good_name

    def get_good_type(self,obj):
        goods = obj["order_goods"]
        if len(goods) and goods[0].has_key("type"):
            good_type = goods[0]["type"]
        else:
            good_type = ""
        return good_type

    def get_order_status_desc(self,obj):
        if obj.has_key("order_status") and obj["order_status"].has_key("desc"):
            order_status_desc = obj["order_status"]["desc"]
        else:
            order_status_desc = ""
        return order_status_desc

    def get_order_status_value(self, obj):
        if obj.has_key("order_status") and obj["order_status"].has_key("value"):
            order_status_value = obj["order_status"]["value"]
        else:
            order_status_value = ""
        return order_status_value

    def get_pay_status_desc(self, obj):
        if obj.has_key("pay_status") and obj["pay_status"].has_key("desc"):
            pay_status_desc = obj["pay_status"]["desc"]
        else:
            pay_status_desc = ""
        return pay_status_desc

    def get_pay_status_value(self, obj):
        if obj.has_key("pay_status") and obj["pay_status"].has_key("value"):
            pay_status_value = obj["pay_status"]["value"]
        else:
            pay_status_value = ""
        return pay_status_value

