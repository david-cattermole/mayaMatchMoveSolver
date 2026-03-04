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

import json
import os
import subprocess
import threading

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat

import maya.cmds

import mmSolver.tools.camerasolver.constant as const

from mmSolver.tools.camerasolver.lib.save_data import (
    INCHES_TO_MM,
    construct_output_file_path,
    save_markers_to_file,
    save_camera_to_file,
    save_nuke_lens_to_file,
    save_solver_settings_to_file,
)

LOG = mmSolver.logger.get_logger()


class AdjustmentSolver(object):
    def __init__(self):
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
        self.__attribute_to_bounds = {}
        self.__attribute_to_sample_count = {}

    def get_attribute_names(self):
        # type: (AdjustmentAttributes) -> list[str]
        return list(self.__attribute_to_bounds.keys())

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


def find_executable_file_path():
    # type: (...) -> str | None
    var_name = const.MMSOLVER_LOCATION_ENV_VAR_NAME
    module_location = os.environ.get(var_name)
    if not module_location or not os.path.isdir(module_location):
        return None
    executable_file_path = os.path.join(
        module_location, 'bin', const.EXECUTABLE_FILE_NAME
    )
    if not os.path.isfile(executable_file_path):
        return None
    return executable_file_path


class SolveProcess(object):
    """Handle for a running (or completed) camera solver process.

    Call :meth:`wait` to block until finished, or poll :meth:`is_done`
    from the main thread without blocking.
    """

    def __init__(self, proc, stdout_thread, stderr_thread, stdout_lines, stderr_lines):
        self._proc = proc
        self._stdout_thread = stdout_thread
        self._stderr_thread = stderr_thread
        self._stdout_lines = stdout_lines
        self._stderr_lines = stderr_lines

    def is_done(self):
        # type: () -> bool
        """Return True when the subprocess has finished."""
        return self._proc.poll() is not None

    def wait(self):
        """Block until the subprocess and reader threads have finished."""
        self._stdout_thread.join()
        self._stderr_thread.join()
        self._proc.wait()

    def result(self):
        # type: () -> tuple[int, str, str]
        """Return (returncode, stdout, stderr).  Call after :meth:`wait`."""
        stdout = '\n'.join(self._stdout_lines)
        stderr = '\n'.join(self._stderr_lines)
        returncode = self._proc.returncode
        if returncode != 0:
            LOG.error(
                'Camera solver failed (exit %d):\n%s', returncode, stderr or stdout
            )
        return (returncode, stdout, stderr)


