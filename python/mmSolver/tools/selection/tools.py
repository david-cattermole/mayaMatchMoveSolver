
import maya.cmds

import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes
import mmSolver.tools.selection.convert as convert_selection


def swap_between_markers_and_bundles():
    sel = maya.cmds.ls(sl=True, long=True)
    print 'swap_between_markers_and_bundles sel:', sel

    node_filtered = filter_nodes.get_nodes(sel)
    print 'swap_between_markers_and_bundles filtered:', node_filtered
    new_sel = []

    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])
    if num_marker >= num_bundle:
        print 'swap_between_markers_and_bundles mkr_nodes:', node_filtered['marker']
        bnd_nodes = convert_selection.get_bundles_from_markers(node_filtered['marker'])
        print 'swap_between_markers_and_bundles bnd_nodes:', bnd_nodes
        new_sel += bnd_nodes
        new_sel += node_filtered['camera']
        new_sel += node_filtered['collection']
        new_sel += node_filtered['other']
    else:
        print 'swap_between_markers_and_bundles bnd_nodes:', node_filtered['bundle']
        mkr_nodes = convert_selection.get_markers_from_bundles(node_filtered['bundle'])
        print 'swap_between_markers_and_bundles mkr_nodes:', mkr_nodes
        new_sel += mkr_nodes
        new_sel += node_filtered['camera']
        new_sel += node_filtered['collection']
        new_sel += node_filtered['other']

    print 'swap_between_markers_and_bundles new_sel:', new_sel
    maya.cmds.select(new_sel, replace=True)
    return