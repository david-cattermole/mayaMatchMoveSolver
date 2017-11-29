"""
Test functions for sethelper module.
"""

import sys
import os
import unittest

import maya.cmds


class TestSetHelper(unittest.TestCase):
    def test_create(self):
        import mmSolver.api.sethelper as sethelper
        x = sethelper.SetHelper()
        node = x.createNode('newSet')
        self.assertTrue(maya.cmds.objExists(node))


if __name__ == '__main__':
    prog = unittest.main()
