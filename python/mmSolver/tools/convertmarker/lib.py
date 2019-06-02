# Copyright (C) 2019 David Cattermole.
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
The 'Convert to Marker' library functions.
"""

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.tools.loadmarker.lib.interface as loadmkr_interface
import mmSolver.utils.reproject as reproject_utils

LOG = mmSolver.logger.get_logger()


def convert_nodes_to_marker_data_list(cam_tfm, cam_shp,
                                      nodes,
                                      start_frame, end_frame):
    # Create nodes and objects for loop.
    node_pairs = []
    reproj_nodes = []
    mkr_data_list = []
    for node in nodes:
        reproj = reproject_utils.create_reprojection_on_camera(cam_tfm, cam_shp)
        reproject_utils.connect_transform_to_reprojection(node, reproj)
        reproj_nodes.append(reproj)

        mkr_data = loadmkr_interface.MarkerData()
        mkr_data.set_name(node)
        mkr_data_list.append(mkr_data)

        node_pairs.append((node, reproj, mkr_data))

    # Query Screen-space coordinates across time for all nodes
    cur_time = maya.cmds.currentTime(query=True)
    for f in xrange(start_frame, end_frame + 1):
        maya.cmds.currentTime(f, edit=True, update=True)
        for node, reproj, mkr_data in node_pairs:
            node_attr = reproj + '.outNormCoord'
            mkr_u = maya.cmds.getAttr(node_attr + 'X')
            mkr_v = maya.cmds.getAttr(node_attr + 'Y')
            mkr_enable = True
            mkr_weight = 1.0

            mkr_data.weight.set_value(f, mkr_weight)
            mkr_data.enable.set_value(f, mkr_enable)
            mkr_data.x.set_value(f, mkr_u)
            mkr_data.y.set_value(f, mkr_v)

    if len(reproj_nodes) > 0:
        maya.cmds.delete(reproj_nodes)

    maya.cmds.currentTime(cur_time, edit=True, update=True)
    return mkr_data_list