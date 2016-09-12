# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-06-07
#
import rsa
import base64
import os
from urllib import quote
from dxb.app import get_options
import types


class Alipay(object):
    ## default value
    service = "mobile.securitypay.pay"# api name, default value
    _input_charset = "utf-8"
    sign_type = "RSA"# only support RSA
    payment_type = 1
    _GATEWAY = 'https://mapi.alipay.com/gateway.do?'

    options = get_options()

    # partner = options.ALIPAY_PARTNER
    notify_url = options.ALIPAY_NOTIFY_URL
    # the account id of seller (email or phone or partner id)
    # seller_id = options.ALIPAY_SELLER

    def  __init__(self, out_trade_no, subject, body, total_fee,company='dxb'):
        # unique value, max=64
        self.out_trade_no = out_trade_no
        # order title/ trade keys, max=128
        self.subject = subject
        # the detail info of order, max=512
        self.body = body
        # the total pay fee
        self.total_fee = total_fee

        options = get_options()




        if company == 'dxb':
            priv_path = options.root_path+"/ssl/rsa_private_key.pem"
            pub_path_ali = options.root_path+"/ssl/rsa_public_key.pem"
            self.partner = options.ALIPAY_PARTNER
            self.seller_id = options.ALIPAY_SELLER
        elif company == 'hanzheng':
            priv_path = options.root_path+"/ssl/hz/rsa_private_key.pem"
            pub_path_ali = options.root_path+"/ssl/hz/rsa_public_key.pem"
            self.partner = '2088712170646781'
            self.seller_id = '18918175400'
        try:
            pem = open(priv_path, "r").read()
            self._private_rsa_key = rsa.PrivateKey.load_pkcs1(pem)

            pem = open(pub_path_ali, "r").read()
            self._public_rsa_key_ali = rsa.PublicKey.load_pkcs1_openssl_pem(pem)
        except:
            self._private_rsa_key = None
            self._public_rsa_key_ali = None

    def init_optional_value(self, it_b_pay):
        # order timeout, m:minute, h:hour, d:day ("30m")
        self.it_b_pay = it_b_pay

    def smart_str(self,s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Returns a bytestring version of 's', encoded as specified in 'encoding'.
        If strings_only is True, don't convert (some) non-string-like objects.
        """
        if strings_only and isinstance(s, (types.NoneType, int)):
            return s
        if not isinstance(s, basestring):
            try:
                return str(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    # An Exception subclass containing non-ASCII data that doesn't
                    # know how to print itself properly. We shouldn't raise a
                    # further exception.
                    return ' '.join([self.smart_str(arg, encoding, strings_only,
                            errors) for arg in s])
                return unicode(s).encode(encoding, errors)
        elif isinstance(s, unicode):
            return s.encode(encoding, errors)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s

    def params_filter(self,params):
        ks = params.keys()
        ks.sort()
        newparams = {}
        prestr = ''
        for k in ks:
            v = params[k]
            if k not in ('sign','sign_type') and v != '':
                newparams[k] = v
                prestr += '%s="%s"&' % (k, newparams[k])
        prestr = prestr[:-1]
        return newparams, prestr

    def _build_sign_url(self):
        # 即时到账交易接口
        options = get_options()
        params = {}
        params['service'] = 'mobile.securitypay.pay'
        params['payment_type'] = '1'

        # 获取配置文件
        params['partner'] = self.partner
        params['seller_id'] = self.seller_id
        params['return_url'] = 'm.alipay.com'
        params['notify_url'] = options.ALIPAY_NOTIFY_URL
        params['_input_charset'] = "utf-8"
        params['it_b_pay'] = '30m'

        # 从订单数据中动态获取到的必填参数
        params['out_trade_no']  = self.out_trade_no        # 请与贵网站订单系统中的唯一订单号匹配
        params['subject']       = self.subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
        params['body']          = self.body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
        params['total_fee']     = self.total_fee # 订单总金额，显示在支付宝收银台里的“应付总额”里

        params,prestr = self.params_filter(params)

        return self._GATEWAY + prestr

    def _create_sign(self, content):
        content = content.encode(self._input_charset)
        sign = rsa.sign(content, self._private_rsa_key, "SHA-1")
        sign = base64.encodestring(sign).replace("\n", "")
        return 'sign="%s"&sign_type="%s"' % (quote(sign), self.sign_type)

    def create_pay_url(self):

        content = self._build_sign_url()
        sign_url = self._create_sign(content)
        res = "%s&%s" % (content, sign_url)
        return res

def notify_sign_value(request, content, key):
    if key in request.POST:
        value = request.POST[key]
        return "&%s=%s"%(key, value)
    else:
        return ""

def check_notify_sign(request):
    """
    按照字母顺序排序，然后使用阿里云的公匙验证。
    """
    content = ""
    post_list = sorted(request.POST.iteritems(), key=lambda d:d[0], reverse=False)
    for key_value in post_list:
        if key_value[0] not in ["sign", "sign_type"]:
            content = "%s&%s=%s"%(content, key_value[0], key_value[1])

    #remove the first &
    content = content[1:]
    content = content.encode("utf-8")
    try:
        sign = request.POST["sign"]
        sign = base64.decodestring(sign)
        #rsa.verify(content, sign, _public_rsa_key_ali)
        return True
    except Exception as e:
        print ("check_notify_sign error", e)
        return False
# from Crypto.PublicKey import RSA
# import json
# from dxb.app import get_options
# import urllib
# import types
# import dxb.libs.utils as utils
# import hashlib
# import base64
# from Crypto.Signature import PKCS1_v1_5 as pk
# from Crypto.Hash import SHA
# # from OpenSSL.crypto import load_privatekey, FILETYPE_PEM, sign
# import binascii
#
# #网关地址
# _GATEWAY = 'https://mapi.alipay.com/gateway.do?'
#
# def format_order_info(out_trade_no,subject,body,total_fee):
#     options = get_options()
#     order_info_array = {
#         "partner":options.ALIPAY_PARTNER,
#         "seller_id":options.ALIPAY_SELLER,
#         "out_trade_no":out_trade_no,
#         "subject":subject,
#         "body":body,
#         "total_fee":total_fee,
#         "notify_url":options.ALIPAY_NOTIFY_URL,
#         "service":"mobile.securitypay.pay",
#         "payment_type":"1",
#         "_input_charset":"utf-8",
#         "it_b_pay":"30m",
#         "return_url":"m.alipay.com"
#     }
#     order_info_url = urllib.urlencode(order_info_array)
#     order_info = json.dumps(order_info_url)
#     print order_info
#     return order_info
#
#
# def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
#     """
#     Returns a bytestring version of 's', encoded as specified in 'encoding'.
#     If strings_only is True, don't convert (some) non-string-like objects.
#     """
#     if strings_only and isinstance(s, (types.NoneType, int)):
#         return s
#     if not isinstance(s, basestring):
#         try:
#             return str(s)
#         except UnicodeEncodeError:
#             if isinstance(s, Exception):
#                 # An Exception subclass containing non-ASCII data that doesn't
#                 # know how to print itself properly. We shouldn't raise a
#                 # further exception.
#                 return ' '.join([smart_str(arg, encoding, strings_only,
#                         errors) for arg in s])
#             return unicode(s).encode(encoding, errors)
#     elif isinstance(s, unicode):
#         return s.encode(encoding, errors)
#     elif s and encoding != 'utf-8':
#         return s.decode('utf-8', errors).encode(encoding, errors)
#     else:
#         return s
#
# def params_filter(params):
#     ks = params.keys()
#     ks.sort()
#     newparams = {}
#     prestr = ''
#     for k in ks:
#         v = params[k]
#         k = smart_str(k)
#         if k not in ('sign','sign_type') and v != '':
#             newparams[k] = smart_str(v)
#             prestr += '%s=%s&' % (k, newparams[k])
#     prestr = prestr[:-1]
#     return newparams, prestr
#
#
# # 生成签名结果
# def build_mysign(prestr, key, sign_type = 'MD5'):
#     if sign_type == 'MD5':
#         return utils.md5(prestr + key)
#     elif sign_type == 'RSA':
#         # sha1 = hashlib.sha1()
#         # sha1.update(prestr)
#         # sha1.update(key)
#         # print base64.b64encode(sha1.hexdigest())
#         # return base64.b64encode(sha1.hexdigest())
#         # h = SHA.new(prestr)
#         # signer = pk.new(key)
#         # signature = signer.sign(h)
#         # print base64.b64encode(signature)
#         # return base64.b64encode(signature)
#         # d = sign(key, prestr, 'sha1')  #d为经过SHA1算法进行摘要、使用私钥进行签名之后的数据
#         # b = base64.b64encode(d)  #将d转换为BASE64的格式
#         # print b
#         # return b
#         pass
#     return ''
#
# def base64ToString(s):
#     try:
#         return base64.decodestring(s)
#     except binascii.Error, e:
#         raise SyntaxError(e)
#     except binascii.Incomplete, e:
#         raise SyntaxError(e)
#
# def stringToBase64(s):
#     return base64.encodestring(s).replace("\n", "")
#
# def sign_with_rsa(msg):
#     '''
#     将msg使用当前文件中定义的_private_rsa_key来签名, 返回base64编码的字符串
#     '''
#     options = get_options()
#     key = RSA.importKey(open(options.root_path+"/ssl/rsa_private_key.pem"))
#     h = SHA.new(msg)
#     signer = pk.new(key)
#     signature = signer.sign(h)
#     signature = stringToBase64(signature)
#     print signature
#     return signature
#
# def check_with_rsa(msg, signature):
#     '''
#     使用当前文件中定义的_public_rsa_key来验证签名是否正确
#     '''
#     options = get_options()
#     signature = base64ToString(signature)
#     key = RSA.importKey(open(options.root_path+"/ssl/rsa_public_key.pem"))
#     h = SHA.new(msg)
#     verifier = pk.new(key)
#     return verifier.verify(h, signature)
#
# # 即时到账交易接口
# def create_direct_pay_by_user(tn, subject, body, total_fee):
#     options = get_options()
#     params = {}
#     params['service'] = 'mobile.securitypay.pay'
#     params['payment_type'] = '1'
#
#     # 获取配置文件
#     params['partner'] = options.ALIPAY_PARTNER
#     params['seller_id'] = options.ALIPAY_SELLER
#     params['return_url'] = '"m.alipay.com"'
#     params['notify_url'] = options.ALIPAY_NOTIFY_URL
#     params['_input_charset'] = "utf-8"
#     params['it_b_pay'] = '"30m"'
#
#     # 从订单数据中动态获取到的必填参数
#     params['out_trade_no']  = tn        # 请与贵网站订单系统中的唯一订单号匹配
#     params['subject']       = subject   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
#     params['body']          = body      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
#     params['total_fee']     = total_fee # 订单总金额，显示在支付宝收银台里的“应付总额”里
#
#     params,prestr = params_filter(params)
#
#     params['sign'] = params['sign'] = sign_with_rsa(prestr)
#     params['sign_type'] = 'RSA'
#
#     print _GATEWAY + urllib.urlencode(params)
#     return _GATEWAY + prestr + urllib.urlencode(params)
#
# def alipay_test():
#     options = get_options()
#     params = {}
#     params['service'] = '"mobile.securitypay.pay"'
#     params['payment_type'] = '"1"'
#
#     # 获取配置文件
#     params['partner'] = '"2088121791097463"'
#     params['seller_id'] = '"nj.dhcs@donghuienterprise.com"'
#     params['return_url'] = '"m.alipay.com"'
#     params['notify_url'] = '"https://www.dxb.com/api/notify/alipay"'
#     params['_input_charset'] = '"utf-8"'
#     params['it_b_pay'] = '"30m"'
#
#     # 从订单数据中动态获取到的必填参数
#     params['out_trade_no']  = '"AP44628115_1465201173"'        # 请与贵网站订单系统中的唯一订单号匹配
#     params['subject']       = '"东汇商城订单"'   # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
#     params['body']          = '"东汇商城订单"'      # 订单描述、订单详细、订单备注，显示在支付宝收银台里的“商品描述”里
#     params['total_fee']     = '"2500"' # 订单总金额，显示在支付宝收银台里的“应付总额”里
#
#     params,prestr = params_filter(params)
#     print params
#     print prestr
#
#     # pkcs8_private_key = RSA.importKey(open(options.root_path+"/ssl/pkcs8_key.pem"))
#     #pkcs8_private_key = load_privatekey(FILETYPE_PEM,open(options.root_path+"/ssl/rsa_private_key.pem").read())
#
#     #params['sign'] = build_mysign(prestr, pkcs8_private_key, 'RSA')
#     params['sign'] = sign_with_rsa(prestr)
#     params['sign_type'] = 'RSA'
#
#     print _GATEWAY + urllib.urlencode(params)