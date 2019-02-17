"""
Aim the selected transform nodes at the current viewport's camera.
"""

import warnings
import maya.cmds
import mmSolver.logger
import mmSolver.tools.cameraaim.lib as lib


LOG = mmSolver.logger.get_logger()


def __get_model_editor():
    """
    Get the active model editor.
    """
    the_panel = maya.cmds.getPanel(withFocus=1)
    panel_type = maya.cmds.getPanel(typeOf=the_panel)

    if panel_type != 'modelPanel':
        return None

    model_ed = maya.cmds.modelPanel(the_panel, modelEditor=1, query=1)
    return model_ed


def __get_camera():
    """
    Get the camera from the active model editor
    """
    model_ed = __get_model_editor()
    cam = None
    if model_ed is not None:
        cam = maya.cmds.modelEditor(model_ed, query=True, camera=True)
    if maya.cmds.nodeType(cam) == 'camera':
        cam = maya.cmds.listRelatives(cam, parent=True) or []
        if len(cam) > 0:
            cam = cam[0]
        else:
            cam = None
    return cam


def main():
    """
    Aims the selected transforms at the active viewport's camera
    transform node.
    """
    sel = maya.cmds.ls(sl=True, type='transform') or []
    if len(sel) == 0:
        LOG.warning('Please select at least one object!')
        return

    cam = __get_camera()
    if cam is None:
        LOG.warning('Please select an active viewport to get a camera.')
        return

    lib.aim_at_target(sel, cam, remove_after=True)
    return


def aim_at_camera():
    warnings.warn("Use 'main' function instead.")
    main()
