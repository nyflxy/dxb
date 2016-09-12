# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

import sys,os,pdb
import shutil

root_dir = os.getcwd()
app_root_dir = os.path.dirname(root_dir.split("/management")[0])
app_root_dir = root_dir

command_args = sys.argv

def startapp(argvs):
    try:
        app_name = argvs[1]
    except Exception,e:
        raise Exception("The app name cannot be empty !")

    if not app_name.endswith("app"):
        raise Exception("The app name error : must endwith 'app'! ")

    generate_app(app_name)

def generate_app(app_name):
    app_dir = app_root_dir + "/" + app_name
    if os.path.exists(app_dir):
        raise Exception("%s has exist !"%app_dir)

    app_template_dir = app_root_dir + "/dxb/" + "apptemplate"
    shutil.copytree(app_template_dir, app_dir)

    print "create new app %s"%app_name

if __name__ == "__main__" :
    startapp(command_args)