def _start_solve_process(cmd_args):
    # type: (list[str]) -> SolveProcess
    proc = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout_lines = []
    stderr_lines = []

    def _read_stream(stream, line_list, log_fn):
        for raw in iter(stream.readline, b''):
            line = raw.decode('utf-8', errors='replace').rstrip('\n')
            line_list.append(line)
            log_fn('%s', line)
        stream.close()

    stdout_thread = threading.Thread(
        target=_read_stream,
        args=(proc.stdout, stdout_lines, LOG.info),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_read_stream,
        args=(proc.stderr, stderr_lines, LOG.warning),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()
    return SolveProcess(proc, stdout_thread, stderr_thread, stdout_lines, stderr_lines)


def _build_solve_cmd_args(
    cam,  # type: mmapi.Camera
    lens,  # type: mmapi.Lens | None
    mkr_list,  # type: list[mmapi.Marker]
    frame_range,  # type: time_utils.FrameRange
    adjustment_solver,  # type: AdjustmentSolver
    adjustment_attrs,  # type: AdjustmentAttributes
    log_level,  # type: str
    prefix_name,  # type: str
    output_dir,  # type: str
):
    # type: (...) -> list[str] | None
    """Write input files and return the solver command-line arguments.

    Returns None if the executable cannot be found.
    """
    executable_file_path = find_executable_file_path()
    if executable_file_path is None:
        LOG.error('Could not find %r executable!', const.EXECUTABLE_FILE_NAME)
        return None

    uv_file_path = save_markers_to_file(mkr_list, frame_range, prefix_name, output_dir)
    mmcamera_file_path = save_camera_to_file(cam, frame_range, prefix_name, output_dir)
    solver_settings_file_path = save_solver_settings_to_file(
        frame_range, adjustment_solver, adjustment_attrs, prefix_name, output_dir
    )

    nuke_lens_file_path = None
    if lens is not None:
        nuke_lens_file_path = save_nuke_lens_to_file(
            cam, lens, frame_range, prefix_name, output_dir
        )

    cmd_args = [
        executable_file_path,
        uv_file_path,
        '--mmcamera',
        mmcamera_file_path,
        '--solver-settings',
        solver_settings_file_path,
    ]

    if nuke_lens_file_path is not None:
        cmd_args += ['--nuke-lens', nuke_lens_file_path]

    cmd_args += [
        '--prefix',
        prefix_name,
        '--output-dir',
        output_dir,
        '--log-level',
        log_level,
    ]
    return cmd_args


def launch_solve(
    cam,  # type: mmapi.Camera
    lens,  # type: mmapi.Lens | None
    mkr_list,  # type: list[mmapi.Marker]
    frame_range,  # type: time_utils.FrameRange
    adjustment_solver,  # type: AdjustmentSolver
    adjustment_attrs,  # type: AdjustmentAttributes
    log_level,  # type: str
    prefix_name,  # type: str
    output_dir,  # type: str
):
    # type: (...) -> tuple[int, str, str]
    """
    Write .uv/.mmcamera/.mmsettings (and optionally .nk) then run the
    camera solver executable.

    Returns (returncode, stdout, stderr).
    """
    assert isinstance(cam, mmapi.Camera)
    assert lens is None or isinstance(lens, mmapi.Lens)
    assert isinstance(mkr_list, list)
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(adjustment_solver, AdjustmentSolver)
    assert isinstance(adjustment_attrs, AdjustmentAttributes)
    assert log_level in const.LOG_LEVEL_LIST
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)

    cmd_args = _build_solve_cmd_args(
        cam,
        lens,
        mkr_list,
        frame_range,
        adjustment_solver,
        adjustment_attrs,
        log_level,
        prefix_name,
        output_dir,
    )
    if cmd_args is None:
        return (-1, '', '')

    LOG.debug('Camera solver command: %s', ' '.join(cmd_args))
    solve_process = _start_solve_process(cmd_args)

    solve_process.wait()
    returncode, stdout, stderr = solve_process.result()
    if returncode == 0:
        load_camera_outputs(cam, prefix_name, output_dir)
        load_bundle_outputs(mkr_list, prefix_name, output_dir)
        # TODO: Load Nuke lens distortion values.
    return (returncode, stdout, stderr)


def launch_solve_async(
    cam,  # type: mmapi.Camera
    lens,  # type: mmapi.Lens | None
    mkr_list,  # type: list[mmapi.Marker]
    frame_range,  # type: time_utils.FrameRange
    adjustment_solver,  # type: AdjustmentSolver
    adjustment_attrs,  # type: AdjustmentAttributes
    log_level,  # type: str
    prefix_name,  # type: str
    output_dir,  # type: str
):
    # type: (...) -> SolveProcess | None
    """Non-blocking variant of :func:`launch_solve`.

    Writes the input files, starts the solver executable in the
    background, and returns a :class:`SolveProcess` immediately so the
    caller can continue working.  Call :meth:`SolveProcess.wait` /
    :meth:`SolveProcess.result` when the result is needed.
    """
    assert isinstance(cam, mmapi.Camera)
    assert lens is None or isinstance(lens, mmapi.Lens)
    assert isinstance(mkr_list, list)
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(adjustment_solver, AdjustmentSolver)
    assert isinstance(adjustment_attrs, AdjustmentAttributes)
    assert log_level in const.LOG_LEVEL_LIST
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)

    cmd_args = _build_solve_cmd_args(
        cam,
        lens,
        mkr_list,
        frame_range,
        adjustment_solver,
        adjustment_attrs,
        log_level,
        prefix_name,
        output_dir,
    )
    if cmd_args is None:
        return None

    LOG.debug('Camera solver command: %s', ' '.join(cmd_args))
    return _start_solve_process(cmd_args)


