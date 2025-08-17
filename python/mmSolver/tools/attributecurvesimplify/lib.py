# Copyright (C) 2025 David Cattermole.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.node as node_utils
import mmSolver.ui.channelboxutils as channelbox_utils
import mmSolver.tools.attributecurvesimplify.constant as const


LOG = mmSolver.logger.get_logger()


def get_frame_range(frame_range_mode, custom_start_frame, custom_end_frame):
    LOG.debug("custom_start_frame: %r", custom_start_frame)
    LOG.debug("custom_end_frame: %r", custom_end_frame)
    LOG.debug("frame_range_mode: %r", frame_range_mode)
    assert isinstance(frame_range_mode, pycompat.TEXT_TYPE)
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES
    assert isinstance(custom_start_frame, pycompat.INT_TYPES)
    assert isinstance(custom_end_frame, pycompat.INT_TYPES)

    frame_range = None
    if frame_range_mode == const.FRAME_RANGE_MODE_INPUT_ANIM_CURVE_VALUE:
        frame_range = time_utils.FrameRange(0, 0)
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_outer()
    elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
        frame_range = time_utils.FrameRange(custom_start_frame, custom_end_frame)
    else:
        LOG.error("Invalid frame range mode: %r", frame_range_mode)
    return frame_range


def _get_node_attrs_for_selected_keyframes():
    """Get animCurve nodes from the selected keyframes (in the graph
    editor).
    """
    selected_anim_curve_nodes = (
        maya.cmds.keyframe(query=True, selected=True, name=True) or []
    )
    node_attrs = set()
    for anim_curve_node in selected_anim_curve_nodes:
        node_attr = anim_curve_node + ".output"
        conns = (
            maya.cmds.listConnections(
                node_attr, destination=False, source=False, plugs=True
            )
            or []
        )
        node_attrs |= set(conns)
    return list(sorted(node_attrs))


def _get_selected_graph_editor_outliner_node_attributes():
    """
    Get the attributes from the selected graph editor outliner.
    """
    # NOTE: Do we need to support multiple graph editors?
    connection_object = "graphEditor1FromOutliner"
    objects = (
        maya.cmds.selectionConnection(connection_object, query=True, object=True) or []
    )

    node_attrs = set()
    for obj in objects:
        if not isinstance(obj, pycompat.TEXT_TYPE):
            continue
        if "." in obj:
            node_attrs.add(obj)
    return list(sorted(node_attrs))


def _get_selected_channelbox_attributes():
    """Get the selected attributes from the channel box."""
    name = channelbox_utils.get_ui_name()
    attrs = maya.cmds.channelBox(name, query=True, selectedMainAttributes=True) or []
    return attrs


def get_selected_node_attrs(nodes):
    """
    Get the selected node attributes, from the Graph Editor or
    Channel Box.

    A universal function to get whatever the user has "selected" for
    the animation curve. This includes looking at the channel box, or
    using the selected curves in the Graph Editor, etc.
    """
    node_attrs = _get_node_attrs_for_selected_keyframes()
    if len(node_attrs) > 0:
        return node_attrs

    node_attrs = _get_selected_graph_editor_outliner_node_attributes()
    if len(node_attrs) > 0:
        return node_attrs

    channelbox_attrs = _get_selected_channelbox_attributes()
    if len(channelbox_attrs) == 0:
        LOG.warn("Please select at least 1 attribute in the Channel Box.")
        return []

    # Combine nodes with attributes
    node_attrs = []
    for node in nodes:
        for attr in channelbox_attrs:
            if node_utils.attribute_exists(attr, node):
                node_attr = "{}.{}".format(node, attr)
                node_attrs.append(node_attr)

    return node_attrs


def get_attribute_anim_curves(node_attrs):
    """
    Return anim curve nodes from attributes.

    :param node_attrs: Node attribute names.
    :rtype: []
    """
    assert len(node_attrs) > 0
    assert isinstance(node_attrs, (list, set))
    anim_curve_node = maya.cmds.listConnections(node_attrs, type="animCurve") or []

    anim_curve_nodes = []
    if isinstance(anim_curve_node, pycompat.TEXT_TYPE):
        anim_curve_nodes = [anim_curve_node]
    elif isinstance(anim_curve_node, list):
        anim_curve_nodes = anim_curve_node
    return anim_curve_nodes


