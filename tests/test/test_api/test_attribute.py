"""
Test functions for attribute module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.attribute as attribute
import mmSolver._api.marker as marker
import mmSolver._api.constant as const


# @unittest.skip
class TestAttribute(test_api_utils.APITestCase):
    def test_init(self):
        # TODO: More exhaustive test.
        node = maya.cmds.createNode('transform')
        node = api_utils.get_long_name(node)
        x = attribute.Attribute(node=node, attr='translateX')
        y = attribute.Attribute(node=node, attr='ty')
        self.assertEqual(x.get_node(), node)
        self.assertEqual(x.get_attr(), 'translateX')
        self.assertEqual(x.get_name(), '|transform1.translateX')

        self.assertEqual(y.get_attr(), 'translateY')
        self.assertEqual(y.get_name(), '|transform1.translateY')

    def test_get_state(self):
        node = maya.cmds.createNode('transform')
        node = api_utils.get_long_name(node)

        # Animated
        maya.cmds.setKeyframe(node, attribute='rotateY', time=1, value=-1.0)
        maya.cmds.setKeyframe(node, attribute='rotateY', time=10, value=1.0)

        # Locked
        maya.cmds.setAttr(node + '.rotateZ', lock=True)

        # Connected
        multdiv = maya.cmds.createNode('multiplyDivide')
        maya.cmds.connectAttr(multdiv + '.outputX', node + '.translateX')

        # Create the Attribute objects
        tx = attribute.Attribute(node=node, attr='translateX')
        rx = attribute.Attribute(node=node, attr='rotateX')
        ry = attribute.Attribute(node=node, attr='rotateY')
        rz = attribute.Attribute(node=node, attr='rotateZ')

        tx_state = tx.get_state()
        rx_state = rx.get_state()
        ry_state = ry.get_state()
        rz_state = rz.get_state()

        # test returned states.
        self.assertEqual(tx_state, const.ATTR_STATE_LOCKED)
        self.assertEqual(rx_state, const.ATTR_STATE_STATIC)
        self.assertEqual(ry_state, const.ATTR_STATE_ANIMATED)
        self.assertEqual(rz_state, const.ATTR_STATE_LOCKED)

        # test 'is_*' functions.
        self.assertEqual(tx.is_locked(), True)
        self.assertEqual(rx.is_static(), True)
        self.assertEqual(ry.is_animated(), True)
        self.assertEqual(rz.is_locked(), True)


if __name__ == '__main__':
    prog = unittest.main()
