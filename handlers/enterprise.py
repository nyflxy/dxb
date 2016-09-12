# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-18
"""

import json,pdb
import oauth2
import datetime
import tornado
import urllib
from tornado.options import options as settings
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.wslib as wslib
import libs.modellib as model
import libs.xmllib as xmllib

class EnterpriseListCreateHandler(ListCreateAPIHandler):
    _model = "enterprise.EnterpriseModel"
    query_params  = {}
    mg_extra_params = ["count"]

    def get(self):
        result = utils.init_response_data()
        try:
            page = self.get_argument("page",1)
            page_size = self.get_argument("page_size",10)
            first_industry = self.get_argument("first_industry","")
            time_desc = self.get_argument("time_desc", "all")
            start_time = self.get_argument("start_time", None)
            end_time = self.get_argument("end_time", None)
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        l_query_params = {}
        if first_industry != "":
            l_query_params = {"industryphy":first_industry}
        if time_desc != "all":
            start_time, end_time = self._get_search_time(time_desc, start_time, end_time)
            l_query_params.update({
                "add_time": {
                    "$gte": str(start_time),
                    "$lte": str(end_time),
                }
            })
        else:
            pass  # 全部
        self.request.arguments = {"page":page,"page_size":page_size,"query_params":[json.dumps(l_query_params)]}
        ListCreateAPIHandler.get(self)

    def post(self):
        result = utils.init_response_data()
        try:
            key = self.get_argument("key")
            keytype = self.get_argument("keytype")

            req_xml = """<?xml version="1.0" encoding="UTF-8"?><REQ>
                <SIGN>
                <USERNAME>%s</USERNAME>
                <PASSWORD>%s</PASSWORD>
                </SIGN>
                <PARMAS>
                <KEY>%s</KEY>
                <KEYTYPE>%s</KEYTYPE>
                </PARMAS>
                </REQ>
            """ % (settings.webservice_user,settings.webservice_key,key, keytype)
            res_xml = wslib.post_all_entsingle(req_xml)
            rsp = xmllib.Xml2Json(res_xml).result
            if rsp.has_key("rsp"):
                rsp = rsp["rsp"]
                rsp["code"] = "200"
            if rsp.has_key("code") and rsp["code"] == "200":
                result["data"] = []
                self.finish(result)
                return
            else:
                document = self.model.parse(rsp.get("data",{}))
                document["image"] = "/static/main_company.png"
                self.mp_default_params.update(document)
                self.query_params = ["regno"]
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        self.request.arguments = {}
        ListCreateAPIHandler.post(self)

class EnterpriseRetrieveUpdateDestoryHandler(RetrieveUpdateDestroyAPIHandler):
    _model = "enterprise.EnterpriseModel"
    mp_require_params = ["id"]  # put 方法必要参数
    mp_update_params = ["id"] # put 方法允许参数
    mg_extra_params = ["count"]

    def get(self):
        result = utils.init_response_data()
        try:
            id = self.get_argument("id")
            _id = utils.create_objectid(id)
            obj = self.model.get_coll().find_one({"_id": _id})
            if obj:
                regno = obj["regno"]
                model.BaseModel.get_model("hotrecord.HotRrecordModel").record_search_count({"regno": regno})
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.finish(result)
            return
        RetrieveUpdateDestroyAPIHandler.get(self)

class EnterpriseHotHandler(APIHandler):
    _model = "enterprise.EnterpriseModel"

    def get(self):
        result = utils.init_response_data()
        try:
            page = self.get_argument("page", 1)
            page_size = self.get_argument("page_size", 10)
            sort_params = {"count":-1}
            objs,pager = model.BaseModel.get_model("hotrecord.HotRrecordModel").search_list(page,page_size,sort_params=sort_params)
            enterprise_ids = []
            enterprise_count = {}
            for obj in objs:
                enterprise_count[obj["regno"]] = obj["count"]
                enterprise_ids.append(obj["regno"])
            cursor = self.model.get_coll().find({"regno":{"$in":enterprise_ids}})
            objs = [utils.dump(obj) for obj in cursor]
            for obj in objs:
                obj["count"] = enterprise_count[obj["regno"]]
            objs.sort(key=lambda obj: obj["count"],reverse=True)
            result["data"] = objs
            result["pager"] = pager
        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        self.finish(result)

class EnterpriseSearchHandler(APIHandler):
    _model = "enterprise.EnterpriseModel"

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        result = utils.init_response_data()
        try:
            key = self.get_argument("key")
            if key.isdigit():
                keytype = "3"
            else:
                keytype = "2"
            page = self.get_argument("page",1)
            page_size = self.get_argument("page_size",10)

            query_params = {}
            # 2企业名称 3工商注册号
            if keytype == "3":
                query_params.update({
                    "regno": {"$regex":key},
                })
            elif keytype == "2":
                query_params.update({
                    "entname": {"$regex":key},
                })
            curr_time = datetime.datetime.now()
            deadline = str(curr_time - datetime.timedelta(days=settings.deadline_time))
            query_params.update({"add_time":{"$gte":deadline}})
            datas,pager = self.model.search_list(page,page_size,query_params=query_params)
            if len(datas):
                result["data"] = datas
                result["pager"] = pager
            else:
                body = urllib.urlencode({"key":key.encode("utf-8"),"keytype":keytype})
                client = tornado.httpclient.AsyncHTTPClient()
                response = yield tornado.gen.Task(
                    client.fetch,
                    "http://127.0.0.1:%s"%settings.port + "/api/enterprise/list",
                    method='POST',
                    body=body)
                response_body = json.loads(response.body)
                res_data = response_body["response"]["data"]
                if type(res_data) == list:
                    pager = utils.count_page(0, page, page_size)
                    result["data"] = []
                    result["pager"] = pager
                else:
                    pager = utils.count_page(1, page, page_size)
                    result["data"] = [res_data]
                    result["pager"] = pager

            try:
                if keytype == "2":
                    body = urllib.urlencode({"keyword": key.encode("utf-8")})
                    client = tornado.httpclient.AsyncHTTPClient()
                    response = yield tornado.gen.Task(
                        client.fetch,
                        "http://127.0.0.1:%s"%settings.port + "/api/search/list",
                        method='POST',
                        body=body)
            except:
                pass

        except Exception, e:
            result = utils.reset_response_data(0, unicode(e))
            self.finish(result)
            return
        self.finish(result)

handlers = [
    (r"/api/enterprise/list", EnterpriseListCreateHandler),
    (r"/api/enterprise", EnterpriseRetrieveUpdateDestoryHandler),
    (r"/api/enterprise/hot", EnterpriseHotHandler),
    (r"/api/enterprise/search", EnterpriseSearchHandler),
]