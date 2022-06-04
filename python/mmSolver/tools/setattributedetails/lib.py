# Copyright (C) 2020 David Cattermole.
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
Library functions for Solver UI.
"""

import collections
import math

import maya.cmds
import maya.mel
import maya.OpenMaya as OpenMaya1
import maya.OpenMayaAnim as OpenMayaAnim1

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as animcurve_utils

# TODO: Remove the connection between the 'setattributedetails' tool
#  to the 'solver' tool.
import mmSolver.tools.solver.constant as solver_const
import mmSolver.tools.solver.lib.scene_data as scene_data

import mmSolver.tools.setattributedetails.constant as const

LOG = mmSolver.logger.get_logger()


AttrDetail = collections.namedtuple(
    "AttrDetail",
    (
        "state",
        "min_enable",
        "min_value",
        "max_enable",
        "max_value",
        "smoothness_enable",
        "smoothness_variance",
        "smoothness_weight",
        "stiffness_enable",
        "stiffness_variance",
        "stiffness_weight",
        "curve_min",
        "curve_max",
        "curve_mean",
        "curve_variance",
        "curve_frame_variance",
        "curve_max_variance",
    ),
)


def create_attr_detail(
    state=None,
    min_enable=None,
    min_value=None,
    max_enable=None,
    max_value=None,
    smoothness_enable=None,
    smoothness_variance=None,
    smoothness_weight=None,
    stiffness_enable=None,
    stiffness_variance=None,
    stiffness_weight=None,
    curve_min=None,
    curve_max=None,
    curve_mean=None,
    curve_variance=None,
    curve_frame_variance=None,
    curve_max_variance=None,
):
    value = AttrDetail(
        state=state,
        min_enable=min_enable,
        min_value=min_value,
        max_enable=max_enable,
        max_value=max_value,
        smoothness_enable=smoothness_enable,
        smoothness_variance=smoothness_variance,
        smoothness_weight=smoothness_weight,
        stiffness_enable=stiffness_enable,
        stiffness_variance=stiffness_variance,
        stiffness_weight=stiffness_weight,
        curve_min=curve_min,
        curve_max=curve_max,
        curve_mean=curve_mean,
        curve_variance=curve_variance,
        curve_frame_variance=curve_frame_variance,
        curve_max_variance=curve_max_variance,
    )
    return value


def attr_detail_from_previous(
    value,
    state=None,
    min_enable=None,
    min_value=None,
    max_enable=None,
    max_value=None,
    smoothness_enable=None,
    smoothness_variance=None,
    smoothness_weight=None,
    stiffness_enable=None,
    stiffness_variance=None,
    stiffness_weight=None,
    curve_min=None,
    curve_max=None,
    curve_mean=None,
    curve_variance=None,
    curve_frame_variance=None,
    curve_max_variance=None,
):
    assert isinstance(value, AttrDetail)

    if state is None:
        state = value.state
    if min_enable is None:
        min_enable = value.min_enable
    if min_value is None:
        min_value = value.min_value
    if max_enable is None:
        max_enable = value.max_enable
    if max_value is None:
        max_value = value.max_value

    if stiffness_enable is None:
        stiffness_enable = value.stiffness_enable
    if stiffness_weight is None:
        stiffness_weight = value.stiffness_weight
    if stiffness_variance is None:
        stiffness_variance = value.stiffness_variance

    if smoothness_enable is None:
        smoothness_enable = value.smoothness_enable
    if smoothness_weight is None:
        smoothness_weight = value.smoothness_weight
    if smoothness_variance is None:
        smoothness_variance = value.smoothness_variance

    if curve_min is None:
        curve_min = value.curve_min
    if curve_max is None:
        curve_max = value.curve_max
    if curve_mean is None:
        curve_mean = value.curve_mean
    if curve_variance is None:
        curve_variance = value.curve_variance
    if curve_frame_variance is None:
        curve_frame_variance = value.curve_frame_variance
    if curve_max_variance is None:
        curve_max_variance = value.curve_max_variance

    new_value = create_attr_detail(
        state=state,
        min_enable=min_enable,
        min_value=min_value,
        max_enable=max_enable,
        max_value=max_value,
        smoothness_enable=smoothness_enable,
        smoothness_variance=smoothness_variance,
        smoothness_weight=smoothness_weight,
        stiffness_enable=stiffness_enable,
        stiffness_variance=stiffness_variance,
        stiffness_weight=stiffness_weight,
        curve_min=curve_min,
        curve_max=curve_max,
        curve_mean=curve_mean,
        curve_variance=curve_variance,
        curve_frame_variance=curve_frame_variance,
        curve_max_variance=curve_max_variance,
    )
    return new_value


CurveStatistics = collections.namedtuple(
    "CurveStatistics",
    (
        "min_value",
        "max_value",
        "mean_value",
        "variance",
        "frame_variance",
        "max_variance",
    ),
)


def create_curve_statistics(
    min_value=None,
    max_value=None,
    mean_value=None,
    variance=None,
    frame_variance=None,
    max_variance=None,
):
    value = CurveStatistics(
        min_value=min_value,
        max_value=max_value,
        mean_value=mean_value,
        variance=variance,
        frame_variance=frame_variance,
        max_variance=max_variance,
    )
    return value


def get_active_collection():
    """
    Get the active collection object in the current scene file.

    :returns: The active Collection object, or None if no Collection
              is active.
    :rtype: Collection or None
    """
    uid = scene_data.get_scene_data(solver_const.SCENE_DATA_ACTIVE_COLLECTION_UID)
    if uid is None:
        return None
    nodes = maya.cmds.ls(uid, long=True) or []
    col = None
    if len(nodes) > 0:
        col = mmapi.Collection(node=nodes[0])
    return col


def _get_channel_box_ui_name():
    """
    Get the internal channel box Maya UI path.

    .. note::
        When the Maya GUI has not launched yet, this function
        returns None.

    :return: UI path str.
    :rtype: str or None
    """
    cmd = 'global string $gChannelBoxName;' 'string $temp = $gChannelBoxName;'
    return maya.mel.eval(cmd)


def get_selected_maya_attributes():
    """
    Get the currently selected attributes from the Channel Box.

    This function uses Maya ChannelBox logic to get the objects, which
    is based on the selection, but may be doing more complex logic.

    :return: List of Attribute objects for all nodes in the Channel Box.
    :rtype: list of Attribute
    """
    name = _get_channel_box_ui_name()

    # Main Nodes and Attribute
    main_nodes = maya.cmds.channelBox(name, query=True, mainObjectList=True) or []
    main_attrs = (
        maya.cmds.channelBox(name, query=True, selectedMainAttributes=True) or []
    )

    # Shape Nodes and Attribute
    shape_nodes = maya.cmds.channelBox(name, query=True, shapeObjectList=True) or []
    shape_attrs = (
        maya.cmds.channelBox(name, query=True, selectedShapeAttributes=True) or []
    )

    # History Nodes and Attribute
    history_nodes = maya.cmds.channelBox(name, query=True, historyObjectList=True) or []
    history_attrs = (
        maya.cmds.channelBox(name, query=True, selectedHistoryAttributes=True) or []
    )

    # Output Nodes and Attribute
    output_nodes = maya.cmds.channelBox(name, query=True, outputObjectList=True) or []
    output_attrs = (
        maya.cmds.channelBox(name, query=True, selectedOutputAttributes=True) or []
    )

    attr_list = []
    nodes_and_attrs = [
        (main_nodes, main_attrs),
        (shape_nodes, shape_attrs),
        (history_nodes, history_attrs),
        (output_nodes, output_attrs),
    ]
    for nodes, attrs in nodes_and_attrs:
        for n in nodes:
            for a in attrs:
                possible_attrs = maya.cmds.listAttr(n, shortNames=False) or []
                possible_attrs += maya.cmds.listAttr(n, shortNames=True) or []
                if a not in possible_attrs:
                    continue
                attr = mmapi.Attribute(node=n, attr=a)
                if attr.get_name() is not None:
                    attr_list.append(attr)
    return attr_list


def get_selected_node_default_attributes():
    """
    Get the attributes on the selected nodes.

    :returns: List of mmSolver API Attribute objects.
    :rtype: [Attribute, ..]
    """
    attr_list = []
    sel = maya.cmds.ls(selection=True, long=True) or []
    if len(sel) == 0:
        return attr_list

    for node in sel:
        node_type = maya.cmds.nodeType(node)
        obj_type = mmapi.get_object_type(node)
        attr_names = []
        if obj_type == mmapi.OBJECT_TYPE_BUNDLE:
            # Default bundle attributes.
            attr_names += [
                'translateX',
                'translateY',
                'translateZ',
            ]
        elif obj_type == mmapi.OBJECT_TYPE_CAMERA:
            # Camera default attributes, for both transform and
            # camera nodes.
            if node_type == 'transform':
                attr_names += [
                    'translateX',
                    'translateY',
                    'translateZ',
                    'rotateX',
                    'rotateY',
                    'rotateZ',
                ]
            elif node_type == 'camera':
                attr_names += [
                    'focalLength',
                ]
        else:
            # Fallback - get all logical attributes.
            attrs = (
                maya.cmds.listAttr(
                    node,
                    keyable=True,
                    settable=True,
                    scalar=True,
                    shortNames=False,
                )
                or []
            )
            attr_types = [
                'doubleLinear',
                'doubleAngle',
                'double',
                'float',
            ]
            attr_names += [
                n
                for n in attrs
                if maya.cmds.attributeQuery(n, node=node, attributeType=True)
                in attr_types
            ]

        for attr_name in attr_names:
            attr_obj = mmapi.Attribute(node=node, attr=attr_name)
            attr_list.append(attr_obj)
    return attr_list


def input_attributes_filter(attr_list):
    """
    Apply logic to remove any non-input attributes from the given list.

    :param attr_list: Attribute list to filter.
    :type attr_list: [Attribute, ..]

    :returns: List of attributes that are filtered.
    :rtype: [Attribute, ..]
    """
    result = []
    for attr_obj in attr_list:
        node = attr_obj.get_node()
        obj_type = mmapi.get_object_type(node)
        if obj_type in solver_const.ATTR_INVALID_OBJECT_TYPES:
            continue
        result.append(attr_obj)
    return result


def get_curve_statistics(attr):
    curve = create_curve_statistics()

    plug_name = attr.get_name()
    anim_curves = animcurve_utils.get_anim_curves_from_nodes([plug_name])
    if len(anim_curves) == 0:
        return curve
    anim_curve_name = anim_curves[0]

    obj = node_utils.get_as_object_apione(anim_curve_name)
    animfn = OpenMayaAnim1.MFnAnimCurve(obj)
    animCurveType = animfn.animCurveType()

    ui_unit = OpenMaya1.MTime.uiUnit()
    num_keys = animfn.numKeys()
    start_time = animfn.time(0)
    end_time = animfn.time(num_keys - 1)
    start_frame = int(start_time.asUnits(ui_unit))
    end_frame = int(end_time.asUnits(ui_unit))
    frame_nums = end_frame - start_frame

    values = []
    curve_min_value = 999999999.0
    curve_max_value = -999999999.0
    curve_mean_value = 0.0
    for i, frame in enumerate(range(start_frame, end_frame + 1)):
        t = OpenMaya1.MTime(float(frame), ui_unit)
        value = animfn.evaluate(t)
        if animCurveType == OpenMayaAnim1.MFnAnimCurve.kAnimCurveTA:
            value = math.degrees(value)
        values.append(value)
        curve_min_value = min(curve_min_value, value)
        curve_max_value = max(curve_max_value, value)
        curve_mean_value += value
    curve_mean_value /= len(values)

    curve_variance = 0.0
    for value in values:
        diff = value - curve_mean_value
        diff = diff * diff
        curve_variance += diff
    curve_variance /= len(values)
    curve_variance = math.sqrt(curve_variance)

    curve_max_variance = 0.0
    curve_frame_variance = 0.0
    for i, value in enumerate(values):
        idx_prev = max(0, i - 1)
        idx_next = min(i + 1, len(values) - 1)
        value_prev = values[idx_prev]
        value_next = values[idx_next]
        diff = abs(value - value_prev)
        curve_max_variance = max(curve_max_variance, diff)
        diff = diff * diff
        curve_frame_variance += diff
        diff = abs(value - value_next)
        curve_max_variance = max(curve_max_variance, diff)
        diff = diff * diff
        curve_frame_variance += diff
    curve_frame_variance /= len(values) * 2
    curve_frame_variance = math.sqrt(curve_frame_variance)

    curve = create_curve_statistics(
        min_value=curve_min_value,
        max_value=curve_max_value,
        mean_value=curve_mean_value,
        variance=curve_variance,
        frame_variance=curve_frame_variance,
        max_variance=curve_max_variance,
    )
    return curve


def convert_attributes_to_detail_values(col, attr_list):
    assert isinstance(col, mmapi.Collection)
    assert isinstance(attr_list, (list, tuple))

    values_dict = {}
    for attr in attr_list:
        assert isinstance(attr, mmapi.Attribute)
        attr_state = attr.get_state()
        attr_animated = int(attr_state == mmapi.ATTR_STATE_ANIMATED)

        attr_min_enable = col.get_attribute_min_enable(attr)
        attr_min_value = col.get_attribute_min_value(attr)

        attr_max_enable = col.get_attribute_max_enable(attr)
        attr_max_value = col.get_attribute_max_value(attr)

        attr_stiffness_enable = col.get_attribute_stiffness_enable(attr)
        attr_stiffness_weight = col.get_attribute_stiffness_weight(attr)
        attr_stiffness_variance = col.get_attribute_stiffness_variance(attr)

        attr_smoothness_enable = col.get_attribute_smoothness_enable(attr)
        attr_smoothness_weight = col.get_attribute_smoothness_weight(attr)
        attr_smoothness_variance = col.get_attribute_smoothness_variance(attr)

        attr_curve = create_curve_statistics()
        if attr_animated:
            attr_curve = get_curve_statistics(attr)

        attr_detail = create_attr_detail(
            state=attr_state,
            min_enable=attr_min_enable,
            min_value=attr_min_value,
            max_enable=attr_max_enable,
            max_value=attr_max_value,
            stiffness_enable=attr_stiffness_enable,
            stiffness_variance=attr_stiffness_variance,
            stiffness_weight=attr_stiffness_weight,
            smoothness_enable=attr_smoothness_enable,
            smoothness_variance=attr_smoothness_variance,
            smoothness_weight=attr_smoothness_weight,
            curve_min=attr_curve.min_value,
            curve_max=attr_curve.max_value,
            curve_mean=attr_curve.mean_value,
            curve_variance=attr_curve.variance,
            curve_frame_variance=attr_curve.frame_variance,
            curve_max_variance=attr_curve.max_variance,
        )
        attr_name = attr.get_name()
        values_dict[attr_name] = attr_detail

    return values_dict


def set_attribute_state(attr, state):
    node = attr.get_node()
    plug_name = attr.get_name()
    if node is None or plug_name is None:
        LOG.warn("Attribute is invalid: %r", attr)
        return
    if state == mmapi.ATTR_STATE_LOCKED:
        if not node_utils.node_is_referenced(node):
            maya.cmds.setAttr(plug_name, lock=True)

    elif state == mmapi.ATTR_STATE_STATIC:
        if not node_utils.node_is_referenced(node):
            maya.cmds.setAttr(plug_name, lock=False)
        # Break the connection going in to the attribute.
        src = maya.cmds.connectionInfo(plug_name, sourceFromDestination=True) or None
        if src is None:
            return
        dst = plug_name
        connected = maya.cmds.isConnected(src, dst)
        if connected:
            maya.cmds.disconnectAttr(src, dst)

    elif state == mmapi.ATTR_STATE_ANIMATED:
        if not node_utils.node_is_referenced(node):
            maya.cmds.setAttr(plug_name, lock=False)
        locked = maya.cmds.getAttr(plug_name, lock=True)
        if locked is False:
            maya.cmds.setKeyframe(plug_name)

    else:
        LOG.warn("Cannot set invalid attribute state: %r", attr)
    return


def set_attribute_details(col, attr, values):
    assert isinstance(col, mmapi.Collection)
    assert isinstance(attr, mmapi.Attribute)
    assert isinstance(values, AttrDetail)
    set_attribute_state(attr, values.state)
    col.set_attribute_min_enable(attr, values.min_enable)
    col.set_attribute_min_value(attr, values.min_value)
    col.set_attribute_max_enable(attr, values.max_enable)
    col.set_attribute_max_value(attr, values.max_value)
    col.set_attribute_stiffness_enable(attr, values.stiffness_enable)
    col.set_attribute_stiffness_variance(attr, values.stiffness_variance)
    col.set_attribute_stiffness_weight(attr, values.stiffness_weight)
    col.set_attribute_smoothness_enable(attr, values.smoothness_enable)
    col.set_attribute_smoothness_variance(attr, values.smoothness_variance)
    col.set_attribute_smoothness_weight(attr, values.smoothness_weight)
