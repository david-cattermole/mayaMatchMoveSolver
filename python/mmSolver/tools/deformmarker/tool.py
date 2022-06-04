# Copyright (C) 2019 Anil Reddy.
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
This tool creates anim layer override to create offset for markers
"""

import operator

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.tools.deformmarker.lib as lib
import mmSolver.tools.deformmarker.constant as const

LOG = mmSolver.logger.get_logger()


def create_offset_layer():
    """
    Creates anim layer for the selected markers.

    :return: None
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = mmapi.filter_marker_nodes(selection)
    if len(selected_markers) == 0:
        LOG.warning('Please select a marker to create offset')
        return None

    marker_nodes = []
    for marker in selected_markers:
        marker = mmapi.Marker(node=marker)
        marker_node = marker.get_node()
        marker_nodes.append(marker_node)

    if not marker_nodes:
        LOG.warning('Please select a marker to create offset')
        return None

    attrs = lib.get_attrs_for_offset(marker_nodes)
    if attrs is None:
        LOG.warning('Please select marker to create override')
        return None

    anim_layer_name = const.ANIM_LAYER
    anim_layer = lib.find_animlayer(anim_layer_name)

    for attr in attrs:
        if lib.is_in_layer(attr, anim_layer):
            LOG.warning('Selected marker is already having a override')
            return None

    maya.cmds.animLayer(anim_layer, attribute=attrs, edit=True)
    return None


def bake_offset():
    """
    Bakes offset for the selected markers.

    :return: None
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = mmapi.filter_marker_nodes(selection)
    if len(selected_markers) == 0:
        LOG.warning('Please select a marker to bake offset')
        return None

    marker_nodes = []
    for marker in selected_markers:
        marker = mmapi.Marker(node=marker)
        marker_node = marker.get_node()
        marker_nodes.append(marker_node)
    if not marker_nodes:
        LOG.warning('Please select a marker to bake offset')
        return None

    attrs = lib.get_attrs_for_offset(marker_nodes)
    anim_layer = const.ANIM_LAYER
    for attr in attrs:
        if not lib.is_in_layer(attr, anim_layer):
            text = 'Selected marker is not having a layer override'
            LOG.warning(text)
            return None
    if not lib.is_key_framed(attrs):
        maya.cmds.setKeyframe(attrs)

    for attr in attrs:
        first_frame, last_frame = lib.__get_first_last_frame(attr, anim_layer)
        input_a, input_b = lib.get_attr_blend_plugs(attr, anim_layer)
        input_a_value = lib.__get_attr_value_array(input_a, first_frame, last_frame)
        input_b_value = lib.__get_attr_value_array(input_b, first_frame, last_frame)
        new_array = list(map(operator.add, input_a_value, input_b_value))

        maya.cmds.animLayer(anim_layer, removeAttribute=attr, edit=True)
        lib.set_attr_value_array(attr, new_array, first_frame, last_frame)

    if maya.cmds.animLayer(anim_layer, attribute=True, query=True) is None:
        maya.cmds.delete(anim_layer)

    maya.cmds.select(selected_markers)
    maya.cmds.dgdirty(selected_markers)
    return


def remove_layer_override():
    """
    Removed markers layer override.

    :return: None
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = mmapi.filter_marker_nodes(selection)
    if len(selected_markers) == 0:
        text = 'Please select a marker to remove anim layer override'
        LOG.warning(text)
        return None

    marker_nodes = []
    for marker in selected_markers:
        marker = mmapi.Marker(node=marker)
        marker_node = marker.get_node()
        marker_nodes.append(marker_node)

    if not marker_nodes:
        text = 'Please select a marker to remove anim layer override'
        LOG.warning(text)
        return

    attrs = lib.get_attrs_for_offset(marker_nodes)
    anim_layer = const.ANIM_LAYER
    for attr in attrs:
        maya.cmds.animLayer(anim_layer, removeAttribute=attr, edit=True)

    if maya.cmds.animLayer(anim_layer, attribute=True, query=True) is None:
        maya.cmds.delete(anim_layer)
    return