def get_selected_anim_curves():
    nodes = maya.cmds.ls(selection=True) or []
    LOG.debug("nodes: %r", nodes)
    if len(nodes) == 0:
        LOG.warn("Please select at least 1 object.")
        return []

    node_attrs = get_selected_node_attrs(nodes)
    LOG.debug("node_attrs: %r", node_attrs)
    if len(node_attrs) == 0:
        LOG.warn(
            "Please select at least 1 attribute in the Channel Box or Graph Editor."
        )
        return []

    anim_curve_nodes = get_attribute_anim_curves(
        node_attrs,
    )
    LOG.debug("anim_curve_nodes: %r", anim_curve_nodes)
    if len(anim_curve_nodes) == 0:
        LOG.warn(
            "No animation curves found on attributes, "
            "please bake attribute curves first."
        )
        return []

    return anim_curve_nodes


def node_attr_from_anim_curve_nodes(anim_curve_nodes):
    return [node_attr_from_anim_curve_node(x) for x in anim_curve_nodes]


def node_attr_from_anim_curve_node(anim_curve_node):
    assert isinstance(anim_curve_node, pycompat.TEXT_TYPE)
    assert len(anim_curve_node) > 0
    assert maya.cmds.objExists(anim_curve_node)
    assert maya.cmds.nodeType(anim_curve_node).startswith("animCurve")
    plugs = (
        maya.cmds.listConnections(
            anim_curve_node, destination=True, source=False, plugs=True
        )
        or []
    )
    assert len(plugs) > 0
    return plugs[0]


def sort_anim_curves_by_node_attrs(anim_curve_nodes, node_attrs):
    """
    Sort by anim_curve_nodes by the attribute name, especially
    ensuring that translateXYZ goes before rotateXYZ, then scaleXYZ,
    and then any other attributes in alphabetical order.
    """

    all_anim_curve_nodes = list(anim_curve_nodes)
    all_node_attrs = list(node_attrs)
    all_attrs = []
    for node_attr in all_node_attrs:
        all_attrs.append(node_attr.split('.')[-1])

    out_anim_curve_nodes = []
    out_node_attrs = []

    # Sort the translation attributes.
    attr_sort_order = ['translate', 'rotate', 'scale']
    for attr_name_sort_begin in attr_sort_order:
        combined = zip(all_anim_curve_nodes, all_node_attrs, all_attrs)

        filtered = []
        for item in combined:
            anim_curve_node, node_attr, attr_name = item
            if attr_name.startswith(attr_name_sort_begin):
                filtered.append(item)

        for item in sorted(filtered, key=lambda x: x[2]):
            out_anim_curve_nodes.append(item[0])
            out_node_attrs.append(item[1])

    # Sort everything that hasn't been sorted.
    combined = zip(all_anim_curve_nodes, all_node_attrs, all_attrs)
    filtered = []
    for item in combined:
        anim_curve_node, node_attr, attr_name = item

        already_sorted = False
        for attr_name_sort_begin in attr_sort_order:
            if attr_name.startswith(attr_name_sort_begin):
                already_sorted = True
                break

        if already_sorted:
            continue

        out_anim_curve_nodes.append(anim_curve_node)
        out_node_attrs.append(node_attr)

    return out_anim_curve_nodes, out_node_attrs


def query_anim_curve_data(anim_curve_node, frame_range):
    assert isinstance(anim_curve_node, pycompat.TEXT_TYPE)
    assert len(anim_curve_node) > 0
    assert maya.cmds.objExists(anim_curve_node)
    assert maya.cmds.nodeType(anim_curve_node).startswith("animCurve")
    assert isinstance(frame_range, time_utils.FrameRange)

    frame_start = frame_range.start
    frame_end = frame_range.end
    if frame_start == 0 and frame_end == 0:
        # start=0 and end=0 is special, we get the start/end time
        # values from the animCurve node.
        keyframe_count = maya.cmds.keyframe(
            anim_curve_node, query=True, keyframeCount=True
        )
        first_index = 0
        last_index = keyframe_count - 1
        frame_start = maya.cmds.keyframe(
            anim_curve_node, query=True, index=(first_index,)
        )
        frame_end = maya.cmds.keyframe(anim_curve_node, query=True, index=(last_index,))
        frame_start = int(frame_start[0])
        frame_end = int(frame_end[0])

    x_data = list(range(frame_start, frame_end + 1))

    # Query the curve data for the frame range.
    times = [(x,) for x in x_data]
    y_data = (
        maya.cmds.keyframe(anim_curve_node, time=times, query=True, eval=True) or []
    )

    if maya.cmds.nodeType(anim_curve_node) == "animCurveTA":
        scale_factor = math.radians(1)
        y_data = [y * scale_factor for y in y_data]

    assert len(x_data) > 0
    assert len(x_data) == len(y_data)
    return x_data, y_data


