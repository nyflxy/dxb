# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-08-18
"""

import pdb

from bson.son import SON
import libs.modellib as model
import libs.utils as utils
import dxb.consts as consts

import jieba.posseg as pseg

class AdminUserModel(model.BaseModel,model.Singleton):
    __name = "dxb.adminuser"

    def __init__(self):
        model.BaseModel.__init__(self,AdminUserModel.__name)
