"""
This tool toggles selected bundle lock state
"""

import maya.cmds
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.togglebundlelock.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggles selected bundle lock state.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_bundles = filternodes.get_bundle_nodes(selection)
    if len(selected_bundles) == 0:
        LOG.warning("Please select bundle's to lock or unlock")
        return

    attrs = const.ATTRS
    bundle_attrs = []
    for bundle in selected_bundles:
        for attr in attrs:
            bundle_attrs.append('%s.%s' % (bundle, attr))

    is_locked = False
    for attr in bundle_attrs:
        if maya.cmds.getAttr(attr, lock=True):
            is_locked = True

    for attr in bundle_attrs:
        lock_value = not is_locked
        maya.cmds.setAttr(attr, lock=lock_value)
    return
