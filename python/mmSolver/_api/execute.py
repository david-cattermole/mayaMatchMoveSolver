# Copyright (C) 2019 David Cattermole.
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
Execute a solve.
"""


import time
import pprint
import collections

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver._api.state as api_state
import mmSolver._api.utils as api_utils
import mmSolver._api.compile as api_compile
import mmSolver._api.excep as excep
import mmSolver._api.solveresult as solveresult
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.collectionutils as collectionutils

LOG = mmSolver.logger.get_logger()

ExecuteOptions = collections.namedtuple(
    'ExecuteOptions',
    ('verbose',
     'refresh',
     'force_update',
     'pre_solve_force_eval',
     'do_isolate',
     'display_grid',
     'display_node_types')
)


def createExecuteOptions(verbose=False,
                         refresh=False,
                         force_update=False,
                         do_isolate=False,
                         pre_solve_force_eval=True,
                         display_grid=True,
                         display_node_types=None):
    """
    Create ExecuteOptions.

    :param verbose: Print extra solver information while a solve is running.
    :type verbose: bool

    :param refresh: Should the solver refresh the viewport while solving?
    :type refresh: bool

    :param force_update: Force updating the DG network, to help the
                         solver in case of a Maya evaluation DG bug.
    :type force_update: bool

    :param do_isolate: Isolate only solving objects while performing
                       the solve.
    :type do_isolate: bool

    :param display_grid: Display grid in the viewport while performing
                         the solve?
    :type display_grid: bool

    :param display_node_types: Allow a dict to be passed to the function
                               specifying the object type and the
                               visibility status during solving. This
                               allows us to turn on/off any object type
                               during solving. If an argument is not
                               given or is None, the object type
                               visibility will not be changed.
    """
    if display_node_types is None:
        display_node_types = dict()
    options = ExecuteOptions(
        verbose=verbose,
        refresh=refresh,
        force_update=force_update,
        do_isolate=do_isolate,
        pre_solve_force_eval=pre_solve_force_eval,
        display_grid=display_grid,
        display_node_types=display_node_types
    )
    return options


def preSolve_updateProgress(prog_fn, status_fn):
    LOG.debug('preSolve_updateProgress')
    # Start up solver
    collectionutils.run_progress_func(prog_fn, 0)
    ts = solveresult.format_timestamp(time.time())
    collectionutils.run_status_func(status_fn, 'Solve start (%s)' % ts)
    api_state.set_solver_running(True)
    return


def preSolve_queryViewportState(options, panels):
    """
    If 'refresh' is 'on' change all viewports to 'isolate
    selected' on only the markers and bundles being solved. This
    will speed up computations, especially per-frame solving as
    it will not re-compute any invisible nodes (such as rigs or
    image planes).

    :param options:
    :param panels:
    :return:
    """
    LOG.debug('preSolve_queryViewportState')
    panel_objs = {}
    panel_node_type_vis = collections.defaultdict(dict)
    if options.refresh is not True:
        return panel_objs, panel_node_type_vis

    display_node_types = options.display_node_types
    if display_node_types is not None:
        assert isinstance(display_node_types, dict)
        for panel in panels:
            node_types = display_node_types.keys()
            node_type_vis = dict()
            for node_type in node_types:
                value = viewport_utils.get_node_type_visibility(panel, node_type)
                node_type_vis[node_type] = value
            panel_node_type_vis[panel] = node_type_vis

    if options.do_isolate is True:
        for panel in panels:
            state = maya.cmds.isolateSelect(
                panel,
                query=True,
                state=True)
            nodes = None
            if state is True:
                nodes = viewport_utils.get_isolated_nodes(panel)
            panel_objs[panel] = nodes

    return panel_objs, panel_node_type_vis


def preSolve_setIsolatedNodes(actions_list, options, panels):
    """
    Prepare frame solve

    Isolate all nodes used in all of the kwargs to be run.
    Note; This assumes the isolated objects are visible, but
    they may actually be hidden.
    """
    LOG.debug('preSolve_setIsolatedNodes')
    if options.refresh is not True:
        return
    s = time.time()
    if options.do_isolate is True:
        isolate_nodes = set()
        for action in actions_list:
            kwargs = action.kwargs
            isolate_nodes |= collectionutils.generate_isolate_nodes(kwargs)
        if len(isolate_nodes) == 0:
            raise excep.NotValid
        isolate_node_list = list(isolate_nodes)
        for panel in panels:
            viewport_utils.set_isolated_nodes(panel, isolate_node_list, True)

    display_node_types = options.display_node_types
    if display_node_types is not None:
        assert isinstance(display_node_types, dict)
        for panel in panels:
            for node_type, value in display_node_types.items():
                if value is None:
                    continue
                assert isinstance(value, bool)
                viewport_utils.set_node_type_visibility(panel, node_type, value)

    e = time.time()
    LOG.debug('Perform Pre-Isolate; time=%r', e - s)
    return


def preSolve_triggerEvaluation(action_list, cur_frame, options):
    """
    Set the first current time to the frame before current.

    This is to help trigger evaluations on the 'current
    frame', if the current frame is the same as the first
    frame.

    :param action_list:
    :type action_list: [Action, .. ]

    :param cur_frame:
    :type cur_frame: int or float

    :param options:
    :type options:
    """
    LOG.debug('preSolve_triggerEvaluation')
    if options.pre_solve_force_eval is not True:
        return
    s = time.time()
    frame_list = []
    for action in action_list:
        kwargs = action.kwargs
        frame_list += kwargs.get('frame', [])
    frame_list = list(set(frame_list))
    frame_list = list(sorted(frame_list))
    is_whole_solve_single_frame = len(frame_list) == 1
    if is_whole_solve_single_frame is False:
        maya.cmds.currentTime(
            cur_frame - 1,
            edit=True,
            update=options.force_update,
            )
    e = time.time()
    LOG.debug('Update previous of current time; time=%r', e - s)
    return


def postSolve_refreshViewport(options, frame):
    LOG.debug(
        'postSolve_refreshViewport: '
        'options=%r '
        'frame=%r ',
        options,
        frame)
    
    # Refresh the Viewport.
    if options.refresh is not True:
        return
    # TODO: If we solve per-frame without "refresh"
    # on, then we get wacky solves
    # per-frame. Interestingly, the 'force_update'
    # does not seem to make a difference, just the
    # 'maya.cmds.refresh' call.
    #
    # Test scene file:
    # ./tests/data/scenes/mmSolverBasicSolveD_before.ma
    s = time.time()
    maya.cmds.currentTime(
        frame[0],
        edit=True,
        update=options.force_update,
    )
    # TODO: Refresh should not add to undo queue, we
    # should skip it. This should fix the problem of
    # stepping over the viewport each time we undo an
    # 'animated' solve. Or we pause the viewport while
    # we undo?
    maya.cmds.refresh()
    e = time.time()
    LOG.debug('Refresh Viewport; time=%r', e - s)
    return


def postSolve_setViewportState(options, panel_objs, panel_node_type_vis):
    LOG.debug(
        'postSolve_setViewportState: '
        'options=%r '
        'panel_objs=%r '
        'panel_node_type_vis=%r',
        options,
        panel_objs,
        panel_node_type_vis)
    if options.refresh is not True:
        return
    s = time.time()

    # Isolate Objects restore.
    for panel, objs in panel_objs.items():
        if objs is None:
            # No original objects, disable 'isolate
            # selected' after resetting the objects.
            if options.do_isolate is True:
                viewport_utils.set_isolated_nodes(panel, [], False)
        else:
            if options.do_isolate is True:
                viewport_utils.set_isolated_nodes(panel, list(objs), True)

    # Show menu restore.
    for panel, node_types_vis in panel_node_type_vis.items():
        for node_type, value in node_types_vis.items():
            LOG.debug('turn on node_type=%r with value=%r', node_type, value)
            if value is None:
                continue
            viewport_utils.set_node_type_visibility(panel, node_type, value)

    e = time.time()
    LOG.debug('Finally; reset isolate selected; time=%r', e - s)
    return


def postSolve_setUpdateProgress(progress_min,
                                progress_value,
                                progress_max,
                                solres,  # SolveResult or None
                                prog_fn, status_fn):
    LOG.debug(
        'postSolve_setUpdateProgress: '
        'progress_min=%r '
        'progress_value=%r '
        'progress_max=%r '
        'solres=%r '
        'prog_fn=%r '
        'status_fn=%r',
        progress_min,
        progress_value,
        progress_max,
        solres,
        prog_fn, status_fn)
    stop_solving = False

    # Update progress
    ratio = float(progress_value) / float(progress_max)
    percent = float(progress_min) + (ratio * (100.0 - progress_min))
    collectionutils.run_progress_func(prog_fn, int(percent))

    # Check if the user wants to stop solving.
    if solres is None:
        cmd_cancel = False
    else:
        cmd_cancel = solres.get_user_interrupted()
    gui_cancel = api_state.get_user_interrupt()
    if cmd_cancel is True or gui_cancel is True:
        msg = 'Cancelled by User'
        api_state.set_user_interrupt(False)
        collectionutils.run_status_func(status_fn, 'WARNING: ' + msg)
        LOG.warning(msg)
        stop_solving = True
    if (solres is not None) and (solres.get_success() is False):
        msg = 'Solver failed!!!'
        collectionutils.run_status_func(status_fn, 'ERROR: ' + msg)
        LOG.error(msg)
    return stop_solving


def execute(col,
            options=None,
            log_level=None,
            prog_fn=None,
            status_fn=None,
            info_fn=None):
    """
    Compile the collection, then pass that data to the 'mmSolver' command.

    The mmSolver command will return a list of strings, which will then be
    passed to the SolveResult class so the user can query the raw data
    using an interface.

    :param col: The Collection to execute.
    :type col: Collection

    :param options: The options for the execution.
    :type options: ExecuteOptions

    :param log_level: The log level for the execution.
    :type log_level: str

    :param prog_fn: The function used report progress messages to
                    the user.
    :type prog_fn: callable or None

    :param status_fn: The function used to report status messages
                      to the user.
    :type status_fn: callable or None

    :param info_fn: The function used to report information
                    messages to the user.
    :type info_fn: callable or None

    :return: List of SolveResults from the executed collection.
    :rtype: [SolverResult, ..]
    """
    if options is None:
        options = createExecuteOptions()
    if log_level is None:
        log_level = 'info'
    assert isinstance(log_level, (str, unicode))

    start_time = time.time()

    # Ensure the plug-in is loaded, so we fail before trying to run.
    api_utils.load_plugin()
    assert 'mmSolver' in dir(maya.cmds)

    # TODO: Pause viewport 2.0 while solving? Assumes viewport 2 is
    # used.  This might not be supported below Maya 2017?

    # TODO: Test if 'isolate selected' works at all perhaps we're
    #  better off just turning the node types on/off.

    panels = viewport_utils.get_all_model_panels()
    panel_objs, panel_node_type_vis = preSolve_queryViewportState(
        options, panels
    )

    # Save current frame, to revert to later on.
    cur_frame = maya.cmds.currentTime(query=True)

    try:
        preSolve_updateProgress(prog_fn, status_fn)

        # Check for validity and compile actions.
        solres_list = []
        col_node = col.get_node()
        sol_list = col.get_solver_list()
        mkr_list = col.get_marker_list()
        attr_list = col.get_attribute_list()
        try:
            actions_list = api_compile.collection_compile(
                col_node,
                sol_list,
                mkr_list,
                attr_list,
                prog_fn=prog_fn, status_fn=status_fn
            )
        except excep.NotValid as e:
            # Not valid
            # LOG.warning('Collection not valid: %r', col.get_node())
            LOG.warning(e)
            return solres_list
        collectionutils.run_progress_func(prog_fn, 1)

        # Prepare frame solve
        preSolve_setIsolatedNodes(actions_list, options, panels)
        preSolve_triggerEvaluation(actions_list, cur_frame, options)

        # Run Solver Actions...
        start = 0
        total = len(actions_list)
        for i, action in enumerate(actions_list):
            func, args, kwargs = api_action.action_to_components(action)
            func_is_mmsolver = api_action.action_func_is_mmSolver(action)

            save_node_attrs = None
            is_single_frame = None
            if func_is_mmsolver is True:
                frame = kwargs.get('frame')
                collectionutils.run_status_func(info_fn, 'Evaluating frames %r' % frame)
                if frame is None or len(frame) == 0:
                    raise excep.NotValid

                # Write solver flags to a debug file.
                debug_file_path = kwargs.get('debugFile', None)
                if debug_file_path is not None:
                    options_file_path = debug_file_path.replace('.log', '.flags')
                    text = pprint.pformat(kwargs)
                    with open(options_file_path, 'w') as file_:
                        file_.write(text)

                # Overriding the verbosity, irrespective of what
                # the solver verbosity value is set to.
                if log_level is not None and log_level.lower() == 'verbose':
                    kwargs['verbose'] = True

                # TODO: Try to test and remove the need to disconnect
                #  and re-connect animation curves.
                #
                # HACK for single frame solves.
                save_node_attrs = []
                is_single_frame = collectionutils.is_single_frame(kwargs)
                if is_single_frame is True:
                    save_node_attrs = collectionutils.disconnect_animcurves(kwargs)

            # TODO: Detect if we can re-run the mmSolver command
            #  multiple times, to get better quality.
            #
            # TODO: Run the solver multiple times for a hierarchy. First,
            #  solve DAG level 0 nodes, then add DAG level 1, then level 2,
            #  etc. This will allow us to incrementally add solving of
            #  hierarchy, without getting the optimiser confused which
            #  attributes to solve first to get a stable solve.
            #
            # Run Solver Maya plug-in command
            solve_data = func(*args, **kwargs)

            # Revert special HACK for single frame solves
            if func_is_mmsolver is True:
                if is_single_frame is True:
                    collectionutils.reconnect_animcurves(kwargs, save_node_attrs)

            # Create SolveResult.
            solres = None
            if solve_data is not None and func_is_mmsolver is True:
                solres = solveresult.SolveResult(solve_data)
                solres_list.append(solres)

            # Update Progress
            interrupt = postSolve_setUpdateProgress(
                start, i, total, solres,
                prog_fn, status_fn
            )
            if interrupt is True:
                break

            # Refresh the Viewport.
            if func_is_mmsolver is True:
                frame = kwargs.get('frame')
                postSolve_refreshViewport(options, frame)
    finally:
        postSolve_setViewportState(
            options, panel_objs, panel_node_type_vis
        )

        collectionutils.run_status_func(status_fn, 'Solve Ended')
        collectionutils.run_progress_func(prog_fn, 100)
        api_state.set_solver_running(False)
        maya.cmds.currentTime(cur_frame, edit=True, update=True)

    # Store output information of the solver.
    end_time = time.time()
    duration = end_time - start_time
    col._set_last_solve_timestamp(end_time)
    col._set_last_solve_duration(duration)
    col._set_last_solve_results(solres_list)
    return solres_list
