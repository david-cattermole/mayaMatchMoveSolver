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
Testing marker min/max attribute (box constraints).
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
class TestSolverMinMaxValues(solverUtils.SolverTestCase):
    def test_single_frame(self):
        """
        Test 2 markers, one enabled, one disabled; only the "enabled"
        marker should be "used" by the solver.
        """
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', 10.0)

        # Create a group, and add both bundles underneath.
        bundle_01_tfm, bundle_01_shp = self.create_bundle('bundle_01')

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_01_tfm, marker_01_shp = self.create_marker(
            'marker_01', mkr_grp, bnd_tfm=bundle_01_tfm
        )
        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.486112083)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_01_tfm, cam_shp, bundle_01_tfm),)
        node_attrs = [
            (bundle_01_tfm + '.tx', '-5.0', '5.0', 'None', 'None'),
            (bundle_01_tfm + '.ty', 'None', 'None', 'None', 'None'),
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
        path = self.get_output_path('solver_min_max_values_staticframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        tx = maya.cmds.getAttr(bundle_01_tfm + '.tx')
        ty = maya.cmds.getAttr(bundle_01_tfm + '.ty')
        self.assertApproxEqual(tx, -5.0)
        self.assertApproxEqual(ty, 2.3)

    def test_single_frame_lower_bound_only(self):
        """
        Test 2 markers, one enabled, one disabled; only the "enabled"
        marker should be "used" by the solver.

        Only set the lower bound.
        """
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', 10.0)

        # Create a group, and add both bundles underneath.
        bundle_01_tfm, bundle_01_shp = self.create_bundle('bundle_01')

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_01_tfm, marker_01_shp = self.create_marker(
            'marker_01', mkr_grp, bnd_tfm=bundle_01_tfm
        )
        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.486112083)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_01_tfm, cam_shp, bundle_01_tfm),)
        node_attrs = [
            (bundle_01_tfm + '.tx', '-5.0', 'None', 'None', 'None'),
            (bundle_01_tfm + '.ty', 'None', 'None', 'None', 'None'),
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
        path = self.get_output_path(
            'solver_min_max_values_staticframe_lower_bound_only_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        tx = maya.cmds.getAttr(bundle_01_tfm + '.tx')
        ty = maya.cmds.getAttr(bundle_01_tfm + '.ty')
        self.assertApproxEqual(tx, -5.0)
        self.assertApproxEqual(ty, 2.3)

    def test_single_frame_upper_bound_only(self):
        """
        Test 2 attributes; one is upper bounded, the other with no bounds.
        """
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', 10.0)

        # Create a group, and add both bundles underneath.
        bundle_01_tfm, bundle_01_shp = self.create_bundle('bundle_01')

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_01_tfm, marker_01_shp = self.create_marker(
            'marker_01', mkr_grp, bnd_tfm=bundle_01_tfm
        )
        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.486112083)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_01_tfm, cam_shp, bundle_01_tfm),)
        node_attrs = [
            (bundle_01_tfm + '.tx', 'None', '5.0', 'None', 'None'),
            (bundle_01_tfm + '.ty', 'None', 'None', 'None', 'None'),
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
        path = self.get_output_path(
            'solver_min_max_values_staticframe_upper_bound_only_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        tx = maya.cmds.getAttr(bundle_01_tfm + '.tx')
        ty = maya.cmds.getAttr(bundle_01_tfm + '.ty')
        self.assertApproxEqual(tx, -6.0)
        self.assertApproxEqual(ty, 2.3)


if __name__ == '__main__':
    prog = unittest.main()
