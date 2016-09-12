# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-08-02
"""
import jpush as jpush
from jpush import common

_jpush = jpush.JPush("5d4173b694e8efa78d84fb41", "32801a523b363dae0ad2e378")

push = _jpush.create_push()
# if you set the logging level to "DEBUG",it will show the debug logging.
_jpush.set_logging("DEBUG")
push.audience = jpush.audience(
            jpush.alias("test")
)
push.notification = jpush.notification(alert="TEST ALERT ！！！！！")
push.platform = jpush.all_
try:
    response=push.send()
except common.Unauthorized:
    raise common.Unauthorized("Unauthorized")
except common.APIConnectionException:
    raise common.APIConnectionException("conn error")
except common.JPushFailure:
    print ("JPushFailure")
except:
    print ("Exception")