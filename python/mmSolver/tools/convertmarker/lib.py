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

import itertools

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.tools.loadmarker.lib.interface as loadmkr_interface
import mmSolver.utils.reproject as reproject_utils

LOG = mmSolver.logger.get_logger()


def convert_nodes_to_marker_data_list(cam_tfm, cam_shp,
                                      nodes,
                                      start_frame, end_frame):
    cur_time = maya.cmds.currentTime(query=True)
    mkr_data_list = []
    frames = range(start_frame, end_frame + 1)
    for node in nodes:
        image_width = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture')
        image_height = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture')
        image_width *= 1000.0
        image_height *= 1000.0
        # BUG: If a camera has 'camera scale' attribute set other than
        # 1.0, the reprojected values will not be correct.
        values = maya.cmds.mmReprojection(
            node,
            time=frames,
            imageResolution=(image_width, image_height),
            camera=(cam_tfm, cam_shp),
            asNormalizedCoordinate=True)
        assert (len(frames) * 3) == len(values)

        mkr_data = loadmkr_interface.MarkerData()
        mkr_data.set_name(node)
        mkr_data.weight.set_value(start_frame, 1.0)

        iterator_u = itertools.islice(values, 0, len(values), 3)
        iterator_v = itertools.islice(values, 1, len(values), 3)
        for frame, mkr_u, mkr_v in zip(frames, iterator_u, iterator_v):
            mkr_data.enable.set_value(frame, True)
            # TODO: The values calculated are slightly wrong in Y (V
            # axis), this looks like an aspect ratio problem overall.
            mkr_data.x.set_value(frame, mkr_u)
            mkr_data.y.set_value(frame, mkr_v)
        mkr_data_list.append(mkr_data)

    maya.cmds.currentTime(cur_time, edit=True, update=True)
    return mkr_data_list
