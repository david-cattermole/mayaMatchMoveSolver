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
The standard solver - allows solving static and animated attributes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger

import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.marker as marker
import mmSolver._api.solverutils as solverutils
import mmSolver._api.solverstep as solverstep
import mmSolver._api.solvertriangulate as solvertriangulate
import mmSolver._api.markerutils as markerutils
import mmSolver._api.rootframe as rootframe
import mmSolver._api.action as api_action
import mmSolver._api.compile as api_compile


LOG = mmSolver.logger.get_logger()


def _gen_two_frame_fwd(int_list):
    """
    Given a list of integers, create list of Frame pairs, moving
    though the original list in a forward direction.

    :param int_list: List of frame numbers.
    :type int_list: List of int

    :returns: List of integer pairs.
    :rtype: [[int, int], ...]
    """
    if len(int_list) == 1:
        num = int_list[0]
        batch_list = [[frame.Frame(num), frame.Frame(num)]]
        return batch_list
    end = len(int_list) - 1
    batch_list = []
    for i in range(end):
        s = i
        e = i + 2
        tmp_list = int_list[s:e]
        frm_list = []
        for j, num in enumerate(tmp_list):
            frm = frame.Frame(num)
            frm_list.append(frm)
        batch_list.append(frm_list)
    return batch_list


def _filter_mkr_list_by_frame_list(mkr_list, frame_list):
    """
    Sort the Markers into used and unused based on the frames needed.

    :param mkr_list: List of Markers to filter.
    :type mkr_list: [Marker, ..]

    :param frame_list: List of frames to use for filtering.
    :type frame_list: [Frame, ..]

    :return: Two lists, one list is for Markers that have 2 or more
             frames specified in frame_list, and the other list is
             for Markers that do not have more than 2 frames in
             frame_list.
    :rtype: ([Marker, ..], [Marker, ..])
    """
    frame_list_num = [x.get_number() for x in frame_list]
    used_mkr_list = []
    unused_mkr_list = []
    for mkr in mkr_list:
        assert isinstance(mkr, marker.Marker) is True
        frame_count = 0
        for f in frame_list_num:
            frame_count += mkr.get_enable(f)
        if frame_count >= 2:
            used_mkr_list.append(mkr)
        else:
            unused_mkr_list.append(mkr)
    return used_mkr_list, unused_mkr_list


def _compile_multi_root_frames(
    col,
    mkr_list,
    attr_list,
    batch_frame_list,
    root_iter_num,
    use_attr_blocks,
    remove_unused_objects,
    solver_version,
    solver_type,
    scene_graph_mode,
    precomputed_data,
    withtest,
    verbose,
):
    """
    Compile actions for solving Root frames.

    :param mkr_list:
        List of Markers to use for Root frames.
    :type mkr_list: [Marker, ..]

    :param attr_list:
        List of Attributes to use for Root frames.
    :type attr_list: [Attribute, ..]

    :param batch_frame_list:
        List of frame lists to be computed successively.
    :type batch_frame_list: [[int, ..], ..]

    :param root_iter_num:
        Number of iterations to use, when solving root frames.
    :type root_iter_num: int

    :param remove_unused_objects:
        Should objects that are detected as 'unused' be removed from
        the solver?
    :type remove_unused_objects: bool

    :param solver_version:
        Which Solver Version should be used?
        A value in mmSolver.api.SOLVER_VERSION_LIST.
    :type solver_version: int

    :param solver_type:
        Which Solver type should be used?
        A value in mmSolver.api.SOLVER_TYPE_*.
    :type solver_type: int

    :param scene_graph_mode:
        Which Scene Graph should be used? 0=Maya DAG or 1=MM Scene Graph.
    :type scene_graph_mode: int

    :param withtest:
        Compile the test/validation Action, as well as the solve Action?
    :type withtest: bool

    :param verbose:
        Print out more detail to 'stderr'.
    :type verbose: bool

    :return:
        Yields two Actions at each iteration; first Action is for
        solving, second Action is to validate the inputs given.
    :rtype: (Action, Action or None)
    """
    assert isinstance(root_iter_num, int)
    assert isinstance(remove_unused_objects, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(scene_graph_mode, int)
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    # Solve root frames.
    for frm_list in batch_frame_list:
        # Get root markers
        root_mkr_list, non_root_mkr_list = _filter_mkr_list_by_frame_list(
            mkr_list, frm_list
        )
        assert len(root_mkr_list) > 0

        mkr_attr_map = markerutils.find_marker_attr_mapping(root_mkr_list, attr_list)
        root_attr_list = []
        for i, mkr in enumerate(root_mkr_list):
            for j, attr in enumerate(attr_list):
                x = mkr_attr_map[i][j]
                if x is True and attr not in root_attr_list:
                    root_attr_list.append(attr)

        attr_blocks = solverutils.create_attr_blocks(use_attr_blocks, root_attr_list)

        sol = solverstep.SolverStep()
        sol.set_max_iterations(root_iter_num)
        sol.set_frame_list(frm_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)
        sol.set_solver_version(solver_version)
        sol.set_solver_type(solver_type)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE)
        sol.set_remove_unused_markers(remove_unused_objects)
        sol.set_remove_unused_attributes(remove_unused_objects)
        sol.set_precomputed_data(precomputed_data)

        cache = api_compile.create_compile_solver_cache()
        generator = solverutils.compile_solver_step_blocks_with_cache(
            sol, col, mkr_list, attr_blocks, withtest, cache
        )
        for action, vaction in generator:
            yield action, vaction
    return


def _compile_remove_inbetween_frames(
    attr_list, non_root_frame_list, start_frame, end_frame, withtest, verbose
):
    """
    Compile actions to delete keyframes for all attributes with-in a
    specific start/end frame range.

    :param attr_list:
        List of Attributes.
    :type attr_list: [Attribute, ..]

    :type non_root_frame_list: [[int, ..], ..]
    :type start_frame: Frame
    :type end_frame: Frame

    :param withtest:
        Compile the test/validation Action, as well as the solve Action?
    :type withtest: bool

    :param verbose:
        Print out more detail to 'stdout'.
    :type verbose: bool

    :return:
        Yields an Action and None, at each iteration.
    :rtype: (Action, None)
    """
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)

    attr_names = [x.get_name() for x in attr_list]

    for frm in non_root_frame_list:
        frame_num = frm.get_number()
        func = 'maya.cmds.cutKey'
        args = attr_names
        kwargs = {'time': (frame_num, frame_num)}
        action = api_action.Action(func=func, args=args, kwargs=kwargs)
        yield action, None

    # Change all attribute keyframes to linear tangents.
    func = 'maya.cmds.keyTangent'
    kwargs = {
        'inTangentType': 'linear',
        'outTangentType': 'linear',
        'time': (start_frame.get_number() - 1, end_frame.get_number() + 1),
    }
    action = api_action.Action(func=func, args=attr_names, kwargs=kwargs)
    yield action, None


