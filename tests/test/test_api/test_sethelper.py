"""
Test functions for sethelper module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as testApiUtils
import mmSolver.api.utils as apiUtils
import mmSolver.api.sethelper as sethelper


# @unittest.skip
class TestSetHelper(testApiUtils.APITestBase):
    def test_init(self):
        x = sethelper.SetHelper()
        self.assertEqual(x.get_node(), None)
        self.assertEqual(x.get_annotation(), None)
        self.assertEqual(x.get_all_nodes(), [])

        node = maya.cmds.sets(name='mySet')
        x = sethelper.SetHelper(name=node)
        self.assertEqual(x.get_node(), node)
        # NOTE: 'Unnamed object set' is the default set node annotation.
        self.assertEqual(x.get_annotation(), 'Unnamed object set')
        self.assertEqual(x.get_all_nodes(), [])
        self.assertTrue(maya.cmds.objExists(x.get_node()))

    def test_get_node(self):
        name = 'mySet'
        node = maya.cmds.sets(name=name)
        x = sethelper.SetHelper(name=node)
        self.assertEqual(x.get_node(), name)

    def test_set_node(self):
        name1 = 'mySet'
        name2 = 'myNextSet'
        node1 = maya.cmds.sets(name=name1)
        node2 = maya.cmds.sets(name=name2)
        x = sethelper.SetHelper(name=node1)
        self.assertEqual(x.get_node(), name1)
        x.set_node(node2)
        self.assertEqual(x.get_node(), name2)

    def test_create_node(self):
        state1 = maya.cmds.ls(long=True)

        x = sethelper.SetHelper()
        node = x.create_node('newSet')
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
        x = sethelper.SetHelper()
        x.create_node('mySet')
        anno = x.get_annotation()
        self.assertEqual(anno, 'Unnamed object set')
        line = 'This is the best set in the world!'
        x.set_annotation(line)
        anno = x.get_annotation()
        self.assertEqual(anno, line)

    def test_set_annotation(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')
        anno = x.get_annotation()
        self.assertEqual(anno, 'Unnamed object set')
        line = 'This is the best set in the world!'
        x.set_annotation(line)
        anno = x.get_annotation()
        self.assertEqual(anno, line)

    def test_get_all_nodes(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')
        x.get_all_nodes()

        node1 = maya.cmds.createNode('transform', name='myParent')
        node1 = apiUtils.get_long_name(node1)

        node2 = maya.cmds.createNode('transform', name='myChild', parent=node1)
        node2 = apiUtils.get_long_name(node2)

        node3 = maya.cmds.createNode('transform', name='myChild')
        node3 = apiUtils.get_long_name(node3)

        node4 = maya.cmds.createNode('multiplyDivide', name='myMathsNode')
        node4 = apiUtils.get_long_name(node4)

        node_attr1 = node1 + '.tx'  # short attribute name
        node_attr2 = node2 + '.rotateY'
        node_attr3 = node3 + '.rotateX'
        node_attr4 = node4 + '.operation'

        x.add_node(node1)
        x.add_node(node2)
        x.add_node(node3)
        x.add_node(node4)
        x.add_node(node_attr1)
        x.add_node(node_attr2)
        x.add_node(node_attr3)
        x.add_node(node_attr4)

        # Get the full path node names
        nodes = x.get_all_nodes(fullPath=True)
        self.assertEqual(len(nodes), 8)
        self.assertIn(node1, nodes)
        self.assertIn(node2, nodes)
        self.assertIn(node3, nodes)
        self.assertIn(node4, nodes)
        node_attr1 = node1 + '.translateX'  # full attribute name
        self.assertIn(node_attr1, nodes)
        self.assertIn(node_attr2, nodes)
        self.assertIn(node_attr3, nodes)
        self.assertIn(node_attr4, nodes)

        # Make sure short-names are handled too
        node1 = 'myParent'
        node2 = 'myParent|myChild'
        node3 = '|myChild'
        node4 = 'myMathsNode'
        node_attr1 = node1 + '.translateX'
        node_attr2 = node2 + '.rotateY'
        node_attr3 = node3 + '.rotateX'
        node_attr4 = node4 + '.operation'
        nodes = x.get_all_nodes(fullPath=False)
        self.assertEqual(len(nodes), 8)
        self.assertIn(node1, nodes)
        self.assertIn(node2, nodes)
        self.assertIn(node3, nodes)
        self.assertIn(node4, nodes)
        self.assertIn(node_attr1, nodes)
        self.assertIn(node_attr2, nodes)
        self.assertIn(node_attr3, nodes)
        self.assertIn(node_attr4, nodes)

        # TODO: Test 'flatten' argument, with nested sets.


if __name__ == '__main__':
    prog = unittest.main()
