"""
The Create Marker tool.
"""

import warnings

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes


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


def is_startup_cam(x):
    """
    Return True if the given camera node is a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return maya.cmds.camera(x, query=True, startupCamera=True) is True


def is_not_startup_cam(x):
    """
    Return True if the given camera node is NOT a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return is_startup_cam(x) is False


def main():
    """
    Create a new marker under the current viewport camera, or under
    the selected camera, if a camera is selected.
    """
    mmapi.load_plugin()

    sel = maya.cmds.ls(sl=True, long=True)
    node_filtered = filter_nodes.get_nodes(sel)
    cams = node_filtered['camera']
    cams = filter(is_not_startup_cam, cams)
    mkr_grps = node_filtered['markergroup']

    cam = None
    mkr_grp = None
    if len(cams) > 0 and len(mkr_grps) > 0:
        msg = 'Please select a camera or marker group; '
        msg += 'both node types are selected.'
        LOG.error(msg)

    elif len(cams) == 0 and len(mkr_grps) == 0:
        node = __get_camera()
        if node is None:
            msg = 'Please activate a viewport to get a camera.'
            LOG.error(msg)
            return
        if is_startup_cam(node) is True:
            msg = "Cannot create Markers in 'persp' camera."
            LOG.error(msg)
            return
        if maya.cmds.nodeType(node) == 'transform':
            cam = mmapi.Camera(transform=node)
        elif maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            LOG.error('Camera node is invalid; %r', node)
            return

    elif len(cams) > 0 and len(mkr_grps) == 0:
        node = cams[0]
        if maya.cmds.nodeType(node) == 'transform':
            cam = mmapi.Camera(transform=node)
        elif maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            LOG.error('Camera node is invalid; %r', node)
            return

    elif len(cams) == 0 and len(mkr_grps) > 0:
        node = mkr_grps[0]
        mkr_grp = mmapi.MarkerGroup(name=node)

    else:
        LOG.error('Should not get here.')

    bnd_name = mmapi.get_bundle_name('bundle1')
    bnd = mmapi.Bundle().create_node(
        name=bnd_name
    )

    mkr_name = mmapi.get_marker_name('marker1')
    mkr = mmapi.Marker().create_node(
        name=mkr_name,
        cam=cam,
        mkr_grp=mkr_grp,
        bnd=bnd
    )

    maya.cmds.select(mkr.get_node(), replace=True)
    return


def create_marker():
    warnings.warn("Use 'main' function instead.")
    main()
