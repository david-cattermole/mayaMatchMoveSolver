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
Test a multi-frame bundle solve, with the bundle very, very far away from the camera.
"""

import os
import math
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver9(solverUtils.SolverTestCase):

    def test_init(self):
        """
        Solve an animated bundle across time.
        """
        start = 1
        end = 2

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

        marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
        maya.cmds.setAttr(marker_tfm + '.tx', 0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        # Bundle is created very, very far away from camera.
        bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)

        depth_list = [
            # These depths solve correctly.
            0.0,
            -10.0,
            -100.0,
            -1000.0,
            -10000.0,

            # These depths produce errors.
            -100000.0,
            -1000000.0,
            -10000000.0,
            -100000000.0,
        ]
        for d in depth_list:
            print 'Solve Depth: %r' % d
            maya.cmds.cutKey(bundle_tfm, cl=True, t=(), f=(), at='tx')
            maya.cmds.cutKey(bundle_tfm, cl=True, t=(), f=(), at='ty')
            maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
            maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
            maya.cmds.setAttr(bundle_tfm + '.tz', d)

            # Ensure the far-clip-plane is large enough to see the bundle.
            if d > 0:
                maya.cmds.setAttr(cam_shp + '.farClipPlane', d * 1.1)

            cameras = (
                (cam_tfm, cam_shp),
            )
            markers = (
                (marker_tfm, cam_shp, bundle_tfm),
            )
            # NOTE: All dynamic attributes must have a keyframe before
            # starting to solve.
            node_attrs = [
                (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
                (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
            ]

            # Run solver!
            s = time.time()
            frames = []
            for f in range(start, end+1):
                # Default values for the solver should get us a good solve.
                result = maya.cmds.mmSolver(
                    camera=cameras,
                    marker=markers,
                    attr=node_attrs,
                    frame=[f],
                    verbose=True,
                )
                # Ensure the values are correct
                self.assertEqual(result[0], 'success=1')
                # # Stopped by low error
                # self.assertEqual(result[2], 'reason_num=6')
            e = time.time()
            print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test9_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()
