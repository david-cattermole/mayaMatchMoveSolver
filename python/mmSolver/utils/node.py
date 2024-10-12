# Copyright (C) 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Utilities built around Maya nodes and node paths.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import maya.cmds
import maya.OpenMaya as OpenMaya1
import maya.api.OpenMaya as OpenMaya2

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def get_node_full_path(*args, **kwargs):
    msg = 'Use mmSolver.utils.node.get_long_name function instead'
    warnings.warn(msg, DeprecationWarning)
    return get_long_name(*args, **kwargs)


def node_is_referenced(node):
    """
    Is the node given referenced (from a referenced file)?

    :param node: Node to query.

    :return: True or False, is it referenced?
    :rtype: bool
    """
    return maya.cmds.referenceQuery(node, isNodeReferenced=True)


def set_attr(plug, value, relock=False):
    """
    Set a numeric attribute to a value.

    Optionally unlocks and re-locks the plugs.

    :param plug: Node.Attr to set.
    :param value: The new value to set.
    :param relock: If the plug was already locked, should we set the new
                   value, then re-lock afterward?

    :return: True or False, depending if the value was set or not.
    :rtype: bool
    """
    node = plug.partition('.')[0]
    is_referenced = node_is_referenced(node)
    locked = maya.cmds.getAttr(plug, lock=True)
    if is_referenced is True and locked is True:
        msg = 'Cannot set attr %r, it is locked and the node is referenced.'
        LOG.warning(msg, plug)
        return False
    if is_referenced is False:
        # Make sure the plug is unlocked.
        maya.cmds.setAttr(plug, lock=False)
    maya.cmds.setAttr(plug, value)
    if is_referenced is False and relock is True:
        maya.cmds.setAttr(plug, lock=locked)
    return True


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


def get_node_parents(node):
    """
    Get all the parents above the given node.

    :param node: Valid Maya DAG node path.
    :type node: str

    :returns: The parent nodes of node, in order from node upwards.
    :rtype: [str, ..]
    """
    assert isinstance(node, pycompat.TEXT_TYPE)
    parent_nodes = []
    parents = maya.cmds.listRelatives(node, parent=True, fullPath=True) or []
    parent_nodes += parents
    while len(parents) > 0:
        parents = maya.cmds.listRelatives(parents, parent=True, fullPath=True) or []
        parent_nodes += parents
    return parent_nodes


def sort_nodes_by_depth(nodes, reverse=False):
    """
    Sort nodes by depth, shallow nodes first.

    :param nodes: List of Maya DAG node paths.
    :type nodes: [str, ..]

    :param reverse: Reverses the list of nodes.
    :type reverse: bool

    :returns: List of sorted nodes.
    :rtype: [str, ..]
    """
    assert isinstance(nodes, (list, set))

    def func(a):
        return a.count('|')

    nodes = sorted(nodes, key=func, reverse=reverse)
    return nodes


def get_as_selection_list_apione(paths):
    """
    Get a Maya API selection list with the given valid Maya node paths.

    :param paths: List of Maya node paths.
    :type paths: list of str

    :return: MSelectionList with valid nodes added to list.
    :rtype: OpenMaya1.MSelectionList
    """
    assert isinstance(paths, list) or isinstance(paths, tuple)
    sel_list = OpenMaya1.MSelectionList()
    for node in paths:
        try:
            sel_list.add(node)
        except RuntimeError:
            pass
    return sel_list


def get_as_dag_path_apione(node_str):
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
    dagPath = OpenMaya1.MDagPath()
    sel_list.getDagPath(0, dagPath)
    return dagPath


def get_as_object_apione(node_str):
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
    obj = OpenMaya1.MObject()
    try:
        selList.getDependNode(0, obj)
    except RuntimeError:
        obj = None
    return obj


def get_as_plug_apione(node_attr):
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
            plug = OpenMaya1.MPlug()
            sel.getPlug(0, plug)
        except RuntimeError:
            plug = None
    return plug


