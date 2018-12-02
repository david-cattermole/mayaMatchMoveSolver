"""
Solver Step - holds data representing a logical solver step.
"""

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()

def _gen_two_frame_fwd(int_list):
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

def _solve_anim_attrs(max_iter_num, int_list):
    sol_list = []
    batch_list = _gen_two_frame_fwd(int_list)
    for frm_list in batch_list:
        sol = mmapi.Solver()
        sol.set_max_iterations(max_iter_num)
        sol.set_frame_list(frm_list)
        sol.set_attributes_use_animated(True)
        sol.set_attributes_use_static(False)
        sol_list.append(sol)
    return sol_list


def _solve_static_attrs(max_iter_num, int_list, strategy):
    sol_list = []
    raise NotImplementedError
    return sol_list


def _solve_all_attrs(max_iter_num, int_list, strategy):
    LOG.debug('strategy: %r', strategy)
    sol_list = []

    if len(int_list) == 0:
        msg = 'Cannot compile solver steps, no frames given; %r'
        LOG.warning(msg, int_list)
        return sol_list

    if strategy == const.STRATEGY_TWO_FRAMES_FWD:
        batch_list = _gen_two_frame_fwd(int_list)
        for frm_list in batch_list:
            sol = mmapi.Solver()
            sol.set_max_iterations(max_iter_num)
            sol.set_attributes_use_animated(True)
            sol.set_attributes_use_static(True)
            sol.set_frame_list(frm_list)
            sol_list.append(sol)

    elif strategy == const.STRATEGY_ALL_FRAMES_AT_ONCE:
        frm_list = map(lambda x: mmapi.Frame(x), int_list)
        sol = mmapi.Solver()
        sol.set_max_iterations(max_iter_num)
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

    def compile(self):
        """
        Convert Solver Step into a list of Solvers.
        """
        sol_list = []
        enabled = self.get_enabled()
        if enabled is not True:
            return sol_list
        max_iter_num = 10
        use_anim_attrs = self.get_use_anim_attrs()
        use_static_attrs = self.get_use_static_attrs()
        strategy = self.get_strategy()
        int_list = self.get_frame_list()
        if use_anim_attrs is False and use_static_attrs is False:
            pass
        elif use_anim_attrs is True and use_static_attrs is False:
            sol_list = _solve_anim_attrs(
                max_iter_num,
                int_list,
            )
        elif use_anim_attrs is False and use_static_attrs is True:
            sol_list = _solve_static_attrs(
                max_iter_num,
                int_list,
                strategy,
            )
        elif use_anim_attrs is True and use_static_attrs is True:
            sol_list = _solve_all_attrs(
                max_iter_num,
                int_list,
                strategy,
            )
        else:
            raise ValueError('We should not get here')
        return sol_list

