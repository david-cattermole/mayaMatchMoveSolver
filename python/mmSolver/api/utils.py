"""
Utility functions for Maya API.
"""

import maya.OpenMaya as OpenMaya


def getMSelectionList(paths):
    assert isinstance(paths, list) or isinstance(paths, tuple)
    selList = OpenMaya.MSelectionList()
    try:
        for node in paths:
            selList.add(node)
    except RuntimeError:
        return None
    return selList


def getAsDagPath(nodeStr):
    selList = getMSelectionList([nodeStr])
    if not selList:
        return None
    dagPath = OpenMaya.MDagPath()
    selList.getDagPath(0, dagPath)
    return dagPath


def getNodeAsMObject(nodeStr):
    selList = getMSelectionList([nodeStr])
    if not selList:
        return None
    obj = OpenMaya.MObject()
    selList.getDependNode(0, obj)
    return obj


def getNodeAttrAsMPlug(nodeAttr):
    sel = getMSelectionList([nodeAttr])
    plug = None
    if not sel.isEmpty():
        try:
            plug = sel.getPlug(0)
        except RuntimeError:
            pass
    return plug

