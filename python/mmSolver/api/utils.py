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
    sel_list = OpenMaya.MSelectionList()
    for node in paths:
        try:
            sel_list.add(node)
        except RuntimeError:
            pass
    return sel_list


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


def detect_object_type(node):
    assert isinstance(node, (str, unicode))
    assert maya.cmds.objExists(node)

    node_type = maya.cmds.nodeType(node)
    shape_nodes = maya.cmds.listRelatives(node, children=True, shapes=True) or []
    shape_node_types = []
    for shape_node in shape_nodes:
        shape_node_type = maya.cmds.nodeType(shape_node)
        shape_node_types.append(shape_node_type)
    attrs = maya.cmds.listAttr(node)

    object_type = 'unknown'
    if '.' in node:
        object_type = 'attribute'

    elif ((node_type == 'transform') and
            ('locator' in shape_node_types) and
            ('enable' in attrs) and
            ('weight' in attrs) and
            ('bundle' in attrs)):
        object_type = 'marker'

    elif ((node_type == 'transform') and
            ('camera' in shape_node_types)):
        object_type = 'camera'

    elif node_type == 'transform':
        object_type = 'bundle'

    return object_type
