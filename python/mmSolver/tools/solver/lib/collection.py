# Copyright (C) 2018, 2019 David Cattermole.
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
Collection and solving functions.
"""

import logging
import pprint
import time

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.converttypes as convert_types

import mmSolver.utils.time as utils_time
import mmSolver.utils.converttypes as converttypes
import mmSolver.utils.python_compat as pycompat

import mmSolver.tools.userpreferences.constant as userprefs_const
import mmSolver.tools.userpreferences.lib as userprefs_lib
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as col_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


# Function aliases, for the 'collectionstate' module.
get_attribute_toggle_animated_from_collection = (
    col_state.get_attribute_toggle_animated_from_collection
)
set_attribute_toggle_animated_on_collection = (
    col_state.set_attribute_toggle_animated_on_collection
)
get_attribute_toggle_static_from_collection = (
    col_state.get_attribute_toggle_static_from_collection
)
set_attribute_toggle_static_on_collection = (
    col_state.set_attribute_toggle_static_on_collection
)
get_attribute_toggle_locked_from_collection = (
    col_state.get_attribute_toggle_locked_from_collection
)
set_attribute_toggle_locked_on_collection = (
    col_state.set_attribute_toggle_locked_on_collection
)
get_object_toggle_camera_from_collection = (
    col_state.get_object_toggle_camera_from_collection
)
set_object_toggle_camera_on_collection = (
    col_state.set_object_toggle_camera_on_collection
)
get_object_toggle_marker_from_collection = (
    col_state.get_object_toggle_marker_from_collection
)
set_object_toggle_marker_on_collection = (
    col_state.set_object_toggle_marker_on_collection
)
get_object_toggle_bundle_from_collection = (
    col_state.get_object_toggle_bundle_from_collection
)
set_object_toggle_bundle_on_collection = (
    col_state.set_object_toggle_bundle_on_collection
)
get_object_toggle_line_from_collection = (
    col_state.get_object_toggle_line_from_collection
)
set_object_toggle_line_on_collection = col_state.set_object_toggle_line_on_collection


def get_collections():
    """
    Get all Collection objects defined in the scene.

    :returns: A list of Collection objects.
    :rtype: [Collection, ..]
    """
    nodes = maya.cmds.ls(type='objectSet', long=True) or []
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    cols = []
    for col_node in node_categories['collection']:
        col = mmapi.Collection(node=col_node)
        cols.append(col)
    return cols


def create_collection(name=None):
    """
    Create a new Collection in the scene.

    :param name: The node name for the created collection.
    :type name: str or None

    :returns: A new Collection object.
    :rtype: Collection
    """
    if name is None:
        name = const.COLLECTION_DEFAULT_NODE_NAME
    col = mmapi.Collection().create_node(name)
    return col


def rename_collection(col, new_name):
    """
    Rename a Collection node name.

    Note: The Collection object stores a pointer to the underlying
    node. We can change the name without affecting the Collection
    object..

    :param col: Collection object to rename.
    :type col: Collection

    :param new_name: The new name to rename the Collection to.
    :type new_name: str
    """
    if col is None:
        msg = 'rename_collection: Can not rename, collection invalid.'
        LOG.warning(msg)
        return
    node = col.get_node()
    if node is None or maya.cmds.objExists(node) is False:
        msg = 'rename_collection: Can not rename, node invalid.'
        LOG.warning(msg)
        return
    maya.cmds.rename(node, new_name)
    return


def delete_collection(col):
    """
    Delete a Collection object (and underlying Maya node).

    :param col: The Collection object to delete.
    :type col: Collection
    """
    if col is None:
        return
    node = col.get_node()
    node = str(node)
    del col
    maya.cmds.delete(node)
    return


def select_collection(col):
    """
    Select the collection node, not the members of the collection node.

    :param col: The Collection object to select.
    :type col: Collection
    """
    if col is None:
        return
    node_uid = col.get_node_uid()
    if node_uid is None:
        return
    nodes = maya.cmds.ls(node_uid)
    if nodes is None:
        return

    # Run selection when Maya is idle next, otherwise this fails to
    # select the objectSet and instead selects the contents of the
    # objectSet. Issue #23
    cmd = 'maya.cmds.select(%r, replace=True, noExpand=True)'
    cmd = cmd % str(nodes[0])
    maya.cmds.evalDeferred(cmd)
    return


def get_previous_collection_and_index(cols, current_col):
    """
    Get the previous collection to the current collection, in list of
    collections.

    :param cols: List of collections.
    :type cols: [Collection, ..]

    :param current_col: The current collection.
    :type current_col: Collection

    :returns: Collection and index in 'cols' of the previous collection.
    :rtype: Collection, int
    """
    prev_col = None
    prev_index = None
    if len(cols) < 2:
        return prev_col, prev_index
    col_names = [col.get_node() for col in cols]
    current_col_name = current_col.get_node()
    current_index = col_names.index(current_col_name)
    prev_index = current_index - 1
    prev_col = cols[prev_index]
    return prev_col, prev_index


def get_previous_collection(cols, current_col):
    """
    Get the previous collection to the current collection, in list of
    collections.

    :param cols: List of collections.
    :type cols: [Collection, ..]

    :param current_col: The current collection.
    :type current_col: Collection

    :returns: The previous Collection in cols relative to current_col.
    :rtype: Collection
    """
    prev_col, prev_index = get_previous_collection_and_index(cols, current_col)
    return prev_col


def log_solve_results(
    log, solres_list, timestamp=None, total_time=None, status_fn=None
):
    """
    Displays / saves the Solve Results.

    :param log: Logging object to log with.
    :type log: logger

    :param solres_list: List of Solve Results to log.
    :type solres_list: list of SolveResult

    :param timestamp: The current time; as a UNIX Epoch floating point
                      number (as returned by 'time.time()').
    :type timestamp: None or float

    :param total_time: The duration of the solve to log, in seconds.
    :type total_time: None or float

    :param status_fn: Function to set the status text.
    :type status_fn: callable function or None

    :returns: Nothing.
    :rtype: None
    """
    status_str = ''
    long_status_str = ''

    if timestamp is not None:
        stamp = mmapi.format_timestamp(timestamp)
        status_str += stamp + ' | '
        long_status_str += stamp + ' | '

    frame_list = mmapi.merge_frame_list(solres_list)
    num_frames = len(frame_list)

    # Get Solver success.
    success = True
    for solres in solres_list:
        value = solres.get_success()
        if value is not True:
            success = False
            break
    if success is True:
        status_str += 'Solved %s frames | ' % num_frames
        long_status_str += 'Solved %s frames | ' % num_frames
    else:
        status_str += 'Failed %s frames | ' % num_frames
        long_status_str += 'Failed %s frames | ' % num_frames

    frame_error_list = mmapi.merge_frame_error_list(solres_list)
    if log and (log.level > logging.DEBUG):
        frame_error_txt = pprint.pformat(dict(frame_error_list))
        log.debug('Per-Frame Errors:\n%s', frame_error_txt)

        timer_stats = mmapi.combine_timer_stats(solres_list)
        timer_stats_txt = pprint.pformat(dict(timer_stats))
        log.debug('Timer Statistics:\n%s', timer_stats_txt)

    avg_error = mmapi.get_average_frame_error_list(frame_error_list)
    status_str += 'avg deviation %.2fpx' % avg_error
    long_status_str += 'Average Deviation %.2fpx' % avg_error

    max_frame, max_error = mmapi.get_max_frame_error(frame_error_list)
    status_str += ' | max deviation %.2fpx at f%s' % (max_error, max_frame)
    long_status_str += ' | Max Deviation %.2fpx at f%s' % (max_error, max_frame)

    if total_time is not None:
        minutes_in_hour = 60
        seconds_in_minute = 60
        seconds_in_hour = minutes_in_hour * seconds_in_minute
        hours, remainder = divmod(total_time, seconds_in_hour)
        minutes, seconds = divmod(remainder, seconds_in_minute)
        minutes += hours * minutes_in_hour
        time_str = "{}:{:.2f}s".format(int(minutes), seconds)

        frames_per_second = float(num_frames) / total_time
        fps_str = ' (%.2f fps)' % frames_per_second

        if log:
            log.info('Total Time: %s %s', time_str, fps_str)
        status_str += ' | time ' + time_str + fps_str
        long_status_str += ' | Time ' + time_str + fps_str

    if log:
        log.info('Max Frame Deviation: %.2f pixels at frame %s', max_error, max_frame)
        log.info('Average Deviation: %.2f pixels', avg_error)

    if status_fn is not None:
        status_fn(status_str)
    if log:
        log.warning(long_status_str)
    return


def __compile_frame_list(range_type, frame_string, by_frame):
    assert isinstance(range_type, int)
    assert frame_string is None or isinstance(frame_string, pycompat.TEXT_TYPE)
    assert isinstance(by_frame, int)
    frame_nums = []
    if range_type == const.RANGE_TYPE_TIMELINE_INNER_VALUE:
        start, end = utils_time.get_maya_timeline_range_inner()
        frame_nums = [f for f in range(start, end + 1, by_frame)]
    elif range_type == const.RANGE_TYPE_TIMELINE_OUTER_VALUE:
        start, end = utils_time.get_maya_timeline_range_outer()
        frame_nums = [f for f in range(start, end + 1, by_frame)]
    elif range_type == const.RANGE_TYPE_CUSTOM_FRAMES_VALUE:
        if frame_string is None:
            start, end = utils_time.get_maya_timeline_range_inner()
            frame_string = '{0}-{1}'.format(start, end)
        frame_nums = converttypes.stringToIntList(frame_string)

        # Apply 'by_frame' to custom frame ranges.
        start = min(frame_nums)
        frame_nums = [n for n in frame_nums if (float(n - start) % by_frame) == 0]
    return frame_nums


def __get_collection_frame_numbers(col, range_type):
    by_frame = col_state.get_solver_increment_by_frame_from_collection(col)
    frame_string = col_state.get_solver_frames_from_collection(col)
    frame_nums = __compile_frame_list(range_type, frame_string, by_frame)
    return frame_nums


def _calculate_root_frames(
    mkr_list,
    start_frame,
    end_frame,
    extra_frames,
    use_per_marker_frames,
    per_marker_frames,
    use_span_frames,
    span_frames,
):
    assert isinstance(mkr_list, (list, set))
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    assert isinstance(extra_frames, (list, set))
    assert isinstance(use_per_marker_frames, bool)
    assert isinstance(per_marker_frames, int)
    assert isinstance(use_span_frames, bool)
    assert isinstance(span_frames, int)
    s = time.time()

    frames = extra_frames
    if use_per_marker_frames and len(mkr_list) > 0:
        frames = mmapi.get_root_frames_from_markers(
            mkr_list, per_marker_frames, start_frame, end_frame
        )
    frames = mmapi.root_frames_list_combine(frames, extra_frames)

    if use_span_frames:
        frames = mmapi.root_frames_subdivide(frames, span_frames)

    e = time.time()
    LOG.debug('RootFrameWidget calculate_root_frames: %r seconds', e - s)
    return frames


def __get_collection_root_frame_numbers(col):
    range_type = col_state.get_solver_range_type_from_collection(col)
    by_frame = col_state.get_solver_increment_by_frame_from_collection(col)
    frame_string = col_state.get_solver_frames_from_collection(col)
    frame_nums = __compile_frame_list(range_type, frame_string, by_frame)
    start_frame = min(frame_nums)
    end_frame = max(frame_nums)

    user_string = col_state.get_solver_user_frames_from_collection(col)
    user_int_list = convert_types.stringToIntList(user_string)

    use_per_marker_frames = col_state.get_solver_use_per_marker_frames_from_collection(
        col
    )
    per_marker_frames = col_state.get_solver_per_marker_frames_from_collection(col)
    use_span_frames = col_state.get_solver_use_span_frames_from_collection(col)
    span_frames = col_state.get_solver_span_frames_from_collection(col)

    mkr_list = col.get_marker_list()
    root_frames = _calculate_root_frames(
        mkr_list,
        start_frame,
        end_frame,
        user_int_list,
        use_per_marker_frames,
        per_marker_frames,
        use_span_frames,
        span_frames,
    )
    if len(root_frames) < 2:
        LOG.warn('Auto Root Frames failed to calculate.')

    return root_frames


def __compile_solver_basic_tab(col, solver_type, scene_graph_mode):
    sol_list = []
    sol = mmapi.SolverBasic()
    range_type = col_state.get_solver_range_type_from_collection(col)
    if range_type == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
        frame_num = lib_maya_utils.get_current_frame()
        frame = mmapi.Frame(frame_num)
        sol.set_use_single_frame(True)
        sol.set_single_frame(frame)
    else:
        by_frame = col_state.get_solver_increment_by_frame_from_collection(col)
        frame_string = col_state.get_solver_frames_from_collection(col)
        frame_nums = __compile_frame_list(range_type, frame_string, by_frame)

        frames = [mmapi.Frame(f) for f in frame_nums]
        sol.set_frame_list(frames)

    eval_complex_graphs = col_state.get_solver_eval_complex_graphs_from_collection(col)
    solve_focal_length = col_state.get_solver_solve_focal_length_from_collection(col)
    solve_lens_distortion = col_state.get_solver_solve_lens_distortion_from_collection(
        col
    )

    assert isinstance(eval_complex_graphs, bool)
    if eval_complex_graphs is True:
        # Eval Complex Graphs is only supported with the Maya DAG
        # scene graph.
        scene_graph_mode = const.SCENE_GRAPH_MODE_MAYA_DAG

    sol.set_solver_type(solver_type)
    sol.set_scene_graph_mode(scene_graph_mode)
    sol.set_eval_complex_graphs(eval_complex_graphs)
    sol.set_solve_focal_length(solve_focal_length)
    sol.set_solve_lens_distortion(solve_lens_distortion)
    sol_list.append(sol)
    return sol_list


def __compile_solver_standard_tab(col, solver_type, scene_graph_mode):
    sol_list = []
    sol = mmapi.SolverStandard()
    range_type = col_state.get_solver_range_type_from_collection(col)
    if range_type == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
        frame_num = lib_maya_utils.get_current_frame()
        frame = mmapi.Frame(frame_num)
        sol.set_use_single_frame(True)
        sol.set_single_frame(frame)
    else:
        frame_nums = __get_collection_frame_numbers(col, range_type)
        root_frame_nums = __get_collection_root_frame_numbers(col)

        frames = [mmapi.Frame(f) for f in frame_nums if f not in root_frame_nums]
        root_frames = [mmapi.Frame(f) for f in root_frame_nums]
        sol.set_root_frame_list(root_frames)
        sol.set_frame_list(frames)

    global_solve = col_state.get_solver_global_solve_from_collection(col)
    only_root = col_state.get_solver_only_root_frames_from_collection(col)
    eval_complex_graphs = col_state.get_solver_eval_complex_graphs_from_collection(col)
    solve_focal_length = col_state.get_solver_solve_focal_length_from_collection(col)
    solve_lens_distortion = col_state.get_solver_solve_lens_distortion_from_collection(
        col
    )

    assert isinstance(eval_complex_graphs, bool)
    if eval_complex_graphs is True:
        # Eval Complex Graphs is only supported with the Maya DAG
        # scene graph.
        scene_graph_mode = const.SCENE_GRAPH_MODE_MAYA_DAG

    sol.set_global_solve(global_solve)
    sol.set_only_root_frames(only_root)
    sol.set_solver_type(solver_type)
    sol.set_scene_graph_mode(scene_graph_mode)
    sol.set_eval_complex_graphs(eval_complex_graphs)
    sol.set_solve_focal_length(solve_focal_length)
    sol.set_solve_lens_distortion(solve_lens_distortion)
    sol_list.append(sol)
    return sol_list


def __compile_solver_camera_tab(col, solver_type):
    sol_list = []
    sol = mmapi.SolverCamera()
    range_type = col_state.get_solver_range_type_from_collection(col)
    if range_type == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
        msg = 'Select a frame range; camera solver cannot solve single frame.'
        raise ValueError(msg)

    frame_nums = __get_collection_frame_numbers(col, range_type)
    root_frame_nums = __get_collection_root_frame_numbers(col)

    frames = [mmapi.Frame(f) for f in frame_nums]
    root_frames = [mmapi.Frame(f) for f in root_frame_nums]
    sol.set_root_frame_list(root_frames)
    sol.set_frame_list(frames)

    start_frame = min(frame_nums)
    end_frame = max(frame_nums)
    origin_frame_num = col_state.get_solver_origin_frame_from_collection(col)
    origin_frame_num = max(start_frame, origin_frame_num)
    origin_frame_num = min(end_frame, origin_frame_num)
    origin_frame = mmapi.Frame(origin_frame_num)
    sol.set_origin_frame(origin_frame)

    scene_scale = col_state.get_solver_scene_scale_from_collection(col)
    sol.set_scene_scale(scene_scale)

    solve_focal_length = col_state.get_solver_solve_focal_length_from_collection(col)
    solve_lens_distortion = col_state.get_solver_solve_lens_distortion_from_collection(
        col
    )
    sol.set_solve_focal_length(solve_focal_length)
    sol.set_solve_lens_distortion(solve_lens_distortion)

    sol_list.append(sol)
    return sol_list


def compile_collection(col, prog_fn=None):
    """
    Compiles, checks and validates the collection, ready for a solve.

    :param col: Collection to execute.
    :type col: Collection

    :param prog_fn: Progress function that is called each time progress
                    is made. The function should take a single 'int'
                    argument, and the integer is expected to be a
                    percentage value, between 0 and 100.
    :type prog_fn: None or function
    """
    s = time.time()
    sol_list = []

    solver_type = col_state.get_solver_type_from_collection(col)
    if solver_type == const.SOLVER_TYPE_DEFAULT:
        solver_type = mmapi.SOLVER_TYPE_DEFAULT

    scene_graph_mode = col_state.get_solver_scene_graph_mode_from_collection(col)

    solver_tab = col_state.get_solver_tab_from_collection(col)
    assert isinstance(solver_tab, pycompat.TEXT_TYPE)
    if solver_tab == const.SOLVER_TAB_BASIC_VALUE:
        sol_list = __compile_solver_basic_tab(col, solver_type, scene_graph_mode)
    elif solver_tab == const.SOLVER_TAB_STANDARD_VALUE:
        sol_list = __compile_solver_standard_tab(col, solver_type, scene_graph_mode)
    elif solver_tab == const.SOLVER_TAB_CAMERA_VALUE:
        sol_list = __compile_solver_camera_tab(col, solver_type)
    else:
        msg = 'Solver tab value is invalid: %r'
        raise TypeError(msg % solver_tab)

    col.set_solver_list(sol_list)
    e = time.time()
    LOG.debug('Compile time (GUI): %r seconds', e - s)
    return


def gather_execute_options():
    """
    Query the current Solver UI ExecuteOptions state that is saved in the scene.

    :return: The ExecuteOptions ready to be passed to an execution function.
    :rtype: ExecuteOptions
    """
    refresh_state = lib_state.get_refresh_viewport_state()
    disable_viewport_two_state = not refresh_state
    force_update_state = lib_state.get_force_dg_update_state()
    do_isolate_state = lib_state.get_isolate_object_while_solving_state()
    pre_solve_force_eval = lib_state.get_pre_solve_force_eval_state()

    # Display Types
    disp_node_types = dict()
    image_plane_state = lib_state.get_display_image_plane_while_solving_state()
    meshes_state = lib_state.get_display_meshes_while_solving_state()
    disp_node_types['imagePlane'] = image_plane_state
    disp_node_types['mmImagePlaneShape2'] = image_plane_state
    disp_node_types['mesh'] = meshes_state

    # Minimal UI from config file.
    config = userprefs_lib.get_config()
    key = userprefs_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY
    minimal_ui = userprefs_lib.get_value(config, key)
    minimal_ui = (
        minimal_ui == userprefs_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_VALUE
    )

    options = mmapi.create_execute_options(
        refresh=refresh_state,
        disable_viewport_two=disable_viewport_two_state,
        force_update=force_update_state,
        do_isolate=do_isolate_state,
        pre_solve_force_eval=pre_solve_force_eval,
        display_node_types=disp_node_types,
        use_minimal_ui=minimal_ui,
    )
    return options


def execute_collection(
    col, options=None, log_level=None, prog_fn=None, status_fn=None, info_fn=None
):
    """
    Execute the entire collection; Solvers, Markers, Bundles, etc.

    :param col: Collection to execute.
    :type col: Collection

    :param options: Solver execution options.
    :type options: mmSolver.api.ExecuteOptions

    :param log_level: Logging level to print out.
    :type log_level: None or str

    :param prog_fn: A function called with an 'int' argument, to
                    display progress information to the user. The
                    integer is expected to be between 0 and 100 (and
                    is read as a percentage).
    :type prog_fn: None or function

    :param status_fn: A function called with an 'str' argument, to display
                      status information to the user.
    :type status_fn: None or function

    :param info_fn: A function called with an 'str' argument, to display
                    solver information to the user.
    :type info_fn: None or function
    """
    msg = (
        'execute_collection: '
        'col=%r '
        'log_level=%r '
        'refresh=%r '
        'force_update=%r '
        'display_grid=%r '
        'display_node_types=%r '
        'prog_fn=%r '
        'status_fn=%r '
        'info_fn=%r'
    )
    LOG.debug(
        msg,
        col,
        log_level,
        options.refresh,
        options.force_update,
        options.display_grid,
        options.display_node_types,
        prog_fn,
        status_fn,
        info_fn,
    )

    assert isinstance(options.refresh, bool)
    assert isinstance(options.force_update, bool)
    assert isinstance(options.display_node_types, dict)
    assert isinstance(options.do_isolate, bool)
    assert isinstance(log_level, pycompat.TEXT_TYPE)
    assert prog_fn is None or hasattr(prog_fn, '__call__')
    assert status_fn is None or hasattr(status_fn, '__call__')
    assert info_fn is None or hasattr(info_fn, '__call__')

    log = LOG
    if log_level in const.LOG_LEVEL_LIST:
        tmp_log_level = log_level.upper()
        log = mmSolver.logger.get_logger(tmp_log_level)
    else:
        msg = 'log_level value is invalid; value=%r'
        raise ValueError(msg % log_level)

    # TODO: Check common issues in the scene before solving to avoid
    # errors and warn the user.
    #
    # - When using CameraSolver:
    #
    #   - Make sure bundles and camera share the same parent
    #     world-space matrix.
    #
    #   - All bundle values are unlocked and are static (not
    #     animated).
    #
    # TODO: For any bundle, if the connected Marker is not an input
    #       object, the Bundle will be skipped.

    # Execute the solve.
    s = time.time()
    solres_list = mmapi.execute(
        col,
        options=options,
        log_level=log_level,
        prog_fn=prog_fn,
        status_fn=status_fn,
        info_fn=info_fn,
    )
    e = time.time()
    total_time = e - s

    # Display Solver results
    timestamp = e
    log_solve_results(
        log, solres_list, timestamp=timestamp, total_time=total_time, status_fn=info_fn
    )

    # Calculate marker deviation, and set it on the marker.
    mkr_nodes = mmapi.merge_marker_node_list(solres_list)
    mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
    mmapi.update_deviation_on_markers(mkr_list, solres_list)

    # Set keyframe data on the collection for the solver
    mmapi.update_deviation_on_collection(col, solres_list)
    return


def query_solver_info_text(col):
    """
    Get a string of text, telling the user of the current solve inputs/outputs.

    :param col: The collection to compile and query.
    :type col: Collection

    :return: Text, ready for a QLabel.setText().
    :return: str
    """
    LOG.debug('query_solver_info_text: col=%r', col)
    param_num = 0
    dev_num = 0
    frm_num = 0
    failed_num = 0
    success_num = 0

    color = const.COLOR_TEXT_DEFAULT
    pre_text = ''
    text = (
        'Valid Solves {good_solves} | Invalid Solves {bad_solves} | '
        'Deviations {dev} | Parameters {param} | Frames {frm}'
    )
    post_text = ''

    # NOTE: We can return HTML 'rich text' in this string to allow
    # the text to be bold or coloured to indicate warnings or
    # errors.

    if col is not None:
        assert isinstance(col, mmapi.Collection)
        compile_collection(col)
        state_list = mmapi.validate(col, as_state=True)
        status_list = [state.status for state in state_list]
        only_failure_status = [
            x for x in status_list if x != mmapi.ACTION_STATUS_SUCCESS
        ]
        failed_num = len(only_failure_status)
        success_num = len(status_list) - failed_num
        some_failure = bool(failed_num)
        if some_failure is True:
            color = const.COLOR_WARNING
            pre_text = '<font color="{color}">'
            post_text = '</font>'
            message_hashes = set()
            for state in state_list:
                if state.status != mmapi.ACTION_STATUS_SUCCESS:
                    LOG.warn("skip frames: %r", state.frames)
                    h = hash(state.message)
                    if h not in message_hashes:
                        LOG.warn(state.message)
                    message_hashes.add(h)

        param_num_list = [state.parameter_number for state in state_list]
        dev_num_list = [state.error_number for state in state_list]
        frame_num_list = [state.frames_number for state in state_list]

        param_num = sum(param_num_list)
        dev_num = sum(dev_num_list)
        frm_num = sum(frame_num_list)

    if len(pre_text) > 0:
        pre_text = pre_text.format(color=color)
    text = text.format(
        param=param_num,
        dev=dev_num,
        frm=frm_num,
        good_solves=success_num,
        bad_solves=failed_num,
    )
    text = pre_text + text + post_text
    return text


def run_solve_ui(col, options, log_level, window):
    """
    Run the active "solve" (UI state information), and update the UI.

    This is a UI focused function. Calling this function with the
    'window' argument set will update the UI and show progress to the
    user. If the UI window is not given, the solve still runs, but
    does not update the UI.

    :param col: The active collection to solve.
    :type col: Collection

    :param options: Options for the solver options.
    :type options: mmSolver.api.ExecuteOptions

    :param log_level: How much information should we print out;
                      'error', 'warning', 'info', 'verbose' or 'debug'.
    :type log_level: str

    :param window: The SolverWindow object for the UI.
    :type window: SolverWindow or None
    """
    if window is not None:
        window.setStatusLine(const.STATUS_EXECUTING)

    try:
        if window is not None:
            window.progressBar.setValue(0)
            window.progressBar.show()

        if col is None:
            msg = 'No active collection.'
            if window is not None:
                window.setStatusLine('ERROR: ' + msg)
            LOG.error(msg)
            return

        compile_collection(col)
        prog_fn = LOG.info
        status_fn = LOG.info
        info_fn = LOG.info
        if window is not None and uiutils.isValidQtObject(window) is True:
            prog_fn = window.setProgressValue
            status_fn = window.setStatusLine
            info_fn = window.setSolveInfoLine

            # Set a minimal window size while solving.
            if options.use_minimal_ui is True:
                window.setMinimalUI(True)

        execute_collection(
            col,
            options=options,
            log_level=log_level,
            prog_fn=prog_fn,
            status_fn=status_fn,
            info_fn=info_fn,
        )
    finally:
        if window is not None and uiutils.isValidQtObject(window) is True:
            window.progressBar.setValue(100)
            window.progressBar.hide()

            # Reset Window size.
            if options.use_minimal_ui is True:
                window.setMinimalUI(False)

    return
