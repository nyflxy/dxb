#coding=utf-8

import datetime,json
import libs.modellib as model
import libs.utils as utils
import libs.redislib as redis

class OauthModel(model.BaseModel,model.Singleton):
    __name = "dxb.oauth_clients"

    def __init__(self):
        model.BaseModel.__init__(self,OauthModel.__name)

class AuthUserModel(model.BaseModel,model.Singleton):
    __name = "dxb.authuser"

    def __init__(self):
        model.BaseModel.__init__(self,AuthUserModel.__name)

    def get_token_uid(self, token):
        redis_tool = redis.RedisTool()
        uid = redis_tool.get(token)
        return uid

    def save_token_uid(self, token, uid):
        redis_tool = redis.RedisTool()
        if not redis_tool.get(token):
            redis_tool.set(token, uid)
        else:
            pass

    def delay_access_token(self, token):
        redis_tool = redis.RedisTool()
        oauth2_key = "oauth2_" + token
        access = redis_tool.get(oauth2_key)
        access = json.loads(access)
        access["expires_at"] += 3600 * 24 * 14
        access = json.dumps(access)
        redis_tool.set(oauth2_key, access)

    def _get_search_time(self, time_desc, start_time, end_time):
        if time_desc == "user_defined":
            if not start_time or not end_time:
                raise Exception("请选择时间！")
            # start_time = utils.strtodatetime(start_time, '%Y-%m-%d %H:%M:%S')
            # end_time = utils.strtodatetime(end_time,'%Y-%m-%d %H:%M:%S')
            start_time = utils.strtodatetime(start_time, '%Y-%m-%d %H:%M')
            end_time = utils.strtodatetime(end_time, '%Y-%m-%d %H:%M')
            return start_time, end_time
        else:
            curr_time = datetime.datetime.now()
            end_time = curr_time
            if time_desc == "nearly_three_days":
                start_time = curr_time - datetime.timedelta(days=3)
            elif time_desc == "nearly_a_week":
                start_time = curr_time - datetime.timedelta(days=7)
            elif time_desc == "nearly_a_month":
                start_time = curr_time - datetime.timedelta(days=30)
            else:
                raise Exception("查询时间未定义")
        return start_time, end_time

class CheckCode(model.BaseModel,model.Singleton):
    __name = "dxb.checkcode"

    def __init__(self):
        model.BaseModel.__init__(self,CheckCode.__name)

class UserModel(model.BaseModel,model.Singleton):
    __name = "dxb.user"

    def __init__(self):
        model.BaseModel.__init__(self,UserModel.__name)

    def get(self,user):
        _user = self.get_coll().find_one({"wx_user.openid":user['openid']})
        if _user is None:
            _user = {}
            _user['mobile'] = ''
            _user['permission'] = ''
            _user['email'] = ''
            _user['add_time'] = utils.get_now()
            _user['login_time'] = utils.get_now()
            _user['enable_flag'] = 1
            _user['wx_user'] = user
            _user['uid']=SeqModel().getNextSequence()
        else:
            _user['login_time'] = utils.get_now()
            _user['wx_user'].update(user)
        self.get_coll().save(_user)
        return _user

class SeqModel(model.BaseModel,model.Singleton):
    __name = "dxb.seq"

    def __init__(self):
        model.BaseModel.__init__(self,SeqModel.__name)

    def getNextSequence(self):
        ret=self.coll.find_and_modify(
             query={},
             update={'$inc':{'seq':1}},
             upsert=True,
        )
        return 'U'+str(utils.dump(self.coll.find({}))[0].get('seq')).zfill(7)

class CodeModel(model.BaseModel,model.Singleton):
    __name = "dxb.code"

    def __init__(self):
        model.BaseModel.__init__(self,CodeModel.__name)