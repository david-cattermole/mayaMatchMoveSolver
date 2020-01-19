"""
A tool to place a Marker at a position of a mouse click.

.. todo::
    While we are in the middle of a drag operation, we should not store
    undo operations, but at the end we must. If we always store undo
    operations each time the attribute is set we end up filling the undo
    buffer very quickly.

"""

import maya.cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.placemarkermanip.constant as const

LOG = mmSolver.logger.get_logger()


def place_marker():
    """
    Called each time the user left-clicks in the viewport.
    """
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform'
    ) or []
    if len(nodes) == 0:
        msg = 'No nodes selected! Please select Marker nodes to place.'
        LOG.warning(msg)
        return
    mkr_nodes = mmapi.filter_marker_nodes(nodes)
    if len(mkr_nodes) == 0:
        msg = 'No Marker nodes selected!'
        LOG.warning(msg)
        return
    mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
    if len(mkr_list) == 0:
        msg = 'No Marker nodes!'
        LOG.warning(msg)
        return

    # Get viewport coordinate. Viewport coordinate is relative to the
    # viewport resolution in pixels.
    vpX, vpY, vpZ = maya.cmds.draggerContext(
        const.CTX,
        query=True,
        dragPoint=True)

    view = OpenMayaUI.M3dView().active3dView()

    # Get the camera nodes from 3D viewport.
    camDag = view.getCamera()
    camShp = camDag.fullPathName()
    camDag.pop()
    camTfm = camDag.fullPathName()

    # 'Image resolution' is used to make sure the film back aspect
    # ratio is respected.
    imageWidth = maya.cmds.getAttr(camShp + '.horizontalFilmAperture') * 100.0
    imageHeight = maya.cmds.getAttr(camShp + '.verticalFilmAperture') * 100.0

    # Get the world-space location for the clicked point.
    position = OpenMaya.MPoint()
    direction = OpenMaya.MVector()
    view.viewToWorld(
        int(vpX),
        int(vpY),
        position,
        direction)

    # Compute the Marker coordinates for the given camera.
    frame = maya.cmds.currentTime(query=True)
    coord = maya.cmds.mmReprojection(
        worldPoint=(position.x, position.y, position.z),
        camera=(camTfm, camShp),
        asMarkerCoordinate=True,
        imageResolution=(imageWidth, imageHeight),
        time=frame
    )
    if coord is None:
        msg = 'Could not get Marker coordinate.'
        LOG.warning(msg)
        return
    assert len(coord) == 3

    # Set the marker position
    for mkr in mkr_list:
        mkr_grp = mkr.get_marker_group()
        mkr_grp_node = mkr_grp.get_node()
        plug_overscan_x = mkr_grp_node + '.overscanX'
        plug_overscan_y = mkr_grp_node + '.overscanY'
        overscan_x = maya.cmds.getAttr(plug_overscan_x)
        overscan_y = maya.cmds.getAttr(plug_overscan_y)
        node = mkr.get_node()
        plug_tx = node + '.translateX'
        plug_ty = node + '.translateY'
        value_tx = coord[0] * overscan_x
        value_ty = coord[1] * overscan_y
        lock_tx = maya.cmds.getAttr(plug_tx, lock=True)
        lock_ty = maya.cmds.getAttr(plug_tx, lock=True)
        if lock_tx is False and lock_ty is False:
            maya.cmds.setAttr(plug_tx, value_tx)
            maya.cmds.setAttr(plug_ty, value_ty)
        else:
            msg = 'Did not set Marker position, node is locked; node=%r'
            LOG.warning(msg, node)

    maya.cmds.select(nodes, replace=True)
    maya.cmds.refresh()
    return


def on_pre_press():
    LOG.debug('on_pre_press')
    return


def on_press():
    LOG.debug('on_press')
    place_marker()
    # NOTE: Turn OFF the undo stack!
    maya.cmds.undoInfo(stateWithoutFlush=False)
    return


def on_hold():
    # Note: This function is expected not to add any new commands to
    # the undo stack.
    place_marker()
    return


def on_drag():
    # Note: This function is expected not to add any new commands to
    # the undo stack.
    place_marker()
    return


def on_release():
    LOG.debug('on_release')
    place_marker()
    # NOTE: Turn the undo stack back on! (We assume the user wants the
    # undo stack on).
    maya.cmds.undoInfo(stateWithoutFlush=True)
    return


def tool_clean_up():
    LOG.debug('tool_clean_up')
    maya.cmds.undoInfo(stateWithoutFlush=True)


def main():
    """
    Switch to 'place marker at' tool.
    """
    mmapi.load_plugin()

    if maya.cmds.draggerContext(const.CTX, exists=True):
        maya.cmds.deleteUI(const.CTX)

    maya.cmds.draggerContext(
        const.CTX,
        prePressCommand=on_pre_press,
        pressCommand=on_press,
        releaseCommand=on_release,
        holdCommand=on_hold,
        dragCommand=on_drag,
        finalize=tool_clean_up,
        name=const.CTX,
        cursor='crossHair')
    maya.cmds.setToolTo(const.CTX)
