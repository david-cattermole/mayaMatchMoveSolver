"""
Testing Utilities - base class for the test cases.
"""

import os
import math
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import test.baseutils as baseUtils


class UtilsTestCase(baseUtils.TestBase):

    def setUp(self):
        maya.cmds.file(new=True, force=True)
        self.reload_solver()
        super(UtilsTestCase, self).setUp()

    def tearDown(self):
        super(UtilsTestCase, self).tearDown()

