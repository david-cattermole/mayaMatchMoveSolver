"""
This module contains all the helpful function for screenz manipulator
"""
import maya.cmds


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