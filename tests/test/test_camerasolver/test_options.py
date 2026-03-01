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
Camera solver tests for miscellaneous executable options.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import subprocess
import unittest

import mmSolver.utils.time as time_utils
import mmSolver.tools.camerasolver.lib as camerasolver_lib
import mmSolver.tools.camerasolver.constant as camerasolver_const

import test.test_camerasolver.camerasolverutils as camerasolverutils


CUBE_FOCAL_LENGTH_MM = 35.0
CUBE_FILM_BACK_WIDTH_MM = 36.0
CUBE_FILM_BACK_HEIGHT_MM = 24.0


def _run_executable(extra_args):
    """Run the executable directly (bypassing launch_solve) for flag-only tests."""
    exe = camerasolver_lib.find_executable_file_path()
    if exe is None:
        return (-1, '', '')
    proc = subprocess.Popen(
        [exe] + extra_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = proc.communicate()
    return (
        proc.returncode,
        stdout_bytes.decode('utf-8', errors='replace'),
        stderr_bytes.decode('utf-8', errors='replace'),
    )


# @unittest.skip
class TestExecutableHelp(camerasolverutils.CameraSolverTestCase):
    def test_help_flag(self):
        self._skip_if_no_executable()
        returncode, stdout, stderr = _run_executable(['--help'])
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)
        self.assertGreater(len(stdout + stderr), 0)


# @unittest.skip
class TestExecutableVersion(camerasolverutils.CameraSolverTestCase):
    def test_version_flag(self):
        self._skip_if_no_executable()
        returncode, stdout, stderr = _run_executable(['--version'])
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)
        self.assertGreater(len(stdout + stderr), 0)


# @unittest.skip
class TestFrameRangeOverride(camerasolverutils.CameraSolverTestCase):
    def test_solve_custom_frame_range(self):
        self._skip_if_no_executable()
        uv_file = self.get_data_path('uvtrack', 'test_cube_a_markers_v1_fmt.uv')
        self._skip_if_no_file(uv_file)

        cam = self.make_camera(
            name='frame_range_cam',
            focal_length_mm=CUBE_FOCAL_LENGTH_MM,
            film_back_width_mm=CUBE_FILM_BACK_WIDTH_MM,
            film_back_height_mm=CUBE_FILM_BACK_HEIGHT_MM,
        )
        mkr_list, _auto_frame_range = self.load_markers(uv_file, cam)
        self.assertGreater(len(mkr_list), 0)

        frame_range = time_utils.FrameRange(start=1, end=10)
        adj_solver, adj_attrs = self.make_evolution_refine_solver()

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=None,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adj_solver,
            adjustment_attrs=adj_attrs,
            log_level=camerasolver_const.LOG_LEVEL_INFO,
            prefix_name='frame_range',
            output_dir=self._output_dir,
        )
        print('returncode:', returncode)
        print('stdout:', stdout)
        print('stderr:', stderr)
        self.assertEqual(returncode, 0)


if __name__ == '__main__':
    prog = unittest.main()
