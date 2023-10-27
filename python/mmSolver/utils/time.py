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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()

# The canonical object to store integer frame ranges.
#
# Ideally, all frame ranges should be stored with this object. We can
# pass this one variable around, the number of arguments.
FrameRange = collections.namedtuple('FrameRange', ['start', 'end'])


def get_maya_timeline_range_inner():
    """
    Get the Maya frame range (inner bar).

    :returns: Start frame and end frame as FrameRange tuple.
    :rtype: FrameRange or (int, int)
    """
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    frmrange = FrameRange(int(s), int(e))
    return frmrange


def get_maya_timeline_range_outer():
    """
    Get the Maya frame range (outer bar).

    :returns: Start frame and end frame as FrameRange tuple.
    :rtype: FrameRange or (int, int)
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
            times = maya.cmds.keyframe(plug, query=True, timeChange=True) or []
            if len(times) == 0:
                continue
            times = [int(t) for t in times]
            key_times_map[node] |= set(times)
    key_times_map = {k: list(v) for k, v in key_times_map.items()}
    return key_times_map


def get_frame_range(frame_range_mode, start_frame=None, end_frame=None):
    """
    Get the FrameRange from the mode and start/end frame numbers.

    :param frame_range_mode: The mode or type of frame range to
        get. For example we can get the current inner or outer
        timeline defined in the Maya scene.
    :type frame_range_mode: mmSolver.utils.constant.FRAME_RANGE_MODE_*_VALUE

    :param start_frame: If the frame_range_mode is set to
        FRAME_RANGE_MODE_CUSTOM_VALUE, this argument defines the exact
        start_frame to use. This argument is not used for any other
        frame_range_mode and can be left as None.
    :type start_frame: int or None

    :param end_frame: If the frame_range_mode is set to
        FRAME_RANGE_MODE_CUSTOM_VALUE, this argument defines the exact
        end_frame to use. This argument is not used for any other
        frame_range_mode and can be left as None.
    :type end_frame: int or None

    :rtype: FrameRange
    """
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES

    if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        start_frame, end_frame = get_maya_timeline_range_outer()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        start_frame, end_frame = get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
        assert start_frame is not None
        assert end_frame is not None
    else:
        assert False
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    frame_range = FrameRange(start_frame, end_frame)
    return frame_range


def convert_frame_range_to_frame_list(frame_range):
    """
    Convert a FrameRange to a list of integer frame numbers.

    :param frame_range: The frame range to convert to a list.
    :type frame_range: FrameRange

    :rtype: [int, ...] or []
    """
    start_frame, end_frame = frame_range
    frames = list(range(int(start_frame), int(end_frame) + 1))
    return frames
