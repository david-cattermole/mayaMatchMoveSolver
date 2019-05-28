"""
This tool renames selected markers and bundles (and the connected nodes).
"""
import maya.cmds

import mmSolver.logger
import mmSolver.tools.markerbundlerename.constant as const
import mmSolver.tools.markerbundlerename.lib as lib
import mmSolver.tools.selection.filternodes as filternodes

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
    mkr_name = lib.prompt_for_new_node_name(title, message, text)
    if mkr_name is None:
        # If user clicks cancel on prompt window it returns None.
        LOG.warning('User canceled rename.')
        return

    number_format = const.NUMBER_FORMAT
    mkr_suffix = const.MARKER_SUFFIX
    bnd_suffix = const.BUNDLE_SUFFIX
    if mkr_name == text:
        bnd_name = const.BUNDLE_NAME
    else:
        bnd_name = mkr_name
    nodes = lib.rename_markers_and_bundles(
        sel_mkr_nodes, sel_bnd_nodes,
        mkr_name, bnd_name,
        number_format,
        mkr_suffix, bnd_suffix
    )
    maya.cmds.select(nodes, replace=True)
    return
