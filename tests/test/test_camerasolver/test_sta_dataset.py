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
Camera solver tests using the stA real-world dataset.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import mmSolver.api as mmapi
import mmSolver.tools.camerasolver.constant as camerasolver_const

import test.test_camerasolver.camerasolverutils as camerasolverutils


# Intrinsics read from tests/data/mmcamera/stA_copyCamera.mmcamera.
STA_FOCAL_LENGTH_MM = 31.731
STA_FILM_BACK_WIDTH_MM = 28.066
STA_FILM_BACK_HEIGHT_MM = 18.672


def _make_sta_camera(test_case):
    return test_case.make_camera(
        name='stA_cam',
        focal_length_mm=STA_FOCAL_LENGTH_MM,
        film_back_width_mm=STA_FILM_BACK_WIDTH_MM,
        film_back_height_mm=STA_FILM_BACK_HEIGHT_MM,
    )


# @unittest.skip
class TestStAWithCameraFile(camerasolverutils.CameraSolverTestCase):
    """Using mmcamera file input."""

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = _make_sta_camera(self)
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='stA_mmcamera',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestStAWithNukeLens(camerasolverutils.CameraSolverTestCase):
    """Using nuke lens file."""

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_v1_format.uv')
        self._skip_if_no_file(uv_file)

        cam = _make_sta_camera(self)
        lens = mmapi.Lens().create_node(name='stA_lens')

        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=lens,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='stA_nuke_lens',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestStAWithLensUndistortionUV(camerasolverutils.CameraSolverTestCase):
    """UV Track v4 format with embedded lens data + lens file."""

    def test_solve(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_with_lens_undistortion.uv')
        self._skip_if_no_file(uv_file)

        cam = _make_sta_camera(self)
        lens = mmapi.Lens().create_node(name='stA_lens_undistort')

        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=lens,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='stA_undistort',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


# @unittest.skip
class TestStAWithLensUndistortionUVNoLens(camerasolverutils.CameraSolverTestCase):
    """
    UV Track v4 file without a lens file.

    The UV file contains embedded lens-undistortion data but no lens is
    provided, so the executable is expected to warn but still succeed.
    """

    def test_solve_warns_but_succeeds(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'stA_with_lens_undistortion.uv')
        self._skip_if_no_file(uv_file)

        cam = _make_sta_camera(self)
        mkr_list, frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        adj_solver, adj_attrs = self.make_default_solver()

        returncode, stdout, stderr = self.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_WARNING,
            prefix_name='stA_no_lens',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


if __name__ == '__main__':
    prog = unittest.main()
