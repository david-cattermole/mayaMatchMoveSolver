"""
Aim the selected transform nodes at the current viewport's camera.
"""

import maya.cmds
import mmSolver.logger


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


def aim_at_camera():
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

    for node in sel:
        for attr in ['rx', 'ry', 'rz']:
            maya.cmds.setAttr(node + '.' + attr, lock=False)
        aim = maya.cmds.aimConstraint(
            cam,
            node,
            offset=(0, 0, 0),
            weight=1.0,
            aimVector=(1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType='vector',
            worldUpVector=(0, 1, 0)
        )
        if maya.cmds.objExists(aim[0]):
            maya.cmds.delete(aim[0])
    return
