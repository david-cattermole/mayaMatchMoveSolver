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

import mmSolver.logger

import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.marker as marker
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstep as solverstep
import mmSolver._api.solvertriangulate as solvertriangulate
import mmSolver._api.markerutils as markerutils
import mmSolver._api.action as api_action
import mmSolver._api.compile as api_compile


LOG = mmSolver.logger.get_logger()


ATTR_CATEGORIES = [
    'regular',
    'bundle_transform',
    'camera_transform',
    'camera_intrinsic',
    'lens_distortion',
]


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
        batch_list = [
            [frame.Frame(num), frame.Frame(num)]
        ]
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


def _split_mkr_attr_into_categories(mkr_list, attr_list):
    """
    Put Markers and Attributes into categories to be solved individually.

    :param mkr_list: List of Markers.
    :type mkr_list: [Marker, ..]

    :param attr_list: List of Attributes.
    :type attr_list: [Attribute, ..]

    :return:
        List of Markers and List of Attributes. The length of both
        Marker and Attributes will be the same and are designed to
        be used together.
    :rtype: ( [[Marker, ..], ..], [[Attribute, ..]])
    """
    meta_mkr_list = []
    meta_attr_list = []

    mkr_attr_map = markerutils.find_marker_attr_mapping(
        mkr_list,
        attr_list
    )
    attrs_in_categories = api_compile.categorise_attributes(
        attr_list
    )
    for category in ATTR_CATEGORIES:
        category_node_attrs = attrs_in_categories[category]

        # num_attrs = [len(v) for k, v in category_node_attrs.items()]
        # num_attrs = sum(num_attrs)

        # msg = 'Attribute Category=%r'
        # LOG.warn(msg, category)
        # msg = '-> Number of Nodes=%r'
        # LOG.warn(msg, len(category_node_attrs.keys()))
        # msg = '-> Number Of Attributes=%r'
        # LOG.warn(msg, num_attrs)

        for node, attrs in category_node_attrs.items():
            if len(attrs) == 0:
                continue
            attr_names = [x.get_name() for x in attrs]
            new_mkr_list = []
            new_attr_list = []
            for j, attr in enumerate(attr_list):
                attr_name = attr.get_name()
                if attr_name not in attr_names:
                    continue
                for i, mkr in enumerate(mkr_list):
                    affects = mkr_attr_map[i][j]
                    if affects is False:
                        continue
                    if mkr not in new_mkr_list:
                        new_mkr_list.append(mkr)
                        new_attr_list.append(attr)
            if len(new_mkr_list) == 0 or len(new_attr_list) == 0:
                LOG.warn(
                    'No markers found affecting attribute. node=%r',
                    node
                )
                continue
            meta_mkr_list.append(new_mkr_list)
            meta_attr_list.append(new_attr_list)

    return meta_mkr_list, meta_attr_list


def _compile_multi_root_frames(col,
                               mkr_list,
                               attr_list,
                               batch_frame_list,
                               root_iter_num,
                               withtest,
                               verbose):
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

    :param withtest:
        Compile the test/validation Action, as well as the solve Action?
    :type withtest: bool

    :param verbose:
        Print out more detail to 'stdout'.
    :type verbose: bool

    :return:
        Yields two Actions at each iteration; first Action is for
        solving, second Action is to validate the inputs given.
    :rtype: (Action, Action or None)
    """
    # Solve root frames.
    for frm_list in batch_frame_list:
        # Get root markers
        root_mkr_list, non_root_mkr_list = _filter_mkr_list_by_frame_list(
            mkr_list,
            frm_list
        )
        assert len(root_mkr_list) > 0

        mkr_attr_map = markerutils.find_marker_attr_mapping(
            root_mkr_list,
            attr_list
        )
        root_attr_list = []
        for i, mkr in enumerate(root_mkr_list):
            for j, attr in enumerate(attr_list):
                x = mkr_attr_map[i][j]
                if x is True and attr not in root_attr_list:
                    root_attr_list.append(attr)

        sol = solverstep.SolverStep()
        sol.set_verbose(verbose)
        sol.set_max_iterations(root_iter_num)
        sol.set_frame_list(frm_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)

        cache = api_compile.create_compile_solver_cache()
        generator = api_compile.compile_solver_with_cache(
            sol, col, root_mkr_list, root_attr_list, withtest, cache)
        for action, vaction in generator:
            yield action, vaction
        return


def _compile_remove_inbetween_frames(attr_list,
                                     non_root_frame_list,
                                     start_frame,
                                     end_frame,
                                     withtest,
                                     verbose):
    """
    Compile actions to delete keyframes for all attributes with-in a
    specific start/end frame range.

    :param attr_list:
        List of Attributes.
    :type attr_list: [Attribute, ..]

    :param non_root_frame_list:
        pass
    :type non_root_frame_list: [[int, ..], ..]

    :param start_frame:
        pass
    :type start_frame: Frame

    :param end_frame:
        pass
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
    # Solve in-between frames
    attr_names = [x.get_name() for x in attr_list]

    # Solver for all other frames.
    for frm in non_root_frame_list:
        frame_num = frm.get_number()
        func = 'maya.cmds.cutKey'
        args = attr_names
        kwargs = {'time': (frame_num, frame_num)}
        action = api_action.Action(
            func=func,
            args=args,
            kwargs=kwargs)
        yield action, None

    # Change all attribute keyframes to linear tangents.
    func = 'maya.cmds.keyTangent'
    kwargs = {
        'inTangentType': 'linear',
        'outTangentType': 'linear',
        'time': (start_frame.get_number() - 1,
                 end_frame.get_number() + 1)}
    action = api_action.Action(
        func=func,
        args=attr_names,
        kwargs=kwargs)
    yield action, None


