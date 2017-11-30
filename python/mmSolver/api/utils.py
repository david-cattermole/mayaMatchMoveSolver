"""
Utility functions for Maya API.
"""

import maya.OpenMaya as OpenMaya


def get_as_selection_list(paths):
    assert isinstance(paths, list) or isinstance(paths, tuple)
    selList = OpenMaya.MSelectionList()
    try:
        for node in paths:
            selList.add(node)
    except RuntimeError:
        return None
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
        pass
    return obj


def get_as_plug(node_attr):
    sel = get_as_selection_list([node_attr])
    plug = None
    if not sel.isEmpty():
        try:
            plug = sel.getPlug(0)
        except RuntimeError:
            pass
    return plug

