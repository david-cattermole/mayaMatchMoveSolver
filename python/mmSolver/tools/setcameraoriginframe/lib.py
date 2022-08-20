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
Functions to offset a camera to the origin.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.solvercamerautils as solvercamerautils
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def set_camera_origin_frame(
    cam, bnd_list, scene_scale, origin_frame, start_frame, end_frame
):
    assert isinstance(cam, mmapi.Camera)

    bnd_nodes = [x.get_node() for x in bnd_list]
    bnd_nodes = [x for x in bnd_nodes if x]
    cam_tfm = cam.get_transform_node()

    solvercamerautils._set_camera_origin_frame(
        cam_tfm, bnd_nodes, origin_frame, start_frame, end_frame, scene_scale
    )
    return
