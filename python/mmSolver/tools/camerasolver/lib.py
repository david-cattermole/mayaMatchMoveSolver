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
Library functions for Camera Solver.
"""

import os
import subprocess

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat

import mmSolver.tools.savemarkerfile.lib as savemarkerfile_lib
import mmSolver.tools.savelensfile.lib as savelensfile_lib

import mmSolver.tools.camerasolver.constant as const


LOG = mmSolver.logger.get_logger()


class AdjustmentSolver(object):
    def __init__(self):
        # TODO: Should the class have default values?
        self.__adjustment_solver_type = None
        self.__thread_count = None
        self.__evolution_value_range_estimate = None
        self.__evolution_generation_count = None
        self.__evolution_population_count = None

    def get_adjustment_solver_type(self):
        # type: (AdjustmentSolver) -> str | None
        return self.__adjustment_solver_type

    def set_adjustment_solver_type(self, value):
        assert value in const.ADJUSTMENT_SOLVER_TYPE_LIST
        self.__adjustment_solver_type = value

    def get_thread_count(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__thread_count

    def set_thread_count(self, value):
        assert isinstance(value, int)
        assert value > 0
        self.__thread_count = value

    def get_evolution_value_range_estimate(self):
        return self.__evolution_value_range_estimate

    def set_evolution_value_range_estimate(self, value):
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_value_range_estimate = value

    def get_evolution_generation_count(self):
        return self.__evolution_generation_count

    def set_evolution_generation_count(self, value):
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_generation_count = value

    def get_evolution_population_count(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__evolution_population_count

    def set_evolution_population_count(self, value):
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_population_count = value


class AdjustmentAttributes(object):
    def __init__(self):
        # adjustment_attributes
        # - name ('camera.focal_length_mm')
        # - value_min
        # - value_max
        # - sample_count
        self.__attribute_to_bounds = {}
        self.__attribute_to_sample_count = {}

    def get_attribute_bounds(self, attr_name):
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        return self.__attribute_to_bounds.get(attr_name)

    def set_attribute_bounds(self, attr_name, min_value, max_value):
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        assert isinstance(min_value, float)
        assert isinstance(max_value, float)
        self.__attribute_to_bounds[attr_name] = [min_value, max_value]

    def get_attribute_sample_count(self, attr_name):
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        return self.__attribute_to_sample_count.get(attr_name)

    def set_attribute_sample_count(self, attr_name, value):
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        assert isinstance(value, int)
        assert value > 0
        self.__attribute_to_sample_count[attr_name] = value


def construct_output_file_path(output_dir, file_prefix, file_suffix, file_ext):
    assert isinstance(output_dir, pycompat.TEXT_TYPE)
    assert isinstance(file_prefix, pycompat.TEXT_TYPE)
    assert isinstance(file_suffix, pycompat.TEXT_TYPE)
    assert isinstance(file_ext, pycompat.TEXT_TYPE)
    file_name = file_prefix + file_suffix + file_ext
    return os.path.join(output_dir, file_name)


def save_markers_to_file(mkr_list, frame_range, file_prefix, output_dir):
    """
    Save markers to disk.
    """
    data = savemarkerfile_lib.generate(mkr_list, frame_range)
    file_suffix = ''
    file_path = construct_output_file_path(output_dir, file_prefix, file_suffix, '.uv')
    savemarkerfile_lib.write_file(file_path, data)
    return file_path


def save_camera_to_file(cam, file_prefix, output_dir):
    """
    Save camera to disk.
    """
    # TODO: Implement this.
    file_suffix = ''
    file_path = construct_output_file_path(
        output_dir, file_prefix, file_suffix, '.mm camera'
    )
    return file_path


def save_nuke_lens_to_file(cam, lens, frame_range, file_prefix, output_dir):
    """
    Save nuke lens to disk.
    """
    file_suffix = ''
    data_list = savelensfile_lib.generate(cam, lens, frame_range)
    file_path = construct_output_file_path(output_dir, file_prefix, file_suffix, '.nk')
    savelensfile_lib.write_nuke_file(file_path, data_list)
    return file_path


def save_solver_settings_to_file(cam, file_prefix, output_dir):
    """
    Save Solver settings to disk.
    """
    # TODO: Implement this.
    file_suffix = ''
    file_path = construct_output_file_path(
        output_dir, file_prefix, file_suffix, '.mmsettings'
    )
    return file_path


def __find_executable_file_path():
    """
    Find the EXECUTABLE_FILE_NAME from the module directory.
    """
    # type: (...) -> str | None
    var_name = const.MMSOLVER_LOCATION_ENV_VAR_NAME
    module_location = os.environ[var_name]  # type: str
    assert os.path.isdir(module_location)
    executable_file_path = os.path.join(
        module_location, 'bin', const.EXECUTABLE_FILE_NAME
    )
    if not os.path.isfile(executable_file_path):
        return
    return executable_file_path


def launch_solve(
    cam,  # type: mmapi.Camera
    lens,  # type: mmapi.Lens
    mkr_list,  # type: list[mmapi.Marker]
    frame_range,  # type: time_utils.FrameRange
    adjustment_solver,  # type: AdjustmentSolver
    adjustment_attrs,  # type: AdjustmentAttributes
    log_level,  # type: str
    prefix_name,  # type: str
    output_dir,  # type: str
):
    # type: (...) -> None
    """
    Launch solver executable.

    TODO: Read stdout from the process.

    TODO: Do not block Maya main thread.
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(lens, mmapi.Lens)
    assert isinstance(mkr_list, list)
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(adjustment_solver, AdjustmentSolver)
    assert isinstance(adjustment_attrs, AdjustmentAttributes)
    assert log_level in const.LOG_LEVEL_LIST
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)

    executable_file_path = __find_executable_file_path()
    if executable_file_path is None:
        LOG.error('Could not find %r executable!', const.EXECUTABLE_FILE_NAME)
        return
    assert os.path.isfile(executable_file_path)

    # TODO: Convert the arguments into command flags.
    cmd_args = [executable_file_path, '--help']
    subprocess.call(cmd_args)
    return


def load_camera_outputs():
    raise NotImplementedError
    # TODO: Read camera outputs


def load_nuke_lens_file():
    # TODO: Read lens file.
    raise NotImplementedError
