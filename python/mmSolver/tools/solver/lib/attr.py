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

import maya.cmds
import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.undo as undo_utils
import mmSolver.tools.solver.maya_callbacks as maya_callbacks

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
    return col.get_attribute_list()


def add_attributes_to_collection(attr_list, col):
    return col.add_attribute_list(attr_list)


def remove_attr_from_collection(attr_list, col):
    return col.remove_attribute_list(attr_list)


def lock_selected_attributes(attr_list):
    LOG.debug('lock_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setAttr(plug_name, lock=True)

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def unlock_selected_attributes(attr_list):
    LOG.debug('unlock_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setAttr(plug_name, lock=False)

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def set_keyframe_on_selected_attributes(attr_list):
    LOG.debug('set_keyframe_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        maya.cmds.setKeyframe(plug_name)

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def delete_keyframe_current_frame_on_selected_attributes(attr_list):
    LOG.debug('delete_keyframe_current_frame_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        current_frame = maya.cmds.currentTime(query=True)
        node_name, sep, attr_name = plug_name.partition('.')
        time_range = (current_frame,)
        maya.cmds.cutKey(node_name, attribute=attr_name, time=time_range)

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def delete_keyframe_all_frames_on_selected_attributes(attr_list):
    LOG.debug('delete_keyframe_all_frames_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        frame_range = time_utils.get_maya_timeline_range_outer()
        time_range = (frame_range.start, frame_range.end)
        maya.cmds.cutKey(node_name, attribute=attr_name, time=time_range)

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def delete_static_channel_on_selected_attributes(attr_list):
    LOG.debug('delete_static_channel_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        maya.cmds.delete(
            node_name,
            attribute=attr_name,
            staticChannels=True
        )

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def break_connections_on_selected_attributes(attr_list):
    LOG.debug('break_connections_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        src = maya.cmds.connectionInfo(
            plug_name,
            sourceFromDestination=True) or None
        if src is None:
            return
        dst = plug_name
        connected = maya.cmds.isConnected(src, dst)
        if connected:
            maya.cmds.disconnectAttr(src, dst)
        return

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def bake_selected_attributes(attr_list):
    LOG.debug('bake_selected_attributes: %r', attr_list)
    frame_range = time_utils.get_maya_timeline_range_outer()
    plug_names = _get_plug_names_as_set(attr_list)
    plug_names = list(sorted(plug_names))
    with undo_utils.undo_chunk_context() as chunk_name:
        maya.cmds.bakeResults(
            plug_names,
            time=(frame_range.start, frame_range.end)
        )
    return


def reset_values_on_selected_attributes(attr_list):
    LOG.debug('reset_values_on_selected_attributes: %r', attr_list)

    def func(plug_name):
        node_name, sep, attr_name = plug_name.partition('.')
        values = maya.cmds.attributeQuery(
            attr_name, node=node_name,
            listDefault=True) or []
        if len(values) > 0:
            maya.cmds.setAttr(plug_name, values[0])

    with undo_utils.undo_chunk_context() as chunk_name:
        _apply_function_to_attrs(attr_list, func)
    return


def add_callbacks_to_attributes(attr_list, update_func, callback_manager):
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
            update_func,
        )
        callback_manager.add_node_ids(
            callback_type,
            node_uuid,
            callback_ids,
        )
    return


def remove_callbacks_from_attributes(attr_list, callback_manager):
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
    return
