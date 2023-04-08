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
Test functions for marker module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds


import test.test_api.apiutils as test_api_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.node as node_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.markergroup as markergroup
import mmSolver._api.marker as marker


# @unittest.skip
class TestMarker(test_api_utils.APITestCase):
    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name + 'Shape', parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def test_init(self):
        x = marker.Marker()
        x.create_node()
        x_node = x.get_node()
        self.assertTrue(maya.cmds.objExists(x_node))

        y = marker.Marker(x_node)
        y_node = y.get_node()
        self.assertEqual(x_node, y_node)

        z = marker.Marker(node=x_node)
        z_node = z.get_node()
        self.assertEqual(x_node, z_node)

    def test_get_node(self):
        name = 'myMarker1'
        x = marker.Marker().create_node(name=name)
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertIn(name, node)
        self.assertEqual(node, '|myMarker1')

        y = marker.Marker()
        self.assertEqual(y.get_node(), None)

    def test_set_node(self):
        x = marker.Marker().create_node()
        y = marker.Marker()
        y.set_node(x.get_node())
        self.assertEqual(x.get_node(), y.get_node())
        self.assertRaises(RuntimeError, y.set_node, 'myUnknownNode1')

    def test_create_node(self):
        # TODO: Add undo/redo tests.
        x = marker.Marker()
        x.create_node()
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node))

        x = marker.Marker().create_node()
        node = x.get_node()
        self.assertIsInstance(node, pycompat.TEXT_TYPE)
        self.assertTrue(maya.cmds.objExists(node))

        name = 'myMarker1'
        x = marker.Marker().create_node(name=name)
        node = x.get_node()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(x.get_camera(), None)

        cam = self.create_camera('myCamera1')
        cam_shp = cam.get_shape_node()

        # Create marker linked to camera
        x = marker.Marker().create_node(name=name, cam=cam)
        node = x.get_node()
        mkr_cam = x.get_camera()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

        # Create a Bundle.
        bnd = bundle.Bundle().create_node()
        bnd_node = bnd.get_node()

        # Create marker linked to bundle
        x = marker.Marker().create_node(name=name, bnd=bnd)
        node = x.get_node()
        mkr_bnd = x.get_bundle()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(mkr_bnd.get_node(), bnd_node)

        # Create marker linked to camera and bundle
        x = marker.Marker().create_node(name=name, cam=cam, bnd=bnd)
        node = x.get_node()
        self.assertTrue(maya.cmds.objExists(node))
        mkr_cam = x.get_camera()
        mkr_bnd = x.get_bundle()
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)
        self.assertEqual(mkr_bnd.get_node(), bnd_node)

    def test_delete_node(self):
        x = marker.Marker().create_node()
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
        Set colour of the marker.
        """
        red = (1.0, 0.0, 0.0)
        blue = (0.0, 0.0, 1.0)

        x = marker.Marker()
        x_rgb = x.get_colour_rgb()
        self.assertEqual(x_rgb, None)

        # Create nodes
        y = marker.Marker().create_node(name='myMarker1')
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, red)

        y.set_colour_rgb(blue)
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, blue)
        return

    def test_set_colour_rgba(self):
        """
        Set colour of the marker.
        """
        red = (1.0, 0.0, 0.0, 1.0)
        blue = (0.0, 0.0, 1.0, 0.5)

        x = marker.Marker()
        x_rgba = x.get_colour_rgba()
        self.assertEqual(x_rgba, None)

        # Create nodes
        y = marker.Marker().create_node(name='myMarker1')
        y_rgba = y.get_colour_rgba()
        self.assertEqual(y_rgba, red)

        y.set_colour_rgba(blue)
        y_rgba = y.get_colour_rgba()
        self.assertEqual(y_rgba, blue)
        return

    def test_get_bundle(self):
        x = marker.Marker().create_node()
        bnd0 = x.get_bundle()
        self.assertEqual(bnd0, None)

        bnd1 = bundle.Bundle().create_node()
        x.set_bundle(bnd1)

        bnd2 = x.get_bundle()
        self.assertEqual(bnd1.get_node(), bnd2.get_node())

    def test_set_bundle(self):
        x = marker.Marker().create_node()
        bnd0 = x.get_bundle()
        self.assertEqual(bnd0, None)

        bnd1 = bundle.Bundle().create_node()
        x.set_bundle(bnd1)  # link marker to bundle

        bnd2 = x.get_bundle()
        self.assertEqual(bnd1.get_node(), bnd2.get_node())

        x.set_bundle(None)  # unlink bundle from marker
        bnd3 = x.get_bundle()
        self.assertEqual(bnd3, None)
        self.assertNotEqual(bnd1.get_node(), bnd3)

    def test_get_camera(self):
        x = marker.Marker().create_node()
        mkr_cam = x.get_camera()
        self.assertEqual(mkr_cam, None)

        cam = self.create_camera('myCamera1')
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        y = marker.Marker().create_node(cam=cam)
        mkr_cam = y.get_camera()
        self.assertIsInstance(mkr_cam, camera.Camera)
        self.assertEqual(mkr_cam.get_transform_node(), cam_tfm)
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

    def test_set_camera(self):
        cam = self.create_camera('myCamera1')
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        x = marker.Marker().create_node()
        x.set_camera(cam)

        # Get the camera and test
        mkr_cam = x.get_camera()
        self.assertIsInstance(mkr_cam, camera.Camera)
        self.assertEqual(mkr_cam.get_transform_node(), cam_tfm)
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

        # Unlink marker from camera.
        x.set_camera(None)
        mkr_cam = x.get_camera()
        self.assertEqual(mkr_cam, None)

    def test_get_marker_group(self):
        x = marker.Marker().create_node()
        mkr_grp = x.get_marker_group()
        self.assertEqual(mkr_grp, None)

        cam = self.create_camera('myCamera1')
        mkr_grp1 = markergroup.MarkerGroup().create_node(cam=cam)
        mkr_grp2 = markergroup.MarkerGroup().create_node(cam=cam)

        x = marker.Marker().create_node(mkr_grp=mkr_grp1)
        mkr_grp3 = x.get_marker_group()
        self.assertIsInstance(mkr_grp3, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp1.get_node(), mkr_grp3.get_node())

        x.set_marker_group(mkr_grp2)
        mkr_grp4 = x.get_marker_group()
        self.assertIsInstance(mkr_grp4, markergroup.MarkerGroup)
        self.assertEqual(mkr_grp2.get_node(), mkr_grp4.get_node())

    def test_set_marker_group(self):
        x = marker.Marker().create_node()
        mkr_grp1 = x.get_marker_group()
        self.assertEqual(mkr_grp1, None)

        cam = self.create_camera('myCamera1')
        mkr_grp2 = markergroup.MarkerGroup().create_node(cam=cam)
        mkr_grp3 = markergroup.MarkerGroup().create_node(cam=cam)

        x = marker.Marker().create_node()

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

        # Unlink marker from marker group (detach to world).
        x.set_marker_group(None)
        mkr_grp6 = x.get_marker_group()
        self.assertIs(mkr_grp6, None)
        self.assertEqual(mkr_grp6, None)


if __name__ == '__main__':
    prog = unittest.main()
