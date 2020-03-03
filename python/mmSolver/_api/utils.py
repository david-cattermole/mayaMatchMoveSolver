# Copyright (C) 2018, 2019 David Cattermole.
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
Utility functions for Maya API.

NOTE: Maya OpenMaya API 1.0 is used and returned from functions in
this module.

"""

import warnings

import maya.cmds

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.node as node_utils
import mmSolver._api.constant as const


LOG = mmSolver.logger.get_logger()
MM_SOLVER_IS_RUNNING = False
MM_SOLVER_USER_INTERRUPT = False


def load_plugin():
    """
    Load the mmSolver plugin.

    Raises a RuntimeError exception if a plug-in cannot be loaded.

    :return: None
    """
    msg = 'Could not load plug-in %r!'
    for name in const.PLUGIN_NAMES:
        loaded = maya.cmds.pluginInfo(name, query=True, loaded=True)
        if loaded is True:
            continue
        try:
            maya.cmds.loadPlugin(name, quiet=True)
        except RuntimeError as e:
            LOG.error(msg, name)
            raise e
    return


def get_object_type(node):
    """
    The canonical function to interpret a node as an MM Solver object type.

    Possible object type values are:

    - OBJECT_TYPE_MARKER
    - OBJECT_TYPE_BUNDLE
    - OBJECT_TYPE_ATTRIBUTE
    - OBJECT_TYPE_CAMERA
    - OBJECT_TYPE_LENS
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

    elif node_type.startswith('mmLensModel'):
        object_type = const.OBJECT_TYPE_LENS

    elif node_type == 'mmMarkerGroupTransform':
        object_type = const.OBJECT_TYPE_MARKER_GROUP

    elif ((node_type == 'objectSet')
          and ('solver_list' in attrs)):
        object_type = const.OBJECT_TYPE_COLLECTION

    return object_type


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
    dag = node_utils.get_as_dag_path(node)
    while dag.length() != 0:
        name = dag.fullPathName()
        if maya.cmds.nodeType(name) == 'mmMarkerGroupTransform':
            mkr_grp_node = name
            break
        dag.pop(1)
    return mkr_grp_node


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
    msg = 'Use `mmSolver.utils.configmaya` module'
    warnings.warn(msg, DeprecationWarning)
    value = configmaya.get_node_option_structure(
        node_name,
        attr_name
    )
    return value


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
    msg = 'Use `mmSolver.utils.configmaya` module'
    warnings.warn(msg, DeprecationWarning)
    configmaya.set_node_option_structure(
        node_name, attr_name, data,
        add_attr=True)
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
    msg = 'Use `mmSolver.utils.configmaya` module'
    warnings.warn(msg, DeprecationWarning)
    value = configmaya.get_node_option(node_name, attr_name)
    return value


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
    msg = 'Use `mmSolver.utils.configmaya` module'
    warnings.warn(msg, DeprecationWarning)
    configmaya.set_node_option(node_name, attr_name, data)
    return
