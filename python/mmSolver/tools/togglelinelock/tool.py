# Copyright (C) 2022 David Cattermole.
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
This tool toggles selected line lock state
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.togglelinelock.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggles selected line lock state.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_marker_nodes = mmapi.filter_marker_nodes(selection)
    selected_line_nodes = mmapi.filter_line_nodes(selection)
    if len(selected_line_nodes) == 0 and len(selected_marker_nodes) == 0:
        LOG.warning("Please select lines or line markers to (un)lock.")
        return

    line_nodes = []
    if len(selected_line_nodes) > 0:
        line_nodes = selected_line_nodes
    elif len(selected_marker_nodes) > 0:
        for node in selected_marker_nodes:
            line_node = mmapi.get_line_above_node(node)
            line_nodes.append(line_node)
    line_nodes = sorted(set(line_nodes))
    line_nodes = [x for x in line_nodes if x]

    lib.lines_lock_toggle(line_nodes)
    return
