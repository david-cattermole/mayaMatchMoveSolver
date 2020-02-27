"""
Test the mmReprojection command for correctness.
"""

import math
import unittest

import maya.cmds

import test.test_solver.solverutils as solverUtils
import mmSolver.utils.node as node_utils


# @unittest.skip
class TestReprojectionNode(solverUtils.SolverTestCase):

    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name+'Shape',
                                       parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    def test_reprojection_cmd(self):
        start = 1001
        end = 1005
        maya.cmds.playbackOptions(min=start, max=end)

        # Camera
        cam_tfm, cam_shp = self.create_camera('camera')
        maya.cmds.setAttr(cam_tfm + '.translateY', 2.0)
        maya.cmds.setAttr(cam_tfm + '.translateZ', 5)

        attr = 'translateX'
        maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=end, value=2.0)

        attr = 'rotateX'
        maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=start, value=10.0)
        maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=end, value=12.0)

        attr = 'focalLength'
        maya.cmds.setKeyframe(cam_shp, attribute=attr, time=start, value=35.0)
        maya.cmds.setKeyframe(cam_shp, attribute=attr, time=end, value=85.0)

        # Input transform
        in_tfm = maya.cmds.createNode('transform', name='INPUT')
        in_shp = maya.cmds.createNode('locator', parent=in_tfm)

        pnt_x = -0.5
        pnt_y = 2.7
        pnt_z = 0.0
        maya.cmds.setAttr(in_tfm + '.translateX', pnt_x)
        maya.cmds.setAttr(in_tfm + '.translateY', pnt_y)
        maya.cmds.setAttr(in_tfm + '.translateZ', pnt_z)

        # save the scene
        path = self.get_data_path('reprojection_cmd_test_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        print 'coord_values', repr(coord_values)
        self.assertGreater(len(coord_values), 0)
        coord_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        print 'coord_values_b', repr(coord_values_b)
        self.assertListEqual(coord_values, coord_values_b)

        pix_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            imageResolution=(512, 512),
            asPixelCoordinate=True,
        )
        print 'pix_coord_values', repr(pix_coord_values)
        self.assertGreater(len(pix_coord_values), 0)
        pix_coord_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            imageResolution=(512, 512),
            asPixelCoordinate=True,
        )
        print 'pix_coord_values_b', repr(pix_coord_values_b)
        self.assertListEqual(pix_coord_values, pix_coord_values_b)

        norm_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        print 'norm_coord_values', repr(norm_coord_values)
        self.assertGreater(len(norm_coord_values), 0)
        norm_coord_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asNormalizedCoordinate=True,
        )
        print 'norm_coord_values_b', repr(norm_coord_values_b)
        self.assertListEqual(norm_coord_values, norm_coord_values_b)

        marker_coord_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asMarkerCoordinate=True,
        )
        print 'marker_coord_values', repr(marker_coord_values)
        self.assertGreater(len(marker_coord_values), 0)
        marker_coord_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asMarkerCoordinate=True,
        )
        print 'marker_coord_values_b', repr(marker_coord_values_b)
        self.assertListEqual(marker_coord_values, marker_coord_values_b)

        camera_point_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asCameraPoint=True,
        )
        print 'camera_point_values', repr(camera_point_values)
        self.assertGreater(len(camera_point_values), 0)
        camera_point_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asCameraPoint=True,
        )
        print 'camera_point_values_b', repr(camera_point_values_b)
        self.assertListEqual(camera_point_values, camera_point_values_b)

        world_point_values = maya.cmds.mmReprojection(
            in_tfm,
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asWorldPoint=True,
        )
        print 'world_point_values', repr(world_point_values)
        self.assertGreater(len(world_point_values), 0)
        world_point_values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=(1001.0, 1002.0, 1003.0, 1004.0, 1005.0),
            asWorldPoint=True,
        )
        print 'world_point_values_b', repr(world_point_values_b)
        self.assertListEqual(world_point_values, world_point_values_b)

        times = (1001.0, 1002.0, 1003.0, 1004.0, 1005.0,)
        out_tfm = maya.cmds.createNode('transform', name='OUTPUT')
        out_shp = maya.cmds.createNode('locator', parent=out_tfm)
        for i, time in enumerate(times):
            x = world_point_values[(i * 3) + 0]
            y = world_point_values[(i * 3) + 1]
            z = world_point_values[(i * 3) + 2]
            maya.cmds.setKeyframe(out_tfm, attribute='tx', value=x, time=time)
            maya.cmds.setKeyframe(out_tfm, attribute='ty', value=y, time=time)
            maya.cmds.setKeyframe(out_tfm, attribute='tz', value=z, time=time)
        # Ensure it's the same (with-in a small margin of error)
        for i, time in enumerate(times):
            x = world_point_values[(i * 3) + 0]
            y = world_point_values[(i * 3) + 1]
            z = world_point_values[(i * 3) + 2]
            assert self.approx_equal(x, pnt_x), 'X a=%r b=%r' % (x, pnt_x)
            assert self.approx_equal(y, pnt_y), 'Y a=%r b=%r' % (y, pnt_y)
            assert self.approx_equal(z, pnt_z), 'Z a=%r b=%r' % (z, pnt_z)

        # save the output
        path = self.get_data_path('reprojection_cmd_test_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
