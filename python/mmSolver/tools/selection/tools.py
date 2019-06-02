# Copyright (C) 2018 David Cattermole.
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
Common tools for manipulating selection, specific to mmSolver.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def swap_between_selected_markers_and_bundles():
    """
    Toggles the selection of Markers and Bundles.

    If a marker is selected, the attached bundle will be selected and
    vice versa.
    """
    sel = maya.cmds.ls(sl=True, long=True) or []
    if len(sel) == 0:
        LOG.warning('Select a node.')
        return

    node_filtered = mmapi.filter_nodes_into_categories(sel)
    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])
    new_sel = []

    if num_marker >= num_bundle:
        bnd_nodes = mmapi.get_bundle_nodes_from_marker_nodes(
            node_filtered['marker']
        )
        new_sel = bnd_nodes
    else:
        mkr_nodes = mmapi.get_marker_nodes_from_bundle_nodes(
            node_filtered['bundle']
        )
        new_sel = mkr_nodes

    maya.cmds.select(new_sel, replace=True)
    return


def select_both_markers_and_bundles():
    """
    Get the connected Markers and bundles, and select them.
    """
    sel = maya.cmds.ls(sl=True, long=True) or []
    if len(sel) == 0:
        LOG.warning('Select a node.')
        return

    node_filtered = mmapi.filter_nodes_into_categories(sel)
    num_marker = len(node_filtered['marker'])
    num_bundle = len(node_filtered['bundle'])

    mkr_nodes = []
    bnd_nodes = []
    if num_marker >= num_bundle:
        nodes = node_filtered['marker']
        bnd_nodes = mmapi.get_bundle_nodes_from_marker_nodes(nodes)
        mkr_nodes = mmapi.get_marker_nodes_from_bundle_nodes(bnd_nodes)
    else:
        nodes = node_filtered['bundle']
        mkr_nodes = mmapi.get_marker_nodes_from_bundle_nodes(nodes)
        bnd_nodes = mmapi.get_bundle_nodes_from_marker_nodes(mkr_nodes)

    new_sel = mkr_nodes + bnd_nodes
    maya.cmds.select(new_sel, replace=True)
    return
