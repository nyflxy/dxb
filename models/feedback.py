# -*- coding:utf-8 -*-

import libs.utils as utils
import libs.modellib as model

class FeedbackModel(model.BaseModel,model.Singleton):
    __name = "dxb.feedback"

    def __init__(self):
        model.BaseModel.__init__(self,FeedbackModel.__name)