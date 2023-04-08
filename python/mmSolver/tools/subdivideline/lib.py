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
import mmSolver._api.line as line_api


LOG = mmSolver.logger.get_logger()


def _create_new_line_markers(mkr_grp, line_tfm):
    line_shp = maya.cmds.listRelatives(line_tfm, shapes=True)[0]
    mkr_a, bnd_a, mkr_b, bnd_b = line_api.create_default_markers(line_shp, mkr_grp)
    return mkr_a, mkr_b


def _create_new_marker_pair(mkr_grp, line_tfm, mkr_start, mkr_end):
    line_shp = maya.cmds.listRelatives(line_tfm, shapes=True)[0]
    mkr_new, bnd_new = line_api.create_new_line_marker(line_shp, mkr_grp)

    mkr_node_start = mkr_start.get_node()
    mkr_node_new = mkr_new.get_node()
    mkr_node_end = mkr_end.get_node()

    bnd_node_new = bnd_new.get_node()

    tx = maya.cmds.getAttr(mkr_node_start + '.tx')
    tx += maya.cmds.getAttr(mkr_node_end + '.tx')
    tx = tx * 0.5

    ty = maya.cmds.getAttr(mkr_node_start + '.ty')
    ty += maya.cmds.getAttr(mkr_node_end + '.ty')
    ty = ty * 0.5

    maya.cmds.setAttr(mkr_node_new + '.tx', tx)
    maya.cmds.setAttr(mkr_node_new + '.ty', ty)

    maya.cmds.parent(mkr_node_new, line_tfm, relative=True)
    maya.cmds.parent(bnd_node_new, line_tfm, relative=True)
    return mkr_new, bnd_new


def _create_n_new_markers(mkr_grp, line_tfm, mkr_list, current_all_mkr_list):
    new_mkr_list = []
    new_all_mkr_node_list = [x.get_node() for x in current_all_mkr_list]
    new_all_mkr_list = list(current_all_mkr_list)

    mkr_list_start = mkr_list
    mkr_list_end = mkr_list[1:]
    mkr_pairs = list(zip(mkr_list_start, mkr_list_end))
    for mkr_start, mkr_end in mkr_pairs:
        mkr_new, bnd_new = _create_new_marker_pair(
            mkr_grp, line_tfm, mkr_start, mkr_end
        )

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
        mkr_a, mkr_b = _create_new_line_markers(mkr_grp, line_tfm)
        all_mkr_list = [mkr_a, mkr_b]
        new_mkr_list = all_mkr_list
    else:
        current_all_mkr_list = line.get_marker_list()
        all_mkr_list, new_mkr_list = _create_n_new_markers(
            mkr_grp, line_tfm, mkr_list, current_all_mkr_list
        )

    return all_mkr_list, new_mkr_list
