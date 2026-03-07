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
The Camera Solver tool.

High-level entry points for running and loading the camera solve.
Maya scene queries are in lib.scene; solver construction is in lib.defaults.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import uuid

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.configmaya as configmaya

import mmSolver.tools.camerasolver.constant as const
import mmSolver.tools.camerasolver.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_log_level():
    """Read the log level from the Maya scene, falling back to the default."""
    # type: () -> str
    value = configmaya.get_scene_option(
        const.SCENE_OPTION_LOG_LEVEL, default=const.LOG_LEVEL_PROGRESS
    )
    if value not in const.LOG_LEVEL_LIST:
        value = const.LOG_LEVEL_PROGRESS
    return value


def _get_adjustment_solver():
    """Build an AdjustmentSolver from preferences stored in the Maya scene."""
    # type: () -> lib.AdjustmentSolver
    solver_type = configmaya.get_scene_option(
        const.SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE,
        default=const.ADJUSTMENT_SOLVER_TYPE_NONE,
    )
    if solver_type not in const.ADJUSTMENT_SOLVER_TYPE_LIST:
        solver_type = const.ADJUSTMENT_SOLVER_TYPE_NONE

    thread_count = configmaya.get_scene_option(
        const.SCENE_OPTION_THREAD_COUNT, default=4
    )
    if not (isinstance(thread_count, int) and thread_count > 0):
        thread_count = 4

    evolution_generation_count = configmaya.get_scene_option(
        const.SCENE_OPTION_EVOLUTION_GENERATION_COUNT, default=100
    )
    if not (
        isinstance(evolution_generation_count, int) and evolution_generation_count > 0
    ):
        evolution_generation_count = 100

    evolution_population_count = configmaya.get_scene_option(
        const.SCENE_OPTION_EVOLUTION_POPULATION_COUNT, default=100
    )
    if not (
        isinstance(evolution_population_count, int) and evolution_population_count > 0
    ):
        evolution_population_count = 100

    return lib.make_adjustment_solver(
        solver_type,
        thread_count=thread_count,
        evolution_generation_count=evolution_generation_count,
        evolution_population_count=evolution_population_count,
    )


def _get_default_adjustment_attributes():
    """Build an AdjustmentAttributes using the default focal length bounds."""
    # type: () -> lib.AdjustmentAttributes
    return lib.make_adjustment_attributes(
        const.DEFAULT_FOCAL_LENGTH_MIN,
        const.DEFAULT_FOCAL_LENGTH_MAX,
        const.DEFAULT_FOCAL_LENGTH_SAMPLES,
    )


def run_camera_solve():
    """
    Run the camera solver asynchronously using the selected/active camera.

    All markers under the camera are used. The solver runs in a
    background process so that Maya remains interactive.
    Use :func:`load_solved_camera` afterwards to apply the results.
    """
    # type: () -> lib.SolveProcess | None
    mmapi.load_plugin()

    camera = lib.get_camera_from_selection()
    if camera is None:
        LOG.warning('No camera selected or active in viewport.')
        return

    mkr_list = lib.get_markers_under_camera(camera)
    if not mkr_list:
        LOG.warning('No markers found under camera %r.', camera.get_transform_node())
        return

    lens = lib.get_lens_from_camera(camera)
    frame_range = time_utils.get_maya_timeline_range_inner()
    log_level = _get_log_level()
    adjustment_solver = _get_adjustment_solver()
    adjustment_attributes = _get_default_adjustment_attributes()
    output_directory = lib.get_output_directory()
    prefix_name = lib.get_prefix_name(camera)

    solver_process = lib.launch_solve_async(
        camera,
        lens,
        mkr_list,
        frame_range,
        adjustment_solver,
        adjustment_attributes,
        log_level,
        prefix_name,
        output_directory,
    )
    if solver_process is None:
        LOG.error('Failed to launch camera solver.')
        return

    LOG.info(
        'Camera solver launched for %r. Use "Load Solved Camera" when complete.',
        camera.get_transform_node(),
    )
    return solver_process


def load_solved_camera():
    """
    Load a previously solved camera from the output directory.

    The selected/active camera is used. The camera name must match the
    one that was originally solved.
    """
    # type: () -> None
    mmapi.load_plugin()

    undo_id = 'camerasolver load: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(
        use_undo_chunk=True,
        undo_chunk_name=undo_id,
        restore_current_frame=False,
        pre_update_frame=False,
        post_update_frame=False,
        use_dg_evaluation_mode=True,
        disable_viewport=False,
    ):
        camera = lib.get_camera_from_selection()
        if camera is None:
            LOG.warning('No camera selected or active in viewport.')
            return

        mkr_list = lib.get_markers_under_camera(camera)
        if not mkr_list:
            LOG.warning(
                'No markers found under camera %r.',
                camera.get_transform_node(),
            )
            return

        output_directory = lib.get_output_directory()
        prefix_name = lib.get_prefix_name(camera)

        lib.load_camera_outputs(camera, prefix_name, output_directory)
        lib.load_bundle_outputs(mkr_list, prefix_name, output_directory)
        lib.load_residuals_outputs(mkr_list, prefix_name, output_directory)
        LOG.info('Loaded solved camera data for %r.', camera.get_transform_node())
    return


def open_window():
    """
    Open the Camera Solver UI window.
    """
    # type: () -> None
    import mmSolver.tools.camerasolver.ui.camerasolver_window as camerasolver_window

    camerasolver_window.main()
    return
