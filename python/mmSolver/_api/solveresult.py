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
The information returned from a solve.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import datetime

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()
KEY_VALUE_SEP_CHAR = '='
SPLIT_SEP_CHAR = '#'


def parse_command_result(cmd_result):
    """
    Convert results from the mmSolver command into python data structure.

    :param cmd_result: 'mmSolver' command result.
    :type cmd_result: list of str

    :return: dict with keys and values for each entry in the result.
    :rtype: dict
    """
    data = collections.defaultdict(list)
    for res in cmd_result:
        assert isinstance(res, pycompat.TEXT_TYPE)
        splt = res.partition(KEY_VALUE_SEP_CHAR)
        key = splt[0]
        value = splt[-1]
        if len(key) == 0:
            continue
        if SPLIT_SEP_CHAR in value:
            value = value.split(SPLIT_SEP_CHAR)
        data[key].append(value)
    return data


def _convert_to(name, key, typ, value, index):
    """
    Convert data returned from mmSolver into the value it's meant to be.

    :param name: Nice name of the data.
    :type name: str

    :param key: Internal name of the data.
    :type key: str

    :param typ: The type object to convert this data into.
    :type typ: object

    :param value: The value to convert into 'typ'.
    :type value: any

    :param index: The index into 'value', used if value has multiple
                  values.
    :type index: int

    :returns: A value of 'typ' kind.
    """
    msg = 'mmSolver data is incomplete, '
    msg += 'a solver error may have occurred: '
    msg += 'name={0} key={1} typ={2} value={3}'

    if value is None or len(value) == 0:
        LOG.debug(msg.format(name, key, typ, value))
        return typ()

    if typ is float and not isinstance(value[index], (pycompat.TEXT_TYPE, float)):
        return typ()

    if typ is str and not isinstance(
        value[index], (pycompat.TEXT_TYPE, float, int, bool)
    ):
        return typ()

    if typ is int:
        if isinstance(value[index], (pycompat.TEXT_TYPE, float)):
            value[index] = float(value[index])
        else:
            return typ()

    if typ is bool:
        if isinstance(value[index], (pycompat.TEXT_TYPE, float)):
            value[index] = int(value[index])
        else:
            return typ()

    v = typ(value[index])

    if typ is float and (math.isinf(v) or math.isnan(v)):
        LOG.debug(msg.format(name, key, typ, value))
        return typ(-1.0)

    return v


