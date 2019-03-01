"""
This tool duplicates markers from selected markers.
"""
import maya.cmds
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.logger
import mmSolver.tools.createmarker.tool
import mmSolver.api as mmapi
import mmSolver.tools.duplicatemarker.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Main function runs duplicate marker on all selected markers
    :return: None
    """

    selection = maya.cmds.ls(sl=True)
    selected_markers = filternodes.get_marker_nodes(selection)

    if not selected_markers:
        LOG.warning('Please select markers')
        return

    mkr_selection = selected_markers[0]
    mkr = mmapi.Marker(name=mkr_selection)
    # getting camera from the selected marker
    cam_from_mkr = mkr.get_camera()

    new_mkr_nodes = []
    for marker in selected_markers:
        mkr_name = mmapi.get_marker_name('marker1', suffix='_DUP')
        new_mkr = mmapi.Marker().create_node(cam=cam_from_mkr,
                                             name=mkr_name)

        new_mkr_node = new_mkr.get_node()
        bnd_name = mmapi.get_bundle_name('bundle1', suffix='_DUP')
        new_bnd = mmapi.Bundle().create_node(name=bnd_name)
        # connecting bundle to the marker
        new_mkr.set_bundle(new_bnd)

        # running duplicate
        lib.__copy_key_frames(marker, new_mkr_node)
        new_mkr_nodes.append(new_mkr_node)

    maya.cmds.select(new_mkr_nodes)
    return
