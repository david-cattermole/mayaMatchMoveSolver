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
Library functions to perform average marker tool functions.
"""

import maya.cmds


def __get_markers_start_end_frames(selected_markers):
    """
    Gets first and last key from the selected markers list, if no keys
    found it will return current frame.

    :param selected_markers: Markers list.
    :type selected_markers: list

    :return: Start and end frame of given markers list.
    :rtype: int, int
    """
    first_frame = []
    last_frame = []
    for marker in selected_markers:
        plugs = [
            '%s.translateX' % marker,
            '%s.translateY' % marker,
        ]
        for plug_name in plugs:
            anim_curves = maya.cmds.listConnections(plug_name,
                                                    type='animCurve'
                                                    ) or []
            if len(anim_curves) == 0:
                continue

            first_keyframe_num = maya.cmds.keyframe(anim_curves,
                                                    query=True,
                                                    timeChange=True)
            first_frame.append(first_keyframe_num[0])
            last_keyframe_num = maya.cmds.keyframe(anim_curves,
                                                   query=True,
                                                   timeChange=True)
            last_frame.append(last_keyframe_num[-1])

    current_frame = maya.cmds.currentTime(query=True)
    start_frame = current_frame
    end_frame = current_frame
    if len(first_frame) > 0:
        start_frame = min(first_frame)
    if len(last_frame) > 0:
        end_frame = max(last_frame)
    return start_frame, end_frame


def __set_average_marker_position(selected_markers,
                                  start_frame,
                                  end_frame,
                                  new_mkr_node):
    """
    This function sets average value from selected marker to a new
    marker node given.

    :param selected_markers: Markers list
    :type selected_markers: list

    :param start_frame: Start frame
    :type start_frame: int

    :param end_frame: End frame
    :type end_frame: int

    :param new_mkr_node: New marker node which average value to set.
    :type new_mkr_node: str

    :return: None
    """
    for frame in range(int(start_frame), int(end_frame) + 1):
        count = len(selected_markers)
        sums = [0, 0]

        for item in selected_markers:
            src_plug_x = '%s.translateX' % item
            src_plug_y = '%s.translateY' % item
            pos_x = maya.cmds.getAttr(src_plug_x, time=frame)
            pos_y = maya.cmds.getAttr(src_plug_y, time=frame)

            sums[0] += pos_x
            sums[1] += pos_y
            center = [sums[0] / count, sums[1] / count]

            dst_plug_x = '%s.translateX' % new_mkr_node
            dst_plug_y = '%s.translateY' % new_mkr_node
            maya.cmds.setKeyframe(dst_plug_x, value=center[0], time=frame)
            maya.cmds.setKeyframe(dst_plug_y, value=center[1], time=frame)
    return
