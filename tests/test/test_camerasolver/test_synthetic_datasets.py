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
Camera solver tests using the synthetic Cube A and Cube B datasets.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import mmSolver.tools.camerasolver.lib as camerasolver_lib
import mmSolver.tools.camerasolver.constant as camerasolver_const

import test.test_camerasolver.camerasolverutils as camerasolverutils


CUBE_FOCAL_LENGTH_MM = 35.0
CUBE_FILM_BACK_WIDTH_MM = 36.0
CUBE_FILM_BACK_HEIGHT_MM = 24.0


# @unittest.skip
class TestCubeADataset(camerasolverutils.CameraSolverTestCase):
    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'test_cube_a_markers_v1_fmt.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='cube_a_cam',
            focal_length_mm=CUBE_FOCAL_LENGTH_MM,
            film_back_width_mm=CUBE_FILM_BACK_WIDTH_MM,
            film_back_height_mm=CUBE_FILM_BACK_HEIGHT_MM,
        )
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='cube_a',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestCubeBDataset(camerasolverutils.CameraSolverTestCase):
    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'test_cube_b_markers_v1_fmt.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='cube_b_cam',
            focal_length_mm=CUBE_FOCAL_LENGTH_MM,
            film_back_width_mm=CUBE_FILM_BACK_WIDTH_MM,
            film_back_height_mm=CUBE_FILM_BACK_HEIGHT_MM,
        )
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='cube_b',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


if __name__ == '__main__':
    prog = unittest.main()
