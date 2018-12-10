"""
The 'Link / Unlink Marker Bundles' tool.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.linkmarkerbundle.lib as lib


LOG = mmSolver.logger.get_logger()


def link_marker_bundle():
    """
    Select a marker node, and a bundle node, run to link both nodes.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    mkr_nodes = filternodes.get_marker_nodes(sel)
    bnd_nodes = filternodes.get_bundle_nodes(sel)

    if len(mkr_nodes) != 1 and len(bnd_nodes) != 1:
        msg = 'Please select only one Marker and one Bundle.'
        LOG.warning(msg)
        return
    if len(mkr_nodes) != 1:
        msg = 'Please select only one Marker.'
        LOG.warning(msg)
    if len(bnd_nodes) != 1:
        msg = 'Please select only one Bundle.'
        LOG.warning(msg)
    if len(mkr_nodes) != 1 or len(bnd_nodes) != 1:
        return

    lib.link_marker_bundle(mkr_nodes[0], bnd_nodes[0])
    return


def unlink_marker_bundle():
    """
    All selected markers are disconnected from their bundle.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    mkr_nodes = filternodes.get_marker_nodes(sel)

    if len(mkr_nodes) == 1:
        msg = 'Please select one or more Markers.'
        LOG.warning(msg)
        return

    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(name=mkr_node)
        mkr.set_bundle(None)
    return
