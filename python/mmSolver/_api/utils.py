"""
Utility functions for Maya API.

NOTE: Maya OpenMaya API 1.0 is used and returned from functions in
this module.

"""

from functools import wraps
import json

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver._api.constant as const
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def get_long_name(node):
    """
    Given a valid node path, get the 'full path' node name, or None if invalid.

    note::
        DG nodes do not have a 'full path' as they do not have hierarchy and
        will always have unique node names.

    :param node: Maya DG or DAG node path.
    :type node: str

    :return: Full path node name.
    :rtype: None or str
    """
    result = maya.cmds.ls(node, long=True)
    if result and len(result):
        return result[0]
    return None


def get_as_selection_list(paths):
    """
    Get a Maya API selection list with the given valid Maya node paths.

    :param paths: List of Maya node paths.
    :type paths: list of str

    :return: MSelectionList with valid nodes added to list.
    :rtype: OpenMaya.MSelectionList
    """
    assert isinstance(paths, list) or isinstance(paths, tuple)
    sel_list = OpenMaya.MSelectionList()
    for node in paths:
        try:
            sel_list.add(node)
        except RuntimeError:
            pass
    return sel_list


def get_as_dag_path(node_str):
    """
    Convert the given Maya node path into a MDagPath object.

    :param node_str: Maya node path to be converted.
    :type node_str: str

    :return: MDagPath API object or None if the 'node_str' is invalid.
    :type: MDagPath or None
    """
    sel_list = get_as_selection_list([node_str])
    if not sel_list:
        return None
    dagPath = OpenMaya.MDagPath()
    sel_list.getDagPath(0, dagPath)
    return dagPath


def get_as_object(node_str):
    """
    Convert the given Maya node path into a MObject object.

    :param node_str: Maya node path to be converted.
    :type node_str: str

    :return: MObject API object or None, if conversion failed.
    :rtype: MObject or None
    """
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
    """
    Convert the given 'node.attr' path into a MPlug object.

    :param node_attr: Node attribute string in format 'node.attr'.
    :type node_attr: str

    :return: MPlug object or None if conversion failed.
    :type: MPlug or None
    """
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
    """
    The canonical function to interpret a node as an MM Solver object type.

    Possible object type values are:

    - OBJECT_TYPE_MARKER
    - OBJECT_TYPE_BUNDLE
    - OBJECT_TYPE_ATTRIBUTE
    - OBJECT_TYPE_CAMERA
    - OBJECT_TYPE_MARKER_GROUP
    - OBJECT_TYPE_COLLECTION
    - OBJECT_TYPE_UNKNOWN

    .. note:: Giving a shape or transform of an object may return
        different values depending on the type. Below lists the
        types and the expected input node type.

        - Markers - transform nodes
        - Bundle - transform nodes
        - Attribute - plug path (node.attr)
        - Camera - transform or shape node
        - Marker Group - transform 'mmMarkerGroupTransform' node
        - Collection - set node

    :param node: Maya node path to get type of.
    :type node: str

    :return: The object type string; One of the values in OBJECT_TYPE_LIST
    :rtype: OBJECT_TYPE_*
    """
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

    object_type = const.OBJECT_TYPE_UNKNOWN
    if '.' in node:
        object_type = const.OBJECT_TYPE_ATTRIBUTE

    elif ((node_type == 'transform')
          and ('locator' in shape_node_types)
          and ('enable' in attrs)
          and ('weight' in attrs)
          and ('bundle' in attrs)):
        object_type = const.OBJECT_TYPE_MARKER

    elif ((node_type == 'transform') and
          ('camera' in shape_node_types)):
        object_type = const.OBJECT_TYPE_CAMERA

    elif node_type == 'camera':
        object_type = const.OBJECT_TYPE_CAMERA

    elif node_type == 'mmMarkerGroupTransform':
        object_type = const.OBJECT_TYPE_MARKER_GROUP

    elif node_type == 'transform':
        object_type = const.OBJECT_TYPE_BUNDLE

    elif ((node_type == 'objectSet')
          and ('solver_list' in attrs)):
        object_type = const.OBJECT_TYPE_COLLECTION

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


def convert_valid_maya_name(name, prefix=None):
    """
    Get a new valid Maya name - canonical function to get valid Maya node names.

    :param name: The name string to validate.
    :param prefix: Prefix to add to name in case of invalid first character.
    :return:
    """
    # TODO: Use Maya API namespace validator?
    # TODO: name could start with a number; this should be prefixed.
    assert isinstance(name, basestring)
    for char in const.BAD_MAYA_CHARS:
        name.replace(char, '_')
    if name[0].isdigit():
        # Add suffix
        if prefix is None:
            prefix = 'prefix'
        name = prefix + '_' + name
    return name


def get_marker_name(name):
    """
    Create a name for a marker object, using 'name' as the base identifier.

    :param name: Name of object.
    :return: Name for the marker.
    """
    assert isinstance(name, basestring)
    name = convert_valid_maya_name(name, prefix='marker')
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
    name = convert_valid_maya_name(name, prefix='bundle')
    if const.BUNDLE_NAME_SUFFIX.lower() not in name.lower():
        name += const.BUNDLE_NAME_SUFFIX
    return name


def load_plugin():
    """
    Load the mmSolver plugin.

    Raises a RuntimeError exception if a plug-in cannot be loaded.

    :return: None
    """
    msg = 'Could not load plug-in %r!'
    for name in const.PLUGIN_NAMES:
        try:
            maya.cmds.loadPlugin(name, quiet=True)
        except RuntimeError as e:
            LOG.error(msg, name)
            raise e
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


def get_value_on_node_attr(node_name, attr_name):
    """
    Get numeric value from an node attribute.

    :param node_name: Node to get value from.
    :type node_name: str

    :param attr_name: The name of the attribute to get value from.
    :type attr_name: str

    :return: A numeric value.
    :rtype: bool or float or int
    """
    ret = []
    attrs = maya.cmds.listAttr(node_name)
    if attr_name not in attrs:
        msg = 'attr_name not found on node: '
        msg += 'attr_name={name} node={node}'
        msg = msg.format(name=attr_name, node=node_name)
        raise ValueError(msg)
    node_attr = node_name + '.' + attr_name
    ret = maya.cmds.getAttr(node_attr)
    return ret


def set_value_on_node_attr(node_name, attr_name, data):
    """
    Set value onto a node.attr path.

    :param node_name: Node to store value on.
    :type node_name: str

    :param attr_name: Attribute name to store value with.
    :type attr_name: str

    :param data: The numeric value to store.
    :type data: bool or float or int

    ;return: Nothing.
    :rtype: None
    """
    assert isinstance(attr_name, (str, unicode))
    assert isinstance(data, (bool, float, int))
    node_attr = node_name + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, data)
    maya.cmds.setAttr(node_attr, lock=True)
    return
