# Copyright (C) 2019 David Cattermole.
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
Time related utilities.
"""

import collections

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()

FrameRange = collections.namedtuple(
    'FrameRange',
    ['start', 'end']
)


def get_maya_timeline_range_inner():
    """
    Get the Maya frame range (inner bar).

    :returns: Start frame and end frame as FrameRange tuple.
    :rtype: (int, int)
    """
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    frmrange = FrameRange(int(s), int(e))
    return frmrange


def get_maya_timeline_range_outer():
    """
    Get the Maya frame range (outer bar).

    :returns: Start frame and end frame as FrameRange tuple.
    :rtype: (int, int)
    """
    s = maya.cmds.playbackOptions(query=True, animationStartTime=True)
    e = maya.cmds.playbackOptions(query=True, animationEndTime=True)
    frmrange = FrameRange(int(s), int(e))
    return frmrange


def get_keyframe_times_for_node_attrs(nodes, attrs):
    """
    Query keyframe times on each node attribute (sparse keys)

    :param nodes: Nodes to query from.
    :type nodes: [str, ..]

    :param attrs: Attributes to query keyframes from.
    :type attrs: [str, ..]

    :returns: {str: [int, ..]}
    """
    key_times_map = collections.defaultdict(set)
    for node in nodes:
        for attr in attrs:
            plug = node + '.' + attr
            attr_exists = node_utils.attribute_exists(attr, node)
            if attr_exists is False:
                continue
            settable = maya.cmds.getAttr(plug, settable=True)
            if settable is False:
                continue
            times = maya.cmds.keyframe(
                plug,
                query=True,
                timeChange=True
            ) or []
            if len(times) == 0:
                continue
            times = [int(t) for t in times]
            key_times_map[node] |= set(times)
    key_times_map = {k: list(v) for k, v in key_times_map.items()}
    return key_times_map
