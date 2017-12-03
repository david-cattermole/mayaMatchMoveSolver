"""
Test functions for marker module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver.api.utils as api_utils
import mmSolver.api.marker as marker


# @unittest.skip
class TestMarker(test_api_utils.APITestCase):
    def test_init(self):
        x = marker.Marker()
        x.create_node()
        x_node = x.get_node()
        self.assertTrue(maya.cmds.objExists(x_node))

        y = marker.Marker(x_node)
        y_node = y.get_node()
        self.assertEqual(x_node, y_node)

        z = marker.Marker(name=x_node)
        z_node = z.get_node()
        self.assertEqual(x_node, z_node)

    def test_get_node(self):
        name = 'myMarker1'
        x = marker.Marker().create_node(name=name)
        node = x.get_node()
        self.assertIsInstance(node, (str, unicode))
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
        self.assertIsInstance(node, (str, unicode))
        self.assertTrue(maya.cmds.objExists(node))

        x = marker.Marker().create_node()
        node = x.get_node()
        self.assertIsInstance(node, (str, unicode))
        self.assertTrue(maya.cmds.objExists(node))

        name = 'myMarker1'
        x = marker.Marker().create_node(name=name)
        node = x.get_node()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(x.get_camera(), None)

        # Create a Camera.
        cam_tfm = maya.cmds.createNode('transform', name='myCamera1')
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name='myCameraShape1',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        cam = marker.Camera(transform=cam_tfm, shape=cam_shp)

        # Create marker linked to camera
        x = marker.Marker().create_node(name=name, cam=cam)
        node = x.get_node()
        mkr_cam = x.get_camera()
        self.assertTrue(maya.cmds.objExists(node))
        self.assertEqual(mkr_cam.get_shape_node(), cam_shp)

        # Create a Bundle.
        bnd = marker.Bundle().create_node()
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
        self.assertIsInstance(node1, (str, unicode))
        self.assertTrue(maya.cmds.objExists(node1))

        x.delete_node()

        node2 = x.get_node()
        self.assertEqual(node2, None)
        self.assertFalse(maya.cmds.objExists(node1))

        maya.cmds.undo()  # undo delete_node
        node3 = x.get_node()
        self.assertIsInstance(node3, (str, unicode))
        self.assertTrue(maya.cmds.objExists(node1))
        self.assertTrue(maya.cmds.objExists(node3))
        self.assertEqual(node1, node3)

    def test_get_bundle(self):
        x = marker.Marker().create_node()
        bnd0 = x.get_bundle()
        self.assertEqual(bnd0, None)

        bnd1 = marker.Bundle().create_node()
        x.set_bundle(bnd1)

        bnd2 = x.get_bundle()
        self.assertEqual(bnd1.get_node(), bnd2.get_node())

    def test_set_bundle(self):
        x = marker.Marker().create_node()
        bnd0 = x.get_bundle()
        self.assertEqual(bnd0, None)

        bnd1 = marker.Bundle().create_node()
        x.set_bundle(bnd1)  # link marker to bundle

        bnd2 = x.get_bundle()
        self.assertEqual(bnd1.get_node(), bnd2.get_node())

        x.set_bundle(None)  # unlink bundle from marker
        bnd3 = x.get_bundle()
        self.assertEqual(bnd3, None)
        self.assertNotEqual(bnd1.get_node(), bnd3)

    # def test_get_camera(self):
    #     self.fail()
    #     pass

    # def test_set_camera(self):
    #     self.fail()
    #     pass


if __name__ == '__main__':
    prog = unittest.main()
