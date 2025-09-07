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
Test the mmReprojection command for correctness.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestReprojectionNode(solverUtils.SolverTestCase):
    @staticmethod
    def compare_explicit_world_point(
        name, in_tfm, cam_tfm, cam_shp, pnt_x, pnt_y, pnt_z, times, **kwargs
    ):
        values = maya.cmds.mmReprojection(
            in_tfm, camera=(cam_tfm, cam_shp), time=times, **kwargs
        )
        print(name, repr(values))
        values_b = maya.cmds.mmReprojection(
            worldPoint=(pnt_x, pnt_y, pnt_z),
            camera=(cam_tfm, cam_shp),
            time=times,
            **kwargs
        )
        print(str(name + '_b'), repr(values_b))
        return values, values_b

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
        maya.cmds.createNode('locator', parent=in_tfm)

        pnt_x = -0.5
        pnt_y = 2.7
        pnt_z = 0.0
        maya.cmds.setAttr(in_tfm + '.translateX', pnt_x)
        maya.cmds.setAttr(in_tfm + '.translateY', pnt_y)
        maya.cmds.setAttr(in_tfm + '.translateZ', pnt_z)

        # save the scene
        path = self.get_output_path('reprojection_cmd_test_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Test the different flags with using a named transform
        # directly, or a single world point (XYZ) argument.
        test_args = [
            ('coord_values', {'asCoordinate': True}),
            (
                'pix_coord_values',
                {'imageResolution': (512, 512), 'asPixelCoordinate': True},
            ),
            ('norm_coord_values', {'asNormalizedCoordinate': True}),
            ('marker_coord_values', {'asMarkerCoordinate': True}),
            ('camera_point_values', {'asCameraPoint': True}),
            ('camera_dir_ratio_values', {'withCameraDirectionRatio': True}),
        ]
        times = (1001.0, 1002.0, 1003.0, 1004.0, 1005.0)
        for name, kwargs in test_args:
            values, values_b = self.compare_explicit_world_point(
                name, in_tfm, cam_tfm, cam_shp, pnt_x, pnt_y, pnt_z, times, **kwargs
            )
            self.assertGreater(len(values), 0)
            self.assertListEqual(values, values_b)

        # Test World Values
        name = 'world_point_values'
        world_point_values, world_point_values_b = self.compare_explicit_world_point(
            name,
            in_tfm,
            cam_tfm,
            cam_shp,
            pnt_x,
            pnt_y,
            pnt_z,
            times,
            asWorldPoint=True,
        )
        self.assertGreater(len(world_point_values), 0)
        self.assertListEqual(world_point_values, world_point_values_b)

        times = (
            1001.0,
            1002.0,
            1003.0,
            1004.0,
            1005.0,
        )
        out_tfm = maya.cmds.createNode('transform', name='OUTPUT')
        maya.cmds.createNode('locator', parent=out_tfm)
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
            self.assertApproxEqual(x, pnt_x), 'X a=%r b=%r' % (x, pnt_x)
            self.assertApproxEqual(y, pnt_y), 'Y a=%r b=%r' % (y, pnt_y)
            self.assertApproxEqual(z, pnt_z), 'Z a=%r b=%r' % (z, pnt_z)

        # save the output
        path = self.get_output_path('reprojection_cmd_test_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
