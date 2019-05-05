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
Test functions for markergroup module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.markergroup as markergroup
import mmSolver._api.marker as marker


# @unittest.skip
class TestMarkerGroup(test_api_utils.APITestCase):

    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name+'Shape',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def test_init(self):
        x = markergroup.MarkerGroup()
        self.assertEqual(x.get_node(), None)
        self.assertIsInstance(x, markergroup.MarkerGroup)
        self.assertFalse(x.is_valid())

        cam = self.create_camera('camera')
        cam_tfm = cam.get_transform_node()
        node = maya.cmds.createNode('mmMarkerGroupTransform',
                                    name='markerGroup1',
                                    parent=cam_tfm)
        y = markergroup.MarkerGroup(node=node)
        self.assertEqual(y.get_node(), cam_tfm + '|markerGroup1')
        self.assertTrue(y.is_valid())

    def test_set_node(self):
        x = markergroup.MarkerGroup()
        self.assertEqual(x.get_node(), None)
        self.assertFalse(x.is_valid())

        cam = self.create_camera('camera')
        cam_tfm = cam.get_transform_node()
        node = maya.cmds.createNode('mmMarkerGroupTransform',
                                    name='markerGroup1',
                                    parent=cam_tfm)
        x.set_node(node)
        self.assertEqual(x.get_node(), cam_tfm + '|markerGroup1')
        self.assertTrue(x.is_valid())

    def test_get_camera(self):
        camA = self.create_camera('myCamera')
        camA_shp = camA.get_shape_node()
        x = markergroup.MarkerGroup().create_node(cam=camA)
        camB_shp = x.get_camera().get_shape_node()
        self.assertEqual(camA_shp, camB_shp)

    def test_create_node(self):
        cam = self.create_camera('myCamera')
        cam_tfm = cam.get_transform_node()
        x = markergroup.MarkerGroup().create_node(cam=cam)
        self.assertIsInstance(x, markergroup.MarkerGroup)
        self.assertEqual(x.get_node(), cam_tfm + '|markerGroup1')
        self.assertTrue(x.is_valid())

if __name__ == '__main__':
    prog = unittest.main()