def _compile_multi_inbetween_frames(col,
                                    mkr_list,
                                    attr_list,
                                    all_frame_list,
                                    global_solve,
                                    anim_iter_num,
                                    withtest,
                                    verbose):
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

    :param anim_iter_num:
        Number of iterations for solving animated attributes.
    :type anim_iter_num: int

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
    if global_solve is True:
        # Do Global Solve with all frames.
        sol = solverstep.SolverStep()
        sol.set_verbose(verbose)
        sol.set_max_iterations(anim_iter_num)
        sol.set_frame_list(all_frame_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)

        cache = api_compile.create_compile_solver_cache()
        generator = api_compile.compile_solver_with_cache(
            sol, col, mkr_list, attr_list, withtest, cache)
        for action, vaction in generator:
            yield action, vaction
    else:
        cache = api_compile.create_compile_solver_cache()
        for i, frm in enumerate(all_frame_list):
            is_first_frame = i == 0
            one_frame_list = [frm]
            sol = solverstep.SolverStep()
            sol.set_verbose(verbose)
            sol.set_max_iterations(anim_iter_num)
            sol.set_frame_list(one_frame_list)
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(False)
            sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
            sol.set_use_smoothness(not is_first_frame)
            sol.set_use_stiffness(not is_first_frame)

            generator = api_compile.compile_solver_with_cache(
                sol, col, mkr_list, attr_list, withtest, cache)
            for action, vaction in generator:
                yield action, vaction
    return


