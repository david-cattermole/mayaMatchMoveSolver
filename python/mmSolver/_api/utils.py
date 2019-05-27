"""
Utility functions for Maya API.

NOTE: Maya OpenMaya API 1.0 is used and returned from functions in
this module.

"""

from functools import wraps
import warnings
import json
import re

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver._api.constant as const
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
MM_SOLVER_IS_RUNNING = False
MM_SOLVER_USER_INTERRUPT = False


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

    elif ((node_type == 'transform')
          and ('locator' in shape_node_types)):
        object_type = const.OBJECT_TYPE_BUNDLE

    elif ((node_type == 'transform') and
          ('camera' in shape_node_types)):
        object_type = const.OBJECT_TYPE_CAMERA

    elif node_type == 'camera':
        object_type = const.OBJECT_TYPE_CAMERA

    elif ((node_type == 'transform') and
          ('imagePlane' in shape_node_types)):
        object_type = const.OBJECT_TYPE_IMAGE_PLANE

    elif node_type == 'imagePlane':
        object_type = const.OBJECT_TYPE_IMAGE_PLANE

    elif node_type == 'mmMarkerGroupTransform':
        object_type = const.OBJECT_TYPE_MARKER_GROUP

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


def convert_valid_maya_name(name,
                            prefix=None,
                            auto_add_num=True,
                            auto_add_num_padding=3,
                            auto_inc=True,
                            auto_inc_try_limit=999):
    """
    Get a new valid Maya name - canonical function to get valid Maya node names.

    Examples of auto-adding a number suffix::

       >>> convert_valid_maya_name('name')
       name_001
       >>> convert_valid_maya_name('name', auto_add_num_padding=4)
       name_0001

    Examples of auto-incrementing::

       >>> convert_valid_maya_name('name_01')
       name_02
       >>> convert_valid_maya_name('name_001')
       name_002
       >>> convert_valid_maya_name('001')
       prefix_002

    :param name: The name string to validate.
    :type name: str

    :param prefix: Prefix to add to name in case of invalid first character.
    :type prefix: str or None

    :param auto_add_num: If given a node with no number in it, should
                         we add a number automatically?
    :type auto_add_num: bool

    :param auto_add_num_padding: Padding of the number to add,
                                 2 = '01', 3 = '001', 4 = '0001'.
    :type auto_add_num_padding: int

    :param auto_inc: Should we auto-increment the number in the name?
    :type auto_inc: bool

    :param auto_inc_try_limit: When trying to find a non-existing Maya
                               node name, how many times can we
                               increment until we give up?  
    :type auto_inc_try_limit: int

    :return: A valid Maya node name.
    :rtype: str
    """
    assert isinstance(name, basestring)
    assert prefix is None or isinstance(prefix, basestring)
    assert isinstance(auto_add_num, bool)
    assert isinstance(auto_add_num_padding, int)
    assert isinstance(auto_inc, bool)
    assert isinstance(auto_inc_try_limit, int)

    # Ensure no unsupported characters are used in the node name.
    for char in const.BAD_MAYA_CHARS:
        name.replace(char, '_')

    # Add prefix, if the first letter is a digit (which Maya doesn't
    # allow.)
    #
    # NOTE: name could start with a number; this should be prefixed.
    if name[0].isdigit():
        if prefix is None:
            prefix = 'prefix'
        name = prefix + '_' + name

    # Add a number suffix if no number is already added to the
    # node name, add a number.
    if auto_add_num is True:
        splits = []
        contents = re.split('([0-9]+)', name)
        has_digit = len(contents) > 1
        if has_digit is False:
            new_number = '1'.zfill(auto_add_num_padding)
            contents.append('_')
            contents.append(new_number)
        name = ''.join(contents)

    # Auto-increment a number in the name given.
    if auto_inc is True:
        i = 0
        limit = auto_inc_try_limit
        while i <= limit and maya.cmds.objExists(name):
            splits = []
            contents = re.split('([0-9]+)', name)

            # Increment the number.
            incremented = False
            for content in reversed(contents):
                if content.isdigit() is True and incremented is False:
                    size = len(content)
                    num = int(content) + 1
                    content = str(num).zfill(size)
                    incremented = True
                splits.append(content)
            name = ''.join(reversed(splits))
            i = i + 1
    return name


