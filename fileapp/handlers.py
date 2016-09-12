#coding=utf-8

from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.modellib as model
import models

class ImageListHandler(ListCreateAPIHandler):
    model = models.ImageModel()

    def post(self):
        result = utils.init_response_data()
        try:
            request_files = self.request.files
            if request_files.has_key("files"):
                files = request_files["files"]
                data = self.model.upload_image(files,file_type=0)
            else:
                raise ValueError(u"没有上传文件")
            for d in data:
                self.model.create(**d)

        except Exception,e:
            result = utils.reset_response_data(0, unicode(e))
        result["data"] = data
        self.finish(result)

class ImageHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.ImageModel()

    def put(self):
        result = utils.init_response_data()
        try:
            banner_id = self.get_argument("banner_id", "")
            use_type = self.get_argument("use_type", "banner")
            banner = self.model.get_coll().find_one({"_id": utils.create_objectid(banner_id), "enable_flag": 1})
            if banner is None:
                raise ValueError(u'该图片不存在或已被删除')

            files = self.request.files
            if files.has_key("files"):
                files = files["files"]
                data = self.model.upload_image(files, use_type)
            else:
                raise ValueError(u"没有上传文件")
            for d in data:
                banner["file_name"] = d["file_name"]
                banner["use_type"] = d["use_type"]
                banner["add_time"] = d["add_time"]
                banner["file_type"] = d["file_type"]
                banner["logs"].append({
                    "user_id": "",
                    "action_date": utils.get_current_time(),
                    "action": "修改文件",
                    "note": "file_path|from|%s|to|%s" % (banner['file_path'], d['file_path'])
                })
                banner["file_path"] = d["file_path"]
                self.model.get_coll().save(banner)
        except StandardError, e:
            result = utils.reset_response_data(0, unicode(e))
        self.finish(result)

    def delete(self):
        result = utils.init_response_data()
        banner_model_obj = self.model.BannerModel()
        try:
            banner_id = self.get_argument("banner_id", "")
            banner_model_obj.delete(banner_id)

            result["data"] = "success"
        except StandardError, e:
            result = utils.reset_response_data(0, unicode(e))
        self.finish(result)

handlers = [
    (r"/api/image/list",ImageListHandler),
    (r"/api/image",ImageHandler),
]