def load_solved_camera_from_file(cam, file_path):
    # type: (mmapi.Camera, str) -> bool
    """Apply solved camera data from a .mmcamera file to a Maya camera.

    Keyframes are set on the camera transform and shape for every frame
    stored in the file.  Film-back attributes are converted from mm
    (file units) back to inches (Maya units).

    Returns True on success, False if the file could not be loaded.
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(file_path, pycompat.TEXT_TYPE)

    if not os.path.isfile(file_path):
        LOG.error('Solved camera file not found: %r', file_path)
        return False

    with open(file_path, 'r') as fh:
        doc = json.load(fh)

    attr_data = doc.get('data', {}).get('attr', {})
    if not attr_data:
        LOG.error('No attribute data found in: %r', file_path)
        return False

    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    # Map from mmcamera attribute name -> (node, maya_attr, mm_to_inches)
    MM_TO_INCHES = 1.0 / INCHES_TO_MM
    attr_map = {
        'translateX': (cam_tfm, 'translateX', False),
        'translateY': (cam_tfm, 'translateY', False),
        'translateZ': (cam_tfm, 'translateZ', False),
        'rotateX': (cam_tfm, 'rotateX', False),
        'rotateY': (cam_tfm, 'rotateY', False),
        'rotateZ': (cam_tfm, 'rotateZ', False),
        'focalLength': (cam_shp, 'focalLength', False),
        'filmBackWidth': (cam_shp, 'horizontalFilmAperture', True),
        'filmBackHeight': (cam_shp, 'verticalFilmAperture', True),
        'filmBackOffsetX': (cam_shp, 'horizontalFilmOffset', True),
        'filmBackOffsetY': (cam_shp, 'verticalFilmOffset', True),
    }

    for file_attr, (node, maya_attr, convert_to_inches) in attr_map.items():
        samples = attr_data.get(file_attr)
        if not samples:
            continue
        scale = MM_TO_INCHES if convert_to_inches else 1.0
        for frame, value in samples:
            maya.cmds.setKeyframe(
                node, attribute=maya_attr, time=frame, value=value * scale
            )

    return True


def load_camera_outputs(cam, prefix_name, output_dir):
    # type: (mmapi.Camera, str, str) -> bool
    """Load the solved camera from the output directory into Maya.

    The solver writes ``{prefix_name}_camera.mmcamera`` to *output_dir*.
    This function reads that file and keyframes the supplied *cam*.

    Returns True on success.
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)
    file_name = prefix_name + '_camera.mmcamera'
    file_path = os.path.join(output_dir, file_name)
    return load_solved_camera_from_file(cam, file_path)


def load_nuke_lens_file():
    # TODO: Read nuke lens file.
    raise NotImplementedError


def load_solved_bundles_from_file(mkr_list, file_path):
    # type: (list[mmapi.Marker], str) -> bool
    """Apply solved bundle positions from a .mmbundles file to Maya bundles.

    Matches each entry in the file by name to a marker in *mkr_list*,
    then sets translateX/Y/Z on the linked bundle.

    Returns True on success, False if the file could not be loaded.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(file_path, pycompat.TEXT_TYPE)

    if not os.path.isfile(file_path):
        LOG.error('Solved bundle file not found: %r', file_path)
        return False

    with open(file_path, 'r') as fh:
        lines = fh.read().splitlines()

    if not lines:
        LOG.error('Bundle file is empty: %r', file_path)
        return False

    try:
        count = int(lines[0].strip())
    except ValueError:
        LOG.error('Invalid bundle count in: %r', file_path)
        return False

    # Build name -> bundle node map from the marker list.
    name_to_bnd_node = {}
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        if mkr_node is None:
            continue
        mkr_name = mkr_node.split('|')[-1]
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        bnd_node = bnd.get_node()
        if bnd_node is None:
            continue
        name_to_bnd_node[mkr_name] = bnd_node

    line_idx = 1
    applied = 0
    for _ in range(count):
        if line_idx + 1 >= len(lines):
            break
        name = lines[line_idx]
        pos_line = lines[line_idx + 1]
        line_idx += 2

        bnd_node = name_to_bnd_node.get(name)
        if bnd_node is None:
            LOG.warning('No bundle found for marker name %r, skipping.', name)
            continue

        parts = pos_line.split()
        if len(parts) < 3:
            LOG.warning('Invalid position line for %r: %r', name, pos_line)
            continue

        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
        maya.cmds.setAttr(bnd_node + '.translateX', x)
        maya.cmds.setAttr(bnd_node + '.translateY', y)
        maya.cmds.setAttr(bnd_node + '.translateZ', z)
        applied += 1

    LOG.debug('Applied %d bundle positions from %r', applied, file_path)
    return True


def load_bundle_outputs(mkr_list, prefix_name, output_dir):
    # type: (list[mmapi.Marker], str, str) -> bool
    """Load the solved bundle positions from the output directory into Maya.

    The solver writes ``{prefix_name}_bundles.mmbundles`` to *output_dir*.

    Returns True on success.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)
    file_name = prefix_name + '_bundles.mmbundles'
    file_path = os.path.join(output_dir, file_name)
    return load_solved_bundles_from_file(mkr_list, file_path)
