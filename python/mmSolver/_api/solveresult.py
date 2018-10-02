"""
The information returned from a solve.
"""

import collections
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
KEY_VALUE_SEP_CHAR = '='
SPLIT_SEP_CHAR = '#'


def parse_command_result(cmd_result):
    data = collections.defaultdict(list)
    for res in cmd_result:
        assert isinstance(res, (str, unicode))
        splt = res.partition(KEY_VALUE_SEP_CHAR)
        key = splt[0]
        value = splt[-1]
        if len(key) == 0:
            continue
        if SPLIT_SEP_CHAR in value:
            value = value.split(SPLIT_SEP_CHAR)
        data[key].append(value)
    return data


class SolveResult(object):
    """
    The information returned from a solve.

    All information from the solver, can then be queryied as
    needed. This class never modifies data, it only stores and queries
    data.
    """
    def __init__(self, cmd_data):
        assert isinstance(cmd_data, list)
        # import pprint
        # print 'solver result data:', pprint.pformat(cmd_data)
        data = parse_command_result(cmd_data)
        # print 'data:', pprint.pformat(dict(data))

        # Command Success or not? Did the solver fail?
        self._success = bool(data.get('success', None))

        key_msg = 'Key cannot be found in solver return value:'
        key_msg += ' key=%r'

        # Solver statistics
        name_keys = [
            ('success', 'success', bool),
            ('stop_message', 'reason_string', str),
            ('stop_id', 'reason_num', int),
            ('iteration_total_calls', 'iteration_num', int),
            ('iteration_function_calls', 'iteration_function_num', int),
            ('iteration_jacobian_calls', 'iteration_jacobian_num', int),
            ('attempts', 'iteration_attempt_num', int),
        ]
        self._solver_stats = {}
        for name, key, typ in name_keys:
            if key not in data.keys():
                raise KeyError(key_msg % key)
            value = data.get(key)
            self._solver_stats[name] = typ(value[0])

        # Error statistics
        name_keys = [
            ('initial', 'error_initial', float),
            ('maximum', 'error_maximum', float),
            ('final', 'error_final', float),
            ('final_average', 'error_final_average', float),
            ('final_maximum', 'error_final_maximum', float),
            ('final_minimum', 'error_final_minimum', float),
            ('jt', 'error_jt', float),
            ('dp', 'error_dp', float),
        ]
        self._error_stats = {}
        for name, key, typ in name_keys:
            if key not in data.keys():
                raise KeyError(key_msg % key)
            value = data.get(key)
            self._error_stats[name] = typ(value[0])

        # Timer statistics
        name_keys = [
            ('solve_seconds', 'timer_solve', float),
            ('function_seconds', 'timer_function', float),
            ('jacobian_seconds', 'timer_jacobian', float),
            ('parameter_seconds', 'timer_parameter', float),
            ('error_seconds', 'timer_error', float),
            ('solve_ticks', 'ticks_solve', int),
            ('function_ticks', 'ticks_function', int),
            ('jacobian_ticks', 'ticks_jacobian', int),
            ('parameter_ticks', 'ticks_parameter', int),
            ('error_ticks', 'ticks_error', int),
        ]
        self._timer_stats = {}
        for name, key, typ in name_keys:
            if key not in data.keys():
                raise KeyError(key_msg % key)
            value = data.get(key)
            self._timer_stats[name] = typ(value[0])

        # List of errors, per-marker, per-frame.
        # Allows graphing the errors and detecting problems.
        self._per_marker_per_frame_error = collections.defaultdict(dict)
        key = 'error_per_marker_per_frame'
        if key not in data.keys():
            raise KeyError(key_msg % key)
        values = data.get(key)
        for value in values:
            mkr = str(value[0])
            t = float(value[1])
            v = float(value[2])
            self._per_marker_per_frame_error[mkr][t] = v

        # Errors per frame average
        # Allows graphing the errors and detecting problems.
        self._per_frame_error = {}
        key = 'error_per_frame'
        if key not in data.keys():
            raise KeyError(key_msg % key)
        values = data.get(key)
        for value in values:
            t = float(value[0])
            v = float(value[1])
            self._per_frame_error[t] = v

    def get_success(self):
        return self._success

    def get_final_error(self):
        return self._error_stats.get('final')

    def get_error_stats(self):
        return self._error_stats

    def get_timer_stats(self):
        return self._timer_stats

    def get_solver_stats(self):
        return self._solver_stats

    def get_frame_error_list(self):
        return self._per_frame_error.copy()

    def get_marker_error_list(self, marker_node=None):
        v = None
        if marker_node is None:
            v = self._per_marker_per_frame_error.copy()
        elif marker_node in self._per_marker_per_frame_error:
            v = self._per_marker_per_frame_error.get(marker_node)
        return v
