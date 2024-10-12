# Copyright (C) 2020, 2022 David Cattermole.
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
import mmSolver.api as mmapi
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.constant as const_utils
import mmSolver.utils.imageseq as imageseq_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.createimageplane._lib.constant as lib_const
import mmSolver.tools.createimageplane._lib.mmimageplane as lib_mmimageplane
import mmSolver.tools.createimageplane._lib.mmimageplane_v1 as lib_mmimageplane_v1
import mmSolver.tools.createimageplane._lib.nativeimageplane as lib_nativeimageplane
import mmSolver.tools.createimageplane._lib.polyplane as lib_polyplane
import mmSolver.tools.createimageplane._lib.shader as lib_shader
import mmSolver.tools.createimageplane._lib.utilities as lib_utils

LOG = mmSolver.logger.get_logger()


def create_image_plane_on_camera(cam, name=None, version=None):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    if version is None:
        version = lib_const.MM_IMAGE_PLANE_VERSION_TWO
    if name is None:
        name = 'mmImagePlane1'
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST

    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    mm_ip_tfm = lib_mmimageplane.create_transform_node(
        name, cam_tfm, cam_shp, version=version
    )

    poly_plane_name = name + 'MeshShape'
    poly_plane_network = lib_polyplane.create_poly_plane(
        poly_plane_name, mm_ip_tfm, cam_shp
    )

    shader_network = None
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        name_shade = name + 'Shader'
        shader_network = lib_shader.create_network(name_shade, mm_ip_tfm)

    name_img_shp = name + 'Shape'
    mm_ip_shp = lib_mmimageplane.create_shape_node(
        name_img_shp,
        mm_ip_tfm,
        cam_shp,
        poly_plane_network,
        shader_network,
        version=version,
    )

    # Image sequence.
    image_sequence_path = lib_utils.get_default_image_path()
    set_image_sequence(mm_ip_tfm, image_sequence_path)
    return mm_ip_tfm, mm_ip_shp


def convert_image_planes_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)

    # Find image plane currently on the camera.
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_planes = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)

    ip_node_pairs = []
    for native_ip_shp in image_planes:
        # Convert Maya image plane into a polygon image plane.
        name = 'mmImagePlane1'
        mm_ip_tfm = lib_mmimageplane.create_transform_node(name, cam_tfm, cam_shp)

        poly_plane_name = name + 'MeshShape'
        poly_plane_network = lib_polyplane.create_poly_plane(
            poly_plane_name, mm_ip_tfm, cam_shp
        )

        lib_nativeimageplane.copy_depth_value(mm_ip_tfm, native_ip_shp)

        name_img_shp = name + 'Shape'
        mm_ip_shp = lib_mmimageplane.create_shape_node(
            name_img_shp,
            mm_ip_tfm,
            cam_shp,
            poly_plane_network,
        )

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(native_ip_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(native_ip_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(native_ip_shp + '.visibility', False)

        ip_node_pairs.append((mm_ip_tfm, mm_ip_shp))

    return ip_node_pairs


def _guess_color_space(file_path):
    file_extension = file_path.lower().split('.')[-1]
    if file_extension in lib_const.SCENE_LINEAR_FILE_EXTENSIONS:
        color_space = maya.cmds.mmColorIO(roleSceneLinear=True)
    elif file_extension in lib_const.SRGB_FILE_EXTENSIONS:
        color_space = maya.cmds.mmColorIO(roleColorPicking=True)
    else:
        color_space = maya.cmds.mmColorIO(guessColorSpaceFromFile=file_path)

    if not color_space:
        color_space = maya.cmds.mmColorIO(roleData=True)
    if not color_space:
        color_space = maya.cmds.mmColorIO(roleDefault=True)

    exists = maya.cmds.mmColorIO(colorSpaceExists=color_space)
    if exists is False:
        color_space = None

    return color_space


def _set_image_sequence_v1(mm_image_plane_node, image_sequence_path, attr_name=None):
    if attr_name is None:
        attr_name = lib_const.DEFAULT_IMAGE_SEQUENCE_ATTR_NAME
    version = lib_const.MM_IMAGE_PLANE_VERSION_ONE

    tfm, shp = lib_mmimageplane.get_image_plane_node_pair(
        mm_image_plane_node, version=version
    )
    if tfm is None or shp is None:
        LOG.warn('mmImagePlane transform/shape could not be found.')

    file_node = lib_mmimageplane_v1.get_file_node(tfm)
    if file_node is None:
        LOG.warn('mmImagePlane shader file node is invalid.')

    if shp is not None:
        lib_mmimageplane.set_image_sequence(
            shp, image_sequence_path, attr_name, version=version
        )
    if file_node is not None:
        lib_shader.set_file_path(file_node, image_sequence_path)
    return


def _set_locked_string_attr(node_attr, value):
    maya.cmds.setAttr(node_attr, lock=False)
    maya.cmds.setAttr(node_attr, value, type='string')
    maya.cmds.setAttr(node_attr, lock=True)
    return


def _set_image_sequence_v2(mm_image_plane_node, image_sequence_path, attr_name=None):
    if attr_name is None:
        attr_name = lib_const.DEFAULT_IMAGE_SEQUENCE_ATTR_NAME
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert attr_name in lib_const.VALID_INPUT_IMAGE_SEQUENCE_ATTR_NAMES
    version = lib_const.MM_IMAGE_PLANE_VERSION_TWO

    tfm, shp = lib_mmimageplane.get_image_plane_node_pair(
        mm_image_plane_node, version=version
    )
    if tfm is None or shp is None:
        LOG.warn('mmImagePlane transform/shape could not be found.')

    if shp is not None:
        lib_mmimageplane.set_image_sequence(
            shp, image_sequence_path, attr_name, version=version
        )
        lib_mmimageplane.set_image_sequence(
            shp,
            image_sequence_path,
            lib_const.SHADER_FILE_PATH_ATTR_NAME,
            version=version,
        )

        format_style = const_utils.IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME
        (
            file_pattern,
            _,
            _,
            _,
            _,
        ) = imageseq_utils.expand_image_sequence_path(image_sequence_path, format_style)
        first_frame_file_seq = file_pattern.replace('\\', '/')

        input_color_space = _guess_color_space(first_frame_file_seq)
        output_color_space = maya.cmds.mmColorIO(roleSceneLinear=True)

        node_attr = shp + '.' + lib_const.INPUT_COLOR_SPACE_ATTR_NAME
        _set_locked_string_attr(node_attr, input_color_space)

        node_attr = shp + '.' + lib_const.OUTPUT_COLOR_SPACE_ATTR_NAME
        _set_locked_string_attr(node_attr, output_color_space)

    return


def set_image_sequence(
    mm_image_plane_node, image_sequence_path, attr_name=None, version=None
):
    if version is None:
        version = lib_const.MM_IMAGE_PLANE_VERSION_TWO
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        return _set_image_sequence_v1(
            mm_image_plane_node, image_sequence_path, attr_name=attr_name
        )
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        return _set_image_sequence_v2(
            mm_image_plane_node, image_sequence_path, attr_name=attr_name
        )
