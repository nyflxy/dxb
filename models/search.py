# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-18
"""

import pdb

from bson.son import SON
import libs.utils as utils
import libs.modellib as model

import jieba.posseg as pseg

class SearchModel(model.BaseModel,model.Singleton):
    __name = "dhuicredit.search"

    def __init__(self):
        model.BaseModel.__init__(self,SearchModel.__name)

    def create(self,*args,**kwargs):
        keyword = kwargs.get("keyword","")
        if keyword != "":
            pseg_words = pseg.cut(keyword)
            words = []
            for obj in pseg_words:
                print obj.flag
                if obj.flag in ["ns","nrt","nz","n"]:
                    words.append(obj.word)
        else:
            words = []

        coll = self.get_coll()
        for word in words :
            search_obj = coll.find_one({"word":word})
            if search_obj:
                search_obj["count"] += 1
            else:
                search_obj = {
                    "word":word,
                    "count":1,
                    "len":len(word),
                }
            coll.save(search_obj)


