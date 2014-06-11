#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import redis
import socket
import argparse
import datetime

from inspect import getmembers
from inspect import isclass
from importlib import import_module

import logging.config
try:
    logging_config_file = os.path.join(os.path.dirname(__file__), 'logging.ini')
    logging.config.fileConfig(open(logging_config_file), disable_existing_loggers=False)
except Exception as err:
    print '[-] error loading logging configuration from %s: %s' % (logging_config_file, str(err))
    sys.exit(-1)
else:
    logger = logging.getLogger('rebootd')


__version__ = '0.5.1'


class Config(dict):
    """ loads the json configuration file """

    config_values = ['cluster', 'reboot_after', 'redis']

    def __init__(self, config_file):
        dict.__init__(self)
        configfile = os.path.join(os.path.dirname(__file__), config_file)
        self.update(json.load(open(configfile), object_hook=self._string_decode_hook))
        self._validate()

    def _load_hooks(self, config):
        self['loaded_hooks'] = []
        for module_name, options in config.iteritems():
            try:
                module = import_module('hooks.%s' % (module_name, ))
            except ImportError as err:
                logger.error('unable to load module %s: %s' % (module_name, err))
            else:
                for obj_name, obj in getmembers(module):
                    if isclass(obj) and getattr(obj, 'hook_name', None) == module_name:
                        self['loaded_hooks'].append(obj(**options))

    def _validate(self):
        for cv in self.config_values:
            if cv not in self.keys():
                raise ValueError('Missing config key: %s' % (cv, ))

        if 'hooks' in self.keys():
            self._load_hooks(self['hooks'])

    def _string_decode_hook(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            rv[key] = value
        return rv


class RebootDaemon(object):
    def __init__(self, config_file):
        self.config = Config(config_file)
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
        return uptime > datetime.timedelta(**self.config['reboot_after'])

    @property
    def reboot(self):
        key = 'rebootd::%s' % (self.config['cluster'], )
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
            # run configured hooks
            for hook in rebootd.config['loaded_hooks']:
                logger.info('running hook %s...' % (hook.hook_name, ))
                hook.trigger(rebootd.fqdn)
            logger.info('maximum uptime reached! rebooting')
            os.system('/sbin/reboot')
        else:
            logger.info('system should not be rebooted yet')
    except redis.exceptions.ConnectionError as err:
        logger.error("redis conenction error: %s" % (str(err), ))
    except ValueError as err:
        logger.error("error parsing configuration: %s" % (str(err), ))


if __name__ == '__main__':
    main()