def _compile_multi_inbetween_frames(
    col,
    mkr_list,
    attr_list,
    all_frame_list,
    global_solve,
    eval_complex_graphs,
    anim_iter_num,
    use_attr_blocks,
    remove_unused_objects,
    solver_version,
    solver_type,
    scene_graph_mode,
    precomputed_data,
    withtest,
    verbose,
):
    """
    Solve only animated attributes on frames between the root frames.

    :param mkr_list:
        Markers to be solved with.
    :type mkr_list: [Marker, ..]

    :param attr_list:
        Attributes to be solved.
    :type attr_list: [Attribute, ..]

    :param all_frame_list:
        List of Frames to be solved.
    :type all_frame_list: [Frame, ..]

    :param global_solve:
        If True, all attributes and frames will be solved as a single
        solve, rather than one solve per-frame.
    :type global_solve: bool

    :param eval_complex_graphs:
        If True, the solve will try to trigger evalation of complex
        node graphs (such as Mesh Rivets), by changing the timeEvalMode
        of the mmSolver command.
    :type eval_complex_graphs: bool

    :param anim_iter_num:
        Number of iterations for solving animated attributes.
    :type anim_iter_num: int

    :param remove_unused_objects:
        Should objects that are detected as 'unused' be removed from
        the solver?
    :type remove_unused_objects: bool

    :param solver_version:
        Which Solver Version should be used?
        A value in mmSolver.api.SOLVER_VERSION_LIST.
    :type solver_version: int

    :param solver_type:
        Which Solver type should be used?
        A value in mmSolver.api.SOLVER_TYPE_*.
    :type solver_type: int

    :param scene_graph_mode:
        Which Scene Graph should be used? 0=Maya DAG or 1=MM Scene Graph.
    :type scene_graph_mode: int

    :param withtest:
        Should validation tests be generated?
    :type withtest: bool

    :param verbose:
        Print out more detail than usual.
    :type verbose: bool

    :return:
        Yields a generator of two Actions. First Action is for solving,
        the second Action is for validation of inputs.
    :rtype: (Action, Action)
    """
    assert isinstance(global_solve, bool)
    assert isinstance(eval_complex_graphs, bool)
    assert isinstance(anim_iter_num, int)
    assert isinstance(remove_unused_objects, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(scene_graph_mode, int)
    assert isinstance(precomputed_data, dict)
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    attr_blocks = solverutils.create_attr_blocks(use_attr_blocks, attr_list)

    if global_solve is True:
        # Do Global Solve with all frames.
        sol = solverstep.SolverStep()
        sol.set_max_iterations(anim_iter_num)
        sol.set_frame_list(all_frame_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)
        sol.set_solver_version(solver_version)
        sol.set_solver_type(solver_type)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE)
        sol.set_remove_unused_markers(remove_unused_objects)
        sol.set_remove_unused_attributes(remove_unused_objects)
        sol.set_precomputed_data(precomputed_data)

        cache = api_compile.create_compile_solver_cache()
        generator = solverutils.compile_solver_step_blocks_with_cache(
            sol, col, mkr_list, attr_blocks, withtest, cache
        )
        for action, vaction in generator:
            yield action, vaction
    else:
        cache = api_compile.create_compile_solver_cache()

        if scene_graph_mode == const.SCENE_GRAPH_MODE_MAYA_DAG:
            for i, frm in enumerate(all_frame_list):
                is_first_frame = i == 0
                one_frame_list = [frm]
                time_eval_mode = const.TIME_EVAL_MODE_DEFAULT
                if eval_complex_graphs is True:
                    time_eval_mode = const.TIME_EVAL_MODE_SET_TIME

                sol = solverstep.SolverStep()
                sol.set_max_iterations(anim_iter_num)
                sol.set_frame_list(one_frame_list)
                sol.set_attributes_use_animated(True)
                sol.set_attributes_use_static(False)
                sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
                sol.set_use_smoothness(not is_first_frame)
                sol.set_use_stiffness(not is_first_frame)
                sol.set_solver_version(solver_version)
                sol.set_solver_type(solver_type)
                sol.set_scene_graph_mode(scene_graph_mode)
                sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE)
                sol.set_remove_unused_markers(remove_unused_objects)
                sol.set_remove_unused_attributes(remove_unused_objects)
                sol.set_time_eval_mode(time_eval_mode)
                sol.set_precomputed_data(precomputed_data)

                generator = solverutils.compile_solver_step_blocks_with_cache(
                    sol, col, mkr_list, attr_blocks, withtest, cache
                )
                for action, vaction in generator:
                    yield action, vaction

        elif scene_graph_mode == const.SCENE_GRAPH_MODE_MM_SCENE_GRAPH:
            # MM Scene Graph does not support smooth and stiff
            # attributes yet.
            use_smooth_stiff = False

            sol = solverstep.SolverStep()
            sol.set_max_iterations(anim_iter_num)
            sol.set_frame_list(all_frame_list)
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(False)
            sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
            sol.set_use_smoothness(use_smooth_stiff)
            sol.set_use_stiffness(use_smooth_stiff)
            sol.set_solver_version(solver_version)
            sol.set_solver_type(solver_type)
            sol.set_scene_graph_mode(scene_graph_mode)
            sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_PER_FRAME)
            sol.set_remove_unused_markers(remove_unused_objects)
            sol.set_remove_unused_attributes(remove_unused_objects)
            sol.set_precomputed_data(precomputed_data)

            cache = api_compile.create_compile_solver_cache()
            generator = solverutils.compile_solver_step_blocks_with_cache(
                sol, col, mkr_list, attr_blocks, withtest, cache
            )
            for action, vaction in generator:
                yield action, vaction
    return


