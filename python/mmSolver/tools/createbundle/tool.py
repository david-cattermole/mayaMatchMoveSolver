"""
The Create Bundle tool.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filter_nodes
import mmSolver.tools.linkmarkerbundle.lib as linkmarkerbundle_lib


LOG = mmSolver.logger.get_logger()


def create_bundle():
    """
    Create a new Bundle, attached to the selected Marker (if a Marker
    is selected)
    """
    sel = maya.cmds.ls(sl=True, long=True)
    mkr_nodes = filter_nodes.get_marker_nodes(sel)

    bnd_name = mmapi.get_bundle_name('bundle1')
    bnd = mmapi.Bundle().create_node(
        name=bnd_name
    )

    bnd_node = bnd.get_node()
    for mkr_node in mkr_nodes:
        linkmarkerbundle_lib.link_marker_bundle(
            mkr_node,
            bnd_node
        )

    maya.cmds.select(bnd.get_node(), replace=True)
    return
