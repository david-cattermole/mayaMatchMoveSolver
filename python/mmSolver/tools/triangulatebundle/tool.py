"""
Triangulate a 3D Bundle from a 2D Marker.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.triangulatebundle.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Triangulate Bundle using camera and Marker.

    Usage:

    1) Select markers or bundles (or both).

    2) Run tool.

    3) Bundle is triangulated in TX, TY and TZ.
    """
    # Get Markers and Bundles
    sel = maya.cmds.ls(selection=True, long=True) or []
    filter_nodes = filternodes.get_nodes(sel)
    mkr_nodes = filter_nodes.get('marker', [])
    bnd_nodes = filter_nodes.get('bundle', [])
    if len(mkr_nodes) == 0 and len(bnd_nodes) == 0:
        msg = 'Please select at least one marker / bundle!'
        LOG.warning(msg)
        return

    # Get Bundles from Markers
    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(node=mkr_node)
        bnd = mkr.get_bundle()
        bnd_node = bnd.get_node()
        if bnd_node not in bnd_nodes:
            bnd_nodes.append(bnd_node)
    bnd_list = [mmapi.Bundle(node=node) for node in bnd_nodes]

    # Triangulate
    for bnd in bnd_list:
        lib.triangulate_bundle(bnd)

    # Select all bundle nodes.
    if len(bnd_nodes) > 0:
        maya.cmds.select(bnd_nodes, replace=True)
    else:
        msg = 'No Bundle nodes found, see Script Editor for details.'
        LOG.warning(msg)
    return
