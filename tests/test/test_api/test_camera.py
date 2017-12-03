"""
Test functions for camera module.
"""

import sys
import os
import unittest

import maya.cmds


import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.marker as marker


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
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name='myCameraShape1',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)

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

    def test_get_transform_node(self):
        pass

    def test_set_transform_node(self):
        pass
    
    def test_get_shape_node(self):
        pass

    def test_set_shape_node(self):
        pass

    def test_is_valid(self):
        pass


if __name__ == '__main__':
    prog = unittest.main()
