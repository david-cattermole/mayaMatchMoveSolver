# Copyright (C) 2019 Anil Reddy, David Cattermole.
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
Functions to support smoothing animation curve keyframes.
"""

import math

import maya.cmds
import maya.OpenMaya as OpenMaya1
import maya.OpenMayaAnim as OpenMayaAnim1

import mmSolver.logger
import mmSolver.utils.smooth as utils_smooth
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as animcurve_utils

LOG = mmSolver.logger.get_logger()


def calculate_chunks(selected_keyframes, all_times, all_values):
    """
    Create a list of chunks; each chunk is a list of time values.

    `all_times` is assumed to already be sorted.
    """
    chunks_time_list = []
    chunks_value_list = []
    chunk_time = []
    chunk_value = []
    for t, v in zip(all_times, all_values):
        if t in selected_keyframes:
            chunk_time.append(t)
            chunk_value.append(v)
        elif len(chunk_time) > 0:
            chunks_time_list.append(list(chunk_time))
            chunks_value_list.append(list(chunk_value))
            chunk_time = []
            chunk_value = []
    return chunks_time_list, chunks_value_list


def create_first_last_keyframe_animCurve(selected_keyframes,
                                         all_times,
                                         all_values):
    curve_times = []
    curve_values = []
    chunks_time_list, chunks_value_list = calculate_chunks(
        selected_keyframes,
        all_times,
        all_values)

    for chunk_time, chunk_value in zip(chunks_time_list, chunks_value_list):
        first_time = chunk_time[0]
        first_value = chunk_value[0]
        last_time = chunk_time[-1]
        last_value = chunk_value[-1]

        curve_times.append(first_time)
        curve_times.append(last_time)

        curve_values.append(first_value)
        curve_values.append(last_value)

    tangent = OpenMayaAnim1.MFnAnimCurve.kTangentLinear
    anim_chunk_fn = animcurve_utils.create_anim_curve_node_apione(
        curve_times,
        curve_values,
        tangent_in_type=tangent,
        tangent_out_type=tangent)
    return anim_chunk_fn


def blend_curves_with_difference(selected_keyframes,
                                 all_times,
                                 value_array,
                                 new_value_array):
    """Create a new array of values based on the difference between
    value_array at the start/end of of each chunk of selected
    keyframes.

    The algorithm works like this:

    #. Calculate chunks.

    #. Create a linear curve between start/end keyframe values of the
       smoothed curve.

    #. Subtract the linear curve from the smoothed curve.

    #. Create another linear curve between start/end keyframe values
       of the value curve.

    #. Subtract the linear curve from the value curve.

    #. Add the difference between the linear value curve and the
       linear smooth curve, to the smoothed curve.

    #. Blend between the smooth and original value.

    :rtype: [float, ..]
    """
    old_linear_curve_fn = create_first_last_keyframe_animCurve(
        selected_keyframes,
        all_times,
        value_array,
    )
    new_linear_curve_fn = create_first_last_keyframe_animCurve(
        selected_keyframes,
        all_times,
        new_value_array,
    )

    # Adjust smooth values based on the difference between the old and
    # new values.
    ui_unit = OpenMaya1.MTime.uiUnit()
    for i, t in enumerate(all_times):
        frame = OpenMaya1.MTime(float(t), ui_unit)
        old_linear_value = old_linear_curve_fn.evaluate(frame)
        new_linear_value = new_linear_curve_fn.evaluate(frame)
        new_value = new_value_array[i]
        new_value_array[i] = old_linear_value + (new_value - new_linear_value)

    old_linear_curve_node_name = old_linear_curve_fn.name()
    new_linear_curve_node_name = new_linear_curve_fn.name()
    maya.cmds.delete(old_linear_curve_node_name)
    maya.cmds.delete(new_linear_curve_node_name)
    return new_value_array


def smooth_animcurve(animcurve, selected_keyframes,
                     smooth_type, width,
                     blend_smooth_type, blend_width):
    """
    Smooth the given keyframes for an animCurve.

    :param animcurve:
        Animation curve node name.
    :type animcurve: str

    :param selected_keyframes:
        The frame numbers that are 'selected' to be smoothed.
    :type selected_keyframes: [int, ..] or []

    :param smooth_type:
        What algorithm to use for smoothing.
    :type smooth_type: ?

    :param width:
        The width of the smoothing kernel; higher values produce more
        smoothing, and is slower to compute.
    :type width: float

    :param blend_smooth_type:
        What algorithm to use for smoothing the blend?
    :type blend_smooth_type: ?

    :param blend_width:
        The width of the smoothing kernel; higher values produce more
        smoothing, and is slower to compute.
    :type blend_width: float
    """
    times = maya.cmds.keyframe(animcurve, query=True, timeChange=True)
    if len(times) < 1:
        return
    first_time = int(times[0])
    last_time = int(times[-1])
    first_time_padded = int(first_time - (width * 2))
    last_time_padded = int(last_time + (width * 2))
    all_times = xrange(first_time_padded, last_time_padded + 1)

    sel_first_time = int(selected_keyframes[0])
    sel_last_time = int(selected_keyframes[-1])
    sel_range_length = sel_last_time - sel_first_time
    original_range_length = last_time - first_time

    all_keys_selected = original_range_length == sel_range_length

    plug = animcurve + '.output'
    animCurve_obj = node_utils.get_as_object_apione(animcurve)
    animCurve_fn = OpenMayaAnim1.MFnAnimCurve(animCurve_obj)
    animCurve_type = animCurve_fn.animCurveType()
    ui_unit = OpenMaya1.MTime.uiUnit()

    initial_weight = 0.0
    if all_keys_selected:
        initial_weight = 1.0

    values = []
    weight_array = [initial_weight] * len(all_times)
    value_array = [None] * len(all_times)
    for i, t in enumerate(all_times):
        frame = OpenMaya1.MTime(float(t), ui_unit)
        value = animCurve_fn.evaluate(frame)
        if animCurve_type == OpenMayaAnim1.MFnAnimCurve.kAnimCurveTA:
            value = math.degrees(value)
        value_array[i] = value

        if t < first_time:
            first_weight = initial_weight
            weight_array[i] = first_weight
            continue

        if t > last_time:
            last_weight = initial_weight
            weight_array[i] = last_weight
            continue

        if t in selected_keyframes:
            weight_array[i] = 1.0

    new_weight_array = utils_smooth.smooth(
        blend_smooth_type,
        weight_array,
        width
    )
    new_value_array = utils_smooth.smooth(
        smooth_type,
        value_array,
        blend_width
    )
    assert len(value_array) == len(new_value_array)
    assert len(weight_array) == len(new_weight_array)

    if all_keys_selected is False:
        new_value_array = blend_curves_with_difference(
            selected_keyframes,
            all_times,
            value_array,
            new_value_array,
        )

    # Blend betwen original and smoothed curves using the weight.
    for frame, old_value, new_value, weight in zip(all_times,
                                                   value_array,
                                                   new_value_array,
                                                   new_weight_array):
        if frame not in times:
            continue
        inverse_weight = 1.0 - weight
        v = (new_value * weight) + (old_value * inverse_weight)
        time_range = (frame, frame)
        maya.cmds.keyframe(
            animcurve,
            valueChange=v,
            time=time_range)
    return
