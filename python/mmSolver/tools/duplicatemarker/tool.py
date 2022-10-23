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
This tool duplicates markers from selected markers.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.tools.duplicatemarker.lib as lib
import mmSolver.tools.duplicatemarker.constant as const

LOG = mmSolver.logger.get_logger()


def main():
    """
    Main function runs duplicate marker on all selected markers.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = mmapi.filter_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('Please select markers')
        return

    mkr_selection = selected_markers[0]
    mkr = mmapi.Marker(node=mkr_selection)
    # getting camera from the selected marker
    cam_from_mkr = mkr.get_camera()

    new_mkr_nodes = []
    for marker in selected_markers:
        # Get Marker's name
        mkr = mmapi.Marker(node=marker)
        # old_mkr_node is expected to be a long name.
        old_mkr_node = mkr.get_node()
        if old_mkr_node is None:
            LOG.warning('Invalid Marker, skipping duplicate.')
            continue
        mkr_name = old_mkr_node.rpartition('|')[-1]
        mkr_name = mkr_name[0].upper() + mkr_name[1:]
        mkr_name = 'dup' + mkr_name

        # Get Bundles's name
        bnd_name = 'dupBundle1'
        bnd = mkr.get_bundle()
        if bnd is None:
            pass
        else:
            bnd_node = bnd.get_node()
            bnd_name = bnd_node.rpartition('|')[-1]
            bnd_name = bnd_name[0].upper() + bnd_name[1:]
            bnd_name = 'dup' + bnd_name

        # get attrs lock state
        lock_value = lib.__get_lock_state(marker, const.MKR_ATTRS)

        mkr_name = mmapi.get_new_marker_name(mkr_name)
        new_mkr = mmapi.Marker().create_node(cam=cam_from_mkr, name=mkr_name)
        new_mkr_node = new_mkr.get_node()
        bnd_name = mmapi.get_new_bundle_name(bnd_name)
        new_bnd = mmapi.Bundle().create_node(name=bnd_name)
        # connecting bundle to the marker
        new_mkr.set_bundle(new_bnd)

        # running duplicate
        lib.__copy_key_frames(marker, new_mkr_node)

        # set lock state on newly created markers
        lib.__set_lock_state(marker, new_mkr_node, const.MKR_ATTRS, lock_value)
        new_mkr_nodes.append(new_mkr_node)

    if len(new_mkr_nodes) > 0:
        maya.cmds.select(new_mkr_nodes, replace=True)
    else:
        # Restore the original selection.
        maya.cmds.select(selection, replace=True)
    return
