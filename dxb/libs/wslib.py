# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-04-14
#
from suds import WebFault
from suds.client import Client
import pyDes
import base64
import types
# import logging
# import os
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from tornado.options import options as settings

def encode(str):
    if type(str) == types.UnicodeType:
        str = str.encode("utf-8")
    key = pyDes.des('12312312',pyDes.CBC, "12312312", pad=None,padmode=pyDes.PAD_PKCS5)
    des_data = key.encrypt(str)
    b_data = base64.b64encode(des_data)
    return b_data

def decode(secret):
    key = pyDes.des('12312312',pyDes.CBC, "12312312", pad=None,padmode=pyDes.PAD_PKCS5)
    b_secret = base64.b64decode(secret)
    des_secret = key.decrypt(b_secret)
    return des_secret

def send_msg(mobile,content):
    client = Client('http://%s/eis/webService/BizInvestService?wsdl'%settings.webservice_root)
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <REQ>
    <SIGN>
    <USERNAME>%s</USERNAME>
    <PASSWORD>%s</PASSWORD>
    </SIGN>
    <PARMAS>
    <ITEM>
    <MOBILE>%s</MOBILE>
    <MSGCONTENT>%s</MSGCONTENT>
    <MSGSIGN>2</MSGSIGN>
    </ITEM>
    </PARMAS>.
    </REQ>
    '''%(settings.webservice_user,settings.webservice_key,mobile,content)

    str = encode(xml)
    try:
        secret = client.service.sendMsgMd(str)
        res = decode(secret)
    except WebFault as detail:
        res = detail
    tree = ET.fromstring(res)
    code = tree.find('CODE').text
    return code

def test(str=''):
    if str == '':
        xml = '''
        <REQ>
        <SIGN>
        <USERNAME></USERNAME>
        <PASSWORD></PASSWORD>
        </SIGN>
        <PARMAS>
        <ITEM>
        <MOBILE></MOBILE>
        <MSGCONTENT></MSGCONTENT>
        </ITEM>
        </PARMAS>
        </REQ>
        '''
        print encode(xml)
    else:
        print decode(str)

def post_all_entsingle(xml=""):
    client = Client('http://%s/eis/webService/BizInvestService?wsdl'%settings.webservice_root)
    str = encode(xml)
    try:
        secret = client.service.postAllEntSingle(str)
        res = decode(secret)
    except WebFault as detail:
        res = detail
    tree = ET.fromstring(res)
    return res

if __name__ ==  "__main__":
    print send_msg(15151834774,"（东信宝），尊敬的用户：您好，您的短信验证码为：123456.有效时间为10分钟，请及时输入。")
    # post_all_entsingle()
