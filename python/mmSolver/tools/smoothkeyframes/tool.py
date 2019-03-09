"""
Smooths the selected keyframes.
"""

import maya.cmds

import mmSolver.utils.constant as utils_const
import mmSolver.utils.smooth as utils_smooth


def main():
    """
    Smooth the selected keyframes in the Graph Editor.

    Usage:
    1) Select keyframes in Graph Editor.
    2) Run tool
    3) Keyframe values will be smoothed.
    """
    key_attr = maya.cmds.keyframe(query=True, name=True)
    selected_keyframes = maya.cmds.keyframe(query=True, selected=True) or []

    value_array = []
    for frame in selected_keyframes:
        plug = key_attr[0] + '.output'
        value = maya.cmds.getAttr(plug, time=frame)
        value_array.append(value)

    smooth_type = utils_const.SMOOTH_TYPE_FOURIER
    width = 2
    new_array = utils_smooth.smooth(smooth_type, value_array, width)

    assert len(selected_keyframes) == len(new_array)
    for frame, value in zip(selected_keyframes, new_array):
        time_range = (frame, frame)
        maya.cmds.keyframe(
            key_attr[0],
            valueChange=value,
            time=time_range)
    return
