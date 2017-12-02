"""
Test functions for API utils module.
"""

import sys
import os
import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver.api.utils as api_utils


# @unittest.skip
class TestUtils(test_api_utils.APITestCase):
    def test_get_long_name(self):
        node = maya.cmds.createNode('transform', name='myNode1')
        self.assertEqual(node, 'myNode1')
        node = api_utils.get_long_name(node)
        self.assertEqual(node, '|myNode1')

        chd1 = maya.cmds.createNode('transform', name='myNode1', parent=node)
        self.assertEqual(chd1, '|myNode1|myNode1')
        chd1 = api_utils.get_long_name(chd1)
        self.assertEqual(chd1, '|myNode1|myNode1')

        chd2 = maya.cmds.createNode('transform', name='myNode1', parent=chd1)
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')
        chd2 = api_utils.get_long_name(chd2)
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')

        chd3 = maya.cmds.createNode('transform', name='myChild1', parent=node)
        self.assertEqual(chd3, 'myChild1')
        chd3 = api_utils.get_long_name(chd3)
        self.assertEqual(chd3, '|myNode1|myChild1')

        node2 = maya.cmds.createNode('transform', name='myChild1')
        self.assertEqual(node2, '|myChild1')
        node2 = api_utils.get_long_name(node2)
        self.assertEqual(node2, '|myChild1')

    def test_get_as_selection_list(self):
        node1 = maya.cmds.createNode('transform', name='myNode1')
        node2 = maya.cmds.createNode('transform', name='myNode1')
        node3 = maya.cmds.createNode('transform', name='myNode1')
        nodes = [node1, node2, node3 + '.translateZ']

        sel_list = api_utils.get_as_selection_list(nodes)
        self.assertIsInstance(sel_list, OpenMaya.MSelectionList)
        self.assertEqual(sel_list.length(), 3)

        select_strings = []
        sel_list.getSelectionStrings(select_strings)
        self.assertEqual(len(select_strings), 3)

        myNodes = ['myNode1', 'myNode2', 'myNode3.translateZ']
        self.assertEqual(select_strings, myNodes)

    def test_get_as_dag_path(self):
        node = maya.cmds.createNode('transform', name='myNode1')
        node_dag = api_utils.get_as_dag_path(node)
        node = node_dag.fullPathName()
        self.assertEqual(node, '|myNode1')
        self.assertEqual(node_dag.partialPathName(), 'myNode1')

        chd1 = maya.cmds.createNode('transform', name='myNode1', parent=node)
        chd1_dag = api_utils.get_as_dag_path(chd1)
        chd1 = chd1_dag.fullPathName()
        self.assertEqual(chd1, '|myNode1|myNode1')
        self.assertEqual(chd1, chd1_dag.partialPathName())
        self.assertEqual(node_dag.childCount(), 1)

        chd2 = maya.cmds.createNode('transform', name='myNode1', parent=chd1)
        chd2_dag = api_utils.get_as_dag_path(chd2)
        chd2 = chd2_dag.fullPathName()
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')
        self.assertEqual(chd2, chd2_dag.partialPathName())
        self.assertEqual(node_dag.childCount(), 1)
        self.assertEqual(chd1_dag.childCount(), 1)

        chd3 = maya.cmds.createNode('transform', name='myChild1', parent=node)
        chd3_dag = api_utils.get_as_dag_path(chd3)
        chd3 = chd3_dag.fullPathName()
        self.assertEqual(chd3, '|myNode1|myChild1')
        self.assertEqual(chd3_dag.partialPathName(), 'myChild1')
        self.assertEqual(node_dag.childCount(), 2)

        node2 = maya.cmds.createNode('transform', name='myChild1')
        node2_dag = api_utils.get_as_dag_path(node2)
        node2 = node2_dag.fullPathName()
        self.assertEqual(node2, '|myChild1')
        self.assertEqual(node2_dag.partialPathName(), '|myChild1')
        self.assertEqual(node2_dag.childCount(), 0)

    def test_get_as_object(self):
        # api_utils.get_as_object()
        pass

    def test_get_as_plug(self):
        # api_utils.get_as_plug()
        pass

    def test_detect_object_type(self):
        # api_utils.detect_object_type(node)
        pass


if __name__ == '__main__':
    prog = unittest.main()
