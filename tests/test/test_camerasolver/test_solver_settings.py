# Copyright (C) 2026 David Cattermole.
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
Camera solver tests for the adjustment solver / .mmsettings feature.

Mirrors test.bash tests 9 and 10.  The .mmsettings file is always
generated from the AdjustmentSolver and AdjustmentAttributes objects,
so both tests configure those objects to match the reference files in
tests/data/mmsettings/.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import mmSolver.tools.camerasolver.constant as camerasolver_const

import test.test_camerasolver.camerasolverutils as camerasolverutils


# @unittest.skip
class TestSolverSettingsFile(camerasolverutils.CameraSolverTestCase):
    """
    Uses the `solver_settings.mmsettings` file.

    Configures evolution_refine with the same focal-length bounds as the
    reference file: value_min=0.1, value_max=120.0, sample_count=8.
    """

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='stA_settings_cam',
            focal_length_mm=50.0,
            film_back_width_mm=36.0,
            film_back_height_mm=24.0,
        )
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_focal_length_solver(
            solver_type=camerasolver_const.ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE,
            focal_min=0.1,
            focal_max=120.0,
            sample_count=8,
        )

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='stA_settings',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestSolverSettingsDisableValueRangeEstimate(
    camerasolverutils.CameraSolverTestCase
):
    """
    Uses `evolution_disable_value_range_estimate.mmsettings` to
    override setting values.

    NOTE: AdjustmentSolver.set_evolution_value_range_estimate currently
    asserts value > 0, so disabling the estimate (False) is not yet
    possible through the API.  This test exercises the evolution_refine
    path with the default behaviour (estimate enabled) as a placeholder.

    """

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='stA_disable_vr_cam',
            focal_length_mm=50.0,
            film_back_width_mm=36.0,
            film_back_height_mm=24.0,
        )
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_focal_length_solver(
            solver_type=camerasolver_const.ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE,
        )

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='stA_disable_vr',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


if __name__ == '__main__':
    prog = unittest.main()
