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
"""

import datetime
import os
import tempfile
import uuid

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.camera as cam_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.viewport as viewport_utils

import mmSolver.tools.camerasolver.constant as const
import mmSolver.tools.camerasolver.lib as lib

LOG = mmSolver.logger.get_logger()

# Scene option keys for storing camera solver preferences.
SCENE_OPTION_LOG_LEVEL = 'mmSolver_camerasolver_log_level'
SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE = 'mmSolver_camerasolver_adj_solver_type'
SCENE_OPTION_THREAD_COUNT = 'mmSolver_camerasolver_thread_count'
SCENE_OPTION_EVOLUTION_GENERATION_COUNT = 'mmSolver_camerasolver_evo_gen_count'
SCENE_OPTION_EVOLUTION_POPULATION_COUNT = 'mmSolver_camerasolver_evo_pop_count'

# Subdirectory under the Maya workspace for solver output.
_WORKSPACE_SUBDIR = 'data'
_OUTPUT_DIR_NAME = 'mmSolver_camerasolver'


def _get_log_level():
    # type: () -> str
    value = configmaya.get_scene_option(
        SCENE_OPTION_LOG_LEVEL, default=const.LOG_LEVEL_PROGRESS
    )
    if value not in const.LOG_LEVEL_LIST:
        value = const.LOG_LEVEL_PROGRESS
    return value


def _get_adjustment_solver():
    # type: () -> lib.AdjustmentSolver
    adj_solver = lib.AdjustmentSolver()

    solver_type = configmaya.get_scene_option(
        SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE,
        default=const.ADJUSTMENT_SOLVER_TYPE_NONE,
    )
    if solver_type not in const.ADJUSTMENT_SOLVER_TYPE_LIST:
        solver_type = const.ADJUSTMENT_SOLVER_TYPE_NONE
    adj_solver.set_adjustment_solver_type(solver_type)

    thread_count = configmaya.get_scene_option(
        SCENE_OPTION_THREAD_COUNT, default=4
    )
    if isinstance(thread_count, int) and thread_count > 0:
        adj_solver.set_thread_count(thread_count)
    else:
        adj_solver.set_thread_count(4)

    gen_count = configmaya.get_scene_option(
        SCENE_OPTION_EVOLUTION_GENERATION_COUNT, default=100
    )
    if isinstance(gen_count, int) and gen_count > 0:
        adj_solver.set_evolution_generation_count(gen_count)
    else:
        adj_solver.set_evolution_generation_count(100)

    pop_count = configmaya.get_scene_option(
        SCENE_OPTION_EVOLUTION_POPULATION_COUNT, default=100
    )
    if isinstance(pop_count, int) and pop_count > 0:
        adj_solver.set_evolution_population_count(pop_count)
    else:
        adj_solver.set_evolution_population_count(100)

    return adj_solver


def _get_default_adjustment_attrs():
    # type: () -> lib.AdjustmentAttributes
    adj_attrs = lib.AdjustmentAttributes()
    adj_attrs.set_attribute_bounds(
        const.ATTR_CAMERA_FOCAL_LENGTH, 1.0, 500.0
    )
    adj_attrs.set_attribute_sample_count(const.ATTR_CAMERA_FOCAL_LENGTH, 100)
    return adj_attrs


def _get_camera_from_selection():
    # type: () -> mmapi.Camera | None
    """Get a camera from the selection, or fall back to the active viewport."""
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    camera_nodes = node_categories.get(mmapi.OBJECT_TYPE_CAMERA, [])
    if camera_nodes:
        cam_tfm, cam_shp = cam_utils.get_camera(camera_nodes[0])
        if cam_shp is not None:
            return mmapi.Camera(shape=cam_shp)

    # Fall back to active viewport camera.
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        return None
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        return None
    return mmapi.Camera(shape=cam_shp)


def _get_markers_under_camera(cam):
    # type: (mmapi.Camera) -> list
    """Get all markers parented under the given camera."""
    cam_tfm = cam.get_transform_node()
    if cam_tfm is None:
        return []
    below_nodes = maya.cmds.ls(cam_tfm, dag=True, long=True) or []
    marker_nodes = mmapi.filter_marker_nodes(below_nodes)
    marker_nodes = list(set(marker_nodes))
    mkr_list = [mmapi.Marker(node=x) for x in marker_nodes]
    return mkr_list


def _get_lens_from_camera(cam):
    # type: (mmapi.Camera) -> mmapi.Lens | None
    cam_shp = cam.get_shape_node()
    if cam_shp is None:
        return None
    lens_nodes = maya.cmds.listConnections(
        cam_shp + '.inLens', source=True, destination=False,
        type='mmLensModel3de'
    ) or []
    if not lens_nodes:
        return None
    return mmapi.Lens(node=lens_nodes[0])


def _get_output_dir():
    # type: () -> str
    """Get output directory, preferring the Maya workspace."""
    workspace_path = maya.cmds.workspace(query=True, fullName=True)
    if workspace_path is not None:
        workspace_path = os.path.abspath(workspace_path)
        output_dir = os.path.join(
            workspace_path, _WORKSPACE_SUBDIR, _OUTPUT_DIR_NAME
        )
        try:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            # Verify writable.
            test_file = os.path.join(output_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('')
            os.remove(test_file)
            return output_dir
        except (OSError, IOError):
            LOG.warning(
                'Workspace output dir not writable, falling back to temp: %r',
                output_dir,
            )

    output_dir = os.path.join(tempfile.gettempdir(), _OUTPUT_DIR_NAME)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    return output_dir


def _get_prefix_name(cam):
    # type: (mmapi.Camera) -> str
    cam_tfm = cam.get_transform_node()
    cam_name = cam_tfm.split('|')[-1]
    return 'camerasolver_' + cam_name


def run_camera_solve():
    """
    Run the camera solver asynchronously using the selected/active camera.

    All markers under the camera are used. The solver runs in a
    background process so that Maya remains interactive.
    Use :func:`load_solved_camera` afterwards to apply the results.
    """
    mmapi.load_plugin()

    cam = _get_camera_from_selection()
    if cam is None:
        LOG.warning('No camera selected or active in viewport.')
        return

    mkr_list = _get_markers_under_camera(cam)
    if not mkr_list:
        LOG.warning(
            'No markers found under camera %r.', cam.get_transform_node()
        )
        return

    lens = _get_lens_from_camera(cam)
    frame_range = time_utils.get_maya_timeline_range_inner()
    log_level = _get_log_level()
    adjustment_solver = _get_adjustment_solver()
    adjustment_attrs = _get_default_adjustment_attrs()
    output_dir = _get_output_dir()
    prefix_name = _get_prefix_name(cam)

    solve_process = lib.launch_solve_async(
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
    if solve_process is None:
        LOG.error('Failed to launch camera solver.')
        return

    LOG.info(
        'Camera solver launched for %r. '
        'Use "Load Solved Camera" when complete.',
        cam.get_transform_node(),
    )
    return solve_process


def load_solved_camera():
    """
    Load a previously solved camera from the output directory.

    The selected/active camera is used. The camera name must match the
    one that was originally solved.
    """
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
        cam = _get_camera_from_selection()
        if cam is None:
            LOG.warning('No camera selected or active in viewport.')
            return

        mkr_list = _get_markers_under_camera(cam)
        if not mkr_list:
            LOG.warning(
                'No markers found under camera %r.',
                cam.get_transform_node(),
            )
            return

        output_dir = _get_output_dir()
        prefix_name = _get_prefix_name(cam)

        lib.load_camera_outputs(cam, prefix_name, output_dir)
        lib.load_bundle_outputs(mkr_list, prefix_name, output_dir)
        lib.load_residuals_outputs(mkr_list, prefix_name, output_dir)
        LOG.info(
            'Loaded solved camera data for %r.', cam.get_transform_node()
        )
    return


def open_window():
    """
    Open the Camera Solver UI window.
    """
    import mmSolver.tools.camerasolver.ui.camerasolver_window as camerasolver_window
    camerasolver_window.main()
    return
