"""
Common tools for manipulating selection, specific to mmSolver.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes
import mmSolver.tools.selection.convert as convert_selection


LOG = mmSolver.logger.get_logger()


def swap_between_selected_markers_and_bundles():
    """
    Toggles the selection of Markers and Bundles.

    If a marker is selected, the attached bundle will be selected and
    vice versa.
    """
    sel = maya.cmds.ls(sl=True, long=True) or []
    if len(sel) == 0:
        LOG.warning('Select a node.')
        return

    node_filtered = filter_nodes.get_nodes(sel)
    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])
    new_sel = []

    if num_marker >= num_bundle:
        bnd_nodes = convert_selection.get_bundles_from_markers(node_filtered['marker'])
        new_sel += bnd_nodes
        new_sel += node_filtered['camera']
        new_sel += node_filtered['collection']
        new_sel += node_filtered['other']
    else:
        mkr_nodes = convert_selection.get_markers_from_bundles(node_filtered['bundle'])
        new_sel += mkr_nodes
        new_sel += node_filtered['camera']
        new_sel += node_filtered['collection']
        new_sel += node_filtered['other']

    maya.cmds.select(new_sel, replace=True)
    return


def select_both_markers_and_bundles():
    """
    Get the connected Markers and bundles, and select them.
    """
    sel = maya.cmds.ls(sl=True, long=True) or []
    if len(sel) == 0:
        LOG.warning('Select a node.')
        return

    node_filtered = filter_nodes.get_nodes(sel)
    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])

    mkr_nodes = []
    bnd_nodes = []
    if num_marker >= num_bundle:
        nodes = node_filtered['marker']
        bnd_nodes = convert_selection.get_bundles_from_markers(nodes)
        mkr_nodes = convert_selection.get_markers_from_bundles(bnd_nodes)
    else:
        nodes = node_filtered['bundle']
        mkr_nodes = convert_selection.get_markers_from_bundles(nodes)
        bnd_nodes = convert_selection.get_bundles_from_markers(mkr_nodes)

    new_sel = []
    new_sel += mkr_nodes
    new_sel += bnd_nodes
    new_sel += node_filtered['camera']
    new_sel += node_filtered['collection']
    new_sel += node_filtered['other']

    maya.cmds.select(new_sel, replace=True)
    return