def compile_multi_frame(
    col,
    mkr_list,
    attr_list,
    root_frame_list,
    frame_list,
    use_attr_blocks,
    block_iter_num,
    only_root_frames,
    root_iter_num,
    anim_iter_num,
    global_solve,
    eval_complex_graphs,
    root_frame_strategy,
    triangulate_bundles,
    use_euler_filter,
    remove_unused_objects,
    solver_version,
    solver_type,
    scene_graph_mode,
    precomputed_data,
    withtest,
    verbose,
):
    """
    Generate Actions to solve multiple-frames.

    :param mkr_list:
        Markers to be solved with.
    :type mkr_list: [Marker, ..]

    :param attr_list:
        Attributes to be solved.
    :type attr_list: [Attribute, ..]

    :param root_frame_list:
        Frames to solve static and animated attributes.
    :type root_frame_list: [[Frame, ..], ..]

    :param frame_list:
        Frames to solve animated attributes.
    :type frame_list: [Frame, ..]

    :param use_attr_blocks:
        Split attributes into stages (based on categories) to be
        separately or together.
    :type use_attr_blocks: bool

    :param block_iter_num:
        How many iterations to perform for attribute categories.
    :type block_iter_num: int

    :param only_root_frames:
        Only solve the root frames.
    :param only_root_frames: bool

    :param root_iter_num:
        Number of iterations for root frame solves.
    :type root_iter_num: int

    :param anim_iter_num:
        Number of iterations for animated attribute solves.
    :type anim_iter_num: int

    :param global_solve:
        Should all frames be solved together, both animated and static
        attributes?
    :type global_solve: bool

    :param eval_complex_graphs:
        If True, the solve will try to trigger evalation of complex
        node graphs (such as Mesh Rivets), by changing the timeEvalMode
        of the mmSolver command.
    :type eval_complex_graphs: bool

    :param root_frame_strategy:
        The strategy ordering of root frames and how to solve them.
        Value must be one in ROOT_FRAME_STRATEGY_VALUE_LIST.
    :type root_frame_strategy: ROOT_FRAME_STRATEGY_*

    :param triangulate_bundles:
        If True, unlocked bundles will be triangulated before being
        further refined by the solver processes.
    :type triangulate_bundles: bool

    :param use_euler_filter:
        Perform a Euler Filter after solving? A Euler filter will make
        sure no two keyframes rotate by more than 180 degrees, which
        will remove "Euler Flipping".
    :type use_euler_filter: bool

    :param remove_unused_objects:
        Should objects that are detected as 'unused' be removed from
        the solver?
    :type remove_unused_objects: bool

    :param solver_version:
        Which Solver Version should be used?
        A value in mmSolver.api.SOLVER_VERSION_LIST.
    :type solver_version: int

    :param solver_type:
        Which Solver type should be used?
        A value in mmSolver.api.SOLVER_TYPE_*.
    :type solver_type: int

    :param scene_graph_mode:
        Which Scene Graph should be used? 0=Maya DAG or 1=MM Scene Graph.
    :type scene_graph_mode: int

    :param withtest:
        Should validation tests be generated?
    :type withtest: bool

    :param verbose:
        Print out more detail than usual.
    :type verbose: bool

    :return:
        Yields a generator of two Actions. First Action is for solving,
        the second Action is for validation of inputs.
    :rtype: (Action, Action)
    """
    assert isinstance(use_attr_blocks, bool)
    assert isinstance(block_iter_num, int)
    assert isinstance(only_root_frames, bool)
    assert isinstance(root_iter_num, int)
    assert isinstance(anim_iter_num, int)
    assert isinstance(global_solve, bool)
    assert isinstance(root_frame_strategy, int)
    assert isinstance(triangulate_bundles, bool)
    assert isinstance(use_euler_filter, bool)
    assert isinstance(remove_unused_objects, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(scene_graph_mode, int)
    assert isinstance(precomputed_data, dict)
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)
    assert root_frame_strategy in const.ROOT_FRAME_STRATEGY_VALUE_LIST
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    # Get Frame numbers.
    root_frame_list_num = [x.get_number() for x in root_frame_list]
    frame_list_num = [x.get_number() for x in frame_list]
    non_root_frame_list_num = set(frame_list_num) - set(root_frame_list_num)
    non_root_frame_list = [frame.Frame(x) for x in non_root_frame_list_num]

    all_frame_list_num = list(set(frame_list_num + root_frame_list_num))
    all_frame_list_num = list(sorted(all_frame_list_num))
    all_frame_list = [frame.Frame(x) for x in all_frame_list_num]
    start_frame = all_frame_list[0]
    end_frame = all_frame_list[-1]

    # Triangulate the (open) bundles here. We triangulate all
    #  valid bundles after the root frames have solved.
    #
    # NOTE: Bundle triangulation can only happen if the camera
    # is not nodal.
    if triangulate_bundles is True:
        sol = solvertriangulate.SolverTriangulate()
        cache = api_compile.create_compile_solver_cache()
        generator = api_compile.compile_solver_with_cache(
            sol, col, mkr_list, attr_list, withtest, cache
        )
        for action, vaction in generator:
            yield action, vaction

    # Solver root frames, breaking attributes into little blocks
    # to solve.
    root_mkr_list, non_root_mkr_list = _filter_mkr_list_by_frame_list(
        mkr_list, root_frame_list
    )
    if len(root_mkr_list) == 0:
        # TODO: Test we have enough markers to solve with, if not warn
        #  the user.
        # action = api_action.Action(func='pass', args=[], kwargs={})
        # vaction = api_action.Action(func='', args=[], kwargs={})
        # yield action, vaction
        LOG.warn("Not enough Markers given for root frames.")
        return

    attr_blocks = solverutils.create_attr_blocks(use_attr_blocks, attr_list)

    # TODO: Create a list of markers specially for root frames.
    #  Loop over all given markers, determine which markers have 2
    #  or more root frames, only use those markers for root frame
    #  computation. Overall, we must filter out all markers that
    #  cannot/should not be used for different solves.
    #
    # TODO: We must make sure to allow the solver to detect that
    #  not enough markers are being used, and warn the user.
    #
    # TODO: All markers that do not have enough root frames to solve
    #  correctly, but the Bundle is still in the solver, then it should
    #  be triangulated after the initial root frame solve is performed.
    #
    # TODO: Run the solver multiple times for a hierarchy. First,
    #  solve DAG level 0 nodes, then add DAG level 1, then level 2,
    #  etc. This will allow us to incrementally add solving of
    #  hierarchy, without getting the optimiser confused which
    #  attributes to solve first to get a stable solve.

    if root_frame_strategy == const.ROOT_FRAME_STRATEGY_GLOBAL_VALUE:
        # Global solve of root frames.
        sol = solverstep.SolverStep()
        sol.set_max_iterations(root_iter_num)
        sol.set_frame_list(root_frame_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)
        sol.set_solver_version(solver_version)
        sol.set_solver_type(solver_type)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE)
        sol.set_remove_unused_markers(remove_unused_objects)
        sol.set_remove_unused_attributes(remove_unused_objects)
        sol.set_precomputed_data(precomputed_data)

        cache = api_compile.create_compile_solver_cache()
        generator = solverutils.compile_solver_step_blocks_with_cache(
            sol, col, root_mkr_list, attr_blocks, withtest, cache
        )
        for action, vaction in generator:
            yield action, vaction
    else:
        # Get the order of frames to solve with.
        batch_frame_list = []

        if root_frame_strategy == const.ROOT_FRAME_STRATEGY_FWD_PAIR_VALUE:
            # Two frames at a time, moving forward.
            batch_frame_list = _gen_two_frame_fwd(root_frame_list_num)

        elif root_frame_strategy == const.ROOT_FRAME_STRATEGY_FWD_PAIR_AND_GLOBAL_VALUE:
            # Two frames at a time, moving forward, plus a global solve
            # at the end.
            batch_frame_list = _gen_two_frame_fwd(root_frame_list_num)
            batch_frame_list.append(root_frame_list)

        elif root_frame_strategy == const.ROOT_FRAME_STRATEGY_FWD_INCREMENT_VALUE:
            # 3 frames at a time, incrementing by 3 frames, moving
            # forward.
            frame_tmp_list = rootframe.generate_increment_frame_forward(
                root_frame_list_num
            )
            for frame_tmp in frame_tmp_list:
                batch_frame_list.append([frame.Frame(f) for f in frame_tmp])

        else:
            # TODO: Root frame ordering can be determined by the
            #  count of markers available at each frame. After we
            #  have an ordering of these frames, we can solve the
            #  frames incrementally, starting with the first
            #  highest, then add the next highest, etc. This
            #  should ensure stability of the solver is maximum.
            raise NotImplementedError

        generator = _compile_multi_root_frames(
            col,
            mkr_list,
            attr_list,
            batch_frame_list,
            root_iter_num,
            use_attr_blocks,
            remove_unused_objects,
            solver_type,
            scene_graph_mode,
            precomputed_data,
            withtest,
            verbose,
        )
        for action, vaction in generator:
            yield action, vaction

    # Clear out all the frames between the solved root frames, this
    # helps us use the new solve root frames to hint the 'in-between'
    # frame solve.
    generator = _compile_remove_inbetween_frames(
        attr_list, non_root_frame_list, start_frame, end_frame, withtest, verbose
    )
    for action, vaction in generator:
        yield action, vaction
    if only_root_frames is True:
        return

    # Perform an euler filter on all unlocked rotation attributes.
    if use_euler_filter is True:
        generator = solverutils.compile_euler_filter(attr_list, withtest)
        for action, vaction in generator:
            yield action, vaction

    generator = _compile_multi_inbetween_frames(
        col,
        mkr_list,
        attr_list,
        all_frame_list,
        global_solve,
        eval_complex_graphs,
        anim_iter_num,
        use_attr_blocks,
        remove_unused_objects,
        solver_version,
        solver_type,
        scene_graph_mode,
        precomputed_data,
        withtest,
        verbose,
    )
    for action, vaction in generator:
        yield action, vaction
    return


