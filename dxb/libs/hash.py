# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-04-14
#
from libs.utils import options,urldecode,md5
from urllib import urlencode
from Crypto.PublicKey import RSA
import binascii

def sign_encode(data):
    try:
        key = options['SIGN_KEY']
        # enter_sign = data.split('&sign=')[1]
        _values = data.split('&sign=')[0]
        values = urldecode(_values)
        _values_sort = sorted(values.iteritems(),key=lambda a:a[0],reverse=False)
        values_sort = urlencode(_values_sort).replace('+','%20').replace('%27',"'")
        sign = md5(values_sort+'&key='+key).upper()
    except:
        return 0
    return sign

#rsa加密
def rsa_encode(text):
    pub_key = RSA.importKey(open(options.root_path+'/ssl/id_rsa.pub'))
    x = pub_key.encrypt(text,None)
    y = binascii.hexlify(x[0])
    return y

#rsa解密
def rsa_decode(y):
    pri_key = RSA.importKey(open(options.root_path+'/ssl/id_rsa'))
    z = binascii.unhexlify(y)
    decrypted_text = pri_key.decrypt(z)
    return decrypted_text

