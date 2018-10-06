"""
Solver tool.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes

def get_associted_markers_from_selection():
    """
    Given a selection of nodes, find the associated markers.
    :return: list of Marker objects.
    """
    nodes = maya.cmds.ls(long=True, selection=True) or []
    filtered_nodes = filternodes.get_nodes(nodes)

    result = list(filtered_nodes['marker'])

    # TODO: For each camera, get the connected markers.
    # filtered_nodes['camera']

    return result


def gui():
    """
    Open the Window.
    :return:
    """
    pass