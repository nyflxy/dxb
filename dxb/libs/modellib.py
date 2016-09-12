# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-07-13
"""

import sys
import inspect
import json
import pdb,datetime

import mongolib
import utils
from utils import options

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class BaseModel(object):
    coll = None
    _request = None
    _arguments = None

    def __init__(self,name):
        self.__name = name
        self.coll = self.get_coll()

    def set_request(self,request):
        self._request = request
        self._arguments = utils.urldecode(self._request.body)

    def get_argument(self,key,default=None):
        return self._arguments.get(key,default)

    def coll_name(self):
        return self.__name.split(".")[1]

    def db_name(self):
        return self.__name.split(".")[0]

    def get_coll(self):
        coll_name = self.coll_name()
        coll = mongolib.get_coll(coll_name)
        return coll

    def get_columns(self):
        columns = []
        coll = self.get_coll()
        if coll.find().count() > 0:
            document = coll.find_one()
            columns = document.keys()
        return columns

    def is_exist(self,id,column='_id',is_objectid=True):
        try:
            if is_objectid:
                items = self.get_coll().find_one({column:utils.create_objectid(id)})
            else:
                items = self.get_coll().find_one({column:id})
        except:
            return False
        return items != None

    def list(self,query_list,sort_list,use_pager=True,is_origin=False,page=1,page_size=options.page_size):
        length = self.get_coll().find(query_list).count()

        if use_pager:
            pager = utils.count_page(length,page,page_size)
            list = self.get_coll().aggregate([{"$match" : query_list},
                                                   {"$sort":sort_list},
                                                   {"$skip":pager['skip']},
                                                   {"$limit":pager['page_size']}])
        else:
            pager = []
            list = self.get_coll().aggregate([{"$match" : query_list},
                                                   {"$sort":sort_list}
                                                   ])
        if is_origin:
            return list,pager
        else:
            return utils.dump(list),pager

    @classmethod
    def get_model(cls,model_name):
        try:
            model_filename = model_name.split(".")[0]
            model_classname = model_name.split(".")[1]
            model_obj = sys.modules['%s.%s'%("models",model_filename)]
            models = inspect.getmembers(model_obj,inspect.isclass)
            for m in models:
                if m[0] == model_classname:
                    model = m[1]()
        except Exception as e:
            model = None
        return model

    def is_exists(self, query_params):
        obj = self.get_coll().find_one(query_params)
        return obj != None

    def create(self, **obj):
        coll = self.get_coll()
        curr_time = datetime.datetime.now()
        obj = json.loads(json.dumps(obj))
        obj["add_time"] = str(curr_time)
        coll.insert_one(obj)
        return utils.dump(obj)

    def search(self, query_params):
        coll = self.get_coll()
        obj = coll.find_one(query_params)
        obj = utils.dump(obj)
        try:
            for extra_param in self.extra_params:
                exec ("""obj[extra_param] = self.get_%s(obj)""" % extra_param)
        except:
            pass
        return obj

    def update(self, query_params, update_params):
        coll = self.get_coll()
        obj = coll.find_one(query_params)
        if obj:
            obj.update(update_params)
            ret = coll.save(obj)
        else:
            obj = {}
        return utils.dump(obj)

    def delete(self, **query_params):
        coll = self.get_coll()
        ret = coll.remove(query_params)
        return ret

    def search_list(self, page=1, page_size=10, query_params={}, sort_params={},pager_flag=True):
        if sort_params == {}:
            sort_params.update({"add_time": -1})

        coll = self.get_coll()
        if pager_flag:
            length = coll.find(query_params).count()
            pager = utils.count_page(length, page, page_size)
            cr = coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params},
                {"$skip": pager['skip']},
                {"$limit": pager['page_size']}])
        else:
            pager = utils.count_page(0, page, page_size)
            cr = coll.aggregate([
                {"$match": query_params},
                {"$sort": sort_params}])

        objs = []
        for obj in cr:
            obj = utils.dump(obj)
            try:
                for extra_param in self.extra_params:
                    exec("""obj[extra_param] = self.get_%s(obj)"""%extra_param)
                objs.append(obj)
            except:
                objs.append(obj)

        return objs, pager