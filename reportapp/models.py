#coding=utf-8

import libs.modellib as model
import libs.utils as utils

class ReportModel(model.BaseModel):
    __name = "dxb.report"

    def __init__(self):
        model.BaseModel.__init__(self,ReportModel.__name)