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


class TestBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def reload_solver(self):
        maya.cmds.unloadPlugin('mmSolver')
        maya.cmds.loadPlugin('mmSolver')

    def quit_maya(self):
        if maya.cmds.about(batch=True):
            maya.cmds.quit(force=True)

    def approx_equal(self, x, y, eps=0.0001):
        return x == y or (x < (y + eps) and x > (y - eps))
