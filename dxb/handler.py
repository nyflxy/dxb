# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

import traceback
import logging
import logging.config
import urllib
import hashlib
import json,time,pdb
import pdb
import inspect
import sys
import re
import copy
import datetime
from tornado import escape
from tornado.options import options
from tornado.web import RequestHandler as BaseRequestHandler, HTTPError
import dxb.exceptions as exceptions
import libs.utils as utils
import libs.modellib as modellib
import libs.redislib as redislib
import libs.reportlib as reportlib

try:
    import importlib
except:
    import libs.importlib as importlib

class Dict(dict):
    def __missing__(self, key):
        rv = self[key] = Dict()
        return rv
    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)

class BaseHandler(BaseRequestHandler):
    _model = None
    model  = None

    def initialize(self):
        self.set_model()
        super(BaseHandler,self).initialize()

    def set_model(self):
        if self.model == None:
            self.model = modellib.BaseModel.get_model(self._model)
            if self.model is not None:
                self.coll = self.model.get_coll()
            else:
                self.coll = None

    def get(self, *args, **kwargs):
        # enable GET request when enable delegate get to post
        if options.app_get_to_post:
            self.post(*args, **kwargs)
        else:
            raise exceptions.HTTPAPIError(405)

    def prepare(self):
        self.traffic_control()
        pass

    def traffic_control(self):
        # traffic control hooks for api call etc
        self.log_apicall()
        pass

    def log_apicall(self):
        pass

    def format_arguments(self):
        arguments = self.request.arguments
        obj = Dict()
        for (k,v) in arguments.items():
            try:
                exec("%s = '%s'"%(k,v[0].decode()))
            except UnicodeDecodeError as e:
                exec("%s = '%s'"%(k,v[0]))
            except Exception as e:
                print(e)
                pass
        return obj

    def format_request_params(self):
        arguments = self.request.arguments
        format_params = u""
        for (k, v) in arguments.items():
            try:
                if v[0].isdigit():
                    format_params += unicode("%s = '%s'," % (k, v[0]))
                    continue
                try:
                    format_params += unicode("%s = %s," % (k, json.loads(v[0].decode("utf-8"))))
                except:
                    format_params += unicode("%s = '%s'," % (k, v[0].decode("utf-8")))
            except UnicodeDecodeError as e:
                try:
                    temp = "%s = %s," % (k, json.loads(v[0]))
                except:
                    temp = "%s = '%s'," % (k, v[0])
                format_params += temp.decode("utf-8")
            except Exception as e:
                print(e)
                pass
        return format_params

    def check_request_params(self, require_params=[]):
        arguments_keys = self.request.arguments.keys()
        for require_param in require_params:
            if require_param not in arguments_keys:

                raise Exception(u"参数不能为空:"+ require_param)

    def _get_search_time(self, time_desc, start_time, end_time):
        if time_desc == "user_defined":
            if not start_time or not end_time:
                raise Exception("请选择时间！")
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


class RequestHandler(BaseHandler):
    pass


