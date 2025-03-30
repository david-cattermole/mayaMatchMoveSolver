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

import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.solverutils as solverutils
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstandardutils as solverstandardutils


LOG = mmSolver.logger.get_logger()


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
        # These variables are not used by the class.
        self._print_statistics_inputs = False
        self._print_statistics_affects = False
        self._print_statistics_deviation = False
        self._robust_loss_type = 0
        self._robust_loss_scale = 1.0
        return

    ############################################################################

    def get_verbose(self):
        """
        Should we print lots of information to the terminal?

        :rtype: bool or None
        """
        return self._data.get('verbose')

    def set_verbose(self, value):
        """
        Set verbosity option, yes or no.

        :param value: Turn on verbose mode? Yes or no.
        :type value: bool
        """
        if isinstance(value, bool) is False:
            raise TypeError('Expected bool value type.')
        self._data['verbose'] = value

    ############################################################################

    def get_use_single_frame(self):
        """
        Get Use Single Frame value.

        :rtype: bool
        """
        return self._data.get(
            'use_single_frame', const.SOLVER_STD_USE_SINGLE_FRAME_DEFAULT_VALUE
        )

    def set_use_single_frame(self, value):
        """
        Set Use Single Frame value.

        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['use_single_frame'] = bool(value)

    def get_single_frame(self):
        """
        Get Single Frame value.

        :rtype: Frame or None
        """
        value = self._data.get(
            'single_frame', const.SOLVER_STD_SINGLE_FRAME_DEFAULT_VALUE
        )
        frm = None
        if value is not None:
            frm = frame.Frame(value)
        return frm

    def set_single_frame(self, value):
        """
        Set Single Frame value.

        :param value: Value to be set.
        :type value: Frame or int
        """
        assert isinstance(value, (frame.Frame, int, pycompat.LONG_TYPE))
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
            'only_root_frames', const.SOLVER_STD_ONLY_ROOT_FRAMES_DEFAULT_VALUE
        )

    def set_only_root_frames(self, value):
        """
        Set Only Root Frames value.

        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['only_root_frames'] = bool(value)

    ############################################################################

    def get_global_solve(self):
        """
        Get Global Solve value.

        :rtype: bool
        """
        return self._data.get(
            'global_solve', const.SOLVER_STD_GLOBAL_SOLVE_DEFAULT_VALUE
        )

    def set_global_solve(self, value):
        """
        Set Global Solve value.

        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['global_solve'] = bool(value)

    ############################################################################

    def get_triangulate_bundles(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'triangulate_bundles', const.SOLVER_STD_TRIANGULATE_BUNDLES_DEFAULT_VALUE
        )

    def set_triangulate_bundles(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['triangulate_bundles'] = bool(value)

    ############################################################################

    def get_use_attr_blocks(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'use_attr_blocks', const.SOLVER_STD_USE_ATTR_BLOCKS_DEFAULT_VALUE
        )

    def set_use_attr_blocks(self, value):
        """
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['use_attr_blocks'] = bool(value)

    ############################################################################

    def get_eval_object_relationships(self):
        """
        Get 'Pre-Solve Object Relationships' value.

        OBSOLETE! Do not use.

        :rtype: bool
        """
        return True

    def set_eval_object_relationships(self, value):
        """
        Set 'Pre-Solve Object Relationships' value.

        OBSOLETE! Do not use.

        :param value: Value to be set.
        :type value: bool or int
        """
        pass

    ############################################################################

    def get_eval_complex_graphs(self):
        """
        Get 'Evaluate Complex Node Graphs' value.

        :rtype: bool
        """
        return self._data.get(
            'eval_complex_node_graphs',
            const.SOLVER_STD_EVAL_COMPLEX_GRAPHS_DEFAULT_VALUE,
        )

    def set_eval_complex_graphs(self, value):
        """
        Set 'Evaluate Complex Node Graph' value.

        If True, the solve will try to trigger evalation of complex
        node graphs (such as Mesh Rivets), by changing the
        timeEvalMode of the mmSolver command.

        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['eval_complex_node_graphs'] = bool(value)

    ############################################################################

    def get_solver_version(self):
        """
        Get 'Solver Version' value.

        :rtype: int
        """
        return self._data.get('solver_version', const.SOLVER_VERSION_DEFAULT)

    def set_solver_version(self, value):
        """
        Set 'Solver Version' value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, int)
        self._data['solver_version'] = value

    ############################################################################

    def get_solver_type(self):
        """
        Get 'Solver Type' value.

        :rtype: int
        """
        return self._data.get('solver_type', const.SOLVER_STD_SOLVER_TYPE_DEFAULT_VALUE)

    def set_solver_type(self, value):
        """
        Set 'Solver Type' value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, int)
        self._data['solver_type'] = value

    ############################################################################

    def get_scene_graph_mode(self):
        """
        :rtype: int
        """
        return self._data.get(
            'scene_graph_mode', const.SOLVER_STD_SCENE_GRAPH_MODE_DEFAULT_VALUE
        )

    def set_scene_graph_mode(self, value):
        """
        :type value: int
        """
        assert isinstance(value, int)
        self._data['scene_graph_mode'] = value

    ############################################################################

    def get_root_frame_strategy(self):
        """
        Get Root Frame Strategy value.

        :rtype: bool
        """
        return self._data.get(
            'root_frame_strategy', const.SOLVER_STD_ROOT_FRAME_STRATEGY_DEFAULT_VALUE
        )

    def set_root_frame_strategy(self, value):
        """
        Set Root Frame Strategy value.

        The strategy ordering of root frames and how to solve them.
        Value must be one in ROOT_FRAME_STRATEGY_VALUE_LIST.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value in const.ROOT_FRAME_STRATEGY_VALUE_LIST
        self._data['root_frame_strategy'] = value

    ############################################################################

    def get_block_iteration_num(self):
        """
        Get Block Iteration Number value.

        :rtype: bool
        """
        return self._data.get(
            'block_iteration_num', const.SOLVER_STD_BLOCK_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_block_iteration_num(self, value):
        """
        Set Block Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['block_iteration_num'] = value

    def get_root_iteration_num(self):
        """
        Get Root Iteration Number value.

        :rtype: bool
        """
        return self._data.get(
            'root_iteration_num', const.SOLVER_STD_ROOT_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_root_iteration_num(self, value):
        """
        Set Root Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['root_iteration_num'] = value

    def get_anim_iteration_num(self):
        """
        Get Animation Iteration Number value.

        :rtype: int
        """
        return self._data.get(
            'anim_iteration_num', const.SOLVER_STD_ANIM_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_anim_iteration_num(self, value):
        """
        Set Animation Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['anim_iteration_num'] = value

    def get_lineup_iteration_num(self):
        """
        Get Line-up Iteration Number value.

        :rtype: int
        """
        return self._data.get(
            'lineup_iteration_num', const.SOLVER_STD_LINEUP_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_lineup_iteration_num(self, value):
        """
        Set Line-up Iteration Number value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['lineup_iteration_num'] = value

    ############################################################################

    def get_solve_focal_length(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'solve_focal_length', const.SOLVER_STD_SOLVE_FOCAL_LENGTH_DEFAULT_VALUE
        )

    def set_solve_focal_length(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['solve_focal_length'] = bool(value)

    ############################################################################

    def get_solve_lens_distortion(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'solve_lens_distortion',
            const.SOLVER_STD_SOLVE_LENS_DISTORTION_DEFAULT_VALUE,
        )

    def set_solve_lens_distortion(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['solve_lens_distortion'] = bool(value)

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
        triangulate_bundles = self.get_triangulate_bundles()
        use_attr_blocks = self.get_use_attr_blocks()
        remove_unused_objects = True
        eval_complex_graphs = self.get_eval_complex_graphs()
        solver_version = self.get_solver_version()
        solver_type = self.get_solver_type()
        scene_graph_mode = self.get_scene_graph_mode()
        block_iter_num = self.get_block_iteration_num()
        root_iter_num = self.get_root_iteration_num()
        anim_iter_num = self.get_anim_iteration_num()
        lineup_iter_num = self.get_lineup_iteration_num()
        solve_focal_length = self.get_solve_focal_length()
        solve_lens_distortion = self.get_solve_lens_distortion()

        root_frame_strategy = self.get_root_frame_strategy()
        root_frame_list = self.get_root_frame_list()
        frame_list = self.get_frame_list()

        use_euler_filter = True
        withtest = True
        verbose = self.get_verbose()
        if verbose is None:
            verbose = False
        precomputed_data = self.get_precomputed_data()

        attr_list = solverutils.filter_attr_list(
            attr_list,
            use_camera_intrinsics=solve_focal_length,
            use_lens_distortion=solve_lens_distortion,
        )

        # TODO: When should we solve lens distortion? Perhaps it
        # should only be solved after all other parameters are solved?

        auto_scene_graph = scene_graph_mode == const.SCENE_GRAPH_MODE_AUTO
        if auto_scene_graph is True:
            # When 'auto' scene graph is used we are telling the
            # solver to use the best supported scene graph. This will
            # test the scene graph being solved and fall back to Maya
            # DAG scene graph if mmSceneGraph fails.
            scene_graph_mode = const.SCENE_GRAPH_MODE_MM_SCENE_GRAPH
            use_animated_attrs = True
            use_static_attrs = True
            generator = solverutils.compile_solver_scene_graph(
                col,
                mkr_list,
                attr_list,
                use_animated_attrs,
                use_static_attrs,
                scene_graph_mode,
                precomputed_data,
                withtest,
            )
            for action, vaction in generator:
                yield action, vaction

        # Pre-calculate the 'affects' relationship.
        generator = solverutils.compile_solver_affects(
            col, mkr_list, attr_list, precomputed_data, withtest
        )
        for action, vaction in generator:
            yield action, vaction

        if use_single_frame is True:
            generator = solverstandardutils.compile_single_frame(
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
            )
            for action, vaction in generator:
                yield action, vaction
        else:
            generator = solverstandardutils.compile_multi_frame(
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
            )
            for action, vaction in generator:
                yield action, vaction
        return
