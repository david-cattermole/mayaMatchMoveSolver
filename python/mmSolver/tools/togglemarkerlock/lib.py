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
import mmSolver.tools.togglemarkerlock.constant as const

LOG = mmSolver.logger.get_logger()


def get_marker_attrs(mkr_nodes):
    """
    Get the Marker attributes to lock/unlock.
    """
    attrs = const.ATTRS
    marker_attrs = []
    for marker in mkr_nodes:
        for attr in attrs:
            marker_attrs.append('%s.%s' % (marker, attr))
    return marker_attrs


def markers_lock_toggle(mkr_nodes):
    """
    Performs a toggle lock for the given Marker nodes.
    """
    marker_attrs = get_marker_attrs(mkr_nodes)

    # Determine the lock state to toggle.
    is_locked = False
    for attr in marker_attrs:
        if maya.cmds.getAttr(attr, lock=True):
            is_locked = True

    # Lock the Marker attributes.
    lock_value = not is_locked
    markers_lock_set(mkr_nodes, lock_value)
    return


def markers_lock_set(mkr_nodes, lock_value):
    """
    Set the lock value for the given Marker nodes.
    """
    marker_attrs = get_marker_attrs(mkr_nodes)

    # Lock the Marker attributes.
    for attr in marker_attrs:
        maya.cmds.setAttr(attr, lock=lock_value)
    return
