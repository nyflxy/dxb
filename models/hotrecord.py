# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-18
"""

import pdb

from bson.son import SON
import libs.modellib as model
import dxb.consts as consts
import libs.utils as utils

import jieba.posseg as pseg

class HotRrecordModel(model.BaseModel,model.Singleton):
    __name = "renren.hotrecord"

    def __init__(self):
        model.BaseModel.__init__(self,HotRrecordModel.__name)

    def record_search_count(self,query_params=None):
        if query_params :
            obj = self.get_coll().find_one(query_params)
            if obj :
                obj["count"] += 1
                update_params = obj
                self.update(query_params,update_params)
            else:
                obj = query_params
                obj["count"] = 1
                self.create(**obj)
            return obj
        return {}