def _parse_individual_curve(results, curve_index_start, curve_length):
    assert isinstance(results, list)
    assert isinstance(curve_index_start, pycompat.INT_TYPES)
    assert isinstance(curve_length, pycompat.INT_TYPES)
    curve_x_data = [None] * curve_length
    curve_y_data = [None] * curve_length
    for i in range(curve_length):
        index_x = curve_index_start + 1 + (i * 2)
        index_y = index_x + 1
        curve_x_data[i] = results[index_x]
        curve_y_data[i] = results[index_y]
    assert len(curve_x_data) == len(curve_y_data)
    assert len(curve_x_data) == curve_length
    return curve_x_data, curve_y_data


def _parse_curve_results(results):
    assert len(results) > 0
    curves = []

    curve_index_start = 0
    while curve_index_start < (len(results) - 1):
        curve_length = int(results[curve_index_start])
        curve = _parse_individual_curve(results, curve_index_start, curve_length)
        curves.append(curve)

        # Setup up next curve, if it is valid.
        curve_index_start += 1 + (curve_length * 2)
        if curve_index_start < (len(results) - 1):
            break

    return curves


def simplify_curves(
    anim_curve_nodes,
    start_frame,
    end_frame,
    num_control_points,
    distribution,
    interpolation,
    return_results=False,
):
    """
    Simplify the anim curves.

    :param anim_curve_nodes: AnimCurve nodes to simplify.
    :param start_frame: Start frame to simplify.
    :param end_frame: End frame to simplify.
    :param num_control_points: .
    :param distribution: .
    :param interpolation: .
    """
    assert len(anim_curve_nodes) > 0
    assert isinstance(start_frame, pycompat.INT_TYPES)
    assert isinstance(end_frame, pycompat.INT_TYPES)
    assert isinstance(num_control_points, pycompat.INT_TYPES)
    assert distribution in const.DISTRIBUTION_VALUES
    assert interpolation in const.INTERPOLATION_VALUES
    assert num_control_points >= 2
    assert isinstance(return_results, bool)

    cmd_interpolation = None
    if num_control_points == 2:
        cmd_interpolation = const.CMD_INTERPOLATION_LINEAR_VALUE

        # It's only possible to use Linear with only 2 control points.
        new_interpolation = const.INTERPOLATION_LINEAR_VALUE
        if interpolation == const.INTERPOLATION_SMOOTH_VALUE:
            LOG.warn(
                "Not enough control points for %r interpolation, overriding to %r.",
                interpolation,
                new_interpolation,
            )

    elif num_control_points == 3 and interpolation == const.INTERPOLATION_SMOOTH_VALUE:
        # Cubic NUBS requires at least 4 points, so we must hard-code
        # to Quadratic NUBS, which only requires a minimum of 3
        # control points.
        cmd_interpolation = const.CMD_INTERPOLATION_QUADRATIC_NUBS_VALUE

    else:
        if interpolation == const.INTERPOLATION_LINEAR_VALUE:
            cmd_interpolation = const.CMD_INTERPOLATION_LINEAR_VALUE
        elif interpolation == const.INTERPOLATION_SMOOTH_VALUE:
            # Cubic NUBS is preferred because it seems to produce the
            # best results.
            cmd_interpolation = const.CMD_INTERPOLATION_CUBIC_NUBS_VALUE
        else:
            raise NotImplementedError

    kwargs = dict()
    # When start/end_frame is the same, it's assumed we're overriding
    # the frame range to use the animCurve's full frame range.
    use_anim_curve_frame_ranges = start_frame == end_frame
    if not use_anim_curve_frame_ranges:
        # Only give the start/end_frame when we actually want to
        # override that.
        kwargs["startFrame"] = start_frame
        kwargs["endFrame"] = end_frame

    results = maya.cmds.mmAnimCurveSimplify(
        anim_curve_nodes,
        controlPointCount=num_control_points,
        distribution=distribution,
        interpolation=cmd_interpolation,
        returnResultOnly=return_results,
        **kwargs,
    )
    if return_results and results:
        results = _parse_curve_results(results)

    return results


# Statistic type identifiers from the C++ code.
STAT_TYPE_MEAN_ABSOLUTE_DIFF = 0
STAT_TYPE_ROOT_MEAN_SQUARE_DIFF = 1
STAT_TYPE_POPULATION_STD_DEV = 2
STAT_TYPE_PEAK_TO_PEAK_DIFF = 3
STAT_TYPE_SIGNAL_TO_NOISE_RATIO = 4
STAT_TYPE_POPULATION_VARIANCE = 5
STAT_TYPE_MEAN_DIFF = 6
STAT_TYPE_MEDIAN_DIFF = 7
STAT_TYPE_MEAN_ABSOLUTE_ERROR = 8
STAT_TYPE_ROOT_MEAN_SQUARE_ERROR = 9
STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = 10
STAT_TYPE_R_SQUARED = 11


