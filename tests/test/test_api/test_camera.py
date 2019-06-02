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

import sys
import os
import unittest

import maya.cmds


import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.camera as camera


# @unittest.skip
class TestCamera(test_api_utils.APITestCase):
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

    # def test_get_transform_node(self):
    #     pass

    # def test_set_transform_node(self):
    #     pass

    # def test_get_shape_node(self):
    #     pass

    # def test_set_shape_node(self):
    #     pass

    # def test_is_valid(self):
    #     pass


if __name__ == '__main__':
    prog = unittest.main()
