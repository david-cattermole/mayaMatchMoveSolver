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
import datetime
import math
import pprint

import maya.cmds

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
        split = res.partition(KEY_VALUE_SEP_CHAR)
        key = split[0]
        value = split[-1]
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
    assert callable(typ) is True
    msg = 'mmSolver data is incomplete, '
    msg += 'a solver error may have occurred: '
    msg += 'name={0} key={1} type={2} value={3}'

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


def _string_get_solver_stats(input_data):
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
    solver_stats = {}
    for name, key, typ in name_keys:
        value = input_data.get(key)
        v = _convert_to(name, key, typ, value, index)
        solver_stats[name] = v
    return solver_stats


def _string_get_solver_frames_stats(input_data):
    name_keys = [
        ('number_of_valid_frames', 'number_of_valid_frames', int, None),
        ('number_of_invalid_frames', 'number_of_invalid_frames', int, None),
        ('valid_frames', 'valid_frames', list, int),
        ('invalid_frames', 'invalid_frames', list, int),
    ]
    index = 0
    solver_frames = {}
    for name, key, outer_type, inner_type in name_keys:
        value = input_data.get(key)
        if value is None:
            continue
        if inner_type is None:
            v = _convert_to(name, key, outer_type, value, index)
            solver_frames[name] = v
        else:
            if len(value) == 1:
                value = value[0]
            values = []
            for v in value:
                if len(v) > 0:
                    values.append(inner_type(v))
            solver_frames[name] = values
    return solver_frames


def _string_get_error_stats(input_data):
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
    error_stats = {}
    for name, key, typ in name_keys:
        value = input_data.get(key)
        v = _convert_to(name, key, typ, value, index)
        error_stats[name] = v
    return error_stats


def _string_get_timer_stats(input_data):
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
    timer_stats = {}
    for name, key, typ in name_keys:
        value = input_data.get(key)
        v = _convert_to(name, key, typ, value, index)
        timer_stats[name] = v
    return timer_stats


def _string_get_print_stats(input_data):
    name_keys = [
        ('number_of_parameters', 'numberOfParameters', int),
        ('number_of_errors', 'numberOfErrors', int),
    ]
    index = 0
    print_stats = {}
    for name, key, typ in name_keys:
        value = input_data.get(key)
        v = _convert_to(name, key, typ, value, index)
        print_stats[name] = v
    return print_stats


def _string_get_error_per_frame(input_data):
    # Common warning message in this method.
    msg = 'mmSolver data is incomplete, '
    msg += 'a solver error may have occurred: '
    msg += 'name={0} key={1} type={2} value={3}'

    # Errors per frame
    # Allows graphing the errors and detecting problems.
    per_frame_error = {}
    name = ''
    key = 'error_per_frame'
    values = input_data.get(key)
    if values is None or len(values) == 0:
        LOG.debug(msg.format(name, key, 'None', values))
    else:
        for value in values:
            t = _convert_to(name, key, float, value, 0)
            v = _convert_to(name, key, float, value, 1)
            per_frame_error[t] = v
    return per_frame_error


def _string_get_error_per_marker_per_frame(input_data):
    # Common warning message in this method.
    msg = 'mmSolver data is incomplete, '
    msg += 'a solver error may have occurred: '
    msg += 'name={0} key={1} type={2} value={3}'

    # List of errors, per-marker, per-frame.
    # Allows graphing the errors and detecting problems.
    per_marker_per_frame_error = collections.defaultdict(dict)
    key = 'error_per_marker_per_frame'
    values = input_data.get(key)
    name = ''
    if values is None or len(values) == 0:
        LOG.debug(msg.format(name, key, 'None', values))
    else:
        for value in values:
            mkr = _convert_to(name, key, str, value, 0)
            t = _convert_to(name, key, float, value, 1)
            v = _convert_to(name, key, float, value, 2)
            per_marker_per_frame_error[mkr][t] = v

    return per_marker_per_frame_error


def _get_maya_attr_anim_curve(node, attr_name, existing_attrs):
    if attr_name not in existing_attrs:
        return None
    plug = '{}.{}'.format(node, attr_name)
    anim_curves = maya.cmds.listConnections(plug, type='animCurve') or []
    if len(anim_curves) == 0:
        return None
    return anim_curves[0]


def _get_node_frame_list(node, attr_name, existing_attrs):
    anim_curve = _get_maya_attr_anim_curve(node, attr_name, existing_attrs)
    if anim_curve is None:
        return {}

    keyframe_times = maya.cmds.keyframe(anim_curve, query=True, timeChange=True) or []
    return set(keyframe_times)


