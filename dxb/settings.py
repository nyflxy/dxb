# -*- coding: utf-8 -*-
#
# @author: Daemon wang
# Created on 2016-03-02
#

import platform, pdb
import os
import time
import dxb
root_dir = os.path.dirname(os.path.abspath(dxb.__file__))
root_path = root_dir
project_root_path = os.path.dirname(root_path)
debug = False
login_url = "https://lcoalhost/login"
dev_hosts = ['dell-PC','qihua04','SC-201604151426','peixun02','dhui100']
if platform.node() in dev_hosts:
    debug = True
webservice_root = "139.159.35.187:8080"
webservice_user = "ARY9MOZI"
webservice_key = "dmFplsLQXYDckqoc"

###-----------配置区开始--------------
##网站域名
domain = "dev.donghuicredit.cn"
##启动的端口号
port = 8500
##正式服务器的webservice配置
if not debug:
    webservice_root = "139.159.35.187:8080"
    webservice_user = "ARY9MOZI"
    webservice_key = "dmFplsLQXYDckqoc"
##mongodb配置
mongo = {
            "host":"localhost",
            "port":27017,
            "database":"dxb",
            "user":"dxb",
            "password":"dxbAdmin",
        }
##是否启用mongodb用户认证
mongo_auth = False
##redis配置
redis = {
    "host":"localhost",
    "port":6379,
    "db":0
}
##smtp配置
smtp = {"host": "",
        "user": "",
        "password": "",
        "duration": 30,
        "tls": True
        }

##分页相关设置
#一页显示的条数
page_size = 15
#最多显示的页数
page_show = 10

###----------配置区结束-----------------

home_url = "http://%s/api" % domain
root_log_path = os.path.join(root_path,'var','log')
loglevel = "INFO"  # for celeryd
app_url_prefix = ""
sitename = "dxb api"

cookie_secret = "ace87395-8272-4749-b2f2-dcabd3901a1c"
xsrf_cookies = False

#加密的Key值
SIGN_KEY = '87B2447B04E5AA93F00C21A5B98F32A0'

deadline_time = 60

file_download_store_url = project_root_path +"/var/report/"

installed_apps = ["authuserapp","fileapp","reportapp"]
