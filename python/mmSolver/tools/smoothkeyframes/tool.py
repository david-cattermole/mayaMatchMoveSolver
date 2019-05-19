"""
Smooths the selected keyframes.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.constant as utils_const
import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.smoothkeyframes.constant as const
import mmSolver.tools.smoothkeyframes.lib as lib

LOG = mmSolver.logger.get_logger()


def smooth_selected_keyframes():
    """
    Smooth the selected keyframes in the Graph Editor.

    Usage::

    1) Select keyframes in Graph Editor.

    2) Run tool

    3) Keyframe values will be smoothed.

    """
    key_attrs = maya.cmds.keyframe(query=True, name=True) or []
    if len(key_attrs) == 0:
        msg = (
            'Please select keyframes '
            '(in the Graph Editor) to smooth.'
        )
        LOG.warning(msg)
        return
    
    for key_attr in key_attrs:
        selected_keyframes = maya.cmds.keyframe(
            key_attr,
            query=True,
            selected=True
        ) or []
        if len(selected_keyframes) == 0:
            msg = (
                'Please select keyframes '
                '(in the Graph Editor) to smooth.'
            )
            LOG.warning(msg)
            continue

        smooth_type = configmaya.get_scene_option(
            const.CONFIG_MODE_KEY,
            default=const.DEFAULT_MODE)
        width = configmaya.get_scene_option(
            const.CONFIG_WIDTH_KEY,
            default=const.DEFAULT_WIDTH)
        
        blend_smooth_type = utils_const.SMOOTH_TYPE_GAUSSIAN
        blend_width = configmaya.get_scene_option(
            const.CONFIG_BLEND_WIDTH_KEY,
            default=const.DEFAULT_BLEND_WIDTH)
        
        lib.smooth_animcurve(
            key_attr,
            selected_keyframes,
            smooth_type,
            width,
            blend_smooth_type,
            blend_width)
    return


def main():
    import mmSolver.tools.smoothkeyframes.ui.smoothkeys_window as window
    window.main()
