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
Camera solver tests using real-world datasets.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import mmSolver.utils.time as time_utils
import mmSolver.tools.camerasolver.lib as camerasolver_lib
import mmSolver.tools.camerasolver.constant as camerasolver_const

import test.test_camerasolver.camerasolverutils as camerasolverutils


# @unittest.skip
class TestBlasterwalkDataset(camerasolverutils.CameraSolverTestCase):
    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path(
            'uvtrack', 'blasterwalk_camera_2dtracks_v1_format.uv'
        )
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='blasterwalk_cam',
            focal_length_mm=56.4,
            film_back_width_mm=36.0,
            film_back_height_mm=20.25,
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
            prefix_name='blasterwalk',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestHcwPaintingDataset(camerasolverutils.CameraSolverTestCase):
    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'hcw_painting_2dtracks_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='hcw_painting_cam',
            focal_length_mm=35.0,
            film_back_width_mm=36.0,
            film_back_height_mm=20.25,
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
            prefix_name='hcw_painting',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestOperaHouseDataset(camerasolverutils.CameraSolverTestCase):
    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'operahouse_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='operahouse_cam',
            focal_length_mm=91.0,
            film_back_width_mm=36.0,
            film_back_height_mm=27.0,
        )
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_evolution_refine_solver()

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='operahouse',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# TODO: This test takes a long time, so we skip it because it doesn't
# give us too much new test surface.
@unittest.skip
class TestGarageDataset(camerasolverutils.CameraSolverTestCase):
    """
    The garage UV file spans frames 1–2706.

    The frame range is set
    explicitly here rather than derived from the markers.
    """

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'garage_2dtracks_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='garage_cam',
            focal_length_mm=25.0,
            film_back_width_mm=36.0,
            film_back_height_mm=20.25,
        )
        mkr_list, _auto_frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        frame_range = time_utils.FrameRange(start=2000, end=2706)
        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='garage',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


if __name__ == '__main__':
    prog = unittest.main()