def get_marker_name(name, prefix=None, suffix=None):
    """
    Create a name for a marker object, using 'name' as the base
    identifier.

    :param name: Name of object.
    :type name: str

    :param name: Prefix of the marker, if a number is the first
                 letter. If None, a default name is added.
    :type name: str or None

    :param name: Suffix of the marker, added to the name. If None, a
                 default name is added.
    :type name: str or None

    :return: Name for the marker.
    :rtype: str
    """
    assert isinstance(name, basestring)
    assert prefix is None or isinstance(prefix, basestring)
    assert suffix is None or isinstance(suffix, basestring)
    if prefix is None:
        prefix = const.MARKER_NAME_PREFIX
    if suffix is None:
        suffix = const.MARKER_NAME_SUFFIX
    if suffix.lower() not in name.lower():
        name += suffix
    name = convert_valid_maya_name(name, prefix=prefix, auto_add_num=False)
    return name


def get_bundle_name(name, prefix=None, suffix=None):
    """
    Create a name for a bundle object, using 'name' as the base
    identifier.

    :param name: Name of object.
    :type name: str

    :param name: Prefix of the bundle, if a number is the first
                 letter. If None, a default name is added.
    :type name: str or None

    :param name: Suffix of the bundle, added to the name. If None, a
                 default name is added.
    :type name: str or None

    :return: Name for the bundle.
    :rtype: str
    """
    assert isinstance(name, basestring)
    assert prefix is None or isinstance(prefix, basestring)
    assert suffix is None or isinstance(suffix, basestring)
    if prefix is None:
        prefix = const.BUNDLE_NAME_PREFIX
    if suffix is None:
        suffix = const.BUNDLE_NAME_SUFFIX
    if suffix.lower() not in name.lower():
        name += suffix
    name = convert_valid_maya_name(name, prefix=prefix, auto_add_num=False)
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
    msg = 'This is deprecated. Use `mmSolver.utils.config` module'
    warnings.warn(msg)
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
    msg = 'This is deprecated. Use `mmSolver.utils.config` module'
    warnings.warn(msg)
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
    msg = 'This is deprecated. Use `mmSolver.utils.config` module'
    warnings.warn(msg)
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
    msg = 'This is deprecated. Use `mmSolver.utils.config` module'
    warnings.warn(msg)
    assert isinstance(attr_name, (str, unicode))
    assert isinstance(data, (bool, float, int))
    node_attr = node_name + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, data)
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_node_wire_colour_rgb(node):
    """
    Get the current wire-frame colour of the node.

    The 'node' is assumed to a DAG node (capable of having a wireframe
    colour).

    :param node: Maya node path to get wireframe colour from.
    :type node: str

    :returns: Tuple of red, green and blue.
    :rtype: (float, float, float)
    """
    assert maya.cmds.objExists(node) is True
    node_attr = '{0}.{1}'.format(node, 'wireColorRGB')
    value = maya.cmds.getAttr(node_attr)[0]
    return value


def set_node_wire_colour_rgb(node, rgb):
    """
    Change the Wireframe colour of the node.

    :param rgb: Colour as R, G, B; Or None to reset to default colour.
    :type rgb: tuple

    :return: Nothing.
    :rtype: None
    """
    assert rgb is None or isinstance(rgb, (tuple, list))
    if isinstance(rgb, (tuple, list)):
        assert len(rgb) == 3
        maya.cmds.color(node, rgbColor=rgb)
    else:
        # Reset to default wireframe colour.
        maya.cmds.color(node)
    return


def is_solver_running():
    """
    Get the current state of the mmSolver command; is it running?

    :returns: State of mmSolver running.
    :rtype: bool
    """
    global MM_SOLVER_IS_RUNNING
    return MM_SOLVER_IS_RUNNING


def set_solver_running(value):
    """
    Get the current state of the mmSolver command; is it running?

    :param value: Value of the solver running, True or False.
    :type value: bool
    """
    assert isinstance(value, bool)
    global MM_SOLVER_IS_RUNNING
    MM_SOLVER_IS_RUNNING = value
    return


def get_user_interrupt():
    """
    Has the user requested to cancel the current solve?

    :returns: If the user wants to interrupt.
    :rtype: bool
    """
    global MM_SOLVER_USER_INTERRUPT
    return MM_SOLVER_USER_INTERRUPT


def set_user_interrupt(value):
    """
    Tell mmSolver if the user wants to interrupt.

    :param value: Value of the interrupt, True or False.
    :type value: bool
    """
    assert isinstance(value, bool)
    global MM_SOLVER_USER_INTERRUPT
    MM_SOLVER_USER_INTERRUPT = value
    return
