"""
This tool toggles selected bundle lock state
"""

import maya.cmds
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.togglebundlelock.constant as const

LOG = mmSolver.logger.get_logger()


def toggle_bundle_lock():
    """
    Toggles selected bundle lock state.
    :return: None
    """

    selection = maya.cmds.ls(sl=True, long=True) or []
    if not selection:
        LOG.warning('Please select bundle\'s to lock or unlock')
        return

    selected_bundles = filternodes.get_bundle_nodes(selection)

    if not selected_bundles:
        LOG.warning('Please select bundle\'s to lock or unlock')
        return

    attrs = const.ATTRS
    bundle_attrs = []
    for bundle in selected_bundles:
        for attr in attrs:
            bundle_attrs.append('%s.%s' % (bundle, attr))

    is_locked = []
    for attr in bundle_attrs:
        if maya.cmds.getAttr(attr, lock=True):
            is_locked = True

    for attr in bundle_attrs:
        if is_locked:
            maya.cmds.setAttr(attr, lock=False)
        else:
            maya.cmds.setAttr(attr, lock=True)
    return

