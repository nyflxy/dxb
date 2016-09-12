# -*- coding: utf-8 -*-
import json,pdb
import datetime
import time
import pymongo
import tornado
import urllib
import oauth2
import oauth2.tokengenerator
import oauth2.grant
import oauth2.store.redisdb
import oauth2.store.mongodb
from oauth2.web.tornado import OAuth2Handler
from tornado.options import options
import dxb.libs.utils as utils
import dxb.libs.modellib as modellib
import dxb.libs.wslib as wslib
from dxb.mail import send_email
from dxb.vendor.wxpay.wxpay import JsApi_pub,Wxinfo_pub
from dxb.handler import TokenAPIHandler,APIHandler,ListAPIHandler,\
    ListCreateAPIHandler,RetrieveUpdateDestroyAPIHandler
import models

class UserSignUp(APIHandler):
    model = models.AuthUserModel()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        result = utils.init_response_data()
        try:
            user_coll = self.model.get_coll()
            oauth_coll = models.OauthModel().get_coll()
            checkcode_coll = models.CheckCode().get_coll()

            mobile = self.get_argument("mobile")
            mobile_code = self.get_argument("mobile_code")
            email = self.get_argument("email")
            email_code = self.get_argument("email_code")
            password = self.get_argument("password")
            type = self.get_argument("type","b")

            if mobile == "":
                raise Exception("请输入手机号!")
            elif mobile_code == "":
                raise Exception("请输入手机验证码")
            elif password == "":
                raise Exception("请输入password!")

            # 检查手机验证码
            utils.check_code(checkcode_coll, mobile, mobile_code)
            # 检查邮箱验证码
            utils.check_code(checkcode_coll, email, email_code, type="email")

            add_time = datetime.datetime.now()
            login_date = ""
            headimgurl = ""
            nickname = ""
            username = ""
            active = 0
            sex = 0
            city = ""
            address = ""
            privilege = 0
            province = ""
            if not user_coll.find_one({'mobile': mobile}):

                user_coll.insert_one({
                    'mobile':mobile,
                    'email':email,
                    'password':password,
                    'add_time':add_time,
                    'login_date':login_date,
                    'headimgurl':headimgurl,
                    'nickname':nickname,
                    'username':'',
                    'active':active,
                    'sex':sex,
                    'city':city,
                    'address':address,
                    'privilege':privilege,
                    'province':province,
                    'type':type,
                })
                oauth_coll.insert_one({'identifier': mobile,
                                 'secret': password,
                                 'redirect_uris': [],
                                 'authorized_grants': [oauth2.grant.ClientCredentialsGrant.grant_type]})
            params = {
                'login': mobile,
                'password': password,
            }
            body = urllib.urlencode(params)
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(
                client.fetch,
                "http://localhost:8500" + "/api/user/signin",
                method='POST',
                body=body)
            response_body = json.loads(response.body)
            if response_body.has_key("error"):
                result = utils.reset_response_data(0,response_body["error"] + response_body["error_description"])
                self.finish(result)
                return

            result["data"] = response_body["response"]["data"]
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class UserSignIn(APIHandler):
    model = models.AuthUserModel()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        result = utils.init_response_data()
        user_coll = self.model.get_coll()
        try:
            login = self.get_argument("login")
            password = self.get_argument("password")
            is_save_password = int(self.get_argument("is_save_password", False))
            if login == "":
                raise Exception("请输入用户名!")
            elif user_coll.find({"mobile":login}).count() == 0 \
                              and user_coll.find({"email":login}).count() == 0:
                raise Exception("手机或邮箱不存在！")
            elif password == "":
                raise Exception("请输入密码!")

            user = user_coll.find_one({"mobile":login}) or user_coll.find_one({"email":login})
            if user["password"] != password:
                raise Exception("密码错误！")

            user["login_date"] = datetime.datetime.now()
            user_coll.save(user)

            params = {
                'client_id':user["mobile"],
                'client_secret':password,
                'grant_type':'client_credentials',
                'scope':'font-api',
            }
            body = urllib.urlencode(params)
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(
                client.fetch,
                  "http://localhost:8500/token",
                  method='POST',
                  body=body)
            response_body = json.loads(response.body)
            try:
                access_token = response_body["access_token"]
            except Exception ,e:
                result = utils.reset_response_data(-1, str(e) + \
                                                   response_body["error"]+" "+\
                                                   response_body["error_description"]+\
                                                   " or password error!")
                self.finish(result)
                return
            if is_save_password:
                self.model.delay_access_token(access_token)

            user["_id"] = str(user["_id"])
            # 存储 token-uid
            self.model.save_token_uid(access_token, user["_id"])

            user["add_time"] = str(user["add_time"]).split(".")[0]
            user["login_date"] = str(user["login_date"]).split(".")[0]
            del user["password"]
            result["data"] = user
            result["data"]["access_token"] = access_token
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class UserListHandler(ListAPIHandler):
    model = models.AuthUserModel()

class UserRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.AuthUserModel()
    mp_require_params = ["id"]  # put 方法必要参数
    mp_update_params = ["id","mobile","password1","password2","nickname","username"] # put 方法允许参数

    def delete(self):
        result = utils.init_response_data()
        try:
            raise Exception("操作限制！")
        except Exception,e:
            result = utils.reset_response_data(0, str(e))
        self.finish(result)

auth_provider = None
def init_oauth(*args,**options):
    global auth_provider
    if auth_provider :
        return auth_provider
    # Populate mock
    oauth_model = models.OauthModel()
    coll = oauth_model.get_coll()
    client_store = oauth2.store.mongodb.ClientStore(coll)

    # Redis for tokens storage
    token_store = oauth2.store.redisdb.TokenStore(rs=utils.Redis())

    # Generator of tokens
    token_generator = oauth2.tokengenerator.Uuid4()
    token_generator.expires_in[oauth2.grant.ClientCredentialsGrant.grant_type] = 3600 * 24

    # OAuth2 controller
    auth_provider = oauth2.Provider(
        access_token_store=token_store,
        auth_code_store=token_store,
        client_store=client_store,
        token_generator=token_generator
    )
    # auth_controller.token_path = '/oauth/token'

    default_scope = "font-api" # token默认具有的权限 默认具有前端访问权限
    scopes = ["font-api","back-api","system-api"] # token 可获得的权限
    # Add Client Credentials to OAuth2 controller
    auth_provider.add_grant(oauth2.grant.ClientCredentialsGrant(default_scope=default_scope,scopes=scopes))

    return auth_provider

class MobileCheckCode(APIHandler):
    model = models.CheckCode()

    def get(self):
        result = utils.init_response_data()
        checkcode_coll = self.model.get_coll()
        try:
            mobile = self.get_argument("mobile")
            curr_time = datetime.datetime.now()
            if checkcode_coll.find({"mobile":mobile,"enable_flag":True}).count() > 0:
                # 验证码请求限制 每小时限制5条
                if checkcode_coll.find({"mobile":mobile,
                        "add_time":{
                            "$gte":curr_time - datetime.timedelta(hours=1),
                            "$lte":curr_time + datetime.timedelta(hours=1),
                        }
                    }).count() >= 5:
                    raise Exception("验证码请求限制，每小时限制5条！")

                cr = checkcode_coll.find({"mobile":mobile,"enable_flag":True})
                for checkcode in cr:
                    checkcode["enable_flag"] = False
                    checkcode_coll.save(checkcode)
            else:
                pass
            random_code = utils.get_random_num(6,mode="number")

            checkcode_coll.insert_one({
                "mobile":mobile,
                "enable_flag":True,
                "add_time":curr_time,
                "type":"mobile",
                "code":random_code,
            })
            res = wslib.send_msg(mobile,"尊敬的用户您好，您本次的验证码为%s,30分钟内有效"%random_code)
            if res != "0" :
                raise ValueError(u"短信发送失败")
            result["data"]["code"] = random_code
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class EmailCheckCode(APIHandler):
    model = models.CheckCode()

    def get(self):
        result = utils.init_response_data()
        checkcode_coll = self.model.get_coll()
        try:
            email = self.get_argument("email")
            curr_time = datetime.datetime.now()
            if checkcode_coll.find({"email": email, "enable_flag": True}).count() > 0:
                # 验证码请求限制 每天限制5条
                if checkcode_coll.find({"email": email,
                                        "add_time": {
                                            "$gte": curr_time - datetime.timedelta(hours=1),
                                            "$lte": curr_time + datetime.timedelta(hours=1),
                                        }
                                        }).count() >= 5:
                    raise Exception("验证码请求限制，每小时限制5条！")

                cr = checkcode_coll.find({"email": email, "enable_flag": True})
                for checkcode in cr:
                    checkcode["enable_flag"] = False
                    checkcode_coll.save(checkcode)
            else:
                pass
            random_code = utils.get_random_num(6,mode="number")
            checkcode_coll.insert_one({
                "email": email,
                "enable_flag": True,
                "add_time": curr_time,
                "type": "email",
                "code": random_code,
            })
            # result['res'] = send_email('jltx@personcredit.com',[email],u'风控系统邮件验证','',html=u"【风控系统】尊敬的用户您好，您本次的验证码为%s,30分钟内有效"%random_code)
            result["data"]["code"] = random_code
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class WXUserHandler(APIHandler):
    model = models.UserModel()

    def get(self, *args, **kwargs):
        self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        pdb.set_trace()
        result = utils.init_response_data()
        try:
            user_id = self.get_argument("user_id","")
            if user_id != "" and user_id != "undefined":
                result['data'] = utils.dump(self.coll.find_one({"_id":utils.create_objectid(user_id)}))
        except Exception as e:
            result = utils.reset_response_data(0,str(e))
        self.finish(result)

