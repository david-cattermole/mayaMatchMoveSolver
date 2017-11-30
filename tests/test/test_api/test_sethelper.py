"""
Test functions for sethelper module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver.api.utils as api_utils
import mmSolver.api.sethelper as sethelper


# @unittest.skip
class TestSetHelper(test_api_utils.APITestCase):
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
        default_anno = 'Unnamed object set'
        self.assertEqual(anno, default_anno)
        line = 'This is the best set in the world!'
        x.set_annotation(line)
        anno = x.get_annotation()
        self.assertEqual(anno, line)

    def test_set_annotation(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')
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

    def test_get_all_nodes(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')
        x.get_all_nodes()

        node1 = maya.cmds.createNode('transform', name='myParent')
        node1 = api_utils.get_long_name(node1)

        node2 = maya.cmds.createNode('transform', name='myChild', parent=node1)
        node2 = api_utils.get_long_name(node2)

        node3 = maya.cmds.createNode('transform', name='myChild')
        node3 = api_utils.get_long_name(node3)

        node4 = maya.cmds.createNode('multiplyDivide', name='myMathsNode')
        node4 = api_utils.get_long_name(node4)

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
        nodes = x.get_all_nodes(full_path=True)
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
        nodes = x.get_all_nodes(full_path=False)
        self.assertEqual(len(nodes), 8)
        self.assertIn(node1, nodes)
        self.assertIn(node2, nodes)
        self.assertIn(node3, nodes)
        self.assertIn(node4, nodes)
        self.assertIn(node_attr1, nodes)
        self.assertIn(node_attr2, nodes)
        self.assertIn(node_attr3, nodes)
        self.assertIn(node_attr4, nodes)
        x.clear_all_nodes()

        # Test 'flatten' argument, with nested sets.
        y = sethelper.SetHelper()
        y.create_node('myNestedSet')
        y.add_node(node2)
        y.add_node(node3)
        y.add_node(node_attr4)
        x.add_node(node1)
        x.add_node(y.get_node())

        # Query the results.
        x_nodes_flat = x.get_all_nodes(flatten=True)
        y_nodes_flat = y.get_all_nodes(flatten=True)
        x_nodes = x.get_all_nodes(flatten=False)
        y_nodes = y.get_all_nodes(flatten=False)
        self.assertEqual(len(x_nodes_flat), 4)
        self.assertEqual(len(x_nodes), 2)
        self.assertEqual(len(y_nodes_flat), 3)
        self.assertEqual(len(y_nodes), 3)
        self.assertEqual(y_nodes, y_nodes_flat)

    def test_clear_all_nodes(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        node_attrs = []
        nodes = []
        for i in xrange(10):
            node = maya.cmds.createNode('transform')
            nodes.append(node)
        for node in nodes:
            node_attr = node + '.translateX'
            node_attrs.append(node_attr)
        x.add_nodes(nodes)
        x.add_nodes(node_attrs)

        n1 = len(x.get_all_nodes())
        self.assertEqual(n1, 20)
        x.clear_all_nodes()
        n2 = len(x.get_all_nodes())
        self.assertEqual(n2, 0)

        # undo / redo tests
        maya.cmds.undo()
        n3 = len(x.get_all_nodes())
        self.assertEqual(n3, 20)

        maya.cmds.redo()
        n4 = len(x.get_all_nodes())
        self.assertEqual(n4, 0)

    def test_add_nodes(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        nodes = []
        for i in xrange(10):
            node = maya.cmds.createNode('transform')
            attr1 = node + '.translateX'
            attr2 = node + '.rotateY'
            attr3 = node + '.visibility'
            nodes.append(node)
            nodes.append(attr1)
            nodes.append(attr2)
            nodes.append(attr3)
        x.add_nodes(nodes)

        # undo / redo tests
        n1 = len(x.get_all_nodes())
        self.assertEqual(n1, 40)

        maya.cmds.undo()  # undo add nodes
        n2 = len(x.get_all_nodes())
        self.assertEqual(n2, 0)

        maya.cmds.redo()  # redo add nodes
        n3 = len(x.get_all_nodes())
        self.assertEqual(n3, 40)

    def test_remove_nodes(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        # Add nodes.
        nodes = []
        for i in xrange(10):
            node = maya.cmds.createNode('transform')
            attr1 = node + '.translateX'
            attr2 = node + '.rotateY'
            attr3 = node + '.visibility'
            nodes.append(node)
            nodes.append(attr1)
            nodes.append(attr2)
            nodes.append(attr3)
        x.add_nodes(nodes)

        # Remove the nodes.
        nodes1 = x.get_all_nodes()
        x.remove_nodes(nodes)

        # undo / redo tests
        maya.cmds.undo()  # undo remove nodes
        nodes2 = x.get_all_nodes()
        self.assertEqual(nodes2, nodes1)

        maya.cmds.redo()  # redo remove nodes
        nodes3 = x.get_all_nodes()
        self.assertEqual(nodes3, [])

    def test_add_node(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        node = maya.cmds.createNode('transform')
        node_attr = node + '.translateX'
        x.add_node(node)
        x.add_node(node_attr)

        # undo / redo tests
        maya.cmds.undo()  # undo add node_attr
        maya.cmds.undo()  # undo add node
        n1 = len(x.get_all_nodes())
        self.assertEqual(n1, 0)

        maya.cmds.redo()  # redo add node_attr
        maya.cmds.redo()  # redo add node
        n2 = len(x.get_all_nodes())
        self.assertEqual(n2, 2)

    def test_remove_node(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        node = maya.cmds.createNode('transform')
        node_attr = node + '.translateX'
        x.add_nodes([node, node_attr])

        n1 = len(x.get_all_nodes())
        self.assertEqual(n1, 2)

        x.remove_node(node)
        n2 = len(x.get_all_nodes())
        self.assertEqual(n2, n1 - 1)

        x.remove_node(node_attr)
        n3 = len(x.get_all_nodes())
        self.assertEqual(n3, 0)

        # undo / redo tests
        maya.cmds.undo()  # undo remove node_attr
        maya.cmds.undo()  # undo remove node
        n4 = len(x.get_all_nodes())
        self.assertEqual(n4, 2)

        maya.cmds.redo()  # redo remove node_attr
        maya.cmds.redo()  # redo remove node
        n5 = len(x.get_all_nodes())
        self.assertEqual(n5, 0)

    def test_node_in_set(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        node1 = maya.cmds.createNode('transform')
        node2 = maya.cmds.createNode('transform')
        node_attr = node1 + '.translateX'
        x.add_nodes([node1, node_attr])

        self.assertTrue(x.node_in_set(node1))
        self.assertTrue(x.node_in_set(node_attr))
        self.assertFalse(x.node_in_set(node2))

    def test_length(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')

        node1 = maya.cmds.createNode('transform')
        node_attr = node1 + '.translateX'
        x.add_nodes([node1, node_attr])
        self.assertEqual(x.length(), 2)

    def test_is_empty(self):
        x = sethelper.SetHelper()
        x.create_node('mySet')
        self.assertTrue(x.is_empty())

        node1 = maya.cmds.createNode('transform')
        node_attr = node1 + '.translateX'
        x.add_nodes([node1, node_attr])
        self.assertFalse(x.is_empty())

        x.clear_all_nodes()
        y = sethelper.SetHelper()
        y.create_node('myNestedSet')
        x.add_node(y.get_node())

        self.assertFalse(x.is_empty())
        self.assertTrue(y.is_empty())


if __name__ == '__main__':
    prog = unittest.main()
