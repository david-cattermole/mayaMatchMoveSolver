# Copyright (C) 2023 David Cattermole.
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
Functions to add attributes to displayLayer nodes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.tools.mmrendererlayers.constant as const

LOG = mmSolver.logger.get_logger()


def _generate_enum_name_string(enum_dict):
    assert isinstance(enum_dict, dict)
    values = enum_dict.values()
    result_list = []
    # A naive implementation, but it will work for small item counts.
    for value1 in sorted(values):
        for key, value2 in enum_dict.items():
            if value1 == value2:
                result_list.append('{}={}'.format(key, value1))
    return ':'.join(result_list)


def _add_attr_enum(node, attr_name, nice_name, enum_dict, default=None):
    enum_name = _generate_enum_name_string(enum_dict)
    default_value = enum_dict[default]
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        niceName=nice_name,
        attributeType='enum',
        defaultValue=default_value,
        enumName=enum_name,
    )


def _add_attr_bool(node, attr_name, nice_name, default=None):
    assert default is None or isinstance(default, (int, bool))
    if isinstance(default, (int, bool)):
        default = int(default)
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        niceName=nice_name,
        attributeType='bool',
        defaultValue=default,
    )


def _add_attr_float(node, attr_name, nice_name, default=None):
    assert default is None or isinstance(default, float)
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        niceName=nice_name,
        attributeType='float',
        defaultValue=default,
    )


def _add_attr_color(
    node,
    attr_name,
    nice_name,
    attr_children_names,
    nice_children_names,
    existing_attrs,
    default=None,
):
    if default is None:
        default = (1.0, 1.0, 1.0)
    assert len(attr_children_names) == 3
    assert len(nice_children_names) == 3
    assert len(default) == 3
    assert len(existing_attrs) >= 0
    attr_name_r, attr_name_g, attr_name_b = attr_children_names
    nice_name_r, nice_name_g, nice_name_b = nice_children_names
    value_r, value_g, value_b = default

    if attr_name not in existing_attrs:
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            niceName=nice_name,
            attributeType='float3',
            usedAsColor=True,
        )

    if attr_name_r not in existing_attrs:
        maya.cmds.addAttr(
            node,
            longName=attr_name_r,
            niceName=nice_name_r,
            attributeType='float',
            defaultValue=value_r,
            parent=attr_name,
        )
    if attr_name_g not in existing_attrs:
        maya.cmds.addAttr(
            node,
            longName=attr_name_g,
            niceName=nice_name_g,
            attributeType='float',
            defaultValue=value_g,
            parent=attr_name,
        )
    if attr_name_b not in existing_attrs:
        maya.cmds.addAttr(
            node,
            longName=attr_name_b,
            niceName=nice_name_b,
            attributeType='float',
            defaultValue=value_b,
            parent=attr_name,
        )
    return


def _set_attrs_keyable(node, attr_names):
    """
    Make all attributes 'keyable' so they show up in the channel box.
    """
    assert maya.cmds.objExists(node)
    assert len(attr_names) >= 0
    existing_attrs = maya.cmds.listAttr(node) or []
    for attr_name in attr_names:
        if attr_name not in existing_attrs:
            continue
        plug = '{}.{}'.format(node, attr_name)
        maya.cmds.setAttr(plug, edit=True, keyable=True)
    return


