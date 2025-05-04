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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import time
import pprint

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.converttypes as convert_types_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.state as api_state
import mmSolver._api.utils as api_utils
import mmSolver._api.compile as api_compile
import mmSolver._api.excep as excep
import mmSolver._api.solveresult as solveresult
import mmSolver._api.action as api_action
import mmSolver._api.collectionutils as collectionutils
import mmSolver._api.constant as const

import mmSolver._api._execute.options as executeoptions
import mmSolver._api._execute.postsolve as executepostsolve
import mmSolver._api._execute.presolve as executepresolve
import mmSolver._api._execute.actionstate as actionstate


LOG = mmSolver.logger.get_logger()


def validate(col, as_state=None):
    """
    Validates the given collection state, is it ready for solving?

    :param col: The Collection object to be validated.
    :type col: Collection

    :param as_state: If True, return an ActionState class, rather
        than a big plain-old-data structure (documented below).
    :type as_state: bool

    :return:
        A list of states of the validations, or a list of validations,
        with a single valid boolean (did the validation succeed?).
        See :py:func:`_run_validate_action` function return types
        for more details.
    :rtype: (bool, [str, ..], [(int, int, int), ..]) or [ActionState, ..]
    """
    # TODO: Remove the 'as_state' keyword in v0.5.0 release and
    #  always return the ActionState.
    if as_state is None:
        as_state = False
    state_list = []
    try:
        sol_list = col.get_solver_list()
        mkr_list = col.get_marker_list()
        attr_list = col.get_attribute_list()
        action_list, vaction_list = api_compile.collection_compile(
            col,
            sol_list,
            mkr_list,
            attr_list,
            withtest=True,
            prog_fn=None,
            status_fn=None,
        )
    except excep.NotValid as e:
        LOG.warn(e)
        state = actionstate.create_action_state(
            status=const.ACTION_STATUS_FAILED,
            message=str(e),
            error_number=0,
            parameter_number=0,
            frames_number=0,
        )
        state_list.append(state)
        if as_state is False:
            return actionstate.convert_action_state_to_plain_old_data(state_list)
        return state_list

    if len(vaction_list) > 0:
        state_list = actionstate.run_validate_action_list(vaction_list)

    if as_state is False:
        return actionstate.convert_action_state_to_plain_old_data(state_list)
    return state_list


def _validate_scene_graph_in_actions(action_list, vaction_list):
    """
    Run any mmSolverSceneGraph functions and detect failure.
    """
    is_valid = True
    for i, (action, vaction) in enumerate(zip(action_list, vaction_list)):
        func_is_scene_graph = api_action.action_func_is_mmSolverSceneGraph(action)
        if func_is_scene_graph is not True:
            continue

        func, args, kwargs = api_action.action_to_components(action)
        result = func(*args, **kwargs)
        if result is False:
            LOG.warn("Solver inputs are not compatible with Scene Graph.")
            is_valid = False
            break
    return is_valid


def _override_actions_set_results_node(col, action_list, vaction_list):
    col_node = col.get_node()
    assert col_node is not None
    assert maya.cmds.objExists(col_node)

    new_action_list = []
    new_vaction_list = []
    for action, vaction in zip(action_list, vaction_list):
        is_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(action)
        vis_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(vaction)
        if is_mmsolver_v2 is False or vis_mmsolver_v2 is False:
            new_action_list.append(action)
            new_vaction_list.append(vaction)
            continue

        func, args, kwargs = api_action.action_to_components(action)
        vfunc, vargs, vkwargs = api_action.action_to_components(vaction)
        kwargs['resultsNode'] = col_node
        vkwargs['resultsNode'] = col_node

        new_action = api_action.Action(func=func, args=args, kwargs=kwargs)
        new_vaction = api_action.Action(func=vfunc, args=vargs, kwargs=vkwargs)
        new_action_list.append(new_action)
        new_vaction_list.append(new_vaction)

    action_list = new_action_list
    vaction_list = new_vaction_list
    return action_list, vaction_list


