"""
A tool to place a Marker at a position of a mouse click.
"""

import maya.cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI

CTX = 'mmSolverMarkerPlacementCtx'

def context_on_press():
    vpX, vpY, vpZ = maya.cmds.draggerContext(CTX, query=True, anchorPoint=True)
    # print 'vp:', vpX, vpY, vpZ

    view = OpenMayaUI.M3dView().active3dView()

    camDag = view.getCamera()
    camShp = camDag.fullPathName()
    camDag.pop()
    camTfm = camDag.fullPathName()

    position = OpenMaya.MPoint()
    direction = OpenMaya.MVector()
    view.viewToWorld(
        int(vpX),
        int(vpY),
        position,
        direction)

    # print 'pos:', position
    # print 'dir:', direction
    # print 'cam:', camTfm, camShp
    frame = maya.cmds.currentTime(query=True)
    node = maya.cmds.createNode('transform')
    maya.cmds.setAttr('%s.tx' % node, position.x)
    maya.cmds.setAttr('%s.ty' % node, position.y)
    maya.cmds.setAttr('%s.tz' % node, position.z)
    point = maya.cmds.mmReprojection(
        node, camera=(camTfm, camShp),
        asNormalizedCoordinate=True,
        time=frame
    )
    print 'point', point
    maya.cmds.delete(node)
    return


def main():
    maya.cmds.loadPlugin('mmSolver')

    if maya.cmds.draggerContext(CTX, exists=True):
        maya.cmds.deleteUI(CTX)

    maya.cmds.draggerContext(
        CTX,
        pressCommand=context_on_press,
        name=CTX,
        cursor='crossHair')
    maya.cmds.setToolTo(CTX)