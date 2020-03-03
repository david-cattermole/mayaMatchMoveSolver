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
import mmSolver.api as mmapi
import mmSolver.tools.togglemarkerlock.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggles selected marker lock state.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_marker_nodes = mmapi.filter_marker_nodes(selection)
    if len(selected_marker_nodes) == 0:
        LOG.warning("Please select marker's to lock or unlock")
        return

    lib.markers_lock_toggle(selected_marker_nodes)
    return
