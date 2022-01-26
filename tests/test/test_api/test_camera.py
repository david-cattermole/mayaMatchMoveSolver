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
Test functions for camera module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.camera as camera
import mmSolver._api.constant as const


# @unittest.skip
class TestCamera(test_api_utils.APITestCase):

    @staticmethod
    def create_camera(name):
        assert isinstance(name, pycompat.TEXT_TYPE)
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        shp_name = name + 'Shape'
        cam_shp = maya.cmds.createNode(
            'camera', name=shp_name, parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    def test_init(self):
        x = camera.Camera()
        x_tfm = x.get_transform_node()
        x_shp = x.get_shape_node()
        self.assertEqual(x_tfm, None)
        self.assertEqual(x_shp, None)

        # Create nodes
        cam_tfm = maya.cmds.createNode('transform', name='myCamera1')
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name='myCameraShape1',
                                       parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)

        y = camera.Camera(transform=cam_tfm, shape=cam_shp)
        y_tfm = y.get_transform_node()
        y_shp = y.get_shape_node()
        self.assertTrue(maya.cmds.objExists(y_tfm))
        self.assertTrue(maya.cmds.objExists(y_shp))
        self.assertEqual(y_tfm, cam_tfm)
        self.assertEqual(y_shp, cam_shp)

        z1 = camera.Camera(transform=cam_tfm)
        z1_tfm = z1.get_transform_node()
        z1_shp = z1.get_shape_node()
        self.assertEqual(z1_tfm, cam_tfm)
        self.assertEqual(z1_shp, cam_shp)

        z2 = camera.Camera(shape=cam_shp)
        z2_tfm = z2.get_transform_node()
        z2_shp = z2.get_shape_node()
        self.assertEqual(z2_tfm, cam_tfm)
        self.assertEqual(z2_shp, cam_shp)

    def test_init_with_non_standard_transform_node(self):
        """
        Create a camera with a custom transform node.

        Some pipelines custom transform nodes for camera transform
        nodes.

        GitHub issue #123.
        """
        custom_node_type = 'mmMarkerGroupTransform'
        # Create nodes
        cam_tfm = maya.cmds.createNode(custom_node_type, name='myCamera1')
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name='myCameraShape1',
                                       parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)

        y = camera.Camera(transform=cam_tfm, shape=cam_shp)
        y_tfm = y.get_transform_node()
        y_tfm_uid = y.get_transform_uid()
        y_tfm_uid_node = node_utils.get_long_name(y_tfm_uid)
        y_shp = y.get_shape_node()
        y_shp_uid = y.get_shape_uid()
        y_shp_uid_node = node_utils.get_long_name(y_shp_uid)
        self.assertTrue(maya.cmds.objExists(y_tfm))
        self.assertTrue(maya.cmds.objExists(y_shp))
        self.assertTrue(maya.cmds.objExists(y_tfm_uid_node))
        self.assertTrue(maya.cmds.objExists(y_shp_uid_node))
        self.assertEqual(y_tfm, cam_tfm)
        self.assertEqual(y_shp, cam_shp)
        self.assertEqual(y_tfm_uid_node, cam_tfm)
        self.assertEqual(y_shp_uid_node, cam_shp)
        return

    def test_get_plate_resolution(self):
        cam_tfm, cam_shp = self.create_camera('myCamera')
        x = camera.Camera(transform=cam_tfm, shape=cam_shp)
        res = x.get_plate_resolution()
        self.assertTrue(isinstance(res, (tuple, list)))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], const.DEFAULT_PLATE_WIDTH)
        self.assertEqual(res[1], const.DEFAULT_PLATE_HEIGHT)
        return

    def test_is_valid(self):
        cam_tfm, cam_shp = self.create_camera('myCamera')
        x = camera.Camera(transform=cam_tfm, shape=cam_shp)
        valid = x.is_valid()
        self.assertTrue(valid)
        return


if __name__ == '__main__':
    prog = unittest.main()
