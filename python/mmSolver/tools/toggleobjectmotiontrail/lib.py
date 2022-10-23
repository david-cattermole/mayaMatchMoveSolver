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
Toggle the motion trail on a objects.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def motion_trail_get_trail_shape(tfm_node):
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


def motion_trail_get_trail_node(tfm_node):
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


def motion_trail_create_node(tfm_node):
    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
    every_n_frames = 1

    trail_shape, trail_node = maya.cmds.snapshot(
        tfm_node,
        motionTrail=True,
        increment=every_n_frames,
        startTime=start_frame,
        endTime=end_frame,
    )

    maya.cmds.setAttr('{}.keyframeSize'.format(trail_shape), 0.1)

    maya.cmds.setAttr('{}.overrideEnabled'.format(trail_shape), True)
    maya.cmds.setAttr('{}.overrideDisplayType'.format(trail_shape), 2)

    trail_shape_name = '{}_motiontrailHandle'.format(tfm_node.rpartition('|')[-1])
    trail_node_name = '{}_motiontrail'.format(tfm_node.rpartition('|')[-1])
    trail_shape = maya.cmds.rename(trail_shape, trail_shape_name, ignoreShape=False)
    trail_node = maya.cmds.rename(trail_node, trail_node_name)
    trail_shape = node_utils.get_long_name(trail_shape)
    return trail_shape, trail_node


def motion_trail_get_visibility(tfm_node, trail_shape=None):
    if trail_shape is None:
        trail_shape = motion_trail_get_trail_shape(tfm_node)
    if trail_shape is None:
        return None

    node_attr = '{}.visibility'.format(trail_shape)
    value = maya.cmds.getAttr(node_attr)
    return bool(value)


def motion_trail_set_visibility(tfm_node, value, trail_shape=None, trail_node=None):
    assert isinstance(value, bool)

    if trail_shape is None:
        trail_shape = motion_trail_get_trail_shape(tfm_node)
    if trail_node is None:
        trail_node = motion_trail_get_trail_node(tfm_node)

    if trail_shape is None or trail_node is None:
        trail_shape, trail_node = motion_trail_create_node(tfm_node)

    node_attr = '{}.visibility'.format(trail_shape)
    maya.cmds.setAttr(node_attr, value)
    return trail_shape, trail_node


def motion_trails_lock_toggle(tfm_nodes):
    is_visible = False

    trail_shapes = [motion_trail_get_trail_shape(x) for x in tfm_nodes]
    for tfm_node, trail_shape in zip(tfm_nodes, trail_shapes):
        vis = motion_trail_get_visibility(tfm_node, trail_shape=trail_shape)
        if vis is True:
            is_visible = True

    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()

    visibility = not is_visible
    for tfm_node, trail_shape in zip(tfm_nodes, trail_shapes):
        trail_shape, trail_node = motion_trail_set_visibility(
            tfm_node, visibility, trail_shape=trail_shape
        )

        node_attr_start = '{}.startTime'.format(trail_node)
        node_attr_end = '{}.endTime'.format(trail_node)
        maya.cmds.setAttr(node_attr_start, start_frame)
        maya.cmds.setAttr(node_attr_end, end_frame)
    return