class APIHandler(BaseHandler):
    def get_current_user(self):
        pass

    def finish(self, chunk=None, notification=None,origin=False,status_code=200):
        self.set_header("Access-Control-Allow-Origin","*")
        self.set_header("Access-Control-Allow-Headers","X-Requested-With,Set-Cookie")
        self.set_header("Access-Control-Allow-Methods","PUT,DELETE,POST,GET")
        self.set_header('Content-type', 'application/x-www-form-urlencoded; charset=utf-8')
        #设置header键值对
        if chunk is None:
            chunk = {}

        if isinstance(chunk, dict):#chunk默认情况下给chunk一个dict地址值，并执行下列步骤
            if origin != True:
                chunk = {"meta": {"code": status_code}, "response": chunk}  #orgin默认情况下给chunk赋"meta"={"code":200}
                                                                        #"response"=上次的chunk的字典内容

            if notification:
                chunk["notification"] = {"message": notification}#如果notification有值则再chunk中添加notification键值对

        callback = escape.utf8(self.get_argument("callback", None))

        #self.set_header("Access-Control-Allow-Credentials",'true')

        if callback:
            self.set_header("Content-Type", "application/x-javascript; charset=utf-8;")

            if isinstance(chunk, dict):
                chunk = escape.json_encode(chunk)

            self._write_buffer = [callback, "(", chunk, ")"] if chunk else []
            super(APIHandler, self).finish()
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            super(APIHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages."""
        debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]

            if isinstance(e, exceptions.HTTPAPIError):
                pass
            elif isinstance(e, HTTPError):
                e = exceptions.HTTPAPIError(e.status_code)
            else:
                e = exceptions.HTTPAPIError(500)

            exception = "".join([ln for ln in traceback.format_exception(*exc_info)])

            if status_code == 500 and not debug:
                #self._send_error_email(exception)
                e.response["exception"] = exception

            if debug:
                e.response["exception"] = exception

            self.clear()
            self.set_status(200)  # always return 200 OK for API errors
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(unicode(e))
        except Exception:
            logging.error(traceback.format_exc())
            return super(APIHandler, self).write_error(status_code, **kwargs)
'''
    def _send_error_email(self, exception):
        try:
            # send email
            subject = "[%s]Internal Server Error" % options.sitename
            body = self.render_string("errors/500_email.html",
                                      exception=exception)
            if options.send_error_email:
                email_tasks.send_email_task.delay(options.email_from,
                                                  options.admins, subject, body)
        except Exception:
            logging.error(traceback.format_exc())
'''

#带加密字段的处理器
class TokenAPIHandler(APIHandler):

    def initialize(self, provider):
        self.provider = provider

    # authenticate tokens
    def prepare(self):
        try:
            token = self.get_argument('access_token', None)
            if not token:
                auth_header = self.request.headers.get('Authorization', None)
                if not auth_header:
                    raise Exception('This resource need a authorization token')
                token = auth_header[7:]

            key = 'oauth2_{}'.format(token)
            access = self.provider["provider"].access_token_store.rs.get(key)
            if access:
                access = json.loads(access.decode())
            else:
                raise Exception('Invalid Token')
            if access['expires_at'] <= int(time.time()):
                raise Exception('expired token')
            authority = importlib.import_module("dxb.authority").authority
            authority.process(self.request,access)
        except Exception as err:
            self.set_header('Content-Type', 'application/json')
            self.set_status(401)
            result = utils.reset_response_data(0, str(err))
            self.finish(result,status_code=401)

    def get_user_id(self):
        token = self.get_argument('access_token', None)
        if not token:
            auth_header = self.request.headers.get('Authorization', None)
            if not auth_header:
                raise Exception('This resource need a authorization token')
            token = auth_header[7:]
        redis_tool = redislib.RedisTool()
        user_id = redis_tool.get(token)
        return utils.create_objectid(user_id)

class ErrorHandler(RequestHandler):
    """Default 404: Not Found handler."""
    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise HTTPError(404)


class APIErrorHandler(APIHandler):
    """Default API 404: Not Found handler."""
    def prepare(self):
        super(APIErrorHandler, self).prepare()
        raise exceptions.HTTPAPIError(404)

class ListCreateAPIHandler(APIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    mp_require_params = []  # post 方法必要参数
    mp_default_params = {}  # post 方法默认参数
    query_params = []
    mg_extra_params = []  # 返回数据额外字段
    mp_update_or_raise = "update"

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            request_params = self.format_request_params()
            exec("""objs, pager = self.model.search_list(%s)"""%request_params)
            result["data"] = objs
            result["pager"] = pager
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.finish(result)
            return
        self.finish(result)

    def post(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            self.check_request_params(self.mp_require_params)
            request_params = self.format_request_params()
            exec("""request_params = self.mp_default_params.update(%s)"""%request_params)
            request_params = self.mp_default_params

            query_params = {}
            for key in self.query_params:
                query_params.update({
                    key:request_params[key],
                })

            if query_params == {} or not self.model.is_exists(query_params):
                obj = self.model.create(**request_params)
                result["data"] = utils.dump(obj)
            else:
                if self.mp_update_or_raise == "update":
                    obj = self.model.search(query_params)
                    query_params = {"_id":utils.create_objectid(obj["_id"])}
                    result["data"] = self.model.update(query_params,request_params)
                else:
                    raise Exception("已存在！")
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class RetrieveUpdateDestroyAPIHandler(APIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    mp_require_params = []  # put 方法必要参数
    mp_default_params = {}  # put 方法默认参数
    mp_update_params  = []  # put 方法允许参数
    md_require_params = []  # delete 方法必要参数
    md_default_params = {}  # delete 方法默认参数
    query_params = []
    mg_extra_params = [] # 返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            id = self.get_argument("id")
            _id = utils.create_objectid(id)
            ret = self.model.search({"_id": _id})
            if ret:
                result["data"] = ret
            else:
                result["data"] = {}
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def put(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            id = self.get_argument("id")
            _id = utils.create_objectid(id)

            address = self.get_argument("address", "")
            self.check_request_params(self.mp_require_params)
            request_params = self.format_request_params()

            update_params = {}
            exec ("""update_params.update(%s)""" % request_params)
            self.check_update_params(update_params)
            update_params["_id"] = _id
            del update_params["id"]

            ret = self.model.update(query_params={"_id": _id}, update_params=update_params)
            result['data'] = ret
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def check_update_params(self,update_params):
            update_params_keys = update_params.keys()
            for param in update_params:
                if param not in self.mp_update_params:
                    raise Exception("无法修改：%s!"%param)

    def delete(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            ids = json.loads(self.get_argument("ids"))
            _ids = [utils.create_objectid(id) for id in ids]
            for _id in _ids:
                self.model.delete(_id=_id)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class DestroyAPIHandler(APIHandler):

    def delete(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            ids = json.loads(self.get_argument("ids"))
            _ids = [utils.create_objectid(id) for id in ids]
            for _id in _ids:
                self.model.delete(_id=_id)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def get(self):
        raise Exception("method not access")

    def put(self):
        raise Exception("method not access")

class ListCreateTokenAPIHandler(TokenAPIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    mp_require_params = []  # post 方法必要参数
    mp_default_params = {}  # post 方法默认参数
    query_params = []
    mg_extra_params = []  # 返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            request_params = self.format_request_params()
            exec("""objs, pager = self.model.search_list(%s)"""%request_params)
            result["data"] = objs
            result["pager"] = pager
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.finish(result)
            return
        self.finish(result)

    def post(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            self.check_request_params(self.mp_require_params)
            request_params = self.format_request_params()
            exec("""request_params = self.mp_default_params.update(%s)"""%request_params)
            request_params = self.mp_default_params

            query_params = {}
            for key in self.query_params:
                query_params.update({
                    key:request_params[key],
                })

            if not self.model.is_exists(query_params):
                obj = self.model.create(**request_params)
                result = utils.dump(obj)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class RetrieveUpdateDestroyTokenAPIHandler(TokenAPIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    mp_require_params = []  # put 方法必要参数
    mp_default_params = {}  # put 方法默认参数
    mp_update_params  = []  # put 方法允许参数
    md_require_params = []  # delete 方法必要参数
    md_default_params = {}  # delete 方法默认参数
    query_params = []
    mg_extra_params = []  # 返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            id = self.get_argument("id")
            _id = utils.create_objectid(id)
            ret = self.model.search({"_id": _id})
            if ret:
                result["data"] = ret
            else:
                result["data"] = {}
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def put(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            id = self.get_argument("id")
            _id = utils.create_objectid(id)

            address = self.get_argument("address", "")
            self.check_request_params(self.mp_require_params)
            request_params = self.format_request_params()

            update_params = {}
            exec ("""update_params.update(%s)""" % request_params)
            self.check_update_params(update_params)
            update_params["_id"] = _id
            del update_params["id"]

            ret = self.model.update(query_params={"_id": _id}, update_params=update_params)
            result['data'] = ret
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def check_update_params(self,update_params):
            update_params_keys = update_params.keys()
            for param in update_params:
                if param not in self.mp_update_params:
                    raise Exception("无法修改：%s!"%param)

    def delete(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            ids = json.loads(self.get_argument("ids"))
            _ids = [utils.create_objectid(id) for id in ids]
            for _id in _ids:
                self.model.delete(_id=_id)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

class ListAPIHandler(APIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    mg_query_params = {}  # get 方法查询参数
    mg_sort_params = {}   # get 方法排序字段
    mg_extra_params = []  # get 方法返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            page = self.get_argument("page", 1)
            page_size = self.get_argument("page_size", 10)
            time_desc = self.get_argument("time_desc", "all")
            start_time = self.get_argument("start_time", None)
            end_time = self.get_argument("end_time", None)
            if time_desc != "all":
                start_time, end_time = self._get_search_time(time_desc, start_time, end_time)
                self.mg_query_params.update({
                    "add_time": {
                        "$gte": start_time,
                        "$lte": end_time,
                    }
            })
            objs, pager = self.model.search_list(page=page,page_size=page_size,query_params=self.mg_query_params)
            result["data"] = objs
            result["pager"] = pager
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.finish(result)
            return
        self.finish(result)
    def post(self):
        raise Exception("method not access")

class ListTokenAPIHandler(TokenAPIHandler):
    mg_require_params = []  # get 方法必要参数
    mg_default_params = {}  # get 方法默认参数
    query_params = []
    mg_extra_params = []  # 返回数据额外字段

    def get(self):
        result = utils.init_response_data()
        self.model.extra_params = self.mg_extra_params
        try:
            request_params = self.format_request_params()
            exec ("""objs, pager = self.model.search_list(%s)""" % request_params)
            result["data"] = objs
            result["pager"] = pager
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.finish(result)
            return
        self.finish(result)

class ReportHandler(APIHandler):
    _model = "order.OrderModel"
    mg_query_params = {} # get 方法查询参数
    mg_sort_params = {}  # get 方法排序字段
    namelist = [u'序号'] # 报表表头
    column_list = [] #报表表头字段
    report_name = "报表" #报表名

    def get(self):
        try:
            obj_list, pager = self.model.search_list(query_params=self.mg_query_params, pager_flag=False)
            namelist = self.namelist
            column_list = self.column_list
            if len(namelist) != len(column_list) + 1:
                raise Exception("namelist and column_list 长度不一致")
            elif len(column_list) == 0 and len(namelist) == 1:
                if len(obj_list) > 0:
                    obj = obj_list[0]
                    namelist = self.namelist + obj.keys()
                    column_list = obj.keys()

            curr_time = str(datetime.datetime.now())
            report_china_name = "%s%s" % (
                self.report_name, curr_time.replace(".", "-").replace(" ", "-").replace(":", "-"))
            format_column_list = ["%s:None"%column for column in column_list]
            column_dict = {}
            map(lambda x: column_dict.setdefault(x.split(':')[0], x.split(':')[1]), format_column_list)
            temp_column_dict = column_dict
            export_list = []
            for obj in obj_list:
                for column in column_list:
                    if obj.has_key(column):
                        temp_column_dict[column] = obj[column]
                    else:
                        try:
                            temp_column_dict[column] = getattr(self.model, "get_%s" % column)(obj)
                        except:
                            temp_column_dict[column] = ""

                export_list.append(copy.copy(temp_column_dict))
                temp_column_dict = column_dict

            if len(export_list) > 0:
                fieldlist = column_list
            else:
                fieldlist = []
            result = reportlib.export_excel(report_china_name=[report_china_name], namelist=[namelist],
                                              result=[export_list], fieldlist=[fieldlist], )
            file_names = result['filename']
            file_paths = result["file_path"]
            report_data = result["report_data"]
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_names[0])
        with open(file_paths[0], 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        self.finish()