def get_dag_path_shapes_below_apione(dag):
    """
    Get the MDagPath shape nodes under the given MDagPath.

    .. note::
        The given 'dag' MDagPath is not modified during this function.

    :param dag: The DAG path to get shape nodes from.
    :type dag: maya.OpenMaya.MDagPath

    :return:
    :rtype: [maya.OpenMaya.MDagPath, ..]
    """
    assert isinstance(dag, OpenMaya1.MDagPath)
    dag_copy = OpenMaya1.MDagPath(dag)
    dag_shp_list = []

    # Get number of shape nodes.
    shp_num_script_util = OpenMaya1.MScriptUtil()
    uint_ptr = shp_num_script_util.asUintPtr()
    shp_num_script_util.setUint(uint_ptr, 0)
    dag_copy.numberOfShapesDirectlyBelow(uint_ptr)
    shp_num = shp_num_script_util.getUint(uint_ptr)

    for i in range(shp_num):
        dag_copy.extendToShapeDirectlyBelow(i)
        dag_shp = OpenMaya1.MDagPath(dag_copy)
        dag_shp_list.append(dag_shp)
        dag_copy.pop()
    return dag_shp_list


def get_as_selection_list_apitwo(node_names):
    assert isinstance(node_names, list) or isinstance(node_names, tuple)
    sel_list = OpenMaya2.MSelectionList()
    try:
        for node in node_names:
            sel_list.add(node)
    except RuntimeError:
        return sel_list
    return sel_list


def get_as_object_apitwo(node_name):
    sel_list = get_as_selection_list_apitwo([node_name])
    if not sel_list:
        return None
    mobject = None
    if sel_list.length() > 0:
        mobject = sel_list.getDependNode(0)
    return mobject


def get_as_dag_path_apitwo(node_name):
    sel_list = get_as_selection_list_apitwo([node_name])
    if not sel_list:
        return None
    dag_path = None
    if sel_list.length() > 0:
        dag_path = sel_list.getDagPath(0)
    return dag_path


def get_as_plug_apitwo(node_attr):
    sel = get_as_selection_list_apitwo([node_attr])
    plug = None
    if sel.length() > 0:
        plug = sel.getPlug(0)
    return plug


def get_as_selection_list(*args, **kwargs):
    msg = 'Use mmSolver.utils.node.get_as_selection_list_apione instead.'
    warnings.warn(msg, DeprecationWarning)
    return get_as_selection_list_apione(*args, **kwargs)


def get_as_dag_path(*args, **kwargs):
    msg = 'Use mmSolver.utils.node.get_as_dag_path_apione instead.'
    warnings.warn(msg, DeprecationWarning)
    return get_as_dag_path_apione(*args, **kwargs)


def get_as_object(*args, **kwargs):
    msg = 'Use mmSolver.utils.node.get_as_object_apione instead.'
    warnings.warn(msg, DeprecationWarning)
    return get_as_object_apione(*args, **kwargs)


def get_as_plug(*args, **kwargs):
    msg = 'Use mmSolver.utils.node.get_as_plug_apione instead.'
    warnings.warn(msg, DeprecationWarning)
    return get_as_plug_apione(*args, **kwargs)


def get_camera_above_node(node):
    """
    Get the first camera transform and shape node above the node.

    :param node: The node name to check above for a camera.
    :type node: str or unicode

    :return: Tuple of camera transform and shape nodes, or (None, None)
    :rtype: (str, str) or (None, None)
    """
    # TODO: This function may be called many times, we should look into
    # caching some of this computation.
    cam_tfm = None
    cam_shp = None
    dag = get_as_dag_path(node)
    got_it = False
    while dag.length() != 0:
        if dag.apiType() == OpenMaya1.MFn.kTransform:
            num_children = dag.childCount()
            if num_children > 0:
                for i in range(num_children):
                    child_obj = dag.child(i)
                    if child_obj.apiType() == OpenMaya1.MFn.kCamera:
                        cam_tfm = dag.fullPathName()
                        dag.push(child_obj)
                        cam_shp = dag.fullPathName()
                        got_it = True
                        break
        if got_it is True:
            break
        dag.pop(1)
    return cam_tfm, cam_shp


def get_all_parent_nodes(node):
    """
    Get the parent nodes above the given node.

    :param node: The node name to get the parents of.
    :type node: str

    :return: List of parent nodes, in order of deepest to shallowest.
             Nodes unparented into world will have empty lists returned.
    :rtype: [str, ..]
    """
    nodes = []
    dag = get_as_dag_path(node)
    while dag.length() != 0:
        dag.pop(1)
        node_name = dag.fullPathName()
        nodes.append(node_name)
    return nodes


