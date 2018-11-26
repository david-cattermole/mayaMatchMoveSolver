"""
Utility functions for Maya API.
"""

from functools import wraps
import json

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver._api.constant as const


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
    shape_nodes = maya.cmds.listRelatives(
        node,
        children=True,
        shapes=True,
        fullPath=True) or []
    shape_node_types = []
    for shape_node in shape_nodes:
        shape_node_type = maya.cmds.nodeType(shape_node)
        shape_node_types.append(shape_node_type)
    attrs = maya.cmds.listAttr(node)

    object_type = 'unknown'
    if '.' in node:
        object_type = 'attribute'

    elif ((node_type == 'transform')
          and ('locator' in shape_node_types)
          and ('enable' in attrs)
          and ('weight' in attrs)
          and ('bundle' in attrs)):
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

    elif ((node_type == 'objectSet')
          and ('solver_list' in attrs)):
        object_type = 'collection'

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
    # TODO: This function may be called many times, we should look
    # into caching some of this computation.
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
    for char in const.BAD_MAYA_CHARS:
        name.replace(char, '_')
    if name[0].isdigit():
        name = 'marker_' + name
    return name


def get_marker_name(name):
    """
    Create a name for a marker object, using 'name' as the base identifier.

    :param name: Name of object.
    :return: Name for the marker.
    """
    assert isinstance(name, basestring)
    name = convert_valid_maya_name(name)
    if const.MARKER_NAME_SUFFIX.lower() not in name.lower():
        name += const.MARKER_NAME_SUFFIX
    return name


def get_bundle_name(name):
    """
    Create a name for a bundle object, using 'name' as the base identifier.

    :param name: Name of object.
    :return: Name for the bundle.
    """
    assert isinstance(name, basestring)
    name = convert_valid_maya_name(name)
    if const.BUNDLE_NAME_SUFFIX.lower() not in name.lower():
        name += const.BUNDLE_NAME_SUFFIX
    return name


def load_plugin():
    """
    Load the mmSolver plugin.

    :return:
    """
    for name in const.PLUGIN_NAMES:
        maya.cmds.loadPlugin(name, quiet=True)
    return


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


def get_data_on_node_attr(node_name, attr_name):
    """
    Get data from an node attribute.

    :param node_name: Node to get data from.
    :type node_name: str

    :param attr_name: The name of the attribute to get data from.
    :type attr_name: str

    :return: Arbitrary Plain-Old-Data data structures.
    :rtype: list of dict
    """
    ret = []
    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        msg = 'attr_name not found on node: '
        msg += 'attr_name={name} node={node}'
        msg = msg.format(name=attr_name, node=node_name)
        raise ValueError(msg)
    node_attr = node_name + '.' + attr_name
    attr_data = maya.cmds.getAttr(node_attr)
    if attr_data is None:
        return ret
    data = json.loads(attr_data)
    if isinstance(data, list):
        ret = data
    return ret


def set_data_on_node_attr(node_name, attr_name, data):
    """
    Set arbitrary Plain-Old-Data onto a node.attr path.

    :param node_name: Node to store data on.
    :type node_name: str

    :param attr_name: Attribute name to store data with.
    :type attr_name: str

    :param data: The data to store.
    :type data: list or dict

    ;return: Nothing.
    :rtype: None
    """
    assert isinstance(attr_name, (str, unicode))
    assert isinstance(data, (list, dict))
    node_attr = node_name + '.' + attr_name

    new_attr_data = json.dumps(data)
    old_attr_data = maya.cmds.getAttr(node_attr)
    if old_attr_data == new_attr_data:
        return  # no change is needed.

    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, new_attr_data, type='string')
    maya.cmds.setAttr(node_attr, lock=True)
    return
