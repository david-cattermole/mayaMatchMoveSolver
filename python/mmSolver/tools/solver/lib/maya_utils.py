"""
General Maya utility functions
"""

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes


LOG = mmSolver.logger.get_logger()


def ensure_plugin_loaded():
    mmapi.load_plugin()
    name = 'mmSolver'
    if name not in dir(maya.cmds):
        raise mmapi.SolverNotAvailable
    return


def _get_channel_box_ui_name():
    cmd = (
        'global string $gChannelBoxName;'
        'string $temp = $gChannelBoxName;'
    )
    return maya.mel.eval(cmd)


def _get_selected_attributes():
    name = _get_channel_box_ui_name()
    attrs = maya.cmds.channelBox(
        name, query=True,
        selectedMainAttributes=True
    ) or []
    return attrs


def set_scene_selection(nodes):
    maya.cmds.select(nodes, replace=True)
    return


def get_current_frame():
    time = maya.cmds.currentTime(query=True)
    return int(time)


def get_timeline_range_inner():
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    return int(s), int(e)


def get_timeline_range_outer():
    s = maya.cmds.playbackOptions(query=True, animationStartTime=True)
    e = maya.cmds.playbackOptions(query=True, animationEndTime=True)
    return int(s), int(e)


def prompt_for_new_node_name(title, message, text):
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
    """
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = filter_nodes.get_nodes(nodes)
    marker_nodes = list(node_categories['marker'])

    camera_nodes = list(node_categories['camera'])
    for node in camera_nodes:
        tfm_node = None
        if maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
            tfm_node = cam.get_transform_node()
        below_nodes = maya.cmds.ls(tfm_node, dag=True, long=True)
        marker_nodes += filter_nodes.get_marker_nodes(below_nodes)

    marker_group_nodes = list(node_categories['markergroup'])
    for node in marker_group_nodes:
        below_nodes = maya.cmds.ls(node, dag=True, long=True)
        marker_nodes += filter_nodes.get_marker_nodes(below_nodes)

    # Convert nodes into Marker objects.
    marker_nodes = list(set(marker_nodes))
    marker_list = []
    for node in marker_nodes:
        mkr = mmapi.Marker(name=node)
        marker_list.append(mkr)
    return marker_list


def get_selected_maya_attributes():
    attrs = _get_selected_attributes()
    nodes = maya.cmds.ls(sl=True, long=True)
    attr_list = []
    for n in nodes:
        for a in attrs:
            attr = mmapi.Attribute(node=n, attr=a)
            if attr.get_name() is not None:
                attr_list.append(attr)
    return attr_list