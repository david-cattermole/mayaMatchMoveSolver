"""
Test functions for 'frame' module.
"""

import sys
import os
import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver._api.frame as frame


# @unittest.skip
class TestFrame(test_api_utils.APITestCase):
    def test_init(self):
        f1 = frame.Frame(10)
        self.assertIs(f1.get_number(), 10)

        f2 = frame.Frame(10.0)
        self.assertIs(f2.get_number(), 10.0)

        self.assertRaises(AssertionError, frame.Frame, 'string')
        self.assertRaises(AssertionError, frame.Frame, None)

        f3 = frame.Frame(10.0)
        self.assertEqual(f3.get_primary(), False)
        self.assertEqual(f3.get_secondary(), False)

        f4 = frame.Frame(10.0, primary=True)
        self.assertEqual(f4.get_primary(), True)
        self.assertEqual(f4.get_secondary(), False)

        f5 = frame.Frame(10.0, secondary=True)
        self.assertEqual(f5.get_primary(), False)
        self.assertEqual(f5.get_secondary(), True)

    def test_get_number(self):
        f1 = frame.Frame(10)
        self.assertIs(f1.get_number(), 10)

        f2 = frame.Frame(10.0)
        self.assertIs(f2.get_number(), 10.0)

    def test_get_primary(self):
        f = frame.Frame(10, primary=False)
        self.assertIs(f.get_primary(), False)

        f = frame.Frame(10, primary=True)
        self.assertIs(f.get_primary(), True)

    def test_set_primary(self):
        f = frame.Frame(10)
        f.set_primary(True)
        self.assertIs(f.get_primary(), True)

        f.set_primary(False)
        self.assertIs(f.get_primary(), False)

    def test_get_secondary(self):
        f = frame.Frame(10, secondary=False)
        self.assertIs(f.get_secondary(), False)

        f = frame.Frame(10, secondary=True)
        self.assertIs(f.get_secondary(), True)

    def test_set_secondary(self):
        f = frame.Frame(10)
        f.set_secondary(True)
        self.assertIs(f.get_secondary(), True)

        f.set_secondary(False)
        self.assertIs(f.get_secondary(), False)


if __name__ == '__main__':
    prog = unittest.main()