def _compile_multi_frame(col,
                         mkr_list,
                         attr_list,
                         root_frame_list,
                         frame_list,
                         auto_attr_blocks,
                         block_iter_num,
                         only_root_frames,
                         root_iter_num,
                         anim_iter_num,
                         global_solve,
                         root_frame_strategy,
                         triangulate_bundles,
                         withtest,
                         verbose):
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

    :param auto_attr_blocks:
        Split attributes into stages (based on categories) to be
        solved together.
    :type auto_attr_blocks: bool

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

    :param root_frame_strategy:
        The strategy ordering of root frames and how to solve them.
        Value must be one in ROOT_FRAME_STRATEGY_VALUE_LIST
    :type root_frame_strategy:

    :param triangulate_bundles:
        If True, unlocked bundles will be triangulated before being
        further refined by the solver processes.
    :type triangulate_bundles: bool

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
        # sol.root_frame_list = root_frame_list_num
        cache = api_compile.create_compile_solver_cache()
        generator = api_compile.compile_solver_with_cache(
            sol, col, mkr_list, attr_list, withtest, cache)
        for action, vaction in generator:
            yield action, vaction

    # Solver root frames, breaking attributes into little blocks
    # to solve.
    root_mkr_list, non_root_mkr_list = _filter_mkr_list_by_frame_list(
        mkr_list,
        root_frame_list
    )
    if len(root_mkr_list) == 0:
        # TODO: Test we have enough markers to solve with, if not warn
        #  the user.
        # action = api_action.Action(func='pass', args=[], kwargs={})
        # vaction = api_action.Action(func='', args=[], kwargs={})
        # yield action, vaction
        LOG.warn("Not enough Markers given for root frames.")
        return
    if auto_attr_blocks is True:
        meta_mkr_list, meta_attr_list = _split_mkr_attr_into_categories(
            root_mkr_list,
            attr_list
        )
        for new_mkr_list, new_attr_list in zip(meta_mkr_list, meta_attr_list):
            sol = solverstep.SolverStep()
            sol.set_verbose(verbose)
            sol.set_max_iterations(block_iter_num)
            sol.set_frame_list(root_frame_list)
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(True)
            sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
            sol.set_use_smoothness(False)
            sol.set_use_stiffness(False)

            cache = api_compile.create_compile_solver_cache()
            generator = api_compile.compile_solver_with_cache(
                sol, col, new_mkr_list, new_attr_list, withtest, cache)
            for action, vaction in generator:
                yield action, vaction

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
        sol.set_verbose(verbose)
        sol.set_max_iterations(root_iter_num)
        sol.set_frame_list(root_frame_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
        sol.set_use_smoothness(False)
        sol.set_use_stiffness(False)

        cache = api_compile.create_compile_solver_cache()
        generator = api_compile.compile_solver_with_cache(
            sol, col, root_mkr_list, attr_list, withtest, cache)
        for action, vaction in generator:
            yield action, vaction
    else:
        # Get the order of frames to solve with.
        batch_frame_list = []
        if root_frame_strategy == const.ROOT_FRAME_STRATEGY_FWD_PAIR_VALUE:
            # Two frames at a time, moving forward, plus a global solve
            # at the end.
            batch_frame_list = _gen_two_frame_fwd(root_frame_list_num)
            batch_frame_list.append(root_frame_list)
        elif root_frame_strategy == const.ROOT_FRAME_STRATEGY_FWD_PAIR_AND_GLOBAL_VALUE:
            # Two frames at a time, moving forward.
            batch_frame_list = _gen_two_frame_fwd(root_frame_list_num)
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
            withtest,
            verbose
        )
        for action, vaction in generator:
            yield action, vaction

    # Clear out all the frames between the solved root frames, this
    # helps us use the new solve root frames to hint the 'in-between'
    # frame solve.
    generator = _compile_remove_inbetween_frames(
        attr_list,
        non_root_frame_list,
        start_frame,
        end_frame,
        withtest,
        verbose
    )
    for action, vaction in generator:
        yield action, vaction
    if only_root_frames is True:
        return

    generator = _compile_multi_inbetween_frames(
        col,
        mkr_list,
        attr_list,
        all_frame_list,
        global_solve,
        anim_iter_num,
        withtest,
        verbose,
    )
    for action, vaction in generator:
        yield action, vaction
    return


def _compile_single_frame(col,
                          mkr_list,
                          attr_list,
                          single_frame,
                          block_iter_num,
                          lineup_iter_num,
                          auto_attr_blocks,
                          withtest,
                          verbose):
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

    :param auto_attr_blocks:
        Split attributes into stages (based on categories) to be
        solved together.
    :type auto_attr_blocks: bool

    :param block_iter_num:
        How many iterations to perform for attribute categories.
    :type block_iter_num: int

    :param lineup_iter_num:
        pass
    :type lineup_iter_num: int

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
    if auto_attr_blocks is True:
        meta_mkr_list, meta_attr_list = _split_mkr_attr_into_categories(
            mkr_list,
            attr_list
        )
        for new_mkr_list, new_attr_list in zip(meta_mkr_list, meta_attr_list):
            sol = solverstep.SolverStep()
            sol.set_verbose(verbose)
            sol.set_max_iterations(block_iter_num)
            sol.set_frame_list([single_frame])
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(True)
            sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
            sol.set_use_smoothness(False)
            sol.set_use_stiffness(False)

            cache = api_compile.create_compile_solver_cache()
            generator = api_compile.compile_solver_with_cache(
                sol, col, new_mkr_list, new_attr_list, withtest, cache)
            for action, vaction in generator:
                yield action, vaction

    # Single frame solve
    sol = solverstep.SolverStep()
    sol.set_verbose(verbose)
    sol.set_max_iterations(lineup_iter_num)
    sol.set_frame_list([single_frame])
    sol.set_attributes_use_animated(True)
    sol.set_attributes_use_static(True)
    sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
    sol.set_use_smoothness(False)
    sol.set_use_stiffness(False)

    cache = api_compile.create_compile_solver_cache()
    generator = api_compile.compile_solver_with_cache(
        sol, col, mkr_list, attr_list, withtest, cache)
    for action, vaction in generator:
        yield action, vaction
    return


