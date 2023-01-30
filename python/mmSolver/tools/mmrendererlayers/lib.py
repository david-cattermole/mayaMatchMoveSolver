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


def add_attrs_to_layer(node):
    assert maya.cmds.objExists(node)
    LOG.info('MM Renderer: Add Attributes to Display Layer: %r', node)
    existing_attrs = maya.cmds.listAttr(node) or []

    attr_name = const.LAYER_ATTR_LAYER_MODE
    nice_name = const.LAYER_NICE_LAYER_MODE
    enum_dict = const.LAYER_MODE_ENUM_VALUES
    default = const.LAYER_MODE_DEFAULT_VALUE
    if attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_LAYER_MIX
    nice_name = const.LAYER_NICE_LAYER_MIX
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_LAYER_DRAW_DEBUG
    nice_name = const.LAYER_NICE_LAYER_DRAW_DEBUG
    if attr_name not in existing_attrs:
        _add_attr_bool(node, attr_name, nice_name, default=0)

    attr_name = const.LAYER_ATTR_OBJECT_DISPLAY_STYLE
    nice_name = const.LAYER_NICE_OBJECT_DISPLAY_STYLE
    enum_dict = const.OBJECT_DISPLAY_STYLE_ENUM_VALUES
    default = const.OBJECT_DISPLAY_STYLE_DEFAULT_VALUE
    if attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_OBJECT_ALPHA
    nice_name = const.LAYER_NICE_OBJECT_ALPHA
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_ENABLE
    nice_name = const.LAYER_NICE_EDGE_ENABLE
    if attr_name not in existing_attrs:
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
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_DETECT_MODE
    nice_name = const.LAYER_NICE_EDGE_DETECT_MODE
    enum_dict = const.EDGE_DETECT_MODE_ENUM_VALUES
    default = const.EDGE_DETECT_MODE_DEFAULT_VALUE
    if attr_name not in existing_attrs:
        _add_attr_enum(node, attr_name, nice_name, enum_dict, default=default)

    attr_name = const.LAYER_ATTR_EDGE_THICKNESS
    nice_name = const.LAYER_NICE_EDGE_THICKNESS
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_COLOR
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_COLOR
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_ALPHA
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_ALPHA
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    attr_name = const.LAYER_ATTR_EDGE_THRESHOLD_DEPTH
    nice_name = const.LAYER_NICE_EDGE_THRESHOLD_DEPTH
    if attr_name not in existing_attrs:
        _add_attr_float(node, attr_name, nice_name, default=1.0)

    _set_attrs_keyable(node, const.LAYER_ATTR_LIST_ALL)
    return


def add_attrs_to_layers(nodes):
    for node in nodes:
        add_attrs_to_layer(node)
    return