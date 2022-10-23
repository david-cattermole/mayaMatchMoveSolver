# Copyright (C) 2020 David Cattermole.
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
Test functions for Camera utilities module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat


# @unittest.skip
class TestCamera(test_utils.UtilsTestCase):
    """
    Test camera module.
    """

    @staticmethod
    def create_camera(name, tfm_node_type=None):
        assert isinstance(name, pycompat.TEXT_TYPE)
        if tfm_node_type is None:
            tfm_node_type = 'transform'
        cam_tfm = maya.cmds.createNode(tfm_node_type, name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        shp_name = name + 'Shape'
        cam_shp = maya.cmds.createNode('camera', name=shp_name, parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    def test_get_camera(self):
        """
        Test getting a camera from a single half, transform or shape node.
        """
        cam_tfm, cam_shp = self.create_camera('myCamera')

        # Get from transform node.
        x, y = camera_utils.get_camera(cam_tfm)
        self.assertEqual(cam_tfm, x)
        self.assertEqual(cam_shp, y)

        # Get from shape node.
        x, y = camera_utils.get_camera(cam_shp)
        self.assertEqual(cam_tfm, x)
        self.assertEqual(cam_shp, y)
        return

    def test_get_camera_non_standard_transform_node_type(self):
        """
        Test getting a camera from a single half, transform or shape node.

        This function also tests non-standard transform node types.
        In this example we use 'mmMarkerGroupTransform' for the test.

        GitHub issue #123.
        """
        # Custom transform node type. GitHub issue #123.
        custom_node_type = 'mmMarkerGroupTransform'
        cam_tfm, cam_shp = self.create_camera(
            'myCamera', tfm_node_type=custom_node_type
        )

        # Must be a transform type.
        inherited_types = maya.cmds.nodeType(cam_tfm, inherited=True) or []
        self.assertIn('transform', inherited_types)

        # Get from transform node.
        x, y = camera_utils.get_camera(cam_tfm)
        self.assertEqual(cam_tfm, x)
        self.assertEqual(cam_shp, y)

        # Get from shape node.
        x, y = camera_utils.get_camera(cam_shp)
        self.assertEqual(cam_tfm, x)
        self.assertEqual(cam_shp, y)
        return

    def test_startup_camera(self):
        cam_tfm, cam_shp = self.create_camera('myCamera')

        cam_tfm_value = camera_utils.is_startup_cam(cam_tfm)
        cam_shp_value = camera_utils.is_startup_cam(cam_shp)
        cam_tfm_not_value = camera_utils.is_not_startup_cam(cam_tfm)
        cam_shp_not_value = camera_utils.is_not_startup_cam(cam_shp)
        self.assertEqual(cam_tfm_value, False)
        self.assertEqual(cam_shp_value, False)
        self.assertNotEqual(cam_tfm_value, cam_tfm_not_value)
        self.assertNotEqual(cam_shp_value, cam_shp_not_value)

        # Custom transform node type. GitHub issue #123.
        custom_node_type = 'mmMarkerGroupTransform'
        cam_tfm, cam_shp = self.create_camera(
            'myCameraWithCustomNodeType', tfm_node_type=custom_node_type
        )

        cam_tfm_value = camera_utils.is_startup_cam(cam_tfm)
        cam_shp_value = camera_utils.is_startup_cam(cam_shp)
        cam_tfm_not_value = camera_utils.is_not_startup_cam(cam_tfm)
        cam_shp_not_value = camera_utils.is_not_startup_cam(cam_shp)
        self.assertEqual(cam_tfm_value, False)
        self.assertEqual(cam_shp_value, False)
        self.assertNotEqual(cam_tfm_value, cam_tfm_not_value)
        self.assertNotEqual(cam_shp_value, cam_shp_not_value)

        # Maya default start up cameras.
        names = ['persp', 'top', 'side', 'front']
        for name in names:
            tfm_name = '|{name}'.format(name=name)
            shp_name = '|{name}|{name}Shape'.format(name=name)
            cam_tfm_value = camera_utils.is_startup_cam(tfm_name)
            cam_shp_value = camera_utils.is_startup_cam(shp_name)
            self.assertEqual(cam_tfm_value, True)
            self.assertEqual(cam_shp_value, True)
        return


if __name__ == '__main__':
    prog = unittest.main()
