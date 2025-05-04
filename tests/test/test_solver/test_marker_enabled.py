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
Testing marker 'enabled' attribute.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
class TestSolverMarkerEnabled(solverUtils.SolverTestCase):
    def test_single_frame(self):
        """
        Test 2 markers, one enabled, one disabled; only the "enabled"
        marker should be "used" by the solver.
        """
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Create a group, and add both bundles underneath.
        grp = maya.cmds.createNode('transform', name='group1')
        bundle_01_tfm, bundle_01_shp = self.create_bundle('bundle_01', parent=grp)
        bundle_02_tfm, bundle_02_shp = self.create_bundle('bundle_02', parent=grp)
        maya.cmds.setAttr(grp + '.tz', -10)

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_01_tfm, marker_01_shp = self.create_marker(
            'marker_01', mkr_grp, bnd_tfm=bundle_01_tfm
        )
        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.243056042)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1.0)

        # disable this marker
        marker_02_tfm, marker_02_shp = self.create_marker(
            'marker_02', mkr_grp, bnd_tfm=bundle_02_tfm
        )
        maya.cmds.setAttr(marker_02_tfm + '.tx', 0.243056042)
        maya.cmds.setAttr(marker_02_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_02_tfm + '.tz', -1.0)
        maya.cmds.setAttr(marker_02_tfm + '.enable', 0)

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_01_tfm, cam_shp, bundle_01_tfm),
            (marker_02_tfm, cam_shp, bundle_02_tfm),
        )
        node_attrs = [
            (grp + '.tx', 'None', 'None', 'None', 'None'),
            (grp + '.ty', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            1,
        ]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(verbose=True, **kwargs)
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = self.get_data_path('solver_marker_enabled_staticframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(maya.cmds.getAttr(grp + '.tx'), -2.24999755)
        self.assertApproxEqual(maya.cmds.getAttr(grp + '.ty'), 1.65000644)

    def test_multi_frame(self):
        """
        Solve with different marker enabled values, animated across time.
        """
        start = 1
        mid = 5
        end = 10

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-5.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=5.5)

        # Create a group, and add both bundles underneath.
        grp = maya.cmds.createNode('transform', name='group1')
        bundle_01_tfm, bundle_01_shp = self.create_bundle('bundle_01', parent=grp)
        bundle_02_tfm, bundle_02_shp = self.create_bundle('bundle_02', parent=grp)
        maya.cmds.setAttr(grp + '.tz', -10)
        # TODO: Make sure to set tangents to auto, in case the Maya
        #  user contains preferences to change this behaviour.
        maya.cmds.setKeyframe(grp, attribute='translateX', time=start, value=0)
        maya.cmds.setKeyframe(grp, attribute='translateY', time=start, value=0)

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_01_tfm, marker_01_shp = self.create_marker(
            'marker_01', mkr_grp, bnd_tfm=bundle_01_tfm
        )
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1.0)
        maya.cmds.setKeyframe(
            marker_01_tfm, attribute='translateX', time=start, value=-0.243056042
        )
        maya.cmds.setKeyframe(
            marker_01_tfm, attribute='translateX', time=end, value=-0.29166725
        )
        maya.cmds.setKeyframe(
            marker_01_tfm, attribute='translateY', time=start, value=0.218750438
        )
        maya.cmds.setKeyframe(
            marker_01_tfm, attribute='translateY', time=end, value=0.189583713
        )

        # disable this marker
        marker_02_tfm, marker_02_shp = self.create_marker(
            'marker_02', mkr_grp, bnd_tfm=bundle_02_tfm
        )
        maya.cmds.setAttr(marker_02_tfm + '.tz', -1.0)
        maya.cmds.setKeyframe(
            marker_02_tfm, attribute='translateX', time=start, value=0.243056042
        )
        maya.cmds.setKeyframe(
            marker_02_tfm, attribute='translateX', time=end, value=0.29166725
        )
        maya.cmds.setKeyframe(
            marker_02_tfm, attribute='translateY', time=start, value=0.218750438
        )
        maya.cmds.setKeyframe(
            marker_02_tfm, attribute='translateY', time=end, value=0.189583713
        )
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=start, value=1)
        maya.cmds.setKeyframe(
            marker_02_tfm, attribute='enable', time=start + 1, value=0
        )
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=mid, value=0)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=end - 1, value=0)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=end, value=1)

        maya.cmds.keyTangent(
            marker_02_tfm,
            attribute='enable',
            inTangentType='linear',
            outTangentType='step',
        )

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_01_tfm, cam_shp, bundle_01_tfm),
            (marker_02_tfm, cam_shp, bundle_02_tfm),
        )
        # NOTE: All dynamic attributes must have a keyframe before starting to solve.
        node_attrs = [
            (grp + '.tx', 'None', 'None', 'None', 'None'),
            (grp + '.ty', 'None', 'None', 'None', 'None'),
        ]

        all_frames = list(range(start, end + 1))

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, frame=all_frames, **kwargs)

        # Run solver, over each frame!
        #
        # Note: the start and end frames will take longer to solve,
        # because the error cannot be constrained. This is normal for
        # the test set up.
        results = []
        s = time.time()
        for f in all_frames:
            frames = [f]
            result = maya.cmds.mmSolver(frame=frames, verbose=True, **kwargs)
            results.append(result)
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = self.get_data_path('solver_marker_enabled_multiframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        for result in results:
            self.assertEqual(result[0], 'success=1')
        tx_start = maya.cmds.getAttr(grp + '.tx', time=start)
        tx_mid = maya.cmds.getAttr(grp + '.tx', time=mid)
        tx_end = maya.cmds.getAttr(grp + '.tx', time=end)
        ty_start = maya.cmds.getAttr(grp + '.ty', time=start)
        ty_mid = maya.cmds.getAttr(grp + '.ty', time=mid)
        ty_end = maya.cmds.getAttr(grp + '.ty', time=end)
        self.assertApproxEqual(tx_start, -0.51855463, eps=0.001)
        self.assertApproxEqual(tx_mid, -2.3022075714, eps=0.2)
        self.assertApproxEqual(tx_end, -1.48144697, eps=0.001)
        self.assertApproxEqual(ty_start, 1.30993172, eps=0.001)
        self.assertApproxEqual(ty_mid, 1.65431479258, eps=0.2)
        self.assertApproxEqual(ty_end, 2.10503952, eps=0.001)


if __name__ == '__main__':
    prog = unittest.main()