def compile_single_frame(
    col,
    mkr_list,
    attr_list,
    single_frame,
    block_iter_num,
    lineup_iter_num,
    use_attr_blocks,
    remove_unused_objects,
    solver_version,
    solver_type,
    scene_graph_mode,
    precomputed_data,
    withtest,
    verbose,
):
    """
    Compile to Actions for a solve of a single frame.

    :param mkr_list:
        Markers to be solved with.
    :type mkr_list: [Marker, ..]

    :param attr_list:
        Attributes to be solved.
    :type attr_list: [Attribute, ..]

    :param single_frame:
        The Frame to solve on.
    :type single_frame: Frame

    :param use_attr_blocks:
        Split attributes into stages (based on categories) to be
        solved together.
    :type use_attr_blocks: bool

    :param block_iter_num:
        How many iterations to perform for attribute categories.
    :type block_iter_num: int

    :param lineup_iter_num:
        pass
    :type lineup_iter_num: int

    :param remove_unused_objects:
        Should objects that are detected as 'unused' be removed from
        the solver?
    :type remove_unused_objects: bool

    :param solver_version:
        Which Solver Version should be used?
        A value in mmSolver.api.SOLVER_VERSION_LIST.
    :type solver_version: int

    :param solver_type:
        Which Solver type should be used?
        A value in mmSolver.api.SOLVER_TYPE_*.
    :type solver_type: int

    :param scene_graph_mode:
        Which Scene Graph should be used? 0=Maya DAG or 1=MM Scene Graph.
    :type scene_graph_mode: int

    :param withtest:
        Should validation tests be generated?
    :type withtest: bool

    :param verbose:
        Print out more detail than usual.
    :type verbose: bool

    :return:
        Yields a generator of two Actions. First Action is for solving,
        the second Action is for validation of inputs.
    :rtype: (Action, Action)
    """
    assert isinstance(use_attr_blocks, bool)
    assert isinstance(block_iter_num, int)
    assert isinstance(lineup_iter_num, int)
    assert isinstance(remove_unused_objects, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(scene_graph_mode, int)
    assert isinstance(precomputed_data, dict)
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)

    attr_blocks = solverutils.create_attr_blocks(use_attr_blocks, attr_list)

    # Single frame solve
    sol = solverstep.SolverStep()
    sol.set_max_iterations(lineup_iter_num)
    sol.set_frame_list([single_frame])
    sol.set_attributes_use_animated(True)
    sol.set_attributes_use_static(True)
    sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
    sol.set_use_smoothness(False)
    sol.set_use_stiffness(False)
    sol.set_solver_version(solver_version)
    sol.set_solver_type(solver_type)
    sol.set_scene_graph_mode(scene_graph_mode)
    sol.set_frame_solve_mode(const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE)
    sol.set_remove_unused_markers(remove_unused_objects)
    sol.set_remove_unused_attributes(remove_unused_objects)
    sol.set_precomputed_data(precomputed_data)

    cache = api_compile.create_compile_solver_cache()
    generator = solverutils.compile_solver_step_blocks_with_cache(
        sol, col, mkr_list, attr_blocks, withtest, cache
    )
    for action, vaction in generator:
        yield action, vaction
    return
