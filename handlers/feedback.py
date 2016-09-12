#-*- coding:utf-8 -*-

from dxb.handler import APIHandler
from dxb.handler import TokenAPIHandler
import  models.feedback as feedback_model
import libs.utils as utils
import random
import time


class FeedbackHandler(APIHandler):
    _model = 'feedback.FeedbackModel'

    def post(self):
        result = utils.init_response_data()
        try:
            feedback_content = self.get_argument("feedback_content")
            feedback_contact = self.get_argument("feedback_contact",None)
            user_id = self.get_argument("user_id")
            mobile_type = self.get_argument("mobile_type")
            feedback=({
                "user_id":user_id,
                "feedback_content":feedback_content,
                "feedback_contact":feedback_contact,
                "feedback_id":"FK"+mobile_type+time.strftime('%Y%m%d%M%S',time.localtime())+str(random.randint(0,999)).zfill(3),
                "add_time":utils.get_current_time(),
            })

            while self.coll.find_one({"feedback_id":feedback['feedback_id']}):
                feedback['feedback_id']="FK"+mobile_type+time.strftime('%Y%m%d%M%S',time.localtime())+str(random.randint(0,999)).zfill(3)
            self.coll.insert_one(feedback)



            result["data"]=utils.dump(feedback)
        except Exception,e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

    def get(self):
        result = utils.init_response_data()
        try:
            feedback_id = self.get_argument("feedback_id")
            feedback = self.coll.find_one({"feedback_id":feedback_id})
            if not feedback:
                raise ValueError(u"该反馈不存在")
            result["data"]=utils.dump(feedback)
        except Exception,e:
            result=utils.reset_response_data(0,unicode(e))
        self.finish(result)

    def delete(self):
        result = utils.init_response_data()
        try:
            feedback_id = self.get_argument("feedback_id")
            feedback = self.coll.find_one({"feedback_id":feedback_id})
            if feedback==None:
                raise ValueError(u"该反馈不存在")
            self.coll.remove(feedback)
            result["data"]=utils.dump(feedback)
        except Exception,e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

class FeedbackListHandler(APIHandler):
    _model = "feedback.FeedbackModel"
    def get(self):
        result = utils.init_response_data()
        try:
            page_size = self.get_argument("page_size",10)
            page = self.get_argument("page",1)
            length = self.coll.find().count()
            pager = utils.count_page(length,page,int(page_size))
            feedback_list=self.coll.find().limit(pager['page_size']).skip(pager['skip']).sort("add_time",-1)
            result["data"]=utils.dump(feedback_list)
            result["pager"]=pager
        except Exception,e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)



handlers=[
    (r"/api/feedback",FeedbackHandler),
    (r"/api/feedback_list",FeedbackListHandler)

]