"""
This tool renames selected markers and connected bundles.
"""
import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.markerbundlerename.lib as lib
import mmSolver.tools.markerbundlerename.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Renames selected markers and connected bundles.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []

    selected_markers = filternodes.get_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('Please select markers')
        return

    title = const.TITLE
    message = const.MESSAGE
    text = const.MARKER_NAME
    marker_name = lib.prompt_for_new_node_name(title, message, text)
    # if user clicks cancel on prompt window it returns "None"
    if not marker_name:
        return

    mkr_suffix = const.MARKER_SUFFIX
    bnd_suffix = const.BUNDLE_SUFFIX
    if marker_name == text:
        bundle_name = const.BUNDLE_NAME
    else:
        bundle_name = marker_name

    total_mkrs = len(selected_markers)
    for number, marker in enumerate(reversed(selected_markers)):
        num_str = '%02d' % (total_mkrs - number)
        new_mkr_name = mmapi.get_marker_name(
            num_str,
            prefix=marker_name,
            suffix=mkr_suffix
        )

        mkr = mmapi.Marker(node=marker)
        mkr_node = mkr.get_node()
        maya.cmds.rename(mkr_node, new_mkr_name)

        bnd = mkr.get_bundle()
        # checking if marker is connected to bundle
        if not bnd:
            msg = 'Cannot find bundle connected to Marker; mkr_node=%r'
            LOG.warning(msg, mkr_node)
            continue

        new_bnd_name = mmapi.get_bundle_name(
            num_str,
            prefix=bundle_name,
            suffix=bnd_suffix
        )
        bnd_node = bnd.get_node()
        maya.cmds.rename(bnd_node, new_bnd_name)
    return
