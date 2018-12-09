"""
The 'Link / Unlink Marker Bundles' tool.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes


LOG = mmSolver.logger.get_logger()


def link_marker_bundle():
    """
    Select a marker node, and a bundle node, run to link both nodes.
    :return:
    """
    raise NotImplementedError
    # TODO: Get marker and bundle nodes.
    bundle_name = 'the_bundle_node_name_here'
    marker_name = 'the_marker_node_name_here'
    bnd = mmapi.Bundle(name=bundle_name)
    mkr = mmapi.Marker(name=marker_name)
    mkr.set_bundle(bnd)
    return


def unlink_marker_bundle():
    """
    All selected markers are disconnected from their bundle.

    :return:
    """
    raise NotImplementedError
    marker_name = 'the_marker_node_name_here'
    mkr = mmapi.Marker(name=marker_name)
    mkr.set_bundle(None)
    return