def add_attrs_to_layer(node, attr_names=None):
    if attr_names is None:
        attr_names = const.LAYER_ATTR_LIST_ALL
    assert maya.cmds.objExists(node)
    assert isinstance(attr_names, (list, tuple, set))
    LOG.info(
        'MM Renderer: Add %r Attributes to Display Layer: %r', len(attr_names), node
    )
    existing_attrs = maya.cmds.listAttr(node) or []

    attr_name = const.LAYER_ATTR_LAYER_MODE
    nice_name = const.LAYER_NICE_LAYER_MODE
    enum_dict = const.LAYER_MODE_ENUM_VALUES
    default = const.LAYER_MODE_DEFAULT_VALUE
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_LAYER_MIX
    nice_name = const.LAYER_NICE_LAYER_MIX
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_LAYER_DRAW_DEBUG
    nice_name = const.LAYER_NICE_LAYER_DRAW_DEBUG
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_bool(node, attr_name, nice_name, default=0)

    attr_name = const.LAYER_ATTR_OBJECT_DISPLAY_STYLE
    nice_name = const.LAYER_NICE_OBJECT_DISPLAY_STYLE
    enum_dict = const.OBJECT_DISPLAY_STYLE_ENUM_VALUES
    default = const.OBJECT_DISPLAY_STYLE_DEFAULT_VALUE
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_OBJECT_ALPHA
    nice_name = const.LAYER_NICE_OBJECT_ALPHA
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_ENABLE
    nice_name = const.LAYER_NICE_EDGE_ENABLE
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_bool(node, attr_name, nice_name, default=0)

    attr_name = const.LAYER_ATTR_EDGE_COLOR
    nice_name = const.LAYER_NICE_EDGE_COLOR
    attr_children_names = [
        const.LAYER_ATTR_EDGE_COLOR_R,
        const.LAYER_ATTR_EDGE_COLOR_G,
        const.LAYER_ATTR_EDGE_COLOR_B,
    ]
    nice_children_names = [
        const.LAYER_NICE_EDGE_COLOR_R,
        const.LAYER_NICE_EDGE_COLOR_G,
        const.LAYER_NICE_EDGE_COLOR_B,
    ]
    if attr_name in attr_names:
        _add_attr_color(
            node,
            attr_name,
            nice_name,
            attr_children_names,
            nice_children_names,
            existing_attrs,
            default=(1.0, 0.0, 0.0),
        )

    attr_name = const.LAYER_ATTR_EDGE_ALPHA
    nice_name = const.LAYER_NICE_EDGE_ALPHA
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_DETECT_MODE
    nice_name = const.LAYER_NICE_EDGE_DETECT_MODE
    enum_dict = const.EDGE_DETECT_MODE_ENUM_VALUES
    default = const.EDGE_DETECT_MODE_DEFAULT_VALUE
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_EDGE_THICKNESS
    nice_name = const.LAYER_NICE_EDGE_THICKNESS
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_COLOR
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_COLOR
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_ALPHA
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_ALPHA
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_DEPTH
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_DEPTH
    if attr_name in attr_names and attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    _set_attrs_keyable(node, attr_names)
    return


def connect_layer_attributes(src_node=None, dst_node=None):
    assert src_node is not None
    assert dst_node is not None
    for attr_name in const.LAYER_ATTR_LIST_ALL:
        src_attr_exists = node_utils.attribute_exists(attr_name, src_node)
        dst_attr_exists = node_utils.attribute_exists(attr_name, dst_node)

        msg = 'Skipping connection of %r; Attribute %r does not exist on node %r.'
        if src_attr_exists is False:
            LOG.warn(msg, attr_name, attr_name, src_node)
            continue
        if dst_attr_exists is False:
            LOG.warn(msg, attr_name, attr_name, dst_node)
            continue

        src_plug = '{}.{}'.format(src_node, attr_name)
        dst_plug = '{}.{}'.format(dst_node, attr_name)
        if maya.cmds.isConnected(src_plug, dst_plug) is False:
            maya.cmds.connectAttr(src_plug, dst_plug)
    return


def create_set_node(layer_node, hidden=None):
    if hidden is None:
        hidden = False

    src_plug = '{}.message'.format(layer_node)

    connected_nodes = (
        maya.cmds.listConnections(
            src_plug, destination=True, source=False, type='objectSet'
        )
        or []
    )
    if len(connected_nodes) > 0:
        dst_plug = '{}.displayLayer'.format(connected_nodes[0])
        if maya.cmds.isConnected(src_plug, dst_plug) is True:
            set_node = connected_nodes[0]
    else:
        set_name = 'mmRenderer_objectSet_{}'.format(layer_node)
        if maya.cmds.objExists(set_name) is False:
            set_node = maya.cmds.sets(name=set_name, empty=True)
        else:
            set_node = set_name

    maya.cmds.setAttr('{}.hiddenInOutliner'.format(set_node), hidden)

    attr_name = 'displayLayer'
    if node_utils.attribute_exists(attr_name, set_node) is False:
        maya.cmds.addAttr(set_node, longName=attr_name, attributeType='message')

    dst_plug = '{}.displayLayer'.format(set_node)
    if maya.cmds.isConnected(src_plug, dst_plug) is False:
        maya.cmds.connectAttr(src_plug, dst_plug)

    add_attrs_to_layer(set_node, attr_names=const.LAYER_ATTR_LIST_ALL)
    return set_node


def update_set_nodes(set_node, layer_node):
    layer_member_nodes = maya.cmds.editDisplayLayerMembers(layer_node, query=True) or []
    maya.cmds.sets(clear=set_node)
    if len(layer_member_nodes) > 0:
        layer_member_nodes = [x for x in layer_member_nodes
                              if maya.cmds.nodeType(x) not in const.EXCLUDE_DRAW_NODE_TYPES]
        maya.cmds.sets(layer_member_nodes, addElement=set_node)
    return


def add_attrs_to_layers(nodes):
    for layer_node in nodes:
        add_attrs_to_layer(layer_node, attr_names=const.LAYER_ATTR_LIST_MINIMAL)
        set_node = create_set_node(layer_node)
        connect_layer_attributes(src_node=layer_node, dst_node=set_node)
        update_set_nodes(set_node, layer_node)
    return