def _override_actions_scene_graph_use_maya_dag(action_list, vaction_list):
    new_action_list = []
    new_vaction_list = []
    for action, vaction in zip(action_list, vaction_list):
        is_mmsolver_v1 = api_action.action_func_is_mmSolver_v1(action)
        is_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(action)
        if any((is_mmsolver_v1, is_mmsolver_v2)) is not True:
            continue

        func, args, kwargs = api_action.action_to_components(action)
        kwargs['sceneGraphMode'] = const.SCENE_GRAPH_MODE_MAYA_DAG

        vfunc = None
        vargs = None
        vkwargs = None
        if vaction is not None:
            vfunc, vargs, vkwargs = api_action.action_to_components(vaction)
            vkwargs['sceneGraphMode'] = const.SCENE_GRAPH_MODE_MAYA_DAG

        frame_solve_mode = kwargs.get(
            'frameSolveMode', const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE
        )
        if frame_solve_mode == const.FRAME_SOLVE_MODE_PER_FRAME:
            frames = list(kwargs['frame'])
            for frame in frames:
                kwargs['frame'] = [frame]
                new_action = api_action.Action(
                    func=func, args=args, kwargs=kwargs.copy()
                )
                new_action_list.append(new_action)

                if vaction is not None:
                    vkwargs['frame'] = [frame]
                    new_vaction = api_action.Action(
                        func=vfunc, args=vargs, kwargs=vkwargs.copy()
                    )
                    new_vaction_list.append(new_vaction)
        else:
            new_action = api_action.Action(func=func, args=args, kwargs=kwargs)
            new_vaction = api_action.Action(func=vfunc, args=vargs, kwargs=vkwargs)
            new_action_list.append(new_action)
            new_vaction_list.append(new_vaction)

    action_list = new_action_list
    vaction_list = new_vaction_list
    return action_list, vaction_list


def _pretty_int_list(frames):
    frame_str = ''
    if isinstance(frames, list):
        frame_str = convert_types_utils.intListToString(frames)
    if len(frame_str) > 99:
        frame_str = frame_str[:48] + '...' + frame_str[-48:]
    return frame_str


