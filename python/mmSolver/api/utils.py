"""
Utility functions for Maya API.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya


def get_long_name(node):
    result = maya.cmds.ls(node, long=True)
    if result and len(result):
        return result[0]
    return None


def get_as_selection_list(paths):
    assert isinstance(paths, list) or isinstance(paths, tuple)
    selList = OpenMaya.MSelectionList()
    for node in paths:
        try:
            selList.add(node)
        except RuntimeError:
            pass
    return selList


def get_as_dag_path(node_str):
    sel_list = get_as_selection_list([node_str])
    if not sel_list:
        return None
    dagPath = OpenMaya.MDagPath()
    sel_list.getDagPath(0, dagPath)
    return dagPath


def get_as_object(node_str):
    selList = get_as_selection_list([node_str])
    if not selList:
        return None
    obj = OpenMaya.MObject()
    try:
        selList.getDependNode(0, obj)
    except RuntimeError:
        obj = None
    return obj


def get_as_plug(node_attr):
    sel = get_as_selection_list([node_attr])
    plug = None
    if not sel.isEmpty():
        try:
            plug = OpenMaya.MPlug()
            sel.getPlug(0, plug)
        except RuntimeError:
            plug = None
    return plug