def _get_node_frame_error_list(node, attr_name, existing_attrs):
    anim_curve = _get_maya_attr_anim_curve(node, attr_name, existing_attrs)
    if anim_curve is None:
        return {}

    keyframe_times = maya.cmds.keyframe(anim_curve, query=True, timeChange=True) or []
    times_and_values = {}
    for keyframe_time in keyframe_times:
        time = (keyframe_time, keyframe_time)
        value = maya.cmds.keyframe(anim_curve, query=True, eval=True, time=time)[0]
        if value > 0.0:
            times_and_values[keyframe_time] = value
    return times_and_values


def _get_maya_attr(node, attr_name, typ, existing_attrs):
    if attr_name not in existing_attrs:
        return typ()
    plug = '{}.{}'.format(node, attr_name)
    return typ(maya.cmds.getAttr(plug))


def _node_get_error_stats(node, existing_attrs):
    assert maya.cmds.objExists(node) is True
    data = {
        'initial': _get_maya_attr(node, 'error_initial', float, existing_attrs),
        'maximum': _get_maya_attr(node, 'error_maximum', float, existing_attrs),
        'final': _get_maya_attr(node, 'error_final', float, existing_attrs),
        'final_average': _get_maya_attr(
            node, 'error_final_average', float, existing_attrs
        ),
        'final_maximum': _get_maya_attr(
            node, 'error_final_maximum', float, existing_attrs
        ),
        'final_minimum': _get_maya_attr(
            node, 'error_final_minimum', float, existing_attrs
        ),
        'jt': _get_maya_attr(node, 'error_jt', float, existing_attrs),
        'dp': _get_maya_attr(node, 'error_dp', float, existing_attrs),
    }
    return data


def _node_get_timer_stats(node, existing_attrs):
    assert maya.cmds.objExists(node) is True
    data = {
        'solve_seconds': _get_maya_attr(node, 'timer_solve', float, existing_attrs),
        'function_seconds': _get_maya_attr(
            node, 'timer_function', float, existing_attrs
        ),
        'jacobian_seconds': _get_maya_attr(
            node, 'timer_jacobian', float, existing_attrs
        ),
        'parameter_seconds': _get_maya_attr(
            node, 'timer_parameter', float, existing_attrs
        ),
        'error_seconds': _get_maya_attr(node, 'timer_error', float, existing_attrs),
        'solve_ticks': _get_maya_attr(node, 'ticks_solve', int, existing_attrs),
        'function_ticks': _get_maya_attr(node, 'ticks_function', int, existing_attrs),
        'jacobian_ticks': _get_maya_attr(node, 'ticks_jacobian', int, existing_attrs),
        'parameter_ticks': _get_maya_attr(node, 'ticks_parameter', int, existing_attrs),
        'error_ticks': _get_maya_attr(node, 'ticks_error', int, existing_attrs),
    }
    return data


def _node_get_solver_stats(node, existing_attrs):
    assert maya.cmds.objExists(node) is True
    data = {
        'success': _get_maya_attr(node, 'success', bool, existing_attrs),
        'stop_message': _get_maya_attr(node, 'reason_string', str, existing_attrs),
        'stop_id': _get_maya_attr(node, 'reason_num', int, existing_attrs),
        'iteration_total_calls': _get_maya_attr(
            node, 'iteration_num', int, existing_attrs
        ),
        'iteration_function_calls': _get_maya_attr(
            node, 'iteration_function_num', int, existing_attrs
        ),
        'iteration_jacobian_calls': _get_maya_attr(
            node, 'iteration_jacobian_num', int, existing_attrs
        ),
        'attempts': _get_maya_attr(node, 'iteration_attempt_num', int, existing_attrs),
        'user_interrupted': _get_maya_attr(
            node, 'user_interrupted', int, existing_attrs
        ),
    }
    return data


def _node_get_solver_frames_stats(node, existing_attrs):
    assert maya.cmds.objExists(node) is True
    data = {
        'number_of_valid_frames': _get_maya_attr(
            node, 'number_of_valid_frames', int, existing_attrs
        ),
        'number_of_invalid_frames': _get_maya_attr(
            node, 'number_of_invalid_frames', int, existing_attrs
        ),
        'valid_frames': _get_node_frame_list(node, 'valid_frames', existing_attrs),
        'invalid_frames': _get_node_frame_list(node, 'invalid_frames', existing_attrs),
    }
    return data


def _node_get_print_stats(node, existing_attrs):
    assert maya.cmds.objExists(node) is True
    data = {
        'number_of_parameters': _get_maya_attr(
            node, 'numberOfParameters', int, existing_attrs
        ),
        'number_of_errors': _get_maya_attr(node, 'numberOfErrors', int, existing_attrs),
    }
    return data


def _node_get_per_frame_error(node, existing_attrs):
    return _get_node_frame_error_list(node, 'deviation', existing_attrs)


