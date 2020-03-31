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

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils

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
        "min_enable", "min_value",
        "max_enable", "max_value",
        "smoothness_enable", "smoothness_value",
        "stiffness_enable", "stiffness_value",
     )
)


def create_attr_detail(state=None,
                       min_enable=None,
                       min_value=None,
                       max_enable=None,
                       max_value=None,
                       smoothness_enable=None,
                       smoothness_value=None,
                       stiffness_enable=None,
                       stiffness_value=None):
    # TODO: Add logic for the intended default values.
    value = AttrDetail(
        state,
        min_enable,
        min_value,
        max_enable,
        max_value,
        smoothness_enable,
        smoothness_value,
        stiffness_enable,
        stiffness_value
    )
    return value


def get_active_collection():
    """
    Get the active collection object in the current scene file.

    :returns: The active Collection object, or None if no Collection
              is active.
    :rtype: Collection or None
    """
    uid = scene_data.get_scene_data(
        solver_const.SCENE_DATA_ACTIVE_COLLECTION_UID
    )
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
    cmd = (
        'global string $gChannelBoxName;'
        'string $temp = $gChannelBoxName;'
    )
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
    main_nodes = maya.cmds.channelBox(
        name, query=True,
        mainObjectList=True
    ) or []
    main_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedMainAttributes=True
    ) or []

    # Shape Nodes and Attribute
    shape_nodes = maya.cmds.channelBox(
        name, query=True,
        shapeObjectList=True
    ) or []
    shape_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedShapeAttributes=True
    ) or []

    # History Nodes and Attribute
    history_nodes = maya.cmds.channelBox(
        name, query=True,
        historyObjectList=True
    ) or []
    history_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedHistoryAttributes=True
    ) or []

    # Output Nodes and Attribute
    output_nodes = maya.cmds.channelBox(
        name, query=True,
        outputObjectList=True
    ) or []
    output_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedOutputAttributes=True
    ) or []

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


def convert_attributes_to_detail_values(col, attr_list):
    assert isinstance(col, mmapi.Collection)
    assert isinstance(attr_list, (list, tuple))

    # Default values.
    # TODO: Put these in the constant.py file.
    state = mmapi.ATTR_STATE_INVALID
    min_enable = const.MIN_ENABLE_DEFAULT_VALUE
    min_value = const.MIN_VALUE_DEFAULT_VALUE
    max_enable = const.MAX_ENABLE_DEFAULT_VALUE
    max_value = const.MAX_VALUE_DEFAULT_VALUE
    stiffness_enable = const.STIFFNESS_ENABLE_DEFAULT_VALUE
    stiffness_value = const.STIFFNESS_VALUE_DEFAULT_VALUE
    smoothness_enable = const.SMOOTHNESS_ENABLE_DEFAULT_VALUE
    smoothness_value = const.SMOOTHNESS_VALUE_DEFAULT_VALUE

    for attr in attr_list:
        assert isinstance(attr, mmapi.Attribute)
        attr_state = attr.get_state()
        state = max(state, attr_state)

        if min_enable is False and col.get_attribute_min_enable(attr) is True:
            min_enable = True
        # TODO: Ensure the first '0.0' value is not counted in the
        #  'min' function below.
        min_value = min(min_value, col.get_attribute_min_value(attr))

        if max_enable is False and col.get_attribute_max_enable(attr) is True:
            max_enable = True
        max_value = max(max_value, col.get_attribute_max_value(attr))

        if stiffness_enable is False and col.get_attribute_stiffness_enable(attr) is True:
            stiffness_enable = True
        # TODO: Create an average value as a default.
        stiffness_value = max(stiffness_value, col.get_attribute_stiffness_weight(attr))

        if smoothness_enable is False and col.get_attribute_smoothness_enable(attr) is True:
            smoothness_enable = True
        # TODO: Create an average value as a default.
        smoothness_value = max(smoothness_value, col.get_attribute_smoothness_weight(attr))

    value = create_attr_detail(
        state=state,
        min_enable=min_enable,
        min_value=min_value,
        max_enable=max_enable,
        max_value=max_value,
        stiffness_enable=stiffness_enable,
        stiffness_value=stiffness_value,
        smoothness_enable=smoothness_enable,
        smoothness_value=smoothness_value,
    )
    return value


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
        src = maya.cmds.connectionInfo(
            plug_name,
            sourceFromDestination=True) or None
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
    col.set_attribute_stiffness_weight(attr, values.stiffness_value)
    col.set_attribute_smoothness_enable(attr, values.smoothness_enable)
    col.set_attribute_smoothness_weight(attr, values.smoothness_value)
