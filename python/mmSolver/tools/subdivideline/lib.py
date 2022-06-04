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
Functions for sub-dividing a line with more markers.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi

DEFAULT_MARKER_NAME = 'marker1'
LOG = mmSolver.logger.get_logger()


def _create_new_line_markers(mkr_grp):
    mkr_name_a = mmapi.get_new_marker_name(DEFAULT_MARKER_NAME)
    mkr_a = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_a)
    mkr_name_b = mmapi.get_new_marker_name(DEFAULT_MARKER_NAME)
    mkr_b = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_b)

    mkr_node_a = mkr_a.get_node()
    mkr_node_b = mkr_b.get_node()
    maya.cmds.setAttr(mkr_node_a + '.tx', -0.25)
    maya.cmds.setAttr(mkr_node_b + '.tx', 0.25)
    maya.cmds.setAttr(mkr_node_a + '.ty', -0.15)
    maya.cmds.setAttr(mkr_node_b + '.ty', 0.15)
    return mkr_a, mkr_b


def _create_new_marker_pair(mkr_grp, line_tfm, mkr_start, mkr_end):
    mkr_new_name = mmapi.get_new_marker_name(DEFAULT_MARKER_NAME)
    mkr_new = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_new_name)

    mkr_node_a = mkr_start.get_node()
    mkr_node_b = mkr_new.get_node()
    mkr_node_c = mkr_end.get_node()

    tx_b = maya.cmds.getAttr(mkr_node_a + '.tx')
    tx_b += maya.cmds.getAttr(mkr_node_c + '.tx')
    tx_b = tx_b * 0.5

    ty_b = maya.cmds.getAttr(mkr_node_a + '.ty')
    ty_b += maya.cmds.getAttr(mkr_node_c + '.ty')
    ty_b = ty_b * 0.5

    maya.cmds.setAttr(mkr_node_b + '.tx', tx_b)
    maya.cmds.setAttr(mkr_node_b + '.ty', ty_b)
    maya.cmds.parent(mkr_node_b, line_tfm, relative=True)
    return mkr_new


def _create_n_new_markers(mkr_grp, line_tfm, mkr_list, current_all_mkr_list):
    new_mkr_list = []
    new_all_mkr_node_list = [x.get_node() for x in current_all_mkr_list]
    new_all_mkr_list = list(current_all_mkr_list)

    mkr_list_start = mkr_list
    mkr_list_end = mkr_list[1:]
    mkr_pairs = list(zip(mkr_list_start, mkr_list_end))
    for mkr_start, mkr_end in mkr_pairs:
        mkr_new = _create_new_marker_pair(mkr_grp, line_tfm, mkr_start, mkr_end)

        mkr_index = new_all_mkr_node_list.index(mkr_start.get_node())
        mkr_next_index = mkr_index + 1
        new_all_mkr_list.insert(mkr_next_index, mkr_new)
        new_all_mkr_node_list.insert(mkr_next_index, mkr_new.get_node())

        new_mkr_list.append(mkr_new)

    return new_all_mkr_list, new_mkr_list


def subdivide_line(line, mkr_list):
    """
    Subdivides the line, with the given marker list.

    The line segments between each marker in 'mkr_list' will be
    subdivided.

    :param line: The line to subdivide.
    :type line: mmapi.Line

    :param mkr_list: List of marker to subdivide between. Each pair of
        markers represents a 'line segment' that will have a new Marker
        added.
    :type mkr_list: [mmapi.Marker, ..]

    :rtype: ([mmapi.Marker, ..], [mmapi.Marker, ..])
    :returns: Two lists of markers, first list is all the markers that
        are part of the new line, and the second list are the newly
        created markers.
    """
    num_mkrs = len(mkr_list)

    all_mkr_list = []
    new_mkr_list = []
    line_tfm = line.get_node()
    mkr_grp = line.get_marker_group()
    if num_mkrs == 0:
        mkr_a, mkr_b = _create_new_line_markers(mkr_grp)
        all_mkr_list = [mkr_a, mkr_b]
        new_mkr_list = all_mkr_list
    else:
        current_all_mkr_list = line.get_marker_list()
        all_mkr_list, new_mkr_list = _create_n_new_markers(
            mkr_grp, line_tfm, mkr_list, current_all_mkr_list
        )

    return all_mkr_list, new_mkr_list
