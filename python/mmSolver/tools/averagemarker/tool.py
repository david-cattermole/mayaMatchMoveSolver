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
This tool averages markers position from selected markers.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.averagemarker.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Averages marker position from selected markers.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    selected_markers = filternodes.get_marker_nodes(selection)
    if len(selected_markers) < 2:
        LOG.warning('Please select more than 1 marker')
        return

    mkr_selection = selected_markers[0]
    mkr = mmapi.Marker(node=mkr_selection)
    # getting camera from the selected marker
    cam_from_mkr = mkr.get_camera()
    mkr_name = mmapi.get_marker_name('avgMarker1')
    new_mkr = mmapi.Marker().create_node(cam=cam_from_mkr,
                                         name=mkr_name)

    new_mkr_node = new_mkr.get_node()
    bnd_name = mmapi.get_bundle_name('avgBundle1')
    new_bnd = mmapi.Bundle().create_node(name=bnd_name)
    # connecting bundle to the marker
    new_mkr.set_bundle(new_bnd)

    # getting first frame and last frame from the selected markers
    start_frame, end_frame = lib.__get_markers_start_end_frames(
                                                    selected_markers)

    # Running average from selected markers for giving frame range
    lib.__set_average_marker_position(selected_markers,
                                      start_frame,
                                      end_frame,
                                      new_mkr_node)

    maya.cmds.select(new_mkr_node)
    # dgdirty for Channel box value update
    maya.cmds.dgdirty(new_mkr_node)
    return None
