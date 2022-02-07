# Copyright (C) 2022 David Cattermole.
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
Subdivide the number of markers in selected line.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.subdivideline.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Subdivide the selected line (or line connected to selected markers).
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_marker_nodes = mmapi.filter_marker_nodes(selection)
    selected_line_nodes = mmapi.filter_line_nodes(selection)
    if len(selected_line_nodes) == 0 and len(selected_marker_nodes) == 0:
        LOG.warning("Please select lines or line markers to subdivide.")
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

    new_mkr_list = []
    for line_node in line_nodes:
        line = mmapi.Line(node=line_node)
        new_mkr_list += lib.subdivide_line(line)

    new_mkr_nodes = [x.get_node() for x in new_mkr_list]
    if len(new_mkr_nodes) > 0:
        maya.cmds.select(new_mkr_nodes, replace=True)
    else:
        maya.cmds.select(selection, replace=True)
    return
