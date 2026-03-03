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
Shared utilities for Camera Solver integration tests.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tempfile
import shutil
import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.api as mmapi
import mmSolver.utils.time as time_utils

import mmSolver.tools.camerasolver.lib as camerasolver_lib
import mmSolver.tools.camerasolver.constant as camerasolver_const
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read

import test.baseutils as baseUtils

# Maya stores film aperture in inches; camera intrinsics are specified in mm.
_INCHES_TO_MM = 25.4


def frame_range_from_mkr_data_list(mkr_data_list):
    start = int(999999)
    end = int(-999999)
    for mkr_data in mkr_data_list:
        x_keys = mkr_data.get_x()
        s = x_keys.get_start_frame()
        e = x_keys.get_end_frame()
        if s is not None and s < start:
            start = s
        if e is not None and e > end:
            end = e
    return start, end


def load_markers_from_uv_file(uv_file_path, cam):
    """
    Returns (mkr_list, frame_range).
    """
    _file_info, mkr_data_list = marker_read.read(uv_file_path)

    start_frame, end_frame = frame_range_from_mkr_data_list(mkr_data_list)
    frame_range = time_utils.FrameRange(start=start_frame, end=end_frame)

    mkr_grp = mmapi.MarkerGroup().create_node(name='markerGroup1', cam=cam)
    mkr_list = marker_read.create_nodes(
        mkr_data_list,
        cam=cam,
        mkr_grp=mkr_grp,
        with_bundles=True,
        load_bundle_position=False,
    )
    return mkr_list, frame_range


class CameraSolverTestCase(baseUtils.TestBase):
    def setUp(self):
        maya.cmds.file(new=True, force=True)
        self.reload_solver()
        self._output_dir = tempfile.mkdtemp(prefix='mmcamerasolve_test_')
        super(CameraSolverTestCase, self).setUp()

    def tearDown(self):
        shutil.rmtree(self._output_dir, ignore_errors=True)
        super(CameraSolverTestCase, self).tearDown()

    def _skip_if_no_executable(self):
        if camerasolver_lib.find_executable_file_path() is None:
            raise unittest.SkipTest(
                'mmcamerasolve executable not found; '
                'set %s environment variable.'
                % camerasolver_const.MMSOLVER_LOCATION_ENV_VAR_NAME
            )

    def _skip_if_no_file(self, file_path):
        if not os.path.isfile(file_path):
            raise unittest.SkipTest('Test data file not found: %r' % file_path)

    def make_camera(
        self, name, focal_length_mm, film_back_width_mm, film_back_height_mm
    ):
        cam_tfm = maya.cmds.createNode('transform', name=name + '_tfm')
        cam_shp = maya.cmds.createNode('camera', name=name + '_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_shp + '.focalLength', focal_length_mm)
        maya.cmds.setAttr(
            cam_shp + '.horizontalFilmAperture',
            film_back_width_mm / _INCHES_TO_MM,
        )
        maya.cmds.setAttr(
            cam_shp + '.verticalFilmAperture',
            film_back_height_mm / _INCHES_TO_MM,
        )
        return mmapi.Camera(transform=cam_tfm, shape=cam_shp)

    def load_markers(self, uv_file_path, cam):
        return load_markers_from_uv_file(uv_file_path, cam)

    def launch_solve(
        self,
        cam,
        lens,
        mkr_list,
        frame_range,
        adjustment_solver,
        adjustment_attrs,
        log_level,
        prefix_name,
        output_dir,
    ):
        """Wrapper around camerasolver_lib.launch_solve that saves the Maya
        scene before and after the solve."""
        path = self.get_output_path('test_camerasolver_%s_before.ma' % prefix_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        returncode, stdout, stderr = camerasolver_lib.launch_solve(
            cam=cam,
            lens=lens,
            mkr_list=mkr_list,
            frame_range=frame_range,
            adjustment_solver=adjustment_solver,
            adjustment_attrs=adjustment_attrs,
            log_level=log_level,
            prefix_name=prefix_name,
            output_dir=output_dir,
        )

        path = self.get_output_path('test_camerasolver_%s_after.ma' % prefix_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        return returncode, stdout, stderr

    def make_default_solver(self):
        adj_solver = camerasolver_lib.AdjustmentSolver()
        adj_attrs = camerasolver_lib.AdjustmentAttributes()
        return adj_solver, adj_attrs

    def make_evolution_refine_solver(self):
        adj_solver = camerasolver_lib.AdjustmentSolver()
        adj_solver.set_adjustment_solver_type(
            camerasolver_const.ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE
        )
        adj_attrs = camerasolver_lib.AdjustmentAttributes()
        return adj_solver, adj_attrs

    def make_focal_length_solver(
        self,
        solver_type,
        focal_min=0.1,
        focal_max=120.0,
        sample_count=8,
    ):
        adj_solver = camerasolver_lib.AdjustmentSolver()
        adj_solver.set_adjustment_solver_type(solver_type)
        adj_attrs = camerasolver_lib.AdjustmentAttributes()
        adj_attrs.set_attribute_bounds(
            camerasolver_const.ATTR_CAMERA_FOCAL_LENGTH,
            float(focal_min),
            float(focal_max),
        )
        adj_attrs.set_attribute_sample_count(
            camerasolver_const.ATTR_CAMERA_FOCAL_LENGTH, sample_count
        )
        return adj_solver, adj_attrs
