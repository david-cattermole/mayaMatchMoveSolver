"""
Test functions for API utils module.
"""

import sys
import os
import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.marker as marker


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
        # TODO: Add more tests. MObject can be used is so many ways.
        name = 'myNode1'
        node = maya.cmds.createNode('transform', name=name)
        obj = api_utils.get_as_object(node)
        self.assertEqual(obj.apiType(), OpenMaya.MFn.kTransform)

        maya.cmds.delete(node)
        obj = api_utils.get_as_object(node)
        self.assertEqual(obj, None)

    def test_get_as_plug(self):
        name = 'myNode1'
        node = maya.cmds.createNode('transform', name=name)
        plug = api_utils.get_as_plug(node + '.translateY')
        self.assertEqual(plug.name(), 'myNode1.translateY')
        self.assertEqual(plug.asDouble(), 0.0)

        plug.setDouble(3.147)
        self.assertEqual(plug.asDouble(), 3.147)

    def test_detect_object_type(self):
        cam_tfm = maya.cmds.createNode('transform')
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        tfm_obj_type = api_utils.detect_object_type(cam_tfm)
        shp_obj_type = api_utils.detect_object_type(cam_shp)
        self.assertEqual(tfm_obj_type, 'camera')
        self.assertEqual(shp_obj_type, 'camera')

        mkr = marker.Marker().create_node()
        mkr_node = mkr.get_node()
        obj_type = api_utils.detect_object_type(mkr_node)
        self.assertEqual(obj_type, 'marker')

        node = maya.cmds.createNode('transform')
        obj_type = api_utils.detect_object_type(node)
        self.assertEqual(obj_type, 'bundle')

        node_attr = node + '.scaleX'
        obj_type = api_utils.detect_object_type(node_attr)
        self.assertEqual(obj_type, 'attribute')

    def test_get_camera_above_node(self):
        root = maya.cmds.createNode('transform')
        root = api_utils.get_long_name(root)

        cam_tfm = maya.cmds.createNode('transform', parent=root)
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)

        node = maya.cmds.createNode('transform', parent=cam_tfm)
        node = api_utils.get_long_name(node)
        above_cam_tfm, above_cam_shp = api_utils.get_camera_above_node(node)
        self.assertEqual(above_cam_tfm, cam_tfm)
        self.assertEqual(above_cam_shp, cam_shp)


if __name__ == '__main__':
    prog = unittest.main()