class SolveResult(object):
    """
    The information returned from a solve.

    All information from the solver, can then be queried as
    needed. This class never modifies data, it only stores and queries
    data.
    """

    def __init__(self, cmd_data):
        """
        Create a new SolveResult using command data from
        *maya.cmds.mmSolver* command.

        :param cmd_data: Command data from mmSolver.
        :type cmd_data: [[str, ..], ..]
        """
        if isinstance(cmd_data, list) is False:
            msg = 'cmd_data is of type %r, expected a list object.'
            raise TypeError(msg % type(cmd_data))
        self._raw_data = list(cmd_data)
        data = parse_command_result(cmd_data)

        # Common warning message in this method.
        msg = 'mmSolver data is incomplete, '
        msg += 'a solver error may have occurred: '
        msg += 'name={0} key={1} typ={2} value={3}'

        # Solver statistics
        name_keys = [
            ('success', 'success', bool),
            ('stop_message', 'reason_string', str),
            ('stop_id', 'reason_num', int),
            ('iteration_total_calls', 'iteration_num', int),
            ('iteration_function_calls', 'iteration_function_num', int),
            ('iteration_jacobian_calls', 'iteration_jacobian_num', int),
            ('attempts', 'iteration_attempt_num', int),
            ('user_interrupted', 'user_interrupted', bool),
        ]
        index = 0
        self._solver_stats = {}
        for name, key, typ in name_keys:
            value = data.get(key)
            v = _convert_to(name, key, typ, value, index)
            self._solver_stats[name] = v

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
        index = 0
        self._error_stats = {}
        for name, key, typ in name_keys:
            value = data.get(key)
            v = _convert_to(name, key, typ, value, index)
            self._error_stats[name] = v

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
        index = 0
        self._timer_stats = {}
        for name, key, typ in name_keys:
            value = data.get(key)
            v = _convert_to(name, key, typ, value, index)
            self._timer_stats[name] = v

        # Print statistics
        name_keys = [
            ('number_of_parameters', 'numberOfParameters', int),
            ('number_of_errors', 'numberOfErrors', int),
        ]
        index = 0
        self._print_stats = {}
        for name, key, typ in name_keys:
            value = data.get(key)
            v = _convert_to(name, key, typ, value, index)
            self._print_stats[name] = v

        # List of errors, per-marker, per-frame.
        # Allows graphing the errors and detecting problems.
        self._per_marker_per_frame_error = collections.defaultdict(dict)
        key = 'error_per_marker_per_frame'
        values = data.get(key)
        name = ''
        if values is None or len(values) == 0:
            LOG.debug(msg.format(name, key, 'None', values))
        else:
            for value in values:
                mkr = _convert_to(name, key, str, value, 0)
                t = _convert_to(name, key, float, value, 1)
                v = _convert_to(name, key, float, value, 2)
                self._per_marker_per_frame_error[mkr][t] = v

        # Errors per frame
        # Allows graphing the errors and detecting problems.
        self._per_frame_error = {}
        name = ''
        key = 'error_per_frame'
        values = data.get(key)
        if values is None or len(values) == 0:
            LOG.debug(msg.format(name, key, 'None', values))
        else:
            for value in values:
                t = _convert_to(name, key, float, value, 0)
                v = _convert_to(name, key, float, value, 1)
                self._per_frame_error[t] = v
        return

    def get_data_raw(self):
        """
        Get a copy of the raw data given to this object at initialization.

        It is possible to re-create this object exactly by saving this
        raw data and re-initializing the object with this data.
        """
        return list(self._raw_data)

    def get_success(self):
        """
        Command Success or not? Did the solver fail?
        """
        return self._solver_stats.get('success')

    def get_final_error(self):
        """
        The single error value representing the solve at it's last state.
        """
        return self._error_stats.get('final')

    def get_user_interrupted(self):
        """
        Did the user purposely cancel the solve?
        """
        return self._solver_stats.get('user_interrupted', False)

    def get_error_stats(self):
        """
        Details for the error (deviation) of the solve.
        """
        return self._error_stats.copy()

    def get_timer_stats(self):
        """
        Details for how long different aspects of the solve took to compute.
        """
        return self._timer_stats.copy()

    def get_solver_stats(self):
        """
        Details of internal solver.
        """
        return self._solver_stats.copy()

    def get_print_stats(self):
        """
        Details of internal statistics that can be gathered and
        printed out.
        """
        return self._print_stats.copy()

    def get_frame_list(self):
        """
        The list of frames that this solve result contains.
        """
        return list(sorted(self._per_frame_error.keys()))

    def get_frame_error_list(self):
        """
        The error (deviation) per-frame of the solver.
        """
        return self._per_frame_error.copy()

    def get_marker_error_list(self, marker_node=None):
        """
        Get a list of errors (deviation) for all markers, or the given marker.

        :param marker_node: The specific marker node to get an error list for.
        :type marker_node: str or None

        :returns: A dict of marker node names and time values, giving
                  the error (deviation).
        :rtype: {"marker_node": {float: float}}
        """
        assert marker_node is None or isinstance(marker_node, pycompat.TEXT_TYPE)
        v = None
        if marker_node is None:
            v = self._per_marker_per_frame_error.copy()
        elif marker_node in self._per_marker_per_frame_error:
            v = self._per_marker_per_frame_error.get(marker_node)
        return v


def combine_timer_stats(solres_list):
    """
    Combine Timer statistics into one set.

    :param solres_list: List of SolveResult to combine together.
    :type solres_list: [SolveResult, ..]

    :returns: A map of time statistics, accumulated over all runs
              of the Solver.
    :rtype: dict
    """
    assert isinstance(solres_list, (list, tuple))
    stats_list = collections.defaultdict(float)
    msg = 'solres must be a SolveResult object: solres=%r'
    for solres in solres_list:
        if isinstance(solres, SolveResult) is False:
            raise TypeError(msg % solres)
        stats = solres.get_timer_stats()
        for k, v in stats.items():
            if stats_list.get(k) is None:
                if isinstance(v, int):
                    stats_list[k] = 0
                elif isinstance(v, float):
                    stats_list[k] = 0.0
            if isinstance(v, (int, float)):
                stats_list[k] += v
    return stats_list


def merge_frame_list(solres_list):
    """
    Combine a 'frame_list' from a list of SolveResult objects.

    :param solres_list: List of SolveResult to merge together.
    :type solres_list: [SolveResult, ..]

    :returns: A list of frame numbers.
    :rtype: [int, ..] or [float, ..]
    """
    assert isinstance(solres_list, (list, tuple))
    frame_list = set()
    msg = 'solres must be a SolveResult object: solres=%r'
    for solres in solres_list:
        if isinstance(solres, SolveResult) is False:
            raise TypeError(msg % solres)
        frame_list |= set(solres.get_frame_list())
    frame_list = list(frame_list)
    frame_list = list(sorted(frame_list))
    return frame_list


