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
Attribute functions
"""

import time

import maya.cmds
import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.setattributedetails.tool as set_details_tool

LOG = mmSolver.logger.get_logger()


def _get_plug_names_as_set(attr_list):
    plug_names = set()
    for attr_obj in attr_list:
        node_path = attr_obj.get_node(full_path=True)
        if node_utils.node_is_referenced(node_path):
            continue
        plug_name = attr_obj.get_name(full_path=True)
        plug_names.add(plug_name)
    return plug_names


def _apply_function_to_attrs(attr_list, apply_func):
    plug_names = _get_plug_names_as_set(attr_list)
    for plug_name in sorted(plug_names):
        apply_func(plug_name)
    return


def get_attributes_from_collection(col):
    s = time.time()
    result = col.get_attribute_list()
    e = time.time()
    LOG.debug('get_attributes_from_collection: %r seconds', e - s)
    return result


def add_attributes_to_collection(attr_list, col):
    s = time.time()
    result = col.add_attribute_list(attr_list)
    e = time.time()
    LOG.debug('get_attributes_from_collection: %r seconds', e - s)
    return result


def remove_attr_from_collection(attr_list, col):
    s = time.time()
    result = col.remove_attribute_list(attr_list)
    e = time.time()
    LOG.debug('get_attributes_from_collection: %r seconds', e - s)
    return result


def set_details_selected_attributes(attr_list, col):
    LOG.debug('set_details_selected_attributes: %r', attr_list)
    set_details_tool.open_window(col=col, attr_list=attr_list)
    return


def lock_selected_attributes(attr_list):
    LOG.debug('lock_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setAttr(plug_name, lock=True)

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def unlock_selected_attributes(attr_list):
    LOG.debug('unlock_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setAttr(plug_name, lock=False)

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def set_keyframe_on_selected_attributes(attr_list):
    LOG.debug('set_keyframe_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setKeyframe(plug_name)

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def delete_keyframe_current_frame_on_selected_attributes(attr_list):
    LOG.debug('delete_keyframe_current_frame_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        current_frame = maya.cmds.currentTime(query=True)
        node_name, sep, attr_name = plug_name.partition('.')
        time_range = (current_frame,)
        maya.cmds.cutKey(node_name, attribute=attr_name, time=time_range)

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def delete_keyframe_all_frames_on_selected_attributes(attr_list):
    LOG.debug('delete_keyframe_all_frames_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        frame_range = time_utils.get_maya_timeline_range_outer()
        time_range = (frame_range.start, frame_range.end)
        maya.cmds.cutKey(node_name, attribute=attr_name, time=time_range)

    with tools_utils.tool_context(
        pre_update_frame=True,
        restore_current_frame=True,
        use_undo_chunk=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def delete_static_channel_on_selected_attributes(attr_list):
    LOG.debug('delete_static_channel_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        maya.cmds.delete(node_name, attribute=attr_name, staticChannels=True)

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def break_connections_on_selected_attributes(attr_list):
    LOG.debug('break_connections_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        src = maya.cmds.connectionInfo(plug_name, sourceFromDestination=True) or None
        if src is None:
            return
        dst = plug_name
        connected = maya.cmds.isConnected(src, dst)
        if connected:
            maya.cmds.disconnectAttr(src, dst)
        return

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def bake_selected_attributes(attr_list):
    LOG.debug('bake_selected_attributes: %r', attr_list)
    frame_range = time_utils.get_maya_timeline_range_outer()
    plug_names = _get_plug_names_as_set(attr_list)
    plug_names = list(sorted(plug_names))
    with tools_utils.tool_context(
        pre_update_frame=True,
        restore_current_frame=True,
        use_undo_chunk=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
    ):
        maya.cmds.bakeResults(plug_names, time=(frame_range.start, frame_range.end))
    return


def reset_values_on_selected_attributes(attr_list):
    LOG.debug('reset_values_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        values = (
            maya.cmds.attributeQuery(attr_name, node=node_name, listDefault=True) or []
        )
        if len(values) > 0:
            maya.cmds.setAttr(plug_name, values[0])

    with tools_utils.tool_context(
        pre_update_frame=False,
        restore_current_frame=False,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        _apply_function_to_attrs(attr_list, func)
    return


def add_callbacks_to_attributes(attr_list, callback_manager):
    s = time.time()
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    callback_type = maya_callbacks.TYPE_ATTRIBUTE
    for attr_obj in attr_list:
        node_path = attr_obj.get_node(full_path=True)
        node_uuids = maya.cmds.ls(node_path, uuid=True) or []
        if len(node_uuids) != 1:
            LOG.debug(msg, node_path, node_uuids)
            continue
        node_uuid = node_uuids[0]
        if callback_manager.type_has_node(callback_type, node_uuid) is True:
            continue
        callback_ids = maya_callbacks.add_callbacks_attribute(
            node_uuid,
            node_path,
        )
        callback_manager.add_node_ids(
            callback_type,
            node_uuid,
            callback_ids,
        )
    e = time.time()
    LOG.debug('add_callbacks_to_attributes: t=%s', e - s)
    return


def remove_callbacks_from_attributes(attr_list, callback_manager):
    """
    Remove Attribute callbacks from a callback manager.

    :param attr_list: List of attributes to remove callbacks from.
    :type attr_list: [Attribute, ..]

    :param callback_manager:
        The callback manager class which holds all references to the
        callbacks.
    :type callback_manager: CallbackManager
    """
    s = time.time()
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    callback_type = maya_callbacks.TYPE_ATTRIBUTE
    for attr_obj in attr_list:
        node_path = attr_obj.get_node(full_path=True)
        node_uuids = maya.cmds.ls(node_path, uuid=True) or []
        if len(node_uuids) != 1:
            LOG.debug(msg, node_path, node_uuids)
            continue
        node_uuid = node_uuids[0]
        if callback_manager.type_has_node(callback_type, node_uuid) is False:
            continue
        callback_manager.remove_type_node_ids(
            callback_type,
            node_uuid,
        )
    e = time.time()
    LOG.debug('remove_callbacks_from_attributes: %r seconds', e - s)
    return