class WXUserLoginHandler(APIHandler):
    model = models.UserModel()

    def post(self):
        result = utils.init_response_data()
        try:
            code = self.get_argument("code","")
            if code == '':
                raise ValueError(u"登录失败")
            js_pub = JsApi_pub()
            js_pub.setCode(code)
            wx_user = js_pub.get_user_info()
            user = self.model.get(wx_user)
            result['data'] = utils.dump(user)
        except Exception as e:
            result = utils.reset_response_data(0,str(e))
        self.finish(result)

class WXUserBundleHandler(APIHandler):
    def post(self):
            result = utils.init_response_data()
            code_model_obj = models.code_model.CodeModel()
            code_coll = code_model_obj.get_coll()
            user_model_obj = models.user_model.UserModel()
            user_coll = user_model_obj.get_coll()
            try:
                mobile = self.get_argument("mobile")
                mobile_code = self.get_argument("mobile_code")
                user_id = self.get_argument("user_id")
                utils.check_code(code_coll,mobile,mobile_code)

                user = user_coll.find_one({
                    "mobile":mobile,
                })
                if user:
                    raise Exception(u'该手机号已被使用！')

                user = user_coll.find_one({
                    "_id":utils.create_objectid(user_id)
                })
                if user["mobile"] != mobile:
                    user["mobile"] = mobile
                    user_coll.save(user)

            except Exception, e:
                result = utils.reset_response_data(0,unicode(e))
            self.finish(result)


class SendMessageHandler(APIHandler):
    def post(self):
        result = utils.init_response_data()
        code_model_obj = models.code_model.CodeModel()
        code_coll = code_model_obj.get_coll()
        try:
            mobile = self.get_argument("mobile")
            curr_time = datetime.datetime.now()
            if code_coll.find({"mobile":mobile,"enable_flag":True}).count() > 0:
                # 验证码请求限制 每小时限制5条
                if code_coll.find({"mobile":mobile,
                        "add_time":{
                            "$gte":curr_time - datetime.timedelta(hours=1),
                            "$lte":curr_time + datetime.timedelta(hours=1),
                        }
                    }).count() >= 5:
                    raise Exception("验证码请求限制，每小时限制5条！")

                code_list = code_coll.find({"mobile":mobile,"enable_flag":True})
                for c in code_list:
                    c["enable_flag"] = False
                    code_coll.save(c)
            else:
                pass
            random_code = utils.get_random_num(6,mode="number")
            code_coll.insert_one({
                "mobile":mobile,
                "enable_flag":True,
                "add_time":curr_time,
                "type":"mobile",
                "code":random_code,
            })

            res = wslib.send_msg(mobile,"（东信宝），尊敬的用户:您好，您的短信验证码为%s,有效时间为10分钟，请及时输入。"%random_code)
            if res != "0":
                raise ValueError(u'短信发送失败')
            result["code"] = random_code
        except Exception,e :
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

handlers = [
                (r"/api/user/signup", UserSignUp),
                (r"/api/user/signin", UserSignIn),
                (r"/api/user/list", UserListHandler),
                (r"/api/user", UserRetrieveUpdateDestroyHandler),
                (r'/token', OAuth2Handler,init_oauth()),
                (r"/api/checkcode/mobile", MobileCheckCode),
                (r"/api/checkcode/email", EmailCheckCode),

                (r"/api/wx_user", WXUserHandler),
                (r"/api/wx_user/login", WXUserLoginHandler),
                (r"/api/wx_user/bundle", WXUserBundleHandler),
                (r"/api/wx_sms", SendMessageHandler),
            ]