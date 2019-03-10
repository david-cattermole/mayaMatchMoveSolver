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
    """
    Loads all plug-ins required for Solver tool.

    :raises: mmapi.SolverNotAvailable
    """
    mmapi.load_plugin()
    name = 'mmSolver'
    if name not in dir(maya.cmds):
        raise mmapi.SolverNotAvailable
    return


def _get_channel_box_ui_name():
    """
    Get the internal channel box Maya UI path.

    .. note::
        When the Maya GUI has not launched yet, this function
        returns None.

    :return: UI path str.
    :rtype: str or None
    """
    cmd = (
        'global string $gChannelBoxName;'
        'string $temp = $gChannelBoxName;'
    )
    return maya.mel.eval(cmd)


def set_scene_selection(nodes):
    """
    The Maya scene selection is replaced with `nodes`.

    :param nodes: Nodes to set as selected.
    :type nodes: list of str

    :return: Nothing.
    """
    maya.cmds.select(nodes, replace=True)
    return


def get_current_frame():
    """
    Get the current Maya frame number.

    :return: Frame number
    :rtype: int
    """
    time = maya.cmds.currentTime(query=True)
    return int(time)


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
        mkr = mmapi.Marker(node=node)
        marker_list.append(mkr)
    return marker_list


def get_selected_maya_attributes():
    """
    Get the currently selected attributes from the Channel Box.

    This function uses Maya ChannelBox logic to get the objects, which
    is based on the selection, but may be doing more complex logic.

    :return: List of Attribute objects for all nodes in the Channel Box.
    :rtype: list of Attribute
    """
    name = _get_channel_box_ui_name()

    # Main Nodes and Attribute
    main_nodes = maya.cmds.channelBox(
        name, query=True,
        mainObjectList=True
    ) or []
    main_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedMainAttributes=True
    ) or []

    # Shape Nodes and Attribute
    shape_nodes = maya.cmds.channelBox(
        name, query=True,
        shapeObjectList=True
    ) or []
    shape_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedShapeAttributes=True
    ) or []

    # History Nodes and Attribute
    history_nodes = maya.cmds.channelBox(
        name, query=True,
        historyObjectList=True
    ) or []
    history_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedHistoryAttributes=True
    ) or []

    # Output Nodes and Attribute
    output_nodes = maya.cmds.channelBox(
        name, query=True,
        outputObjectList=True
    ) or []
    output_attrs = maya.cmds.channelBox(
        name, query=True,
        selectedOutputAttributes=True
    ) or []

    attr_list = []
    nodes_and_attrs = [
        (main_nodes, main_attrs),
        (shape_nodes, shape_attrs),
        (history_nodes, history_attrs),
        (output_nodes, output_attrs),
    ]
    for nodes, attrs in nodes_and_attrs:
        for n in nodes:
            for a in attrs:
                possible_attrs = maya.cmds.listAttr(n, shortNames=False) or []
                possible_attrs += maya.cmds.listAttr(n, shortNames=True) or []
                if a not in possible_attrs:
                    continue
                attr = mmapi.Attribute(node=n, attr=a)
                if attr.get_name() is not None:
                    attr_list.append(attr)
    return attr_list
