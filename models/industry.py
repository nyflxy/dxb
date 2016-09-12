# -*- coding:utf-8 -*-
import libs.modellib as model

class IndustryModel(model.BaseModel,model.Singleton):
    __name = 'dxb.industry'

    def __init__(self):
        model.BaseModel.__init__(self,IndustryModel.__name)