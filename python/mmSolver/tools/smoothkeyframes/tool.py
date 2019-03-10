"""
Smooths the selected keyframes.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.constant as utils_const
import mmSolver.utils.smooth as utils_smooth

LOG = mmSolver.logger.get_logger()


def main():
    """
    Smooth the selected keyframes in the Graph Editor.

    Usage:
    1) Select keyframes in Graph Editor.
    2) Run tool
    3) Keyframe values will be smoothed.
    """
    key_attrs = maya.cmds.keyframe(query=True, name=True) or []
    if len(key_attrs) == 0:
        msg = (
            'Please select keyframes (in the'
            ' Graph Editor) to smooth.'
        )
        LOG.warning(msg)
        return
    
    for key_attr in key_attrs:
        selected_keyframes = maya.cmds.keyframe(
            key_attr,
            query=True,
            selected=True
        )
        if len(selected_keyframes) < 2:
            msg = (
                'Please select more than 1 keyframes '
                '(in the Graph Editor) to smooth.'
            )
            LOG.warning(msg)
            continue

        value_array = []
        for frame in selected_keyframes:
            plug = key_attr + '.output'
            value = maya.cmds.getAttr(plug, time=frame)
            value_array.append(value)

        smooth_type = utils_const.SMOOTH_TYPE_FOURIER
        width = 2
        new_array = utils_smooth.smooth(smooth_type, value_array, width)

        assert len(selected_keyframes) == len(new_array)
        for frame, value in zip(selected_keyframes, new_array):
            time_range = (frame, frame)
            maya.cmds.keyframe(
                key_attr,
                valueChange=value,
                time=time_range)
    return
