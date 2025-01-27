# Copyright (C) 2019 David Cattermole.
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
Tests printing statistics from the 'mmSolver' command using the
'printStatistics' flag.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.api as mmapi
import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolverPrintStatistics(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        bundle_tfm, bundle_shp = self.create_bundle('bundle')
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

        bundleUnadjustable_tfm, bundleUnadjustable_shp = self.create_bundle(
            'bundleUnadjustable'
        )
        maya.cmds.setAttr(bundleUnadjustable_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundleUnadjustable_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundleUnadjustable_tfm + '.tz', -25.0)

        # This bundle is not affected by any marker.
        bundleUnused_tfm, bundleUnused_shp = self.create_bundle('bundleUnused')

        marker_tfm, marker_shp = self.create_marker(
            'marker', cam_tfm, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        # This marker is not affected by any marker.
        markerUnused_tfm, markerUnused_shp = self.create_marker('markerUnused', cam_tfm)
        maya.cmds.setAttr(markerUnused_tfm + '.tx', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.ty', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.tz', -10)

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
            (markerUnused_tfm, cam_shp, bundleUnadjustable_tfm),
        )
        node_attrs = [
            (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
            (bundleUnused_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (bundleUnused_tfm + '.ty', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            1,
        ]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Print Statistics
        result = maya.cmds.mmSolver(
            frame=frames,
            solverType=solver_index,
            verbose=True,
            printStatistics=(
                'inputs',
                'affects',
                'usedSolveObjects',
                'deviation',
            ),
            **kwargs
        )
        num_params = result[0]
        num_errors = result[1]
        print('result:', result)
        self.assertEqual(num_params, 'numberOfParameters=2')
        self.assertEqual(num_errors, 'numberOfErrors=2')

        # Ensure all unused markers/bundles are found.
        affects_results = [
            x for x in result if x.startswith('marker_affects_attribute=')
        ]
        print('affects result:', affects_results)
        for res in affects_results:
            self.assertGreater(len(res), 0)
            if 'Unused' in res:
                self.assertTrue(res.endswith('#0'))
            else:
                self.assertTrue(res.endswith('#1'))

        def _parse_usage_list(key, input_results):
            split_char = '#'
            results_list = [x for x in input_results if x.startswith(key)]
            results_list = [x.partition(key)[-1] for x in results_list]
            results_list = split_char.join(results_list)
            results_list = results_list.split(split_char)
            results_list = [x for x in results_list if len(x) > 0]
            return results_list

        markers_used = _parse_usage_list('markers_used=', result)
        print('markers_used:', markers_used)
        self.assertEqual(len(markers_used), 1)

        markers_unused = _parse_usage_list('markers_unused=', result)
        print('markers_unused:', markers_unused)
        self.assertEqual(len(markers_unused), 1)

        attributes_used = _parse_usage_list('attributes_used=', result)
        print('attributes_used:', attributes_used)
        self.assertEqual(len(attributes_used), 2)

        attributes_unused = _parse_usage_list('attributes_unused=', result)
        print('attributes_unused:', attributes_unused)
        self.assertEqual(len(attributes_unused), 2)
        return

    def test_init_ceres_lmder(self):
        self.do_solve('ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER)

    def test_init_ceres_lmdif(self):
        self.do_solve('ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER)


if __name__ == '__main__':
    prog = unittest.main()
