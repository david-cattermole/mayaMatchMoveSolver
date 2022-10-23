"""
Test functions for Configuration Maya module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import unittest

import maya.cmds
import test.test_utils.utilsutils as test_utils
import mmSolver.utils.configmaya as configmaya


# @unittest.skip
class TestConfigMaya(test_utils.UtilsTestCase):
    """
    Test config module.
    """

    def test_get_node_option(self):
        node = 'my_option_node'
        node = maya.cmds.createNode('script', name=node)

        name = 'my_int_attr'
        value = configmaya.get_node_option(node, name)
        self.assertIsNone(value)

        value = 42
        regex = 'setAttr: No object matches name: .+'
        with self.assertRaisesRegexp(RuntimeError, regex):
            configmaya.set_node_option(node, name, value)
        configmaya.set_node_option(node, name, value, add_attr=True)
        new_value = configmaya.get_node_option(node, name)
        self.assertEqual(new_value, value)

        name = 'my_float_attr'
        value = 3.0
        configmaya.set_node_option(node, name, value, add_attr=True)
        new_value = configmaya.get_node_option(node, name)
        self.assertEqual(new_value, value)

        name = 'my_bool_attr'
        value = True
        configmaya.set_node_option(node, name, value, add_attr=True)
        new_value = configmaya.get_node_option(node, name)
        self.assertEqual(new_value, value)

        name = 'my_string_attr'
        value = 'hello world'
        configmaya.set_node_option(node, name, value, add_attr=True)
        new_value = configmaya.get_node_option(node, name)
        self.assertEqual(new_value, value)
        return

    # def test_set_node_option(self):
    #     return


if __name__ == '__main__':
    prog = unittest.main()