def get_node_wire_colour_rgb(node):
    """
    Get the current wireframe colour (0.0 to 1.0) of the node.

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
    Change the wireframe colour (0.0 to 1.0) of the node.

    The 'node' is assumed to a DAG node (capable of having a wireframe
    colour set).

    :param node: Maya DAG node path.
    :type node: str

    :param rgb: Colour as R, G, B; Or None to reset to default colour.
    :type rgb: tuple

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


def get_node_draw_override_enabled(node):
    """
    Get the current draw override enabled value of the node.

    The 'node' is assumed to a DAG node (capable of having an draw override).

    :param node: Maya node path to get value from.
    :type node: str

    :rtype: bool
    """
    assert maya.cmds.objExists(node) is True
    node_attr = '{0}.{1}'.format(node, 'overrideEnabled')
    value = maya.cmds.getAttr(node_attr)
    return value


def set_node_draw_override_enabled(node, value):
    """
    Set the draw override enabled value of a node.

    The 'node' is assumed to a DAG node (capable of having an draw override).

    :param node: Maya DAG node path.
    :type node: str

    :type value: bool

    :rtype: None
    """
    assert isinstance(value, bool)
    node_attr = '{0}.{1}'.format(node, 'overrideEnabled')
    maya.cmds.setAttr(node_attr, value)
    return


def get_node_draw_override_colour_rgba(node):
    """
    Get the draw current override colour (0.0 to 1.0) of the node.

    The 'node' is assumed to a DAG node (capable of having a override
    colour).

    :param node: Maya node path to get override colour from.
    :type node: str

    :returns: Tuple of red, green, blue and alpha.
    :rtype: (float, float, float, float)
    """
    assert maya.cmds.objExists(node) is True

    node_attr_rgb = '{0}.{1}'.format(node, 'overrideColorRGB')
    rgb = maya.cmds.getAttr(node_attr_rgb)[0]

    alpha = 1.0
    if maya.cmds.about(apiVersion=True) >= 20230000:
        node_attr_alpha = '{0}.{1}'.format(node, 'overrideColorA')
        alpha = maya.cmds.getAttr(node_attr_alpha)
    return (rgb[0], rgb[1], rgb[2], alpha)


def set_node_draw_override_colour_rgba(node, rgba):
    """
    Change the draw override colour (0.0 to 1.0) of the node.

    The 'node' is assumed to a DAG node (capable of having a colour set).

    :param node: Maya DAG node path.
    :type node: str

    :param rgba: Colour as R, G, B, A; Or None to reset to default colour.
    :type rgba: tuple

    :rtype: None
    """
    assert rgba is None or isinstance(rgba, (tuple, list))
    if not isinstance(rgba, (tuple, list)):
        # Reset to default override colour.
        rgba = (0.0, 0.0, 0.0, 1.0)
    assert len(rgba) == 4

    node_attr_enable = '{0}.{1}'.format(node, 'overrideRGBColors')
    node_attr_r = '{0}.{1}'.format(node, 'overrideColorR')
    node_attr_g = '{0}.{1}'.format(node, 'overrideColorG')
    node_attr_b = '{0}.{1}'.format(node, 'overrideColorB')
    maya.cmds.setAttr(node_attr_enable, True)
    maya.cmds.setAttr(node_attr_r, rgba[0])
    maya.cmds.setAttr(node_attr_g, rgba[1])
    maya.cmds.setAttr(node_attr_b, rgba[2])

    if maya.cmds.about(apiVersion=True) >= 20230000:
        node_attr_a = '{0}.{1}'.format(node, 'overrideColorA')
        maya.cmds.setAttr(node_attr_a, rgba[3])
    return


def attribute_exists(attr, node):
    """
    Check if an attribute exists on the given node.

    This is a Python equivalent of the MEL command 'attributeExists'.

    :param attr: Attribute name to check for existence.
    :type attr: str

    :param node: The node to look for the attribute.
    :type node: str

    :returns: A boolean, if the attribute exists or not.
    :rtype: bool
    """
    if (attr == '') or (node == ''):
        return False

    # See if the node exists!
    if not maya.cmds.objExists(node):
        return False

    # First check to see if the attribute matches the short names
    attrs = maya.cmds.listAttr(node, shortNames=True)
    if attr in attrs:
        return True

    # Now check against the long names
    attrs = maya.cmds.listAttr(node)
    if attr in attrs:
        return True

    # Finally check if there are any alias
    # attributes with that name.
    alias_attrs = maya.cmds.aliasAttr(node, query=True)
    if alias_attrs is not None:
        if attr in alias_attrs:
            return True
    return False
