"""
This tool renames selected markers and bundles (and the connected nodes).
"""
import maya.cmds

import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.markerbundlerename.lib as lib
import mmSolver.tools.markerbundlerename.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Renames selected markers and bundles (and the connected nodes).
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    sel_mkr_nodes = filternodes.get_marker_nodes(selection)
    sel_bnd_nodes = filternodes.get_bundle_nodes(selection)
    if len(sel_mkr_nodes) == 0 and len(sel_bnd_nodes) == 0:
        LOG.warning('Please select markers or bundles to rename.')
        return

    title = const.TITLE
    message = const.MESSAGE
    text = const.MARKER_NAME
    marker_name = lib.prompt_for_new_node_name(title, message, text)
    if marker_name is None:
        # If user clicks cancel on prompt window it returns None.
        LOG.warning('User canceled rename.')
        return

    name_format = const.NAME_FORMAT
    mkr_suffix = const.MARKER_SUFFIX
    bnd_suffix = const.BUNDLE_SUFFIX
    if marker_name == text:
        bundle_name = const.BUNDLE_NAME
    else:
        bundle_name = marker_name
    nodes = lib.rename_markers_and_bundles(
        sel_mkr_nodes, sel_bnd_nodes,
        marker_name, bundle_name, name_format,
        mkr_suffix, bnd_suffix
    )
    maya.cmds.select(nodes, replace=True)
    return
