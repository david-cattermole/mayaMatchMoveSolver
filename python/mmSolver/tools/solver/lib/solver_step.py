"""
Solver Step - holds data representing a logical solver step.
"""
import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _gen_two_frame_fwd(int_list):
    """
    Given a list of integers, create list of Frame pairs, moving
    though the original list.

    :param int_list: List of frame numbers.
    :type int_list: List of int

    :returns: List of integer pairs.
    :rtype: list of list of Frame
    """
    end = len(int_list) - 1
    batch_list = []
    for i in range(end):
        s = i
        e = i + 2
        tmp_list = int_list[s:e]
        frm_list = []
        for j, num in enumerate(tmp_list):
            frm = mmapi.Frame(num)
            frm_list.append(frm)
        batch_list.append(frm_list)
    return batch_list


def _solve_anim_attrs(max_iter_num, auto_diff_type, int_list):
    """
    Solve only animated attributes.

    .. todo::

       Split attributes into groups of markers. By definition
       of 'animated attributes', each set of animated attributes can
       only affect the connected attributes. Therefore we should
       create multiple solvers that filter out specific attributes.

    """
    sol_list = []
    for f in int_list:
        frm = mmapi.Frame(f)
        frm_list = [frm]

        sol = mmapi.Solver()
        sol.set_max_iterations(max_iter_num)
        sol.set_auto_diff_type(auto_diff_type)
        sol.set_frame_list(frm_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(False)
        sol_list.append(sol)
    return sol_list


def _solve_all_attrs(max_iter_num, auto_diff_type, int_list, strategy):
    sol_list = []
    batch_frm_list = []

    if len(int_list) == 0:
        msg = 'Cannot compile solver steps, no frames given; %r'
        LOG.warning(msg, int_list)
        return sol_list

    if strategy == const.STRATEGY_TWO_FRAMES_FWD:
        batch_frm_list = _gen_two_frame_fwd(int_list)
    elif strategy == const.STRATEGY_ALL_FRAMES_AT_ONCE:
        frm_list = map(lambda x: mmapi.Frame(x), int_list)
        batch_frm_list = [frm_list]
    else:
        msg = 'strategy is not supported: strategy=%r'
        raise ValueError(msg % strategy)

    for frm_list in batch_frm_list:
        sol = mmapi.Solver()
        sol.set_max_iterations(max_iter_num)
        sol.set_auto_diff_type(auto_diff_type)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(True)
        sol.set_frame_list(frm_list)
        sol_list.append(sol)
    return sol_list


class SolverStep(object):
    def __init__(self, data=None):
        super(SolverStep, self).__init__()
        assert 'name' in data
        assert isinstance(data.get('name'), basestring) is True
        self._data = data.copy()

    def get_name(self):
        data = self.get_data()
        return data.get('name')

    def get_data(self):
        return self._data.copy()

    def set_data(self, value):
        self._data = value.copy()

    def get_enabled(self):
        data = self.get_data()
        return data.get('enabled')

    def set_enabled(self, value):
        data = self.get_data()
        data['enabled'] = value
        self.set_data(data)

    def get_frame_list(self):
        data = self.get_data()
        return data.get('frame_list')

    def set_frame_list(self, value):
        data = self.get_data()
        data['frame_list'] = value
        self.set_data(data)

    def get_strategy(self):
        data = self.get_data()
        return data.get('strategy')

    def set_strategy(self, value):
        data = self.get_data()
        data['strategy'] = value
        self.set_data(data)

    def get_use_anim_attrs(self):
        data = self.get_data()
        return data.get('use_anim_attrs')

    def set_use_anim_attrs(self, value):
        data = self.get_data()
        data['use_anim_attrs'] = value
        self.set_data(data)

    def get_use_static_attrs(self):
        data = self.get_data()
        return data.get('use_static_attrs')

    def set_use_static_attrs(self, value):
        data = self.get_data()
        data['use_static_attrs'] = value
        self.set_data(data)

    def compile(self, col, override_current_frame=False):
        """
        Convert Solver Step into a list of Solvers.

        :param col: The collection this solver step belongs to.
        :type col: Collection

        :param override_current_frame: Forces the solve to only use
                                       the current frame.
        :type override_current_frame: bool

        :returns: List of solvers compiled from this solver step.
        :rtype: list of Solver
        """
        sol_list = []
        enabled = self.get_enabled()
        if enabled is not True:
            return sol_list

        # Default Solver values
        max_iter_num = const.MAX_ITERATION_NUM_DEFAULT_VALUE
        auto_diff_type = const.AUTO_DIFF_TYPE_DEFAULT_VALUE

        strategy = self.get_strategy()

        # If the option 'override current frame' is on, we ignore the
        # frames given and override with the current frame number.
        int_list = []
        if override_current_frame is True:
            time = maya.cmds.currentTime(query=True)
            cur_frame = int(time)
            int_list = [cur_frame]
        else:
            int_list = self.get_frame_list()

        # Use number of different attributes later on to switch strategies.
        attr_list = col.get_attribute_list()
        attrs_anim_num = 0
        attrs_static_num = 0
        for attr in attr_list:
            if attr.is_animated():
                attrs_anim_num += 1
            if attr.is_static():
                attrs_static_num += 1

        # If there are no static attributes, the solver will consider
        # "use_static_attrs" to be off. 
        use_anim_attrs = self.get_use_anim_attrs() and attrs_anim_num > 0
        use_static_attrs = self.get_use_static_attrs() and attrs_static_num > 0
        if use_anim_attrs is True and use_static_attrs is False:
            # Solve only animated attributes.
            sol_list = _solve_anim_attrs(
                max_iter_num,
                auto_diff_type,
                int_list,
            )
        elif ((use_anim_attrs is True and use_static_attrs is True)
              or (use_anim_attrs is False and use_static_attrs is True)):
            # Solve static attributes, as well as animated attributes.
            sol_list = _solve_all_attrs(
                max_iter_num,
                auto_diff_type,
                int_list,
                strategy,
            )
        elif use_anim_attrs is False and use_static_attrs is False:
            pass
            # msg = 'No attributes will be solved: '
            # msg += 'use_static_attrs=%r, use_anim_attrs=%r'
            # msg = msg % (use_static_attrs, use_anim_attrs)
            # LOG.debug(msg)
        else:
            msg = 'We should not get here: '
            msg += 'use_static_attrs=%r, use_anim_attrs=%r'
            msg = msg % (use_static_attrs, use_anim_attrs)
            raise ValueError(msg)
        return sol_list
