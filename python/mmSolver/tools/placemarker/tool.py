"""
A tool to place a Marker at a position of a mouse click.
"""

import maya.cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes


LOG = mmSolver.logger.get_logger()
CTX = 'mmSolverMarkerPlacementCtx'


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
    mkr_nodes = filternodes.get_marker_nodes(nodes)
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
        CTX,
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
    #
    # TODO: Find a way to not create a node each time we want to
    # reprojection a point.
    frame = maya.cmds.currentTime(query=True)
    node = maya.cmds.createNode('transform')
    coord = None
    try:
        maya.cmds.setAttr('%s.tx' % node, position.x)
        maya.cmds.setAttr('%s.ty' % node, position.y)
        maya.cmds.setAttr('%s.tz' % node, position.z)
        coord = maya.cmds.mmReprojection(
            node, camera=(camTfm, camShp),
            asMarkerCoordinate=True,
            imageResolution=(imageWidth, imageHeight),
            time=frame
        )
    finally:
        maya.cmds.delete(node)
    if coord is None:
        msg = 'Could not get Marker coordinate.'
        LOG.warning(msg)
        return
    assert len(coord) == 3

    # Set the marker position
    for mkr in mkr_list:
        node = mkr.get_node()
        plug_tx = node + '.translateX'
        plug_ty = node + '.translateY'
        value_tx = coord[0]
        value_ty = coord[1]
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


def on_press():
    LOG.debug('on_press')
    place_marker()


def on_release():
    LOG.debug('on_release')
    place_marker()


def on_hold():
    LOG.debug('on_hold')
    place_marker()


def on_drag():
    LOG.debug('on_drag')
    place_marker()


def tool_clean_up():
    LOG.debug('tool_clean_up')


def main():
    """
    Switch to 'place marker at' tool.
    """
    mmapi.load_plugin()

    if maya.cmds.draggerContext(CTX, exists=True):
        maya.cmds.deleteUI(CTX)

    maya.cmds.draggerContext(
        CTX,
        prePressCommand=on_pre_press,
        pressCommand=on_press,
        releaseCommand=on_release,
        holdCommand=on_hold,
        dragCommand=on_drag,
        finalize=tool_clean_up,
        name=CTX,
        cursor='crossHair')
    maya.cmds.setToolTo(CTX)