class SolverStandard(solverbase.SolverBase):
    """
    The standard solver for mmSolver.

    This solver is designed for Animated and Static attributes.

    Parameters for solver:

    - Frame Range - with options:

      - "Single Frame"
      - "Time Slider (Inner)"
      - "Time Slider (Outer)"
      - "Custom"

    - Root Frames - A list of integer frame numbers.

    - Solver Method

      - "Solve Everything at Once" option - On or Off
      - "Solve Root Frames Only" option - On or Off

    If a Solver is `Single Frame` (current frame), then we solve both
    animated and static attributes on the current frame, in a single step
    and return.

    If the `Solver Root Frames Only` option is On, then we only solve the
    root frames, with both animated and static attributes.

    If the `Solver Root Frames Only` is Off, then we first solve the root
    frames with both animated and static attributes, then secondly we solve
    only animated attributes for the entire frame range.

    If the `Solve Everything at Once` option is On, then the second solve
    step contains static and animated attributes (not just animated),
    and all frames are solved as one big crunch.
    """

    # TODO: Before solving root frames we should query the current
    #  animated attribute values at each root frame, store it, then
    #  remove all keyframes between the first and last frames to
    #  solve. Lastly we should re-keyframe the values at the animated
    #  frames, and ensure the keyframe tangents are linear. This will
    #  ensure that animated keyframe values do not affect a re-solve.
    #  Only the root frames need to be initialized with good values.

    def __init__(self, *args, **kwargs):
        super(SolverStandard, self).__init__(*args, **kwargs)
        # These variables are not officially supported by the class.
        self._auto_attr_blocks = False
        self._triangulate_bundles = False

        # These variables are not used by the class.
        self._print_statistics_inputs = False
        self._print_statistics_affects = False
        self._print_statistics_deviation = False
        self._robust_loss_type = 0
        self._robust_loss_scale = 1.0
        return

    ############################################################################

    def get_use_single_frame(self):
        """
        Get Use Single Frame value.

        :rtype: bool
        """
        return self._data.get(
            'use_single_frame',
            const.SOLVER_STD_USE_SINGLE_FRAME_DEFAULT_VALUE)

    def set_use_single_frame(self, value):
        """
        Set Use Single Frame value.

        :param value: Value to be set.
        :type value: bool or int or long
        """
        assert isinstance(value, (bool, int, long))
        self._data['use_single_frame'] = bool(value)

    def get_single_frame(self):
        """
        Get Single Frame value.

        :rtype: Frame or None
        """
        value = self._data.get(
            'single_frame',
            const.SOLVER_STD_SINGLE_FRAME_DEFAULT_VALUE)
        frm = None
        if value is not None:
            frm = frame.Frame(value)
        return frm

    def set_single_frame(self, value):
        """
        Set Single Frame value.

        :param value: Value to be set.
        :type value: Frame or int or long
        """
        assert isinstance(value, (frame.Frame, int, long))
        number = value
        if isinstance(value, frame.Frame):
            number = value.get_number()
        self._data['single_frame'] = number

    ############################################################################

    def get_only_root_frames(self):
        """
        Get Only Root Frames value.

        :rtype: bool
        """
        return self._data.get(
            'only_root_frames',
            const.SOLVER_STD_ONLY_ROOT_FRAMES_DEFAULT_VALUE)

    def set_only_root_frames(self, value):
        """
        Set Only Root Frames value.

        :param value: Value to be set.
        :type value: bool or int or long
        """
        assert isinstance(value, (bool, int, long))
        self._data['only_root_frames'] = bool(value)

    ############################################################################

    def get_global_solve(self):
        """
        Get Global Solve value.

        :rtype: bool
        """
        return self._data.get(
            'global_solve',
            const.SOLVER_STD_GLOBAL_SOLVE_DEFAULT_VALUE)

    def set_global_solve(self, value):
        """
        Set Global Solve value.

        :param value: Value to be set.
        :type value: bool or int or long
        """
        assert isinstance(value, (bool, int, long))
        self._data['global_solve'] = bool(value)

    ############################################################################

    def get_root_frame_strategy(self):
        """
        Get Root Frame Strategy value.

        :rtype: bool
        """
        return self._data.get(
            'root_frame_strategy',
            const.SOLVER_STD_ROOT_FRAME_STRATEGY_DEFAULT_VALUE)

    def set_root_frame_strategy(self, value):
        """
        Set Root Frame Strategy value.

        :param value: Value to be set.
        :type value: int or long
        """
        assert isinstance(value, (int, long))
        self._data['root_frame_strategy'] = value

    ############################################################################

    def get_block_iteration_num(self):
        """
        Get Block Iteration Number value.

        :rtype: bool
        """
        return self._data.get(
            'block_iteration_num',
            const.SOLVER_STD_BLOCK_ITERATION_NUM_DEFAULT_VALUE)

    def set_block_iteration_num(self, value):
        """
        Set Block Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, (int, long))
        assert value > 0
        self._data['block_iteration_num'] = value

    def get_root_iteration_num(self):
        """
        Get Root Iteration Number value.

        :rtype: bool
        """
        return self._data.get(
            'root_iteration_num',
            const.SOLVER_STD_ROOT_ITERATION_NUM_DEFAULT_VALUE)

    def set_root_iteration_num(self, value):
        """
        Set Root Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, (int, long))
        assert value > 0
        self._data['root_iteration_num'] = value

    def get_anim_iteration_num(self):
        """
        Get Animation Iteration Number value.

        :rtype: int
        """
        return self._data.get(
            'anim_iteration_num',
            const.SOLVER_STD_ANIM_ITERATION_NUM_DEFAULT_VALUE)

    def set_anim_iteration_num(self, value):
        """
        Set Animation Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, (int, long))
        assert value > 0
        self._data['anim_iteration_num'] = value

    def get_lineup_iteration_num(self):
        """
        Get Line-up Iteration Number value.

        :rtype: int
        """
        return self._data.get(
            'lineup_iteration_num',
            const.SOLVER_STD_LINEUP_ITERATION_NUM_DEFAULT_VALUE)

    def set_lineup_iteration_num(self, value):
        """
        Set Line-up Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, (int, long))
        assert value > 0
        self._data['lineup_iteration_num'] = value

    ############################################################################

    def get_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_frame_list_length(self):
        """
        Return the number of frames in the frame list.

        :rtype: int
        """
        return len(self.get_frame_list())

    def add_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to the solver, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_frame(frm)
        return

    def remove_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_frame(frm)
        return

    def set_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_frame_list(frm_list)
        return

    def clear_frame_list(self):
        key = 'frame_list'
        self._data[key] = []
        return

    ############################################################################

    def get_root_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('root_frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_root_frame_list_length(self):
        """
        Return the number of frames in the root frame list.

        :rtype: int
        """
        return len(self.get_root_frame_list())

    def add_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to SolverStandard, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_root_frame(frm)
        return

    def remove_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_root_frame(frm)
        return

    def set_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_root_frame_list(frm_list)
        return

    def clear_root_frame_list(self):
        key = 'root_frame_list'
        self._data[key] = []
        return

    ############################################################################

    def compile(self, col, mkr_list, attr_list, withtest=False):
        # Options to affect how the solve is constructed.
        use_single_frame = self.get_use_single_frame()
        single_frame = self.get_single_frame()
        only_root_frames = self.get_only_root_frames()
        global_solve = self.get_global_solve()
        block_iter_num = self.get_block_iteration_num()
        root_iter_num = self.get_root_iteration_num()
        anim_iter_num = self.get_anim_iteration_num()
        lineup_iter_num = self.get_lineup_iteration_num()
        root_frame_strategy = self.get_root_frame_strategy()
        root_frame_list = self.get_root_frame_list()
        frame_list = self.get_frame_list()

        auto_attr_blocks = self._auto_attr_blocks
        triangulate_bundles = self._triangulate_bundles
        withtest = True
        verbose = True

        if use_single_frame is True:
            generator = _compile_single_frame(
                col,
                mkr_list,
                attr_list,
                single_frame,
                block_iter_num,
                lineup_iter_num,
                auto_attr_blocks,
                withtest,
                verbose,
            )
            for action, vaction in generator:
                yield action, vaction
        else:
            generator = _compile_multi_frame(
                col,
                mkr_list,
                attr_list,
                root_frame_list,
                frame_list,
                auto_attr_blocks,
                block_iter_num,
                only_root_frames,
                root_iter_num,
                anim_iter_num,
                global_solve,
                root_frame_strategy,
                triangulate_bundles,
                withtest,
                verbose,
            )
            for action, vaction in generator:
                yield action, vaction
        return
