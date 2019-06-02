"""
Test the mmReprojection command for correctness.
"""

import math
import unittest

import maya.cmds

import test.test_solver.solverutils as solverUtils
import mmSolver._api.utils as api_utils


# @unittest.skip
class TestReprojectionNode(solverUtils.SolverTestCase):

    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name+'Shape',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    def test_reprojection_cmd(self):
        # Camera
        cam_tfm, cam_shp = self.create_camera('camera')
        maya.cmds.setAttr(cam_tfm + '.translateX', -2.0)
        maya.cmds.setAttr(cam_tfm + '.translateY', 2.0)
        maya.cmds.setAttr(cam_tfm + '.translateZ', 5)
        maya.cmds.setAttr(cam_tfm + '.rotateX', 10.0)

        # Input transform
        in_tfm = maya.cmds.createNode('transform', name='INPUT')
        in_shp = maya.cmds.createNode('locator', parent=in_tfm)

        maya.cmds.setAttr(in_tfm + '.translateX', -0.5)
        maya.cmds.setAttr(in_tfm + '.translateY', -0.27)
        # maya.cmds.setAttr(in_tfm + '.translateZ', -1.0)

        coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        self.assertGreater(len(coord_values), 0)
        print 'coord_values', repr(coord_values)

        pix_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            imageResolution=(512, 512),
            asPixelCoordinate=True,
        )
        self.assertGreater(len(pix_coord_values), 0)
        print 'pix_coord_values', repr(pix_coord_values)

        norm_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        self.assertGreater(len(norm_coord_values), 0)
        print 'norm_coord_values', repr(norm_coord_values)

        marker_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asMarkerCoordinate=True,
        )
        self.assertGreater(len(marker_coord_values), 0)
        print 'marker_coord_values', repr(marker_coord_values)        

        camera_point_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asCameraPoint=True,
        )
        self.assertGreater(len(camera_point_values), 0)
        print 'camera_point_values', repr(camera_point_values)

        world_point_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asWorldPoint=True,
        )
        self.assertGreater(len(world_point_values), 0)
        print 'world_point_values', repr(world_point_values)

        # save the output
        path = self.get_data_path('reprojection_cmd_test_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
