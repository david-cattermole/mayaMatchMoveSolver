"""
Utility functions for Maya API.
"""

from functools import wraps

import maya.cmds
import maya.OpenMaya as OpenMaya


# list of characters that are not supported in maya for node names.
# Note, only ':' and '_' are not in the list.
BAD_MAYA_CHARS = [
    ' ', '#', '-', '@', '!', '$', '%', '^', '&', '*',
    '+', '=', '/', '\\', '~', '`', '.', ',', '?', ';', '|'
    '(', ')', '[', ']', '{', '}', '<', '>'
    '\'', '\"'
]

MARKER_NAME_SUFFIX = '_MKR'
BUNDLE_NAME_SUFFIX = '_BND'


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


def get_object_type(node):
    assert isinstance(node, basestring)
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

    elif node_type == 'camera':
        object_type = 'camera'

    elif node_type == 'mmMarkerGroupTransform':
        object_type = 'markergroup'

    elif node_type == 'transform':
        object_type = 'bundle'

    return object_type


def get_camera_above_node(node):
    """
    Get the first camera transform and shape node above the node.

    :param node: The node name to check above for a camera.
    :type node: str or unicode
    :return: Tuple of camera transform and shape nodes, or (None, None)
    :rtype: tuple
    """
    # TODO: This function may be called many times, we should look into
    # caching some of this computation.
    cam_tfm = None
    cam_shp = None
    dag = get_as_dag_path(node)
    got_it = False
    while dag.length() != 0:
        if dag.apiType() == OpenMaya.MFn.kTransform:
            num_children = dag.childCount()
            if num_children > 0:
                for i in xrange(num_children):
                    child_obj = dag.child(i)
                    if child_obj.apiType() == OpenMaya.MFn.kCamera:
                        cam_tfm = dag.fullPathName()
                        dag.push(child_obj)
                        cam_shp = dag.fullPathName()
                        got_it = True
                        break
        if got_it is True:
            break
        dag.pop(1)
    return cam_tfm, cam_shp


def get_marker_group_above_node(node):
    """
    Get the first marker group transform node above the node.

    :param node: The node name to check above for a marker group.
    :type node: str or unicode
    :return: String of marker group found, or None.
    :rtype: str or unicode
    """
    # TODO: This function may be called many times, we should look into
    # caching some of this computation.
    mkr_grp_node = None
    dag = get_as_dag_path(node)
    while dag.length() != 0:
        name = dag.fullPathName()
        if maya.cmds.nodeType(name) == 'mmMarkerGroupTransform':
            mkr_grp_node = name
            break
        dag.pop(1)
    return mkr_grp_node


def convert_valid_maya_name(name):
    # TODO: Use Maya API namespace validator?
    # TODO: name could start with a number; this should be prefixed.
    assert isinstance(name, basestring)
    for char in BAD_MAYA_CHARS:
        name.replace(char, '_')
    return name


def get_marker_name(name):
    """
    Create a name for a marker object, using 'name' as the base identifier.

    :param name: Name of object.
    :return: Name for the marker.
    """
    assert isinstance(name, basestring)
    name = convert_valid_maya_name(name)
    if MARKER_NAME_SUFFIX.lower() not in name.lower():
        name += MARKER_NAME_SUFFIX
    return name


def get_bundle_name(name):
    """
    Create a name for a bundle object, using 'name' as the base identifier.

    :param name: Name of object.
    :return: Name for the bundle.
    """
    assert isinstance(name, basestring)
    name = convert_valid_maya_name(name)
    if BUNDLE_NAME_SUFFIX.lower() not in name.lower():
        name += BUNDLE_NAME_SUFFIX
    return name


def undo_chunk(func):
    """
    Undo/Redo Chunk Decorator.

    Puts the wrapped 'func' into a single Maya Undo action.
    If 'func' raises and exception, we close the chunk.
    """
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            # start an undo chunk
            maya.cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk and undo
            maya.cmds.undoInfo(closeChunk=True)
            maya.cmds.undo()
    return _func
