# Copyright (C) 2022 David Cattermole.
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
Toggle the motion path on a objects.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def motion_path_get_path_shape(tfm_node):
    conns = (
        maya.cmds.listConnections(
            tfm_node,
            connections=False,
            source=False,
            destination=True,
            type='motionTrailShape',
        )
        or []
    )
    if len(conns) > 0:
        return list(sorted(set(conns)))[0]
    return None


def motion_path_get_path_node(tfm_node):
    conns = (
        maya.cmds.listConnections(
            tfm_node,
            connections=False,
            source=False,
            destination=True,
            type='motionTrail',
        )
        or []
    )
    if len(conns) > 0:
        return list(sorted(set(conns)))[0]
    return None


def motion_path_create_node(tfm_node):
    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
    every_n_frames = 1

    path_shape, path_node = maya.cmds.snapshot(
        tfm_node,
        motionTrail=True,
        increment=every_n_frames,
        startTime=start_frame,
        endTime=end_frame,
    )

    attr = '{}.keyframeSize'.format(path_shape)
    maya.cmds.setAttr(attr, 0.1)

    path_shape_name = '{}_motionPathHandle'.format(tfm_node.rpartition('|')[-1])
    path_node_name = '{}_motionPath'.format(tfm_node.rpartition('|')[-1])
    path_shape = maya.cmds.rename(path_shape, path_shape_name, ignoreShape=False)
    path_node = maya.cmds.rename(path_node, path_node_name)
    path_shape = node_utils.get_long_name(path_shape)
    return path_shape, path_node


def motion_path_get_visibility(tfm_node, path_shape=None):
    if path_shape is None:
        path_shape = motion_path_get_path_shape(tfm_node)
    if path_shape is None:
        return None

    node_attr = '{}.visibility'.format(path_shape)
    value = maya.cmds.getAttr(node_attr)
    return bool(value)


def motion_path_set_visibility(tfm_node, value, path_shape=None, path_node=None):
    assert isinstance(value, bool)

    if path_shape is None:
        path_shape = motion_path_get_path_shape(tfm_node)
    if path_node is None:
        path_node = motion_path_get_path_node(tfm_node)

    if path_shape is None or path_node is None:
        path_shape, path_node = motion_path_create_node(tfm_node)

    node_attr = '{}.visibility'.format(path_shape)
    maya.cmds.setAttr(node_attr, value)
    return path_shape, path_node


def motion_paths_lock_toggle(tfm_nodes):
    is_visible = False

    path_shapes = [motion_path_get_path_shape(x) for x in tfm_nodes]
    for tfm_node, path_shape in zip(tfm_nodes, path_shapes):
        vis = motion_path_get_visibility(tfm_node, path_shape=path_shape)
        if vis is True:
            is_visible = True

    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()

    visibility = not is_visible
    for tfm_node, path_shape in zip(tfm_nodes, path_shapes):
        path_shape, path_node = motion_path_set_visibility(
            tfm_node, visibility, path_shape=path_shape
        )

        node_attr_start = '{}.startTime'.format(path_node)
        node_attr_end = '{}.endTime'.format(path_node)
        maya.cmds.setAttr(node_attr_start, start_frame)
        maya.cmds.setAttr(node_attr_end, end_frame)
    return
