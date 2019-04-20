"""
This tool toggles selected marker lock state
"""

import maya.cmds
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.togglemarkerlock.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggles selected marker lock state.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = filternodes.get_marker_nodes(selection)
    if len(selected_markers) == 0:
        LOG.warning("Please select marker's to lock or unlock")
        return

    attrs = const.ATTRS
    marker_attrs = []
    for marker in selected_markers:
        for attr in attrs:
            marker_attrs.append('%s.%s' % (marker, attr))

    is_locked = False
    for attr in marker_attrs:
        if maya.cmds.getAttr(attr, lock=True):
            is_locked = True

    for attr in marker_attrs:
        lock_value = not is_locked
        maya.cmds.setAttr(attr, lock=lock_value)
    return