def execute(
    col,
    options=None,
    validate_mode=None,
    log_level=None,
    prog_fn=None,
    status_fn=None,
    info_fn=None,
):
    """
    Compile the collection, then pass that data to the 'mmSolver' command.

    The mmSolver command will return a list of strings, which will then be
    passed to the SolveResult class so the user can query the raw data
    using an interface.

    :param col: The Collection to execute.
    :type col: Collection

    :param options: The options for the execution.
    :type options: ExecuteOptions

    :param validate_mode: How should the solve validate? Must be one of
                          the VALIDATE_MODE_VALUE_LIST values.
    :type validate_mode: str or None

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
        options = executeoptions.create_execute_options()
    if validate_mode is None:
        validate_mode = const.VALIDATE_MODE_PRE_VALIDATE_VALUE
    assert validate_mode in const.VALIDATE_MODE_VALUE_LIST
    if log_level is None:
        log_level = const.LOG_LEVEL_DEFAULT
    assert isinstance(log_level, pycompat.TEXT_TYPE)
    assert log_level in const.LOG_LEVEL_LIST
    validate_runtime = validate_mode == const.VALIDATE_MODE_AT_RUNTIME_VALUE
    validate_before = validate_mode == const.VALIDATE_MODE_PRE_VALIDATE_VALUE

    start_time = time.time()

    # Ensure the plug-in is loaded, so we error before trying to run.
    api_utils.load_plugin()
    assert 'mmSolver' in dir(maya.cmds)

    vp2_state = viewport_utils.get_viewport2_active_state()
    current_eval_manager_mode = maya.cmds.evaluationManager(query=True, mode=True)

    panels = viewport_utils.get_all_model_panels()
    panel_objs, panel_node_type_vis = executepresolve.preSolve_queryViewportState(
        options.refresh, options.do_isolate, options.display_node_types, panels
    )

    # Save scene state, to revert to later on.
    cur_frame = maya.cmds.currentTime(query=True)
    prev_auto_key_state = maya.cmds.autoKeyframe(query=True, state=True)
    prev_cycle_check = maya.cmds.cycleCheck(query=True, evaluation=True)

    # State information needed to revert reconnect animation curves in
    # 'finally' block.
    kwargs = {}
    save_node_attrs = []
    marker_relock_nodes = set()
    collection_relock_nodes = set()
    func_is_mmsolver_v1 = False
    func_is_mmsolver_v2 = False
    is_single_frame = False

    try:
        if options.disable_viewport_two is True:
            viewport_utils.set_viewport2_active_state(False)
        maya.cmds.autoKeyframe(edit=True, state=False)
        maya.cmds.evaluationManager(mode='off')
        maya.cmds.cycleCheck(evaluation=False)
        executepresolve.preSolve_updateProgress(prog_fn, status_fn)

        # Check for validity and compile actions.
        withtest = validate_mode in [
            const.VALIDATE_MODE_PRE_VALIDATE_VALUE,
            const.VALIDATE_MODE_AT_RUNTIME_VALUE,
        ]
        sol_list = col.get_solver_list()
        mkr_list = col.get_marker_list()
        attr_list = col.get_attribute_list()
        try:
            action_list, vaction_list = api_compile.collection_compile(
                col,
                sol_list,
                mkr_list,
                attr_list,
                withtest=withtest,
                prog_fn=prog_fn,
                status_fn=status_fn,
            )
        except excep.NotValid as e:
            LOG.warn(e)
            return []
        collectionutils.run_progress_func(prog_fn, 1)

        force_maya_dag_scene_graph = (
            _validate_scene_graph_in_actions(action_list, vaction_list) is False
        )
        if force_maya_dag_scene_graph is True:
            action_list, vaction_list = _override_actions_scene_graph_use_maya_dag(
                action_list, vaction_list
            )

        # Prepare nodes so they can be set from mmSolver commands,
        # without needing to unlock attributes (which is not possible
        # using MDGModifier API class).
        collection_relock_nodes |= executepresolve.preSolve_unlockCollectionAttrs(col)
        marker_relock_nodes |= executepresolve.preSolve_unlockMarkerAttrs(mkr_list)

        # Prepare frame solve
        executepresolve.preSolve_setIsolatedNodes(
            action_list,
            options.refresh,
            options.do_isolate,
            options.display_node_types,
            panels,
        )
        executepresolve.preSolve_triggerEvaluation(
            action_list, cur_frame, options.pre_solve_force_eval, options.force_update
        )

        # Ensure prediction attributes are created and initialised.
        collectionutils.set_initial_prediction_attributes(col, attr_list, cur_frame)

        # Ensure the resultsNode flag is set for mmSolver_v2 commands.
        action_list, vaction_list = _override_actions_set_results_node(
            col, action_list, vaction_list
        )

        vaction_state_list = []
        if validate_before is True:
            vaction_state_list = actionstate.run_validate_action_list(vaction_list)
            assert len(vaction_list) == len(vaction_state_list)

        # Run Solver Actions...
        solres_list = []
        message_hashes = set()
        start = 0
        total = len(action_list)
        number_of_solves = 0
        for i, (action, vaction) in enumerate(zip(action_list, vaction_list)):
            state = None
            if len(vaction_state_list) > 0:
                # We have pre-computed the state list.
                state = vaction_state_list[i]
            if isinstance(vaction, api_action.Action) and validate_runtime:
                # We will calculate the state just-in-time.
                state = actionstate.run_validate_action(vaction)
            if state is not None:
                if state.status != const.ACTION_STATUS_SUCCESS:
                    assert isinstance(state, actionstate.ActionState)
                    h = hash(state.message)
                    if h not in message_hashes:
                        LOG.warn(state.message)
                    message_hashes.add(h)
                    # Skip this action, since the test failed.
                    continue

            func, args, kwargs = api_action.action_to_components(action)
            func_is_mmsolver_v1 = api_action.action_func_is_mmSolver_v1(action)
            func_is_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(action)
            func_is_mmsolver = any((func_is_mmsolver_v2, func_is_mmsolver_v1))
            # func_is_mmsolveraffects = api_action.action_func_is_mmSolverAffects(action)
            func_is_scene_graph = api_action.action_func_is_mmSolverSceneGraph(action)
            func_is_camera_solve = api_action.action_func_is_camera_solve(action)

            if func_is_scene_graph is True:
                # The scene graph tests have already been tested in a
                # pre-process, so we can skip them now we're properly
                # solving.
                continue

            if func_is_mmsolver is True:
                frame = kwargs.get('frame')
                if frame is None or len(frame) == 0:
                    raise excep.NotValid

                frame_str = _pretty_int_list(frame)
                collectionutils.run_status_func(
                    info_fn, 'Evaluating {} frames: {}'.format(len(frame), frame_str)
                )

                # Write solver flags to a debug file.
                debug_file_path = kwargs.get('debugFile', None)
                if debug_file_path is not None:
                    options_file_path = debug_file_path.replace('.log', '.flags')
                    text = pprint.pformat(kwargs)
                    with open(options_file_path, 'w') as file_:
                        file_.write(text)

                # Overriding the log level.
                if log_level is not None:
                    kwargs['logLevel'] = const.LOG_LEVEL_NAME_TO_VALUE_MAP[log_level]

                # HACK for single frame solves.
                is_single_frame = collectionutils.is_single_frame(kwargs)
                if is_single_frame is True:
                    save_node_attrs = collectionutils.disconnect_animcurves(kwargs)
                else:
                    # Reset the data structure so in the 'finally'
                    # block we can detect animcurves are not needing
                    # to be reset.
                    save_node_attrs = []

                if force_maya_dag_scene_graph is True:
                    kwargs['sceneGraphMode'] = const.SCENE_GRAPH_MODE_MAYA_DAG

            elif func_is_camera_solve is True:
                root_frames = args[6]
                start_frame = args[7]
                end_frame = args[8]
                assert isinstance(root_frames, list)
                assert isinstance(start_frame, int)
                assert isinstance(end_frame, int)
                root_frames_str = _pretty_int_list(root_frames)
                msg = 'Solving Camera frames: {frames} ({start}-{end})'.format(
                    frames=root_frames_str, start=start_frame, end=end_frame
                )
                collectionutils.run_status_func(info_fn, msg)

            debug_func_inputs_outputs = False
            if debug_func_inputs_outputs:
                current_datetime = datetime.datetime.now()
                LOG.debug(
                    'Running: %s func=%r args=%s kwargs=%s',
                    current_datetime,
                    func,
                    pprint.pformat(args),
                    pprint.pformat(kwargs),
                )

            # Run Solver Maya plug-in command.
            solve_data = func(*args, **kwargs)

            if debug_func_inputs_outputs:
                LOG.debug(
                    'Returned: %s func solve_data=%s',
                    current_datetime,
                    pprint.pformat(solve_data),
                )

            # Revert special HACK for single frame solves
            if func_is_mmsolver is True:
                if is_single_frame is True:
                    collectionutils.reconnect_animcurves(kwargs, save_node_attrs)
                    # Reset the data structure so in the 'finally'
                    # block we can detect animcurves are not needing
                    # to be reset.
                    save_node_attrs = []

            # TODO: Allow the solver version to be passed in.
            solver_version = const.SOLVER_VERSION_DEFAULT

            # Create SolveResult.
            solres = None
            if solve_data is not None:
                if func_is_mmsolver_v2 is True:
                    solve_data = kwargs['resultsNode']
                    solres = solveresult.SolveResult(solve_data)
                    solres_list.append(solres)
                elif func_is_mmsolver_v1 is True:
                    solres = solveresult.SolveResult(solve_data)
                    solres_list.append(solres)
                elif func_is_scene_graph is True:
                    solres = solve_data
                elif func_is_camera_solve is True:
                    if solver_version == const.SOLVER_VERSION_TWO:
                        solve_data = args[0]  # Get the collection node.
                    solres = solveresult.SolveResult(solve_data)
                    solres_list.append(solres)

            if func_is_mmsolver_v1 is True and solres.get_success() is True:
                frame = kwargs.get('frame')
                if frame is None or len(frame) == 0:
                    raise excep.NotValid
                single_frame = frame[0]

                if number_of_solves == 0:
                    collectionutils.set_initial_prediction_attributes(
                        col, attr_list, single_frame
                    )
                # Count number of solves, so we don't need to set the
                # initial prediction attributes again.
                number_of_solves += 1

                # Calculate the mean, variance values, and predict the
                # next attribute value.
                collectionutils.compute_attribute_value_prediction(
                    col,
                    attr_list,
                    single_frame,
                )

            # Update Progress
            interrupt = executepostsolve.postSolve_setUpdateProgress(
                start, i, total, solres, prog_fn, status_fn
            )
            if interrupt is True:
                break

            # Refresh the Viewport.
            if func_is_mmsolver_v1 is True:
                frame = kwargs.get('frame')
                executepostsolve.postSolve_refreshViewport(
                    options.refresh, options.force_update, frame
                )
    finally:
        # If something has gone wrong, or the user cancels the solver
        # without finishing, then we make sure to reconnect animcurves
        # that were disconnected for single frame solves.
        if func_is_mmsolver_v1 is True and is_single_frame is True:
            if len(save_node_attrs):
                collectionutils.reconnect_animcurves(kwargs, save_node_attrs)

        # Re-lock attributes that were unlocked so that the
        # mmSolver command could set values on them.
        executepostsolve.postSolve_relockCollectionAttrs(collection_relock_nodes)
        executepostsolve.postSolve_relockMarkerAttrs(marker_relock_nodes)
        collection_relock_nodes = set()
        marker_relock_nodes = set()

        executepostsolve.postSolve_setViewportState(
            options.refresh, options.do_isolate, panel_objs, panel_node_type_vis
        )
        collectionutils.run_status_func(status_fn, 'Solve Ended')
        collectionutils.run_progress_func(prog_fn, 100)
        maya.cmds.evaluationManager(mode=current_eval_manager_mode[0])
        maya.cmds.cycleCheck(evaluation=prev_cycle_check)
        maya.cmds.autoKeyframe(edit=True, state=prev_auto_key_state)
        api_state.set_solver_running(False)
        if options.disable_viewport_two is True:
            viewport_utils.set_viewport2_active_state(vp2_state)
        maya.cmds.currentTime(cur_frame, edit=True, update=options.force_update)

    # Store output information of the solver.
    end_time = time.time()
    duration = end_time - start_time
    col._set_last_solve_timestamp(end_time)
    col._set_last_solve_duration(duration)
    col._set_last_solve_results(solres_list)
    return solres_list
