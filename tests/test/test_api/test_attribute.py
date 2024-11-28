# Copyright (C) 2018, 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Test functions for attribute module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.attribute as attribute
import mmSolver._api.constant as const


# @unittest.skip
class TestAttribute(test_api_utils.APITestCase):
    def test_init(self):
        # TODO: More exhaustive test.
        node = maya.cmds.createNode('transform')
        node = node_utils.get_long_name(node)
        x = attribute.Attribute(node=node, attr='translateX')
        y = attribute.Attribute(node=node, attr='ty')
        self.assertEqual(x.get_node(), node)
        self.assertEqual(x.get_attr(), 'translateX')
        self.assertEqual(x.get_name(), '|transform1.translateX')

        self.assertEqual(y.get_attr(), 'translateY')
        self.assertEqual(y.get_name(), '|transform1.translateY')

    def test_init_with_attr_alias(self):
        node = maya.cmds.createNode('transform')
        node = node_utils.get_long_name(node)
        maya.cmds.aliasAttr('tilt', node + '.rotateX')
        maya.cmds.aliasAttr('pan', node + '.rotateY')
        maya.cmds.aliasAttr('roll', node + '.rotateZ')

        tx = attribute.Attribute(node=node, attr='translateX')
        tilt = attribute.Attribute(node=node, attr='rotateX')
        pan = attribute.Attribute(node=node, attr='pan')
        roll = attribute.Attribute(node=node, attr='roll')

        self.assertEqual(tx.get_node(), node)
        self.assertEqual(tilt.get_node(), node)
        self.assertEqual(pan.get_node(), node)
        self.assertEqual(roll.get_node(), node)

        self.assertEqual(tx.get_attr(), 'translateX')
        self.assertEqual(tilt.get_attr(), 'rotateX')
        self.assertEqual(pan.get_attr(), 'rotateY')
        self.assertEqual(roll.get_attr(), 'rotateZ')

        self.assertEqual(tx.get_attr_alias_name(), None)
        self.assertEqual(tilt.get_attr_alias_name(), 'tilt')
        self.assertEqual(pan.get_attr_alias_name(), 'pan')
        self.assertEqual(roll.get_attr_alias_name(), 'roll')

        self.assertEqual(tx.get_name(), '|transform1.translateX')
        self.assertEqual(tilt.get_name(), '|transform1.rotateX')
        self.assertEqual(pan.get_name(), '|transform1.rotateY')
        self.assertEqual(roll.get_name(), '|transform1.rotateZ')

    def test_get_state(self):
        node = maya.cmds.createNode('transform')
        node = node_utils.get_long_name(node)

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

    def test_non_unique_node_name(self):
        """
        Test for identical child node names causing Attribute class to
        incorrectly return the wrong node name.

          -> top_node
             `-> left
                 `-> same
             `-< right
                 `-> same

        See GitHub issue #153.
        """
        top_node = maya.cmds.createNode('transform', name='top_node')
        top_node = node_utils.get_long_name(top_node)

        left_node = maya.cmds.createNode('transform', name='left', parent=top_node)
        left_node = node_utils.get_long_name(left_node)

        right_node = maya.cmds.createNode('transform', name='right', parent=top_node)
        right_node = node_utils.get_long_name(right_node)

        # Same name as right_same_node
        left_same_node = maya.cmds.createNode(
            'transform', name='same', parent=left_node
        )
        left_same_node = node_utils.get_long_name(left_same_node)

        # Same name as left_same_node
        right_same_node = maya.cmds.createNode(
            'transform', name='same', parent=right_node
        )
        right_same_node = node_utils.get_long_name(right_same_node)

        left_attr = attribute.Attribute(node=left_same_node, attr='translateX')
        right_attr = attribute.Attribute(node=right_same_node, attr='translateX')

        self.assertEqual(left_attr.get_node(), '|top_node|left|same')
        self.assertEqual(left_attr.get_name(), '|top_node|left|same.translateX')

        self.assertEqual(right_attr.get_node(), '|top_node|right|same')
        self.assertEqual(right_attr.get_name(), '|top_node|right|same.translateX')
        return


if __name__ == '__main__':
    prog = unittest.main()
