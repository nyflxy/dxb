# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-07-13
"""
import pdb
from bson.son import SON
import libs.modellib as model
import dxb.consts as consts
import libs.utils as utils

class EnterpriseModel(model.BaseModel,model.Singleton):
    __name = "dbx.enterprise"

    def __init__(self):
        model.BaseModel.__init__(self,EnterpriseModel.__name)

    def format(self,rsp):
        temp = {}
        data = rsp
        try:
            del data["alidebt"]
            del data["punished"]
            del data["punishbreak"]
        except:
            pass
        data_keys = data.keys()
        for k in data_keys:
            try:
                if k in ["basic"]:
                    item = data[k].get("item",{})
                    temp[k] = item
                else:
                    temp[k] = []
                    items = data[k].get("item",[])
                    if not type(items) == list:
                        items = [items]
                    temp[k].extend(items)
            except :
                continue
        rsp = temp
        return rsp

    def parse(self,data):
        data = self.format(data)
        temp = {}
        basic = data["basic"]
        temp.update(basic)
        del data["basic"]
        temp.update(data)
        data = temp
        return data

    def get_count(self,obj):
        regno = obj.get("regno","")
        hotrecord_coll = model.BaseModel.get_model("hotrecord.HotRrecordModel").get_coll()
        hotrecord = hotrecord_coll.find_one({"regno":regno})
        if hotrecord:
            return hotrecord["count"]
        else:
            return 0
