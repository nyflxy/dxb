# coding=utf-8

"""
    author : youfaNi
    date : 2016-07-13
"""

import pymongo, pdb
import sys, os, re
from tornado.options import options as settings

try:
    import importlib
except:
    from dxb.libs import importlib

client = None


class DB_CONST:
    DB_NAME = "db_name"
    COLL_NAME = "coll_name"
    COLL_HOST = "host"
    COLL_PORT = "port"
    USERNAME = "username"
    PASSWORD = "password"
    COLL_TYPE = "coll_type"


class Collections:
    # MongoDB文档配置
    # TODO 自动生成 基于 model目录下文件
    __COLLECTIONS = dict(

        user=dict(
            coll_name="user",
            db_name=settings.mongo["database"],
            username=settings.mongo["user"],
            password=settings.mongo["password"],
            host=settings.mongo["host"],
            port=settings.mongo["port"],
        ),
        oauth_clients=dict(
            coll_name="oauth_clients",
            db_name=settings.mongo["database"],
            username=settings.mongo["user"],
            password=settings.mongo["password"],
            host=settings.mongo["host"],
            port=settings.mongo["port"],
        ),
        search=dict(
            coll_name="search",
            db_name=settings.mongo["database"],
            username=settings.mongo["user"],
            password=settings.mongo["password"],
            host=settings.mongo["host"],
            port=settings.mongo["port"],
        ),
        banner=dict(
            coll_name="banner",
            db_name=settings.mongo["database"],
            username=settings.mongo["user"],
            password=settings.mongo["password"],
            host=settings.mongo["host"],
            port=settings.mongo["port"],
        ),
        code=dict(
            coll_name="code",
            db_name=settings.mongo["database"],
            username=settings.mongo["user"],
            password=settings.mongo["password"],
            host=settings.mongo["host"],
            port=settings.mongo["port"],
        ),
    )

    @classmethod
    def get_db_name(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            db_name = cls.__COLLECTIONS[table_name][DB_CONST.DB_NAME]
        else:
            db_name = settings.mongo["database"]
        return db_name

    @classmethod
    def get_coll_name(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            coll_name = cls.__COLLECTIONS[table_name][DB_CONST.COLL_NAME]
        else:
            coll_name = table_name
        return coll_name

    @classmethod
    def get_coll_host(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            coll_host = cls.__COLLECTIONS[table_name][DB_CONST.COLL_HOST]
        else:
            coll_host = settings.mongo["host"]
        return coll_host

    @classmethod
    def get_coll_port(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            coll_port = cls.__COLLECTIONS[table_name][DB_CONST.COLL_PORT]
        else:
            coll_port = settings.mongo["port"]
        return coll_port

    @classmethod
    def get_coll_username(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            username = cls.__COLLECTIONS[table_name][DB_CONST.USERNAME]
        else:
            username = settings.mongo["user"]
        return username

    @classmethod
    def get_coll_password(cls, table_name):
        if table_name in cls.__COLLECTIONS:
            password = cls.__COLLECTIONS[table_name][DB_CONST.PASSWORD]
        else:
            password = settings.mongo["password"]
        return password


def get_client(table_name):
    global client
    if client:
        return client
    else:
        host = Collections.get_coll_host(table_name)
        port = Collections.get_coll_port(table_name)
        client = pymongo.MongoClient(host, port)
        return client


def get_address(table_name):
    global client
    if client:
        address = client.address
    else:
        client = get_client(table_name)
        address = client.address
    return address


def get_db_names(table_name):
    global client
    if client:
        db_names = client.database_names()
    else:
        client = get_client(table_name)
        db_names = client.database_names()
    return db_names


def get_database(table_name, **kwargs):
    global client
    if not client:
        client = get_client(table_name)
    db_name = Collections.get_db_name(table_name)
    db = client.get_database(db_name)
    return db


def drop_db(table_name, client=None):
    if client == None:
        client = get_client(table_name)
    db_name = Collections.get_db_name(table_name)
    client.drop_database(db_name)
    print (db_name + " dropped!")


def get_coll_names(table_name):
    db = get_database(table_name)
    coll_names = db.collection_names(include_system_collections=False)
    return coll_names


# 获取mongodb collection Note: 此处需要做性能分析
def get_coll(table_name):
    db_name = Collections.get_db_name(table_name)
    coll_name = Collections.get_coll_name(table_name)
    username = Collections.get_coll_username(table_name)
    password = Collections.get_coll_password(table_name)
    client = get_client(table_name)
    if db_name and coll_name:
        db = client[db_name]
        if settings.mongo_auth:
            db.authenticate(username, password)
            coll = db[coll_name]
        else:
            coll = db[coll_name]
    else:
        raise Exception(u"集合'%s'不存在,请在mongo.py文件中正确配置！" % table_name)
    return coll


def get_coll_db_name(table_name):
    db_name = Collections.get_db_name(table_name)
    return db_name


def drop_coll(table_name):
    db_name = Collections.get_db_name(table_name)
    if db_name == "":
        print (u"集合不存在!")
    else:
        try:
            db = get_database(db_name)
        except Exception  as e:
            print (u"查询数据库失败" + unicode(e))
            return
        db.drop_collection(table_name)
        print (table_name + " dropped!")