def merge_frame_error_list(solres_list):
    """
    Combine a 'frame_error_list' from a list of SolveResult objects.

    The 'solres_list' is assumed to represent sequential solver
    executions; The order of this list is important, because only
    the last solved error value is used.

    :param solres_list: List of SolveResult to merge together.
    :type solres_list: [SolveResult, ..]

    :returns: Mapping of frame number to error values.
    :rtype: dict
    """
    assert isinstance(solres_list, (list, tuple))
    frame_error_list = collections.defaultdict(float)
    msg = 'solres must be a SolveResult object: solres=%r'
    for solres in solres_list:
        if isinstance(solres, SolveResult) is False:
            raise TypeError(msg % solres)
        frm_err_list = solres.get_frame_error_list()
        for k, v in frm_err_list.items():
            frame_error_list[k] = v
    return frame_error_list


def get_average_frame_error_list(frame_error_list):
    """
    Get the average error for the frame error map given.

    :param frame_error_list: Mapping of frame and error deviation.
    :type frame_error_list: {float: float}

    :returns: Average error across all frames.
    :rtype: float
    """
    assert isinstance(frame_error_list, dict)
    error = 0.0
    total = 0
    for k, v in frame_error_list.items():
        error += float(v)
        total += 1
    if total > 0:
        error = error / float(total)
    return error


def get_max_frame_error(frame_error_list):
    """
    Get the frame and error combination for the frame error map given.

    If frame_error_list given is empty, the returned frame will be None.

    :param frame_error_list: Mapping of frame and error deviation.
    :type frame_error_list: {float: float}

    :returns: The frame and error with the maximum amount of error.
    :rtype: (int or None, float)
    """
    assert isinstance(frame_error_list, dict)
    frame = None
    error = -0.0
    for k, v in frame_error_list.items():
        x = float(v)
        if x > error:
            frame = int(k)
            error = x
    return frame, error


def merge_marker_error_list(solres_list):
    """
    Combine a 'marker_error_list' from a list of SolveResult objects.

    .. note::
       The 'solres_list' is assumed to represent sequential
       solver executions; The order of this list is important, because
       only the last solved error value is used.

    :param solres_list: List of SolveResult to merge together.
    :type solres_list: [SolveResult, ..]

    :returns: Mapping of frame number to error values.
    :rtype: dict
    """
    assert isinstance(solres_list, (list, tuple))
    marker_error_list = collections.defaultdict(dict)
    msg = 'solres must be a SolveResult object: solres=%r'
    for solres in solres_list:
        if isinstance(solres, SolveResult) is False:
            raise TypeError(msg % solres)
        mkr_err_data = solres.get_marker_error_list(marker_node=None)
        for k1, v1 in mkr_err_data.items():
            for k2, v2 in v1.items():
                marker_error_list[k1][k2] = v2
    return marker_error_list


def merge_marker_node_list(solres_list):
    """
    Get all the markers used in the SolveResults given.

    :param solres_list: List of SolveResult to merge together.
    :type solres_list: [SolveResult, ..]

    :returns: A list of Maya nodes of Markers.
    :rtype: [str, ..]
    """
    assert isinstance(solres_list, (list, tuple))
    mkr_nodes = set()
    msg = 'solres must be a SolveResult object: solres=%r'
    for solres in solres_list:
        if isinstance(solres, SolveResult) is False:
            raise TypeError(msg % solres)
        data = solres.get_marker_error_list()
        mkr_nodes |= set(data.keys())
    mkr_nodes = list(mkr_nodes)
    mkr_nodes = list(sorted(mkr_nodes))
    return mkr_nodes


def format_timestamp(value):
    """
    Convert a 'UNIX Epoch' float number to a human-readable Timestamp.

    :param value: Input UNIX Epoch as returned by 'time.time()' function.
    :type value: float

    :returns: Human (and machine) readable timestamp.
    :rtype: str
    """
    assert isinstance(value, float)
    ts = datetime.datetime.fromtimestamp(value)
    # Remove microseconds from the datetime object.
    stamp = ts.replace(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, 0)
    stamp = stamp.isoformat(' ')
    assert isinstance(stamp, str)
    return stamp
