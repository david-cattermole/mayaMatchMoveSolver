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
Testing marker 'weight' attribute.
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
class TestSolverMarkerWeight(solverUtils.SolverTestCase):
    def create_scene(self, w1, w2):
        """
        Create a test scene; 2 markers, 1 camera and two bundles under a single group.

        markers will have weights; w1 and w2.
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
        maya.cmds.setAttr(marker_01_tfm + '.weight', w1)

        marker_02_tfm, marker_02_shp = self.create_marker(
            'marker_02', mkr_grp, bnd_tfm=bundle_02_tfm
        )
        maya.cmds.setAttr(marker_02_tfm + '.tx', 0.243056042)
        maya.cmds.setAttr(marker_02_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_02_tfm + '.tz', -1.0)
        maya.cmds.setAttr(marker_02_tfm + '.weight', w2)
        return (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        )

    def test_single_frame_high_weight(self):
        """
        Test 2 markers;
         - marker 01; weight=100.0
         - marker 02; weight=1.0
        """
        w1 = 100.0
        w2 = 1.0
        nodes = self.create_scene(w1, w2)
        # tuple unpack all the node names
        (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        ) = nodes

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
        path = self.get_output_path(
            'solver_marker_weight_staticframe_highweight_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        tx = maya.cmds.getAttr(grp + '.tx')
        ty = maya.cmds.getAttr(grp + '.ty')
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(tx, -2.2252424)
        self.assertApproxEqual(ty, 1.65000000)

    def test_single_frame_low_weight(self):
        """
        Test 2 markers;
         - marker 01; weight=1.0
         - marker 02; weight=0.01
        """
        w1 = 1.0
        w2 = 0.01
        nodes = self.create_scene(w1, w2)
        # tuple unpack all the node names
        (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        ) = nodes

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
        path = self.get_output_path('solver_marker_weight_staticframe_lowweight_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        tx = maya.cmds.getAttr(grp + '.tx')
        ty = maya.cmds.getAttr(grp + '.ty')
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(tx, -2.2252424)
        self.assertApproxEqual(ty, 1.65000000)

    def test_single_frame_ratio_weight(self):
        """
        Test 2 markers;
         - marker 01; weight=100.0
         - marker 02; weight=50.0
        """
        w1 = 100.0
        w2 = 50.0
        nodes = self.create_scene(w1, w2)
        # tuple unpack all the node names
        (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        ) = nodes
        maya.cmds.setAttr(cam_tfm + '.tx', 0.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 0.0)
        maya.cmds.setAttr(cam_tfm + '.tz', 0.0)

        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.097222417)
        maya.cmds.setAttr(marker_02_tfm + '.tx', 0.097222417)

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
        path = self.get_output_path(
            'solver_marker_weight_staticframe_ratioweight_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        tx = maya.cmds.getAttr(grp + '.tx')
        ty = maya.cmds.getAttr(grp + '.ty')
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(tx, -0.333333333333)
        self.assertApproxEqual(ty, 1.300000000000)

    def test_single_frame_same_weight(self):
        """
        Test 2 markers;
         - marker 01; weight=0.5
         - marker 02; weight=0.5
        """
        w1 = 0.5
        w2 = 0.5
        nodes = self.create_scene(w1, w2)
        # tuple unpack all the node names
        (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        ) = nodes

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
        path = self.get_output_path(
            'solver_marker_weight_staticframe_sameweight_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        tx = maya.cmds.getAttr(grp + '.tx')
        ty = maya.cmds.getAttr(grp + '.ty')
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(tx, -1.00000134)
        self.assertApproxEqual(ty, 1.65000055)

    def test_single_frame_no_weight(self):
        """
        Test 2 markers;
         - marker 01; weight=1.0
         - marker 02; weight=0.0

        marker 02 is expected to be treated as if it were disabled.
        """
        w1 = 1.0
        w2 = 0.0
        nodes = self.create_scene(w1, w2)
        # tuple unpack all the node names
        (
            cam_tfm,
            cam_shp,
            marker_01_tfm,
            marker_02_tfm,
            bundle_01_tfm,
            bundle_02_tfm,
            grp,
        ) = nodes

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
        path = self.get_output_path('solver_marker_weight_staticframe_noweight_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        tx = maya.cmds.getAttr(grp + '.tx')
        ty = maya.cmds.getAttr(grp + '.ty')
        self.assertEqual(result[0], 'success=1')
        self.assertApproxEqual(tx, -2.25, eps=0.001)
        self.assertApproxEqual(ty, 1.65, eps=0.001)


if __name__ == '__main__':
    prog = unittest.main()
