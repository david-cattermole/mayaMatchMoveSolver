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
    :return: None
    """
    selection = maya.cmds.ls(selection=True, long=True) or []

    selected_markers = filternodes.get_marker_nodes(selection)
    selected_markers.reverse()
    if not selected_markers:
        LOG.warning('Please select markers')
        return

    total_mkrs = len(selected_markers)
    title = const.TITLE
    message = const.MESSAGE
    text = const.MARKER_NAME

    marker_name = lib.prompt_for_new_node_name(title, message, text)

    # if user click cancel on prompt window it returns "None"
    if not marker_name:
        return

    mkr_suffix = const.MARKER_SUFFIX
    bnd_suffix = const.BUNDLE_SUFFIX

    if marker_name == text:
        bundle_name = const.BUNDLE_NAME
    else:
        bundle_name = marker_name

    for number, marker in enumerate(selected_markers):
        new_mkr_name = '%s%02d' % (marker_name,
                                   total_mkrs
                                   - number) + "_" + mkr_suffix
        mkr = mmapi.Marker(node=marker)
        mkr_node = mkr.get_node()
        maya.cmds.rename(mkr_node, new_mkr_name)

        bnd = mkr.get_bundle()
        # checking if marker is connected to bundle
        if not bnd:
            LOG.warning('Cannot find bundle connected to %s' %
                        new_mkr_name)
            continue

        new_bnd_name = '%s%02d' % (bundle_name,
                                   total_mkrs
                                   - number) + "_" + bnd_suffix
        bnd_node = bnd.get_node()
        maya.cmds.rename(bnd_node, new_bnd_name)
    return
