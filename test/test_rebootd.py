#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from rebootd import RebootDaemon

import unittest

class RebootDaemonTest(unittest.TestCase):
    """
    This Suite will test the rebootd main class
    """

    def setUp(self):
        """ Initializes the test environment """
        self.reboot_daemon=RebootDaemon('config.json')

    def tearDown(self):
        """ Cleans up the test environment """
        pass

    def testMain(self):
        """ Testing the SafeTransport class """

        self.assertTrue(self.reboot_daemon._get_uptime() > 0)
        self.assertTrue(isinstance(self.reboot_daemon.time_to_reboot, bool))


if __name__ == "__main__":
    unittest.main()
