"""
Library functions to perform average marker tool functions.

"""

import maya.cmds


def __get_markers_start_end_frames(selected_markers):
    """
    Gets first and last key from the selected markers list, if no keys
    found it will return current frame
    :param selected_markers: Markers list
    :return: Start and end frame of given markers list
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
            if not anim_curves:
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

    if first_frame:
        start_frame = min(first_frame)
    else:
        start_frame = current_frame

    if last_frame:
        end_frame = max(last_frame)
    else:
        end_frame = current_frame

    return start_frame, end_frame


def __set_average_marker_position(selected_markers,
                                  start_frame,
                                  end_frame,
                                  new_mkr_node):
    """
    This function sets average value from selected marker to a new
    marker node given
    :param selected_markers: Markers list
    :param start_frame: Start frame
    :param end_frame: End frame
    :param new_mkr_node: New marker node which average value to set
    :return: None
    """

    for frame in range(int(start_frame), int(end_frame) + 1):
        count = len(selected_markers)
        sums = [0, 0]

        for item in selected_markers:
            pos_x = maya.cmds.getAttr('%s.translateX' % item,
                                      time=frame)

            pos_y = maya.cmds.getAttr('%s.translateY' % item,
                                      time=frame)
            sums[0] += pos_x
            sums[1] += pos_y
            center = [sums[0] / count, sums[1] / count]

            maya.cmds.setKeyframe('%s.translateX' % new_mkr_node,
                                  v=center[0], time=frame)

            maya.cmds.setKeyframe('%s.translateY' % new_mkr_node,
                                  v=center[1], time=frame)
    return
