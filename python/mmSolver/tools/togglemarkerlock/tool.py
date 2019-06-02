# Copyright (C) 2019 Anil Reddy.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
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
