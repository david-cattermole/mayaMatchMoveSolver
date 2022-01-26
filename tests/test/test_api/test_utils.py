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
Test functions for API utils module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.naming as api_naming
import mmSolver._api.utils as api_utils
import mmSolver._api.marker as marker
import mmSolver._api.constant as const


# @unittest.skip
class TestUtils(test_api_utils.APITestCase):
    def test_get_long_name(self):
        node = maya.cmds.createNode('transform', name='myNode1')
        self.assertEqual(node, 'myNode1')
        node = node_utils.get_long_name(node)
        self.assertEqual(node, '|myNode1')

        chd1 = maya.cmds.createNode('transform', name='myNode1', parent=node)
        self.assertEqual(chd1, '|myNode1|myNode1')
        chd1 = node_utils.get_long_name(chd1)
        self.assertEqual(chd1, '|myNode1|myNode1')

        chd2 = maya.cmds.createNode('transform', name='myNode1', parent=chd1)
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')
        chd2 = node_utils.get_long_name(chd2)
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')

        chd3 = maya.cmds.createNode('transform', name='myChild1', parent=node)
        self.assertEqual(chd3, 'myChild1')
        chd3 = node_utils.get_long_name(chd3)
        self.assertEqual(chd3, '|myNode1|myChild1')

        node2 = maya.cmds.createNode('transform', name='myChild1')
        self.assertEqual(node2, '|myChild1')
        node2 = node_utils.get_long_name(node2)
        self.assertEqual(node2, '|myChild1')

    def test_get_as_selection_list(self):
        node1 = maya.cmds.createNode('transform', name='myNode1')
        node2 = maya.cmds.createNode('transform', name='myNode1')
        node3 = maya.cmds.createNode('transform', name='myNode1')
        nodes = [node1, node2, node3 + '.translateZ']

        sel_list = node_utils.get_as_selection_list(nodes)
        self.assertIsInstance(sel_list, OpenMaya.MSelectionList)
        self.assertEqual(sel_list.length(), 3)

        select_strings = []
        sel_list.getSelectionStrings(select_strings)
        self.assertEqual(len(select_strings), 3)

        myNodes = ['myNode1', 'myNode2', 'myNode3.translateZ']
        self.assertEqual(select_strings, myNodes)

    def test_get_as_dag_path(self):
        node = maya.cmds.createNode('transform', name='myNode1')
        node_dag = node_utils.get_as_dag_path(node)
        node = node_dag.fullPathName()
        self.assertEqual(node, '|myNode1')
        self.assertEqual(node_dag.partialPathName(), 'myNode1')

        chd1 = maya.cmds.createNode('transform', name='myNode1', parent=node)
        chd1_dag = node_utils.get_as_dag_path(chd1)
        chd1 = chd1_dag.fullPathName()
        self.assertEqual(chd1, '|myNode1|myNode1')
        self.assertEqual(chd1, chd1_dag.partialPathName())
        self.assertEqual(node_dag.childCount(), 1)

        chd2 = maya.cmds.createNode('transform', name='myNode1', parent=chd1)
        chd2_dag = node_utils.get_as_dag_path(chd2)
        chd2 = chd2_dag.fullPathName()
        self.assertEqual(chd2, '|myNode1|myNode1|myNode1')
        self.assertEqual(chd2, chd2_dag.partialPathName())
        self.assertEqual(node_dag.childCount(), 1)
        self.assertEqual(chd1_dag.childCount(), 1)

        chd3 = maya.cmds.createNode('transform', name='myChild1', parent=node)
        chd3_dag = node_utils.get_as_dag_path(chd3)
        chd3 = chd3_dag.fullPathName()
        self.assertEqual(chd3, '|myNode1|myChild1')
        self.assertEqual(chd3_dag.partialPathName(), 'myChild1')
        self.assertEqual(node_dag.childCount(), 2)

        node2 = maya.cmds.createNode('transform', name='myChild1')
        node2_dag = node_utils.get_as_dag_path(node2)
        node2 = node2_dag.fullPathName()
        self.assertEqual(node2, '|myChild1')
        self.assertEqual(node2_dag.partialPathName(), '|myChild1')
        self.assertEqual(node2_dag.childCount(), 0)

    def test_get_as_object(self):
        # TODO: Add more tests. MObject can be used is so many ways.
        name = 'myNode1'
        node = maya.cmds.createNode('transform', name=name)
        obj = node_utils.get_as_object(node)
        self.assertEqual(obj.apiType(), OpenMaya.MFn.kTransform)

        maya.cmds.delete(node)
        obj = node_utils.get_as_object(node)
        self.assertEqual(obj, None)

    def test_get_as_plug(self):
        name = 'myNode1'
        node = maya.cmds.createNode('transform', name=name)
        plug = node_utils.get_as_plug(node + '.translateY')
        self.assertEqual(plug.name(), 'myNode1.translateY')
        self.assertEqual(plug.asDouble(), 0.0)

        plug.setDouble(3.147)
        self.assertEqual(plug.asDouble(), 3.147)

    def test_get_object_type(self):
        """
        Test getting string object types from a given Maya node.

        TODO: Does not provide a 'collection' example.
        """
        # Camera Type
        cam_tfm = maya.cmds.createNode('transform')
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        tfm_obj_type = api_utils.get_object_type(cam_tfm)
        shp_obj_type = api_utils.get_object_type(cam_shp)
        self.assertEqual(tfm_obj_type, const.OBJECT_TYPE_CAMERA)
        self.assertEqual(shp_obj_type, const.OBJECT_TYPE_CAMERA)

        # Marker Type
        mkr = marker.Marker().create_node()
        mkr_node = mkr.get_node()
        obj_type = api_utils.get_object_type(mkr_node)
        self.assertEqual(obj_type, const.OBJECT_TYPE_MARKER)

        # Marker shape node must also return as OBJECT_TYPE_MARKER
        mkr_shp_node = maya.cmds.listRelatives(mkr_node, shapes=True)[0]
        obj_type = api_utils.get_object_type(mkr_shp_node)
        self.assertEqual(obj_type, const.OBJECT_TYPE_UNKNOWN)

        # Marker Group
        node = maya.cmds.createNode('mmMarkerGroupTransform')
        obj_type = api_utils.get_object_type(node)
        self.assertEqual(obj_type, const.OBJECT_TYPE_MARKER_GROUP)

        # A Bundle must be more than just a transform and locator.
        # Use mmSolver.api.Bundle.create_node() to create a Bundle.
        #
        # GitHub Issue #6.
        bnd_node = maya.cmds.createNode('transform')
        bnd_shp_node = maya.cmds.createNode('locator', parent=bnd_node)
        obj_type = api_utils.get_object_type(bnd_node)
        self.assertEqual(obj_type, const.OBJECT_TYPE_UNKNOWN)

        # Giving a shape will not work.
        obj_type = api_utils.get_object_type(bnd_shp_node)
        self.assertEqual(obj_type, const.OBJECT_TYPE_UNKNOWN)

        # Attribute Type
        node_attr = node + '.scaleX'
        obj_type = api_utils.get_object_type(node_attr)
        self.assertEqual(obj_type, const.OBJECT_TYPE_ATTRIBUTE)

    def test_get_camera_above_node(self):
        root = maya.cmds.createNode('transform')
        root = node_utils.get_long_name(root)

        cam_tfm = maya.cmds.createNode('transform', parent=root)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)

        node = maya.cmds.createNode('transform', parent=cam_tfm)
        node = node_utils.get_long_name(node)
        above_cam_tfm, above_cam_shp = node_utils.get_camera_above_node(node)
        self.assertEqual(above_cam_tfm, cam_tfm)
        self.assertEqual(above_cam_shp, cam_shp)

    def test_get_marker_group_above_node(self):
        mkr_grp = maya.cmds.createNode('mmMarkerGroupTransform')
        mkr_grp = node_utils.get_long_name(mkr_grp)

        node = maya.cmds.createNode('transform', parent=mkr_grp)
        node = node_utils.get_long_name(node)
        above_mkr_grp = api_utils.get_marker_group_above_node(node)
        self.assertEqual(above_mkr_grp, mkr_grp)

    def test_convert_valid_maya_name__case_normal(self):
        """
        Incrementing numbers at the end of a node name.
        """
        name1 = 'my_node_01'
        node1 = maya.cmds.createNode('transform', name=name1)
        
        name2 = api_naming.find_valid_maya_node_name(name1)
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'my_node_02')
        self.assertEqual(node2, name2)
        
        name3 = api_naming.find_valid_maya_node_name(name2)
        node3 = maya.cmds.createNode('transform', name=name3)
        self.assertEqual(name3, 'my_node_03')
        self.assertEqual(node3, name3)
        return

    def test_convert_valid_maya_name__case_mid_name(self):
        """
        Incrementing numbers in the middle of a node name.
        """
        name1 = 'my_node_01_MKR'
        node1 = maya.cmds.createNode('transform', name=name1)
        
        name2 = api_naming.find_valid_maya_node_name(name1)
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'my_node_02_MKR')
        self.assertEqual(node2, name2)
        
        name3 = api_naming.find_valid_maya_node_name(name2)
        node3 = maya.cmds.createNode('transform', name=name3)
        self.assertEqual(name3, 'my_node_03_MKR')
        self.assertEqual(node3, name3)
        return
    
    def test_convert_valid_maya_name__case_two_numbers(self):
        """
        There are two numbers, only the last one should be incremented.
        """
        name1 = 'my_node_001_001'
        node1 = maya.cmds.createNode('transform', name=name1)
    
        name2 = api_naming.find_valid_maya_node_name(name1)
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'my_node_001_002')
        self.assertEqual(node2, name2)
    
    def test_convert_valid_maya_name__case_no_number(self):
        """
        There is no number in the node name, it should
        """
        name1 = 'my_node'
        node1 = maya.cmds.createNode('transform', name=name1)
        self.assertTrue(maya.cmds.objExists(node1))
        self.assertEqual(node1, 'my_node')
    
        name2 = api_naming.find_valid_maya_node_name(name1)
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'my_node_001')
        self.assertEqual(node2, name2)
        
    def test_get_marker_name(self):
        name1 = api_naming.get_new_marker_name('01')
        node1 = maya.cmds.createNode('transform', name=name1)
        self.assertEqual(name1, 'marker_01_MKR')
        self.assertEqual(node1, name1)

        name2 = api_naming.get_new_marker_name('01')
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'marker_02_MKR')
        self.assertEqual(node2, name2)

        name3 = api_naming.get_new_marker_name('01')
        node3 = maya.cmds.createNode('transform', name=name3)
        self.assertEqual(name3, 'marker_03_MKR')
        self.assertEqual(node3, name3)

        name = api_naming.get_new_marker_name('TopLeft')
        node = maya.cmds.createNode('transform', name=name)
        self.assertEqual(name, 'TopLeft_MKR')
        self.assertEqual(node, name)

    def test_get_bundle_name(self):
        name1 = api_naming.get_new_bundle_name('01')
        node1 = maya.cmds.createNode('transform', name=name1)
        self.assertEqual(name1, 'bundle_01_BND')
        self.assertEqual(node1, name1)

        name2 = api_naming.get_new_bundle_name('01')
        node2 = maya.cmds.createNode('transform', name=name2)
        self.assertEqual(name2, 'bundle_02_BND')
        self.assertEqual(node2, name2)

        name3 = api_naming.get_new_bundle_name('01')
        node3 = maya.cmds.createNode('transform', name=name3)
        self.assertEqual(name3, 'bundle_03_BND')
        self.assertEqual(node3, name3)


if __name__ == '__main__':
    prog = unittest.main()
