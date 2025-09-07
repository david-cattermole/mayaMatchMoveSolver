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
Test we can use the mmSolver to perform a triangulation technique.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

import maya.cmds

import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestTriangulation(solverUtils.SolverTestCase):
    def test_triangulation(self):
        start = 1
        end = 10

        # Camera
        cam_tfm, cam_shp = self.create_camera('camera')
        maya.cmds.setAttr(cam_tfm + '.translateY', 2.0)
        maya.cmds.setAttr(cam_tfm + '.translateZ', 5)
        maya.cmds.setAttr(cam_tfm + '.rotateX', 10.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='translateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='translateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=0.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=20.0)

        # Reprojection node
        node = maya.cmds.createNode('mmReprojection')

        # Connect camera attributes
        maya.cmds.connectAttr(cam_tfm + '.worldMatrix', node + '.cameraWorldMatrix')
        maya.cmds.connectAttr(cam_shp + '.focalLength', node + '.focalLength')
        maya.cmds.connectAttr(cam_shp + '.cameraAperture', node + '.cameraAperture')
        maya.cmds.connectAttr(cam_shp + '.filmOffset', node + '.filmOffset')
        maya.cmds.connectAttr(cam_shp + '.filmFit', node + '.filmFit')
        maya.cmds.connectAttr(cam_shp + '.nearClipPlane', node + '.nearClipPlane')
        maya.cmds.connectAttr(cam_shp + '.farClipPlane', node + '.farClipPlane')
        maya.cmds.connectAttr(cam_shp + '.cameraScale', node + '.cameraScale')

        # Set fake image resolution, to maintain aspect ratio of
        # projection matrix.
        fb_width = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture')
        fb_height = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture')
        maya.cmds.setAttr(node + '.imageWidth', fb_width * 10000.0)
        maya.cmds.setAttr(node + '.imageHeight', fb_height * 10000.0)

        # Get projected point.
        maya.cmds.setAttr(node + '.depthScale', 1.0)

        # Bundle (with aim transform)
        aim_tfm = maya.cmds.createNode('transform', name='aimAt_tfm')
        bundle_tfm, bundle_shp = self.create_bundle('bundle', parent=aim_tfm)

        # Marker
        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_tfm, marker_shp = self.create_marker(
            'marker', mkr_grp, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tz', -1)
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateX', time=start, value=-0.243056042
        )
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateX', time=end, value=-0.048611208
        )

        # Connect transform and calculate reprojected world point.
        maya.cmds.connectAttr(
            marker_tfm + '.worldMatrix', node + '.transformWorldMatrix'
        )
        point = maya.cmds.getAttr(node + '.outWorldPoint')[0]
        maya.cmds.setAttr(aim_tfm + '.translateX', point[0])
        maya.cmds.setAttr(aim_tfm + '.translateY', point[1])
        maya.cmds.setAttr(aim_tfm + '.translateZ', point[2])

        # Aim the bundle at the camera.
        maya.cmds.currentTime(start, edit=True)
        aim_const = maya.cmds.aimConstraint(
            cam_tfm,
            aim_tfm,
            offset=(0, 0, 0),
            weight=1.0,
            aimVector=(1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType='vector',
            worldUpVector=(0, 1, 0),
        )
        if maya.cmds.objExists(aim_const[0]):
            maya.cmds.delete(aim_const[0])

        # Give the bundle an initial good depth position to start with.
        maya.cmds.setAttr(bundle_tfm + '.tx', -1.0)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
        # NOTE: All dynamic attributes must have a keyframe before
        # starting to solve.
        node_attrs = [
            (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
        ]
        frames = []
        for f in range(start, end + 1):
            frames.append(f)

        # Save before we run.
        path = self.get_output_path('solver_triangulation_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(
            affects_mode,
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
        )

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
            iterations=10,
            verbose=True,
        )
        e = time.time()
        print('total time:', e - s)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

        # Save after the run.
        path = self.get_output_path('solver_triangulation_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