def _node_get_per_marker_per_frame_error(node, existing_attrs):
    assert maya.cmds.objExists(node) is True

    # Get all Marker nodes
    marker_attrs = [x for x in existing_attrs if x.startswith("mkr___")]
    marker_names = set([x.split('___')[1] for x in marker_attrs])
    marker_nodes = [x for x in marker_names if maya.cmds.objExists(x) is True]
    marker_nodes = [maya.cmds.ls(x, long=True) or [] for x in marker_nodes]
    marker_nodes = set([x[0] for x in marker_nodes if len(x) > 0])

    data = collections.defaultdict(dict)
    for mkr_node in marker_nodes:
        mkr_existing_attrs = maya.cmds.listAttr(mkr_node) or []
        data[mkr_node] = _get_node_frame_error_list(
            mkr_node, 'deviation', mkr_existing_attrs
        )
    return data


class SolveResult(object):
    """
    The information returned from a solve.

    All information from the solver, can then be queried as
    needed. This class never modifies data, it only stores and queries
    data.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new SolveResult using data from
        "maya.cmds.mmSolver*" commands.

        This class has two possible data sources; a list of strings,
        or a Maya node.

        When a Maya node name is given (as a str) the node is expected
        to have attributes with specific names that are looked up.

        When a list of strings is given (as a list of str), the list
        of strings is parsed and names are expected to be looked up

        :param cmd_data: Command data from mmSolver (v1) command.
        :type cmd_data: [[str, ..], ..]

        :param cmd_data: Maya node name containing attributes filled
            in by 'mmSolver_v2' command.
        :type cmd_data: str
        """
        if isinstance(args[0], pycompat.TEXT_TYPE) is True:
            self._input_mode = 0
            node = args[0]
            existing_attrs = maya.cmds.listAttr(node)
            self._solver_stats = _node_get_solver_stats(node, existing_attrs)
            self._error_stats = _node_get_error_stats(node, existing_attrs)
            self._timer_stats = _node_get_timer_stats(node, existing_attrs)
            self._solver_frames_stats = _node_get_solver_frames_stats(data)
            self._print_stats = _node_get_print_stats(node, existing_attrs)
            self._per_frame_error = _node_get_per_frame_error(node, existing_attrs)
            self._per_marker_per_frame_error = _node_get_per_marker_per_frame_error(
                node, existing_attrs
            )
        elif isinstance(args[0], list) is True:
            self._input_mode = 1
            cmd_data = args[0]
            self._raw_data = list(cmd_data)
            data = parse_command_result(cmd_data)
            self._solver_stats = _string_get_solver_stats(data)
            self._error_stats = _string_get_error_stats(data)
            self._timer_stats = _string_get_timer_stats(data)
            self._solver_frames_stats = _string_get_solver_frames_stats(data)
            self._print_stats = _string_get_print_stats(data)
            self._per_marker_per_frame_error = _string_get_error_per_marker_per_frame(
                data
            )
            self._per_frame_error = _string_get_error_per_frame(data)
        else:
            msg = 'argument is of type %r, expected a list or str.'
            raise TypeError(msg % type(args[0]))
        return

    def get_data_raw(self):
        """
        Get a copy of the raw data given to this object at initialization.

        It is possible to re-create this object exactly by saving this
        raw data and re-initializing the object with this data.
        """
        if self._input_mode == 1:
            return list(self._raw_data)
        elif self._input_mode == 0:
            error_stats = self.get_error_stats()
            timer_stats = self.get_timer_stats()
            solver_stats = self.get_solver_stats()
            print_stats = self.get_print_stats()
            per_frame_error = self.get_frame_error_list()
            per_marker_per_frame_error = self.get_marker_error_list(marker_node=None)
            data = {
                'error_stats': error_stats,
                'timer_stats': timer_stats,
                'solver_stats': solver_stats,
                'print_stats': print_stats,
                'per_frame_error': per_frame_error,
                'per_marker_per_frame_error': per_marker_per_frame_error,
            }
            return data
        else:
            raise NotImplementedError

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

    def get_solver_frames_stats(self):
        """
        Details of internal statistics that can be gathered and
        printed out.
        """
        return self._solver_frames_stats.copy()

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

    def get_solver_valid_frame_list(self):
        """
        The list of valid frames that the solver can solve.
        """
        frame_list = self._solver_frames_stats.get('valid_frames', [])
        return list(sorted(frame_list))

    def get_solver_invalid_frame_list(self):
        """
        The list of invalid frames that the solver can solve.
        """
        frame_list = self._solver_frames_stats.get('invalid_frames', [])
        return list(sorted(frame_list))


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
    assert isinstance(stamp, pycompat.TEXT_TYPE)
    return stamp
