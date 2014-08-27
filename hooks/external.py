#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess

class ExternalCommandHook(object):
    """
    This rebootd hook triggers an external command whenever the system
    needs to be rebooted.
    """

    hook_name = 'external'

    def __init__(self, command):
        self.command = command.split(' ')

    def trigger(self, host):
        ret = subprocess.call(self.command)
        return ret
