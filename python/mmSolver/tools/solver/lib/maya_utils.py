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
General Maya utility functions
"""

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.ui.channelboxutils as channelbox_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.camera as cam_utils
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def ensure_plugin_loaded():
    """
    Loads all plug-ins required for Solver tool.

    :raises: mmapi.SolverNotAvailable
    """
    mmapi.load_plugin()
    name = 'mmSolver'
    if name not in dir(maya.cmds):
        raise mmapi.SolverNotAvailable
    return


def get_scene_selection():
    """Get the currently selected nodes.

    Intended for selection store/restore.

    :return: List of full path node names.
    :rtype: list of str
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    return sel


def set_scene_selection(nodes):
    """
    The Maya scene selection is replaced with `nodes`.

    :param nodes: Nodes to set as selected.
    :type nodes: list of str

    :return: Nothing.
    """
    maya.cmds.select(nodes, replace=True)
    return


def add_scene_selection(nodes):
    """
    The Maya scene selection is appended with `nodes`.

    :param nodes: Nodes to set as selected.
    :type nodes: list of str

    :return: Nothing.
    """
    maya.cmds.select(nodes, add=True)
    return


def remove_scene_selection(nodes):
    """
    The Maya scene selection is removed with `nodes`.

    :param nodes: Nodes to set as selected.
    :type nodes: list of str

    :return: Nothing.
    """
    maya.cmds.select(nodes, deselect=True)
    return


def get_node_names_from_uuids(uuids):
    """Get the full DAG path for the given UUIDs.

    :param uuids: The UUIDs of Maya nodes.
    :type uuids: list of str

    :return: List of full path node names.
    :rtype: list of str or empty list
    """
    sel = maya.cmds.ls(uuids, long=True) or []
    return sel


def get_current_frame():
    """
    Get the current Maya frame number.

    :return: Frame number
    :rtype: int
    """
    time = maya.cmds.currentTime(query=True)
    return int(time)


def set_current_frame(value, update=None):
    """
    Get the current Maya frame number.

    :return: Frame number
    :rtype: int
    """
    assert isinstance(value, (float,) + pycompat.INT_TYPES)
    if isinstance(update, (bool,) + pycompat.INT_TYPES):
        maya.cmds.currentTime(value, update=update)
    else:
        maya.cmds.currentTime(value)
    return


def prompt_for_new_node_name(title, message, text):
    """
    Ask the user for a new node name.

    :param title: Dialog box window title.
    :type title: str

    :param message: Read-only text to show the user, for making a
                    decision.
    :type message: str

    :param text: The initial text to prompt the user as a starting
                 point.
    :type text: str

    :return: New node name, or None if user cancelled.
    :rtype: str or None
    """
    name = None
    result = maya.cmds.promptDialog(
        title=title,
        message=message,
        text=text,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
    )
    if result == 'OK':
        name = maya.cmds.promptDialog(query=True, text=True)
    return name


def get_markers_from_selection():
    """
    Given a selection of nodes, find the associated markers.

    :return: list of Marker objects.
    :rtype: [Marker, ..]
    """
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    marker_nodes = node_categories.get(mmapi.OBJECT_TYPE_MARKER, [])

    camera_nodes = node_categories.get(mmapi.OBJECT_TYPE_CAMERA, [])
    for node in camera_nodes:
        cam_tfm, cam_shp = cam_utils.get_camera(node)
        below_nodes = maya.cmds.ls(cam_tfm, dag=True, long=True)
        marker_nodes += mmapi.filter_marker_nodes(below_nodes)

    marker_group_nodes = list(node_categories[mmapi.OBJECT_TYPE_MARKER_GROUP])
    for node in marker_group_nodes:
        below_nodes = maya.cmds.ls(node, dag=True, long=True)
        marker_nodes += mmapi.filter_marker_nodes(below_nodes)

    # Convert nodes into Marker objects.
    marker_nodes = list(set(marker_nodes))
    mkr_list = [mmapi.Marker(node=x) for x in marker_nodes]
    return mkr_list


def get_lines_from_selection():
    """
    Given a selection of nodes, find the associated markers.

    :return: list of Marker objects.
    :rtype: [Marker, ..]
    """
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    line_nodes = node_categories.get(mmapi.OBJECT_TYPE_LINE, [])

    camera_nodes = node_categories.get(mmapi.OBJECT_TYPE_CAMERA, [])
    for node in camera_nodes:
        cam_tfm, cam_shp = cam_utils.get_camera(node)
        below_nodes = maya.cmds.ls(cam_tfm, dag=True, long=True)
        line_nodes += mmapi.filter_line_nodes(below_nodes)

    marker_group_nodes = list(node_categories[mmapi.OBJECT_TYPE_MARKER_GROUP])
    for node in marker_group_nodes:
        below_nodes = maya.cmds.ls(node, dag=True, long=True)
        line_nodes += mmapi.filter_line_nodes(below_nodes)

    # Convert nodes into Marker objects.
    line_nodes = list(set(line_nodes))
    line_list = [mmapi.Line(node=x) for x in line_nodes]
    return line_list


def get_selected_maya_attributes():
    """
    Get the currently selected attributes from the Channel Box.

    This function uses Maya ChannelBox logic to get the objects, which
    is based on the selection, but may be doing more complex logic.

    :return: List of Attribute objects for all nodes in the Channel Box.
    :rtype: list of Attribute
    """
    name = channelbox_utils.get_ui_name()

    # Main Nodes and Attribute
    main_nodes = maya.cmds.channelBox(name, query=True, mainObjectList=True) or []
    main_attrs = (
        maya.cmds.channelBox(name, query=True, selectedMainAttributes=True) or []
    )

    # Shape Nodes and Attribute
    shape_nodes = maya.cmds.channelBox(name, query=True, shapeObjectList=True) or []
    shape_attrs = (
        maya.cmds.channelBox(name, query=True, selectedShapeAttributes=True) or []
    )

    # History Nodes and Attribute
    history_nodes = maya.cmds.channelBox(name, query=True, historyObjectList=True) or []
    history_attrs = (
        maya.cmds.channelBox(name, query=True, selectedHistoryAttributes=True) or []
    )

    # Output Nodes and Attribute
    output_nodes = maya.cmds.channelBox(name, query=True, outputObjectList=True) or []
    output_attrs = (
        maya.cmds.channelBox(name, query=True, selectedOutputAttributes=True) or []
    )

    attr_list = []
    nodes_and_attrs = [
        (main_nodes, main_attrs),
        (shape_nodes, shape_attrs),
        (history_nodes, history_attrs),
        (output_nodes, output_attrs),
    ]
    for nodes, attrs in nodes_and_attrs:
        for n in nodes:
            possible_attrs = maya.cmds.listAttr(n, shortNames=False) or []
            possible_attrs += maya.cmds.listAttr(n, shortNames=True) or []
            for a in attrs:
                if a not in possible_attrs:
                    continue
                attr = mmapi.Attribute(node=n, attr=a)
                if attr.get_name() is not None:
                    attr_list.append(attr)
    return attr_list


def get_node_default_attributes(nodes):
    """
    Get the default attributes for solving on the given nodes.

    :param nodes: List of nodes to be considered.
    :type nodes: [str, ..]

    :returns: List of mmSolver API Attribute objects.
    :rtype: [Attribute, ..]
    """
    attr_list = []
    for node in nodes:
        node_type = maya.cmds.nodeType(node)
        obj_type = mmapi.get_object_type(node)
        attr_names = []
        if obj_type == mmapi.OBJECT_TYPE_BUNDLE:
            # Default bundle attributes.
            attr_names += [
                'translateX',
                'translateY',
                'translateZ',
            ]
        elif obj_type == mmapi.OBJECT_TYPE_CAMERA:
            # Camera default attributes, for both transform and
            # camera nodes.
            if node_type == 'transform':
                attr_names += [
                    'translateX',
                    'translateY',
                    'translateZ',
                    'rotateX',
                    'rotateY',
                    'rotateZ',
                ]
            elif node_type == 'camera':
                attr_names += [
                    'focalLength',
                ]
        else:
            # Fallback - get all logical attributes.
            attrs = (
                maya.cmds.listAttr(
                    node,
                    keyable=True,
                    settable=True,
                    scalar=True,
                    shortNames=False,
                )
                or []
            )
            attr_types = [
                'doubleLinear',
                'doubleAngle',
                'double',
                'float',
            ]
            attr_names += [
                attr
                for attr in attrs
                if maya.cmds.attributeQuery(attr, node=node, attributeType=True)
                in attr_types
            ]

        for attr_name in attr_names:
            attr_obj = mmapi.Attribute(node=node, attr=attr_name)
            if attr_obj.get_name() is not None:
                attr_list.append(attr_obj)
    return attr_list


def input_attributes_filter(attr_list):
    """
    Apply logic to remove any non-input attributes from the given list.

    :param attr_list: Attribute list to filter.
    :type attr_list: [Attribute, ..]

    :returns: List of attributes that are filtered.
    :rtype: [Attribute, ..]
    """
    result = []
    for attr_obj in attr_list:
        node = attr_obj.get_node()
        obj_type = mmapi.get_object_type(node)
        if obj_type in const.ATTR_INVALID_OBJECT_TYPES:
            continue
        result.append(attr_obj)
    return result
