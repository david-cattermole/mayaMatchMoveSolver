# Copyright (C) 2022 David Cattermole.
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
Test functions for line module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import unittest

import maya.cmds


import test.test_api.apiutils as test_api_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.node as node_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.markergroup as markergroup
import mmSolver._api.marker as marker
import mmSolver._api.line as line


# @unittest.skip
class TestLine(test_api_utils.APITestCase):
    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name + 'Shape', parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def test_init(self):
        x = line.Line()
        x.create_node()
        x_node = x.get_node()
        self.assertTrue(maya.cmds.objExists(x_node))

        y = line.Line(x_node)
        y_node = y.get_node()
        self.assertEqual(x_node, y_node)

        z = line.Line(node=x_node)
        z_node = z.get_node()
        self.assertEqual(x_node, z_node)

    def test_get_node(self):
        name = 'myLine1'
        x = line.Line().create_node(name=name)
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertIn(name, node)
        self.assertEqual(node, '|myLine1')

        y = line.Line()
        self.assertEqual(y.get_node(), None)

    def test_set_node(self):
        x = line.Line().create_node()
        y = line.Line()
        y.set_node(x.get_node())
        self.assertEqual(x.get_node(), y.get_node())
        self.assertRaises(RuntimeError, y.set_node, 'myUnknownNode1')

    def test_create_node(self):
        # TODO: Add undo/redo tests.
        x = line.Line()
        x.create_node()
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node))

        x = line.Line().create_node()
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node))

        name = 'myLine1'
        x = line.Line().create_node(name=name)
        node = x.get_node()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(x.get_camera(), None)

        cam = self.create_camera('myCamera1')
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        # Create line linked to camera
        x = line.Line().create_node(name=name, cam=cam)
        node = x.get_node()
        mkr_cam = x.get_camera()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

    def test_delete_node(self):
        x = line.Line().create_node()
        node1 = x.get_node()
        self.assertIsInstance(node1, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node1))

        x.delete_node()

        node2 = x.get_node()
        self.assertEqual(node2, None)
        self.assertFalse(maya.cmds.objExists(node1))

        maya.cmds.undo()  # undo delete_node
        node3 = x.get_node()
        self.assertIsInstance(node3, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node1))
        self.assertTrue(maya.cmds.objExists(node3))
        self.assertEqual(node1, node3)

    def test_set_colour_rgb(self):
        """
        Set wireframe colour of the line.
        """
        magenta = (1.0, 0.0, 1.0)
        red = (1.0, 0.0, 0.0)
        green = (0.0, 1.0, 0.0)
        blue = (0.0, 0.0, 1.0)

        x = line.Line()
        x_rgb = x.get_colour_rgb()
        self.assertEqual(x_rgb, None)

        # Create nodes
        y = line.Line().create_node(name='myLine1')
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, magenta)

        y.set_colour_rgb(blue)
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, blue)
        return

    def test_get_marker_list(self):
        x = line.Line().create_node()
        mkr_list0 = x.get_marker_list()
        self.assertEqual(len(mkr_list0), 2)

        mkr1 = marker.Marker().create_node()
        x.set_marker_list([mkr1])

        mkr_list2 = x.get_marker_list()
        self.assertEqual(len(mkr_list2), 1)
        self.assertEqual(mkr1.get_node(), mkr_list2[0].get_node())

    def test_set_marker_list(self):
        x = line.Line().create_node()
        mkr_list0 = x.get_marker_list()
        self.assertEqual(len(mkr_list0), 2)

        mkr1 = marker.Marker().create_node()
        x.set_marker_list([mkr1])  # link markers to line

        mkr_list2 = x.get_marker_list()
        self.assertEqual(mkr1.get_node(), mkr_list2[0].get_node())

        x.set_marker_list(None)  # unlink markers from line
        mkr_list3 = x.get_marker_list()
        self.assertEqual(len(mkr_list3), 0)

    def test_get_camera(self):
        x = line.Line().create_node()
        mkr_cam = x.get_camera()
        self.assertEqual(mkr_cam, None)

        cam = self.create_camera('myCamera1')
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        y = line.Line().create_node(cam=cam)
        mkr_cam = y.get_camera()
        self.assertIsInstance(mkr_cam, camera.Camera)
        self.assertEqual(mkr_cam.get_transform_node(), cam_tfm)
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

    def test_set_camera(self):
        cam = self.create_camera('myCamera1')
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        x = line.Line().create_node()
        x.set_camera(cam)

        # Get the camera and test
        mkr_cam = x.get_camera()
        self.assertIsInstance(mkr_cam, camera.Camera)
        self.assertEqual(mkr_cam.get_transform_node(), cam_tfm)
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

        # Unlink line from camera.
        x.set_camera(None)
        mkr_cam = x.get_camera()
        self.assertEqual(mkr_cam, None)

    def test_get_marker_group(self):
        x = line.Line().create_node()
        mkr_grp = x.get_marker_group()
        self.assertEqual(mkr_grp, None)

        cam = self.create_camera('myCamera1')
        mkr_grp1 = markergroup.MarkerGroup().create_node(cam=cam)
        mkr_grp2 = markergroup.MarkerGroup().create_node(cam=cam)

        x = line.Line().create_node(mkr_grp=mkr_grp1)
        mkr_grp3 = x.get_marker_group()
        self.assertIsInstance(mkr_grp3, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp1.get_node(), mkr_grp3.get_node())

        x.set_marker_group(mkr_grp2)
        mkr_grp4 = x.get_marker_group()
        self.assertIsInstance(mkr_grp4, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp2.get_node(), mkr_grp4.get_node())

    def test_set_marker_group(self):
        x = line.Line().create_node()
        mkr_grp1 = x.get_marker_group()
        self.assertEqual(mkr_grp1, None)

        cam = self.create_camera('myCamera1')
        mkr_grp2 = markergroup.MarkerGroup().create_node(cam=cam)
        mkr_grp3 = markergroup.MarkerGroup().create_node(cam=cam)

        x = line.Line().create_node()

        # Set mkr_grp2 as marker group.
        x.set_marker_group(mkr_grp2)
        mkr_grp4 = x.get_marker_group()
        self.assertIsInstance(mkr_grp4, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp2.get_node(), mkr_grp4.get_node())

        # Set mkr_grp3 as marker group.
        x.set_marker_group(mkr_grp3)
        mkr_grp5 = x.get_marker_group()
        self.assertIsInstance(mkr_grp5, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp3.get_node(), mkr_grp5.get_node())

        # Unlink line from marker group (detach to world).
        x.set_marker_group(None)
        mkr_grp6 = x.get_marker_group()
        self.assertIs(mkr_grp6, None)
        self.assertEqual(mkr_grp6, None)


if __name__ == '__main__':
    prog = unittest.main()
