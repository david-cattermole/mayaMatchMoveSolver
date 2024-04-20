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
Test functions for sethelper module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.sethelper as sethelper


# @unittest.skip
class TestSetHelper(test_api_utils.APITestCase):
    def test_init(self):
        x = sethelper.SetHelper()
        self.assertEqual(x.get_node(), None)
        self.assertEqual(x.get_annotation(), None)
        self.assertEqual(x.get_all_members(), [])

        node = maya.cmds.sets(name='mySet')
        x = sethelper.SetHelper(node=node)
        self.assertEqual(x.get_node(), node)
        # NOTE: 'Unnamed object set' is the default set node annotation.
        self.assertEqual(x.get_annotation(), 'Unnamed object set')
        self.assertEqual(x.get_all_members(), [])
        self.assertTrue(maya.cmds.objExists(x.get_node()))

        self.assertRaises(TypeError, sethelper.SetHelper, [])

    def test_get_node(self):
        name = 'mySet'
        node = maya.cmds.sets(name=name)
        x = sethelper.SetHelper(node=node)
        self.assertEqual(x.get_node(), name)

    def test_set_node(self):
        name1 = 'mySet'
        name2 = 'myNextSet'
        node1 = maya.cmds.sets(name=name1)
        node2 = maya.cmds.sets(name=name2)
        x = sethelper.SetHelper(node=node1)
        self.assertEqual(x.get_node(), name1)
        x.set_node(node2)
        self.assertEqual(x.get_node(), name2)

    def test_create_node(self):
        state1 = maya.cmds.ls(long=True)

        x = sethelper.SetHelper()
        x.create_node('newSet')
        node = x.get_node()
        self.assertTrue(maya.cmds.objExists(node))

        # test undo/redo.
        state2 = maya.cmds.ls(long=True)
        self.assertNotEqual(state1, state2)

        maya.cmds.undo()
        state3 = maya.cmds.ls(long=True)
        self.assertEqual(state1, state3)

        maya.cmds.redo()
        state4 = maya.cmds.ls(long=True)
        self.assertEqual(state2, state4)

    def test_delete_node(self):
        state1 = maya.cmds.ls(long=True)

        node = maya.cmds.sets(name='mySet')
        x = sethelper.SetHelper()
        x.set_node(node)
        x.delete_node()
        self.assertFalse(maya.cmds.objExists(node))

        # test undo/redo.
        state2 = maya.cmds.ls(long=True)
        self.assertEqual(state1, state2)

        maya.cmds.undo()  # undo delete_node
        maya.cmds.undo()  # undo sets
        state3 = maya.cmds.ls(long=True)
        self.assertEqual(state1, state3)

        maya.cmds.redo()  # redo sets
        state4 = maya.cmds.ls(long=True)
        self.assertNotEqual(state1, state4)

        maya.cmds.redo()  # redo delete
        state5 = maya.cmds.ls(long=True)
        self.assertEqual(state3, state5)

    def test_get_annotation(self):
        x = sethelper.SetHelper().create_node('mySet')
        anno = x.get_annotation()
        default_anno = 'Unnamed object set'
        self.assertEqual(anno, default_anno)
        line = 'This is the best set in the world!'
        x.set_annotation(line)
        anno = x.get_annotation()
        self.assertEqual(anno, line)

    def test_set_annotation(self):
        x = sethelper.SetHelper().create_node('mySet')
        anno = x.get_annotation()
        default_anno = 'Unnamed object set'
        self.assertEqual(anno, default_anno)
        line = 'This is the best set in the world!'
        x.set_annotation(line)
        anno = x.get_annotation()
        self.assertEqual(anno, line)

        maya.cmds.undo()  # undo set annotation
        anno = x.get_annotation()
        self.assertEqual(anno, default_anno)

        maya.cmds.redo()  # redo set annotation
        anno = x.get_annotation()
        self.assertEqual(anno, line)

    def test_get_all_members(self):
        x = sethelper.SetHelper().create_node('mySet')
        x.get_all_members()

        node1 = maya.cmds.createNode('transform', name='myParent')
        node1 = node_utils.get_long_name(node1)

        node2 = maya.cmds.createNode('transform', name='myChild', parent=node1)
        node2 = node_utils.get_long_name(node2)

        node3 = maya.cmds.createNode('transform', name='myChild')
        node3 = node_utils.get_long_name(node3)

        node4 = maya.cmds.createNode('multiplyDivide', name='myMathsNode')
        node4 = node_utils.get_long_name(node4)

        node_attr1 = node1 + '.tx'  # short attribute name
        node_attr2 = node2 + '.rotateY'
        node_attr3 = node3 + '.rotateX'
        node_attr4 = node4 + '.operation'

        x.add_member(node1)
        x.add_member(node2)
        x.add_member(node3)
        x.add_member(node4)
        x.add_member(node_attr1)
        x.add_member(node_attr2)
        x.add_member(node_attr3)
        x.add_member(node_attr4)

        # Get the full path node names
        members = x.get_all_members(full_path=True)
        self.assertEqual(len(members), 8)
        self.assertIn(node1, members)
        self.assertIn(node2, members)
        self.assertIn(node3, members)
        self.assertIn(node4, members)
        node_attr1 = node1 + '.translateX'  # full attribute name
        self.assertIn(node_attr1, members)
        self.assertIn(node_attr2, members)
        self.assertIn(node_attr3, members)
        self.assertIn(node_attr4, members)

        # Make sure short-names are handled too
        node1 = 'myParent'
        node2 = 'myParent|myChild'
        node3 = '|myChild'
        node4 = 'myMathsNode'
        node_attr1 = node1 + '.translateX'
        node_attr2 = node2 + '.rotateY'
        node_attr3 = node3 + '.rotateX'
        node_attr4 = node4 + '.operation'
        members = x.get_all_members(full_path=False)
        self.assertEqual(len(members), 8)
        self.assertIn(node1, members)
        self.assertIn(node2, members)
        self.assertIn(node3, members)
        self.assertIn(node4, members)
        self.assertIn(node_attr1, members)
        self.assertIn(node_attr2, members)
        self.assertIn(node_attr3, members)
        self.assertIn(node_attr4, members)
        x.clear_all_members()

        # Test 'flatten' argument, with nested sets.
        y = sethelper.SetHelper().create_node('myNestedSet')
        y.add_member(node2)
        y.add_member(node3)
        y.add_member(node_attr4)
        x.add_member(node1)
        x.add_member(y.get_node())

        # Query the results.
        x_members_flat = x.get_all_members(flatten=True)
        y_members_flat = y.get_all_members(flatten=True)
        x_members = x.get_all_members(flatten=False)
        y_members = y.get_all_members(flatten=False)
        self.assertEqual(len(x_members_flat), 4)
        self.assertEqual(len(x_members), 2)
        self.assertEqual(len(y_members_flat), 3)
        self.assertEqual(len(y_members), 3)
        self.assertEqual(y_members, y_members_flat)

    def test_clear_all_members(self):
        x = sethelper.SetHelper().create_node('mySet')

        members = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            node_attr = node + '.translateX'
            members.append(node)
            members.append(node_attr)
        x.add_members(members)

        n1 = len(x.get_all_members())
        self.assertEqual(n1, 20)
        x.clear_all_members()
        n2 = len(x.get_all_members())
        self.assertEqual(n2, 0)

        # undo / redo tests
        maya.cmds.undo()
        n3 = len(x.get_all_members())
        self.assertEqual(n3, 20)

        maya.cmds.redo()
        n4 = len(x.get_all_members())
        self.assertEqual(n4, 0)

    def test_add_members(self):
        x = sethelper.SetHelper().create_node('mySet')

        members = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr1 = node + '.translateX'
            attr2 = node + '.rotateY'
            attr3 = node + '.visibility'
            members.append(node)
            members.append(attr1)
            members.append(attr2)
            members.append(attr3)
        x.add_members(members)

        # undo / redo tests
        n1 = len(x.get_all_members())
        self.assertEqual(n1, 40)

        maya.cmds.undo()  # undo add members
        n2 = len(x.get_all_members())
        self.assertEqual(n2, 0)

        maya.cmds.redo()  # redo add members
        n3 = len(x.get_all_members())
        self.assertEqual(n3, 40)

    def test_remove_members(self):
        x = sethelper.SetHelper().create_node('mySet')

        # Add members.
        members = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr1 = node + '.translateX'
            attr2 = node + '.rotateY'
            attr3 = node + '.visibility'
            members.append(node)
            members.append(attr1)
            members.append(attr2)
            members.append(attr3)
        x.add_members(members)

        # Remove the members.
        members1 = x.get_all_members()
        x.remove_members(members)

        # undo / redo tests
        maya.cmds.undo()  # undo remove members
        members2 = x.get_all_members()
        self.assertEqual(members2, members1)

        maya.cmds.redo()  # redo remove members
        members3 = x.get_all_members()
        self.assertEqual(members3, [])

    def test_add_member(self):
        x = sethelper.SetHelper().create_node('mySet')

        node = maya.cmds.createNode('transform')
        node_attr = node + '.translateX'
        x.add_member(node)
        x.add_member(node_attr)

        # undo / redo tests
        maya.cmds.undo()  # undo add node_attr
        maya.cmds.undo()  # undo add node
        n1 = len(x.get_all_members())
        self.assertEqual(n1, 0)

        maya.cmds.redo()  # redo add node_attr
        maya.cmds.redo()  # redo add node
        n2 = len(x.get_all_members())
        self.assertEqual(n2, 2)

    def test_remove_member(self):
        x = sethelper.SetHelper().create_node('mySet')

        node = maya.cmds.createNode('transform')
        node_attr = node + '.translateX'
        x.add_members([node, node_attr])

        n1 = len(x.get_all_members())
        self.assertEqual(n1, 2)

        x.remove_member(node)
        n2 = len(x.get_all_members())
        self.assertEqual(n2, n1 - 1)

        x.remove_member(node_attr)
        n3 = len(x.get_all_members())
        self.assertEqual(n3, 0)

        # undo / redo tests
        maya.cmds.undo()  # undo remove node_attr
        maya.cmds.undo()  # undo remove node
        n4 = len(x.get_all_members())
        self.assertEqual(n4, 2)

        maya.cmds.redo()  # redo remove node_attr
        maya.cmds.redo()  # redo remove node
        n5 = len(x.get_all_members())
        self.assertEqual(n5, 0)

    def test_member_in_set(self):
        x = sethelper.SetHelper().create_node('mySet')

        node1 = maya.cmds.createNode('transform')
        node2 = maya.cmds.createNode('transform')
        node_attr = node2 + '.translateX'
        x.add_members([node1, node_attr])

        self.assertTrue(x.member_in_set(node1))
        self.assertTrue(x.member_in_set(node_attr))
        self.assertFalse(x.member_in_set(node2))

    def test_length(self):
        x = sethelper.SetHelper().create_node('mySet')

        node1 = maya.cmds.createNode('transform')
        node_attr = node1 + '.translateX'
        x.add_members([node1, node_attr])
        self.assertEqual(x.length(), 2)

    def test_is_empty(self):
        x = sethelper.SetHelper().create_node('mySet')
        self.assertTrue(x.is_empty())

        node1 = maya.cmds.createNode('transform')
        node_attr = node1 + '.translateX'
        x.add_members([node1, node_attr])
        self.assertFalse(x.is_empty())

        x.clear_all_members()
        y = sethelper.SetHelper()
        y.create_node('myNestedSet')
        x.add_member(y.get_node())

        self.assertFalse(x.is_empty())
        self.assertTrue(y.is_empty())


if __name__ == '__main__':
    prog = unittest.main()
