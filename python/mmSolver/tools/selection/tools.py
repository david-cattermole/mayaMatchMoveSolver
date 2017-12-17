
import maya.cmds

import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes
import mmSolver.tools.selection.convert as convert_selection


def swap_between_selected_markers_and_bundles():
    sel = maya.cmds.ls(sl=True, long=True)
    if len(sel) == 0:
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
    sel = maya.cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        return

    node_filtered = filter_nodes.get_nodes(sel)
    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])

    mkr_nodes = []
    bnd_nodes = []
    if num_marker >= num_bundle:
        bnd_nodes = convert_selection.get_bundles_from_markers(node_filtered['marker'])
        mkr_nodes = convert_selection.get_markers_from_bundles(bnd_nodes)
    else:
        mkr_nodes = convert_selection.get_markers_from_bundles(node_filtered['bundle'])
        bnd_nodes = convert_selection.get_bundles_from_markers(mkr_nodes)

    new_sel = []
    new_sel += mkr_nodes
    new_sel += bnd_nodes
    new_sel += node_filtered['camera']
    new_sel += node_filtered['collection']
    new_sel += node_filtered['other']

    maya.cmds.select(new_sel, replace=True)
    return
