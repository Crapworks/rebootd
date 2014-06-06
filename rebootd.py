#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import redis
import socket
import argparse
import datetime


import logging.config
try:
    logging_config_file = os.path.join(os.path.dirname(__file__), 'logging.ini')
    logging.config.fileConfig(open(logging_config_file), disable_existing_loggers=False)
except Exception as err:
    print '[-] error loading logging configuration from %s: %s' % (logging_config_file, str(err))
    sys.exit(-1)
else:
    logger = logging.getLogger('rebootd')


__version__ = '0.2'


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
        logger.debug('system uptime: %s' % (uptime, ))
        return uptime > datetime.timedelta(weeks=int(self.config['weeks']))

    @property
    def reboot(self):
        key = 'rebootd::%s' % (self.config['group'], )
        logger.debug('using redis key %s in redis server %s' % (key, self.config['redis']))
        if self._time_to_reboot:
            self.redis.setnx(key, self.fqdn)
            return self.redis.get(key) == self.fqdn
        else:
            if self.redis.get(key) == self.fqdn:
                self.redis.delete(key)
            return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-c", "--config", help="path to the configuration file", default="config.json")
    args = parser.parse_args()

    try:
        rebootd = RebootDaemon(args.config)
        if rebootd.reboot:
            # possible pre-reboot hooks here
            logger.info('maximum uptime reached! rebooting')
            os.system('reboot')
        else:
            logger.info('system should not be rebooted yet')
    except redis.exceptions.ConnectionError as err:
        logger.error("redis conenction error: %s" % (str(err), ))
    except ValueError as err:
        logger.error("error parsing configuration: %s" % (str(err), ))


if __name__ == '__main__':
    main()
