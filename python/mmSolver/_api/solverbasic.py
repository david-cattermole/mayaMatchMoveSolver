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
The basic solver.

The basic solver is designed to solve only simple, per-frame animated
attributes. Static attributes are not solved at all with this solver.
"""

import mmSolver.logger

import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.solverutils as solverutils
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstep as solverstep
import mmSolver._api.compile as api_compile


LOG = mmSolver.logger.get_logger()


class SolverBasic(solverbase.SolverBase):
    """
    The basic solver for mmSolver.

    This solver will solve Animated attributes only.

    Parameters for solver:

    - Frame Range - with options:

      - "Single Frame"

      - "Time Slider (Inner)"

      - "Time Slider (Outer)"

      - "Custom"

    If a Solver is `Single Frame` (current frame), then we solve only
    animated attributes on the current frame, in a single step
    and return.
    """

    def __init__(self, *args, **kwargs):
        super(SolverBasic, self).__init__(*args, **kwargs)
        # These variables are not officially supported by the class.
        self._use_euler_filter = True

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

    def compile(self, col, mkr_list, attr_list, withtest=False):
        assert isinstance(withtest, bool)

        # Options to affect how the solve is constructed.
        use_single_frame = self.get_use_single_frame()
        single_frame = self.get_single_frame()
        frame_list = self.get_frame_list()
        anim_iter_num = self.get_anim_iteration_num()
        lineup_iter_num = self.get_lineup_iteration_num()
        use_euler_filter = self._use_euler_filter
        precomputed_data = self.get_precomputed_data()

        # Pre-calculate the 'affects' relationship.
        generator = solverutils.compile_solver_affects(
            col,
            mkr_list,
            attr_list,
            precomputed_data,
            withtest)
        for action, vaction in generator:
            yield action, vaction

        if use_single_frame is True:
            # Single frame solve
            sol = solverstep.SolverStep()
            sol.set_max_iterations(lineup_iter_num)
            sol.set_frame_list([single_frame])
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(False)
            sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
            sol.set_use_smoothness(False)
            sol.set_use_stiffness(False)
            sol.set_precomputed_data(precomputed_data)
            for action, vaction in sol.compile(col, mkr_list, attr_list,
                                               withtest=withtest):
                yield action, vaction
        else:
            # Multiple frame solve, per-frame
            vaction_cache = api_compile.create_compile_solver_cache()
            for i, frm in enumerate(frame_list):
                is_first_frame = i == 0
                one_frame_list = [frm]
                sol = solverstep.SolverStep()
                sol.set_max_iterations(anim_iter_num)
                sol.set_frame_list(one_frame_list)
                sol.set_attributes_use_animated(True)
                sol.set_attributes_use_static(False)
                sol.set_auto_diff_type(const.AUTO_DIFF_TYPE_FORWARD)
                sol.set_use_smoothness(not is_first_frame)
                sol.set_use_stiffness(not is_first_frame)
                sol.set_precomputed_data(precomputed_data)

                generator = api_compile.compile_solver_with_cache(
                    sol, col, mkr_list, attr_list, withtest, vaction_cache)
                for action, vaction in generator:
                    yield action, vaction

            # Perform an euler filter on all unlocked rotation attributes.
            if use_euler_filter is True:
                generator = solverutils.compile_euler_filter(
                    attr_list,
                    withtest
                )
                for action, vaction in generator:
                    yield action, vaction

        return
