import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes
from mmSolver.tools.solver.lib.maya_utils \
    import prompt_for_new_node_name
import mmSolver.tools.markerbundlerenamer.constant as const

LOG = mmSolver.logger.get_logger()


def main():
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

    marker_name = prompt_for_new_node_name(title, message, text)
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
        new_bnd_name = '%s%02d' % (bundle_name,
                                   total_mkrs
                                   - number) + "_" + bnd_suffix
        mkr = mmapi.Marker(node=marker)
        mkr_node = mkr.get_node()
        maya.cmds.rename(mkr_node, new_mkr_name)

        bnd = mkr.get_bundle()
        if not bnd:
            LOG.warning('%s cannot find bundle connected' %
                        new_mkr_name)
            continue
        bnd_node = bnd.get_node()
        maya.cmds.rename(bnd_node, new_bnd_name)
    return