# Names for each statistic identifier defined in this module.
STAT_NAME_MEAN_ABSOLUTE_DIFF = "mean_absolute_diff"
STAT_NAME_MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
STAT_NAME_MEAN_DIFF = "mean_diff"
STAT_NAME_MEDIAN_DIFF = "median_diff"
STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = "normalized_rmse"
STAT_NAME_PEAK_TO_PEAK_DIFF = "peak_to_peak_diff"
STAT_NAME_POPULATION_STD_DEV = "population_std_dev"
STAT_NAME_POPULATION_VARIANCE = "population_variance"
STAT_NAME_ROOT_MEAN_SQUARE_DIFF = "root_mean_square_diff"
STAT_NAME_ROOT_MEAN_SQUARE_ERROR = "root_mean_square_error"
STAT_NAME_R_SQUARED = "r_squared"
STAT_NAME_SIGNAL_TO_NOISE_RATIO = "signal_to_noise_ratio"

STAT_NAME_LIST = [
    STAT_NAME_MEAN_ABSOLUTE_DIFF,
    STAT_NAME_MEAN_ABSOLUTE_ERROR,
    STAT_NAME_MEAN_DIFF,
    STAT_NAME_MEDIAN_DIFF,
    STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR,
    STAT_NAME_PEAK_TO_PEAK_DIFF,
    STAT_NAME_POPULATION_STD_DEV,
    STAT_NAME_POPULATION_VARIANCE,
    STAT_NAME_ROOT_MEAN_SQUARE_DIFF,
    STAT_NAME_ROOT_MEAN_SQUARE_ERROR,
    STAT_NAME_R_SQUARED,
    STAT_NAME_SIGNAL_TO_NOISE_RATIO,
]


def _parse_diff_statistics_result(result):
    """Parse the result array into a dictionary of statistics."""
    stats = {}
    stat_count = int(result[0])

    i = 1
    for j in range(stat_count):
        stat_type = int(result[i])
        stat_value = result[i + 1]

        if stat_type == STAT_TYPE_MEAN_ABSOLUTE_DIFF:
            stats[STAT_NAME_MEAN_ABSOLUTE_DIFF] = stat_value
        elif stat_type == STAT_TYPE_ROOT_MEAN_SQUARE_DIFF:
            stats[STAT_NAME_ROOT_MEAN_SQUARE_DIFF] = stat_value
        elif stat_type == STAT_TYPE_POPULATION_STD_DEV:
            stats[STAT_NAME_POPULATION_STD_DEV] = stat_value
        elif stat_type == STAT_TYPE_PEAK_TO_PEAK_DIFF:
            stats[STAT_NAME_PEAK_TO_PEAK_DIFF] = stat_value
        elif stat_type == STAT_TYPE_SIGNAL_TO_NOISE_RATIO:
            stats[STAT_NAME_SIGNAL_TO_NOISE_RATIO] = stat_value
        elif stat_type == STAT_TYPE_POPULATION_VARIANCE:
            stats[STAT_NAME_POPULATION_VARIANCE] = stat_value
        elif stat_type == STAT_TYPE_MEAN_DIFF:
            stats[STAT_NAME_MEAN_DIFF] = stat_value
        elif stat_type == STAT_TYPE_MEDIAN_DIFF:
            stats[STAT_NAME_MEDIAN_DIFF] = stat_value
        elif stat_type == STAT_TYPE_MEAN_ABSOLUTE_ERROR:
            stats[STAT_NAME_MEAN_ABSOLUTE_ERROR] = stat_value
        elif stat_type == STAT_TYPE_ROOT_MEAN_SQUARE_ERROR:
            stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR] = stat_value
        elif stat_type == STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR:
            stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR] = stat_value
        elif stat_type == STAT_TYPE_R_SQUARED:
            stats[STAT_NAME_R_SQUARED] = stat_value

        i += 2

    return stats


def calc_quality_of_fit(x_values, actual_values, predicted_values):
    result = maya.cmds.mmAnimCurveDiffStatistics(
        xValues=x_values,
        yValuesA=actual_values,
        yValuesB=predicted_values,
        normalizedRootMeanSquareError=True,
    )
    stats = _parse_diff_statistics_result(result)

    nrmse = stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR]
    quality = max(0.0, min(100.0, (1.0 - nrmse) * 100.0))

    return quality
