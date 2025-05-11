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


def _parse_usage_list(key, input_results):
    split_char = '#'
    results_list = [x for x in input_results if x.startswith(key)]
    results_list = [x.partition(key)[-1] for x in results_list]
    results_list = split_char.join(results_list)
    results_list = results_list.split(split_char)
    results_list = [x for x in results_list if len(x) > 0]
    return results_list


# @unittest.skip
class TestSolverPrintStatistics(solverUtils.SolverTestCase):
    def _check_result(self, result):
        num_params = result[0]
        num_errors = result[1]
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

        markers_used = _parse_usage_list('markers_used=', result)
        attributes_used = _parse_usage_list('attributes_used=', result)
        print('markers_used:', markers_used)
        print('attributes_used:', attributes_used)
        self.assertEqual(len(markers_used), 1)
        self.assertEqual(len(attributes_used), 2)
        return

    def _run_solve(self, cameras, markers, node_attrs, frames, solver_index):
        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Print Statistics, no real solving.
        result = maya.cmds.mmSolver(
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
        print('result:', result)
        return result

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

        # This bundle is not affected by any marker.
        bundleUnused_tfm, bundleUnused_shp = self.create_bundle('bundleUnused')

        marker_tfm, marker_shp = self.create_marker(
            'marker', cam_tfm, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        # This marker does not affect the bundle - they are not "connected".
        #
        # NOTE: Even if markers and bundles are not physically
        # connected in the Maya DAG, as long as they are passed to
        # mmSolver together in the same tuple, they are considered
        # connected, in terms of solving.
        markerUnused_tfm, markerUnused_shp = self.create_marker(
            'markerUnused', cam_tfm, bnd_tfm=None
        )
        maya.cmds.setAttr(markerUnused_tfm + '.tx', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.ty', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.tz', -10)

        # save the input
        file_name = 'print_statistics_{}_before.ma'.format(solver_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # This solve does not use solve any attributes that are
        # affected by 'markerUnused_tfm' and 'bundleUnused_tfm' nodes.
        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
            (markerUnused_tfm, cam_shp, bundleUnused_tfm),
        )
        node_attrs = [
            (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            1,
        ]
        result_a = self._run_solve(cameras, markers, node_attrs, frames, solver_index)

        # This solve tries to solve attributes (from the
        # 'bundleUnused_tfm' node) that by cannot be affected by the
        # input marker/bundles.
        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
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
        result_b = self._run_solve(cameras, markers, node_attrs, frames, solver_index)

        # save the output
        file_name = 'print_statistics_{}_after.ma'.format(solver_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # An extra marker/bundle pair was given to the solver, which
        # was not used.
        self._check_result(result_a)
        markers_unused_a = _parse_usage_list('markers_unused=', result_a)
        attributes_unused_a = _parse_usage_list('attributes_unused=', result_a)
        print('markers_unused_a:', markers_unused_a)
        print('attributes_unused_a:', attributes_unused_a)
        self.assertEqual(len(markers_unused_a), 1)
        self.assertEqual(len(attributes_unused_a), 0)

        # Two extra attributes were given to the solver, and both
        # could not be used.
        self._check_result(result_b)
        markers_unused_b = _parse_usage_list('markers_unused=', result_b)
        attributes_unused_b = _parse_usage_list('attributes_unused=', result_b)
        print('markers_unused_b:', markers_unused_b)
        print('attributes_unused_b:', attributes_unused_b)
        self.assertEqual(len(markers_unused_b), 0)
        self.assertEqual(len(attributes_unused_b), 2)

        return

    def test_init_ceres_line_search_lbfgs_der(self):
        self.do_solve(
            'ceres_line_search_lbfgs_der', mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER
        )

    def test_init_ceres_lmder(self):
        self.do_solve('ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER)

    # def test_init_ceres_lmdif(self):
    #     self.do_solve('ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF)

    # def test_init_cminpack_lmdif(self):
    #     self.do_solve('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER)


if __name__ == '__main__':
    prog = unittest.main()
