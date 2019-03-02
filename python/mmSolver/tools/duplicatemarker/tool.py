"""
This tool duplicates markers from selected markers.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.duplicatemarker.lib as lib
import mmSolver.tools.duplicatemarker.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Main function runs duplicate marker on all selected markers.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = filternodes.get_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('Please select markers')
        return

    mkr_selection = selected_markers[0]
    mkr = mmapi.Marker(name=mkr_selection)
    # getting camera from the selected marker
    cam_from_mkr = mkr.get_camera()

    # For lock state
    mkr_attrs = const.MKR_ATTRS

    new_mkr_nodes = []
    for marker in selected_markers:
        # Get Marker's name
        mkr = mmapi.Marker(name=marker)
        old_mkr_node = mkr.get_node()
        if old_mkr_node is None:
            LOG.warning('Invalid Marker, skipping duplicate.')
            continue
        mkr_name = old_mkr_node.rpartition('|')
        mkr_name = 'dup' + mkr_name.capitalize()

        # Get Bundles's name
        bnd_name = 'dupBundle1'
        bnd = mkr.get_bundle()
        if bnd is None:
            pass
        else:
            bnd_node = bnd.get_node()
            bnd_name = bnd_node.rpartition('|')
            bnd_name = 'dup' + bnd_name.capitalize()

        # get attrs lock state
        lock_value = lib.__get_lock_state(marker, mkr_attrs)

        mkr_name = mmapi.get_marker_name(mkr_name)
        new_mkr = mmapi.Marker().create_node(cam=cam_from_mkr,
                                             name=mkr_name)
        new_mkr_node = new_mkr.get_node()
        bnd_name = mmapi.get_bundle_name(bnd_name)
        new_bnd = mmapi.Bundle().create_node(name=bnd_name)
        # connecting bundle to the marker
        new_mkr.set_bundle(new_bnd)

        # running duplicate
        lib.__copy_key_frames(marker, new_mkr_node)

        # set lock state on newly created markers
        lib.__set_lock_state(new_mkr_node, mkr_attrs, lock_value)
        new_mkr_nodes.append(new_mkr_node)

    if len(new_mkr_nodes) > 0:
        maya.cmds.select(new_mkr_nodes, replace=True)
    else:
        # Restore the original selection.
        maya.cmds.select(selection, replace=True)
    return
