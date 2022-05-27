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

import mmSolver.utils.camera as camera_utils

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.createimageplane.lib as createimageplane_lib
import mmSolver.tools.createimageplane.tool as createimageplane_tool
import mmSolver.tools.cameracontextmenu.constant as const


LOG = mmSolver.logger.get_logger()


def create_image_plane(camera_shape_node):
    assert camera_shape_node is not None
    cam = mmapi.Camera(shape=camera_shape_node)
    tfm, shp = createimageplane_lib.create_image_plane_on_camera(cam)

    image_seq = createimageplane_tool.prompt_user_for_image_sequence()
    if image_seq:
        createimageplane_lib.set_image_sequence(tfm, image_seq)
    return tfm, shp


def get_image_plane_type_name_label(image_plane_node):
    node_type = maya.cmds.nodeType(image_plane_node)
    if node_type in const.MM_IMAGE_PLANE_NODE_TYPES:
        label = const.IMAGE_PLANE_TYPE_NAME_MM_SOLVER_LABEL
    else:
        label = const.IMAGE_PLANE_TYPE_NAME_MAYA_NATIVE_LABEL
    return label


def get_camera_image_planes(camera_shape_node):
    cam_tfm, cam_shp = camera_utils.get_camera(camera_shape_node)
    native_image_plane_shps = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)

    mmapi.load_plugin()
    mm_image_plane_nodes = maya.cmds.listRelatives(
        cam_tfm,
        children=True,
        shapes=False,
        type='mmImagePlaneTransform'
    ) or []

    nodes = sorted(mm_image_plane_nodes + native_image_plane_shps)
    return nodes
