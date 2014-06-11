#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from urllib import urlencode
from time import strftime
from time import localtime
from time import time

import urllib2


class ThrukDowntimeHook(object):
    """
    This rebootd hook uses thruks cmd.cgi to trigger a downtime
    for the current host for 30 minutes.
    """

    hook_name = 'thruk'

    def __init__(self, url, username, password):
        self.url = url
        self.pw_mngr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.pw_mngr.add_password(None, self.url, username, password)
        self.opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(self.pw_mngr))

    def remove(self, host):
        command = {
            'cmd_typ': 'c5',
            'cmd_mod': 2,
            'active_downtimes': 1,
            'future_downtimes': 2,
            'host': host,
            'btnSubmit': 'Commit'
        }
        data = urlencode(command)
        resp = self.opener.open(self.url, data)
        resp.read()

    def trigger(self, host):
        start_time = localtime(time())
        end_time = localtime(time()+1800)
        command = {
            'cmd_typ': 86,
            'cmd_mod': 2,
            'host': host,
            'com_data': 'rebootd scheduled reboot',
            'trigger': 0,
            'fixed': 1,
            'start_time': strftime('%Y-%m-%d %H:%M:%S', start_time),
            'end_time': strftime('%Y-%m-%d %H:%M:%S', end_time),
            'btnSubmit': 'Commit'
        }
        data = urlencode(command)
        resp = self.opener.open(self.url, data)
        resp.read()
