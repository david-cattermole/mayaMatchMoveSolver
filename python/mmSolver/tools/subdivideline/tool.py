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

This allows adding more detail in areas that are needed without
adding line segments where they are not needed.

The tool works on the current Marker or Line selection. If a line is
selected the line is uniformly subdivided. If markers are selected,
the line segments around the markers are subdivided.
"""

import collections

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.subdivideline.lib as lib

LOG = mmSolver.logger.get_logger()


def _expand_markers_to_line_segments(line, mkr_node_list):
    mkr_node_list = [mmapi.Marker(node=x).get_node() for x in mkr_node_list]

    all_mkr_list = line.get_marker_list()
    all_mkr_node_list = [x.get_node() for x in all_mkr_list]
    all_mkr_index_list = [all_mkr_node_list.index(x) for x in all_mkr_node_list]

    mkr_node_to_index = {}
    for mkr_node, mkr_index in zip(all_mkr_node_list, all_mkr_index_list):
        mkr_node_to_index[mkr_node] = mkr_index

    mkr_index_set = set()
    for mkr_node in mkr_node_list:
        mkr_index = mkr_node_to_index.get(mkr_node)
        if mkr_index is None:
            continue
        mkr_index_min = max(0, mkr_index - 1)
        mkr_index_max = min(mkr_index + 1, len(all_mkr_list) - 1)
        mkr_index_set.add(mkr_index_min)
        mkr_index_set.add(mkr_index)
        mkr_index_set.add(mkr_index_max)

    mkr_list = [all_mkr_list[mkr_index] for mkr_index in sorted(mkr_index_set)]

    return mkr_list


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

    line_to_mkr_list_map = collections.defaultdict(list)
    line_nodes = []
    if len(selected_line_nodes) > 0:
        line_nodes = selected_line_nodes
    elif len(selected_marker_nodes) > 0:
        for node in selected_marker_nodes:
            line_node = mmapi.get_line_above_node(node)
            line_to_mkr_list_map[line_node].append(node)
            line_nodes.append(line_node)
    line_nodes = sorted(set(line_nodes))
    line_nodes = [x for x in line_nodes if x]

    new_mkr_list = []
    for line_node in line_nodes:
        line = mmapi.Line(node=line_node)

        mkr_list = line.get_marker_list()
        mkr_node_list = line_to_mkr_list_map[line_node]

        no_markers = len(mkr_node_list) == 0
        all_markers = len(mkr_node_list) == len(mkr_list)
        if not no_markers or not all_markers:
            mkr_list = _expand_markers_to_line_segments(line, mkr_node_list)

        all_mkrs, new_mkrs = lib.subdivide_line(line, mkr_list)
        new_mkr_list += new_mkrs

        # The full list of markers for the line, keeping the
        # non-subdivided markers as they are. The order of the list is
        # important, as this is the order of the individual line
        # segments.
        line.set_marker_list(all_mkrs)

    new_mkr_nodes = [x.get_node() for x in new_mkr_list]
    if len(new_mkr_nodes) > 0:
        new_mkr_nodes = list(sorted(set(new_mkr_nodes)))
        maya.cmds.select(new_mkr_nodes, replace=True)
    else:
        maya.cmds.select(selection, replace=True)
    return
