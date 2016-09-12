#coding=utf-8
from tornado.options import options
import libs.modellib as model
import libs.utils as utils
import pdb
import hashlib
import mimetypes
import os
from cStringIO import StringIO
import time
from PIL import Image

pool = None
allow_formats = set(['jpeg', 'png', 'gif'])

def write_image(uri,image_file):
    f = open(uri, 'wb')
    im = Image.open(StringIO(image_file['body']))
    im_file = StringIO()
    im.save(im_file, format='png')
    im_data = im_file.getvalue()
    f.write(im_data)
    f.close()


class ImageModel(model.BaseModel):
    __name = "dxb.image"

    def __init__(self):
        model.BaseModel.__init__(self,ImageModel.__name)

    def check_image(self,files):

        for res in files:
            content = StringIO(res['body'])

            mime = Image.open(content).format.lower()
            if mime not in allow_formats:
                raise Exception("图片格式不正确！")

            if 'content_type' not in res or res['content_type'].find('/') < 1 or len(res['content_type']) > 128:
                raise Exception('文件类型错误')

            if 'filename' not in res or res['filename'] == '':
                raise Exception('文件名错误')

            if len(res['body']) > 4*1024*1024:
                raise Exception('上传图片不能大于4M')

    def upload_image(self,files,file_type):

        self.check_image(files)
        global pool
        pool = utils.get_concurrent_pool()
        images_list = []
        for image_file in files:
            ets = mimetypes.guess_all_extensions(image_file['content_type'])
            ext = os.path.splitext(image_file['filename'])[1].lower()
            if ets and ext not in ets:
                ext = ets[0]

            md5 = hashlib.md5()
            md5.update(image_file['body'])
            key = md5.hexdigest()
            url = '/static/image/'
            name = time.strftime('%Y/%m/%d/')+ str(time.time()).replace('.','') + os.path.splitext(image_file['filename'])[0] + ext
            uri = options.root_path + url + name
            file_path = url + name
            if not os.path.exists(os.path.dirname(uri)):
                os.makedirs(os.path.dirname(uri), mode=0777)
            pool.submit(write_image,uri,image_file)

            if image_file.has_key("upload_key"):
                upload_key = image_file["upload_key"]
            else:
                upload_key = "upload"

            image = {
                "file_path":file_path,
                "file_type":image_file['content_type'],
                "use_type":file_type,
                "file_name":image_file['filename'],
                "upload_key":upload_key,
                "add_time":time.time(),
            }
            # image_coll.insert_one(image)
            images_list.append(image)
        return utils.dump(images_list)
