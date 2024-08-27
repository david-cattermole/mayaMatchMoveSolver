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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.tools.createcamera.lib as createcamera_lib
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def create_camera():
    cam = createcamera_lib.create_camera()
    cam_shp = cam.get_shape_node()
    maya.cmds.select(cam_shp, replace=True)
    return cam


def camera_lens_distortion_enabled(camera_shape_node):
    assert camera_shape_node is not None
    cam = mmapi.Camera(shape=camera_shape_node)
    return cam.get_lens_enable() is True


def toggle_camera_lens_distortion_enabled(camera_shape_node):
    assert camera_shape_node is not None
    cam = mmapi.Camera(shape=camera_shape_node)
    enable = cam.get_lens_enable()
    if enable is None:
        LOG.warn('Cannot toggle camera lens distortion.')
        return
    cam.set_lens_enable(not enable)
    return
