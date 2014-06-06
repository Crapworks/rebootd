#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import json
import redis
import socket
import datetime

class RebootDaemon(object):
    def __init__(self, config_file):
        self.config = json.load(open(config_file))
        self.fqdn = socket.getfqdn()
        self.redis = redis.StrictRedis(host=self.config['redis'], port=6379, db=0)

    def _get_uptime(self):
        with open('/proc/uptime', 'r') as fh:
            uptime_seconds = float(fh.readline().split()[0])
        return int(uptime_seconds)

    @property
    def _time_to_reboot(self):
        uptime = datetime.timedelta(seconds=self._get_uptime())
        return uptime > datetime.timedelta(weeks=int(self.config['weeks']))

    @property
    def reboot(self):
        key = 'rebootd::%s' % (self.config['group'], )
        if self._time_to_reboot:
            self.redis.setnx(key, self.fqdn)
            return self.redis.get(key) == self.fqdn
        else:
            if self.redis.get(key) == self.fqdn:
                self.redis.delete(key)
            return False


def main():
    rebootd = RebootDaemon('config.json')
    if rebootd.reboot:
        # possible pre-reboot hooks
        os.system('reboot')

if __name__ == '__main__':
    main()
