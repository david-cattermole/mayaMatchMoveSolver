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
"""
Library functions for creating and modifying image planes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.createimageplane.constant as const
import mmSolver.tools.createimageplane._lib.constant as lib_const
import mmSolver.tools.createimageplane._lib.mmimageplane_v1 as lib_mmimageplane_v1
import mmSolver.tools.createimageplane._lib.mmimageplane_v2 as lib_mmimageplane_v2
import mmSolver.tools.createimageplane._lib.utilities as lib_utils
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def create_transform_node(name_tfm, cam_tfm, cam_shp, version=None):
    """
    Create a default polygon image plane under camera.
    """
    assert isinstance(name_tfm, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(cam_tfm)
    assert maya.cmds.objExists(cam_shp)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    tfm_node_type = lib_const.MM_IMAGE_PLANE_TRANSFORM

    mmapi.load_plugin()
    tfm = maya.cmds.createNode(tfm_node_type, name=name_tfm, parent=cam_tfm)

    # Create (dynamic) attributes.
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        lib_mmimageplane_v1.create_transform_attrs(tfm)
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        lib_mmimageplane_v2.create_transform_attrs(tfm)
    else:
        assert False

    # Image plane depth be far away, but still visible.
    far_clip_plane = maya.cmds.getAttr(cam_tfm + '.farClipPlane')
    maya.cmds.setAttr(tfm + '.depth', far_clip_plane * 0.9)

    # Connect camera attributes
    attrs = [
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'horizontalFilmOffset',
        'verticalFilmOffset',
    ]
    for attr in attrs:
        src = cam_shp + '.' + attr
        dst = tfm + '.' + attr
        if not maya.cmds.isConnected(src, dst):
            lib_utils.force_connect_attr(src, dst)

    return tfm


def create_shape_node(
    name_img_shp,
    tfm,
    cam_shp,
    poly_plane_node_network,
    shader_node_network,
    version=None,
):
    """
    Convert mesh to a mmImagePlaneShape.
    """
    assert isinstance(name_img_shp, pycompat.TEXT_TYPE)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    shp_node_type = lib_const.MM_IMAGE_PLANE_SHAPE_MAP[version]
    assert shp_node_type in lib_const.MM_IMAGE_PLANE_SHAPE_LIST
    assert maya.cmds.objExists(tfm)
    assert maya.cmds.objExists(cam_shp)

    img_plane_poly_shp = poly_plane_node_network.mesh_shape
    img_plane_poly_shp_original = poly_plane_node_network.mesh_shape_original
    poly_creator = poly_plane_node_network.plane_creator

    if shader_node_network is not None:
        shd_node = shader_node_network.shd_node
        file_node = shader_node_network.file_node
        color_gamma_node = shader_node_network.color_gamma_node
        alpha_channel_blend_node = shader_node_network.alpha_channel_blend_node
        image_load_invert_boolean_node = (
            shader_node_network.image_load_invert_boolean_node
        )
        alpha_channel_reverse_node = shader_node_network.alpha_channel_reverse_node

    mmapi.load_plugin()
    shp = maya.cmds.createNode(shp_node_type, name=name_img_shp, parent=tfm)

    maya.cmds.setAttr(shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleZ', channelBox=False)

    maya.cmds.setAttr(shp + '.cameraWidthInch', channelBox=False)
    maya.cmds.setAttr(shp + '.cameraHeightInch', channelBox=False)

    # Image plane hash will be used to stop updating the Viewport 2.0
    # shape when the lens distortion values stay the same.
    lens_eval_node = maya.cmds.createNode('mmLensEvaluate')
    if node_utils.attribute_exists('outLens', cam_shp):
        lib_utils.force_connect_attr(cam_shp + '.outLens', lens_eval_node + '.inLens')
    lib_utils.force_connect_attr(lens_eval_node + '.outHash', shp + '.lensHashCurrent')

    maya.cmds.reorder(shp, back=True)
    maya.cmds.reorder(img_plane_poly_shp_original, back=True)
    maya.cmds.reorder(img_plane_poly_shp, back=True)

    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        lib_mmimageplane_v1.create_image_plane_shape_attrs(shp)
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        lib_mmimageplane_v2.create_image_plane_shape_attrs(shp)
    else:
        assert False

    # Nodes to drive the image plane shape.
    lib_utils.force_connect_attr(img_plane_poly_shp + '.outMesh', shp + '.geometryNode')
    lib_utils.force_connect_attr(cam_shp + '.message', shp + '.cameraNode')
    if shader_node_network is not None:
        lib_utils.force_connect_attr(shd_node + '.outColor', shp + '.shaderNode')

    # The image drives the pixel aspect ratio of the image plane.
    lib_utils.force_connect_attr(shp + '.imagePixelAspect', tfm + '.pixelAspect')

    # Set the camera size of the image plane shape HUD.
    lib_utils.force_connect_attr(
        tfm + '.horizontalFilmAperture', shp + '.cameraWidthInch'
    )
    lib_utils.force_connect_attr(
        tfm + '.verticalFilmAperture', shp + '.cameraHeightInch'
    )

    if shader_node_network is not None:
        # Use the image alpha channel, or not
        lib_utils.force_connect_attr(
            shp + '.imageUseAlphaChannel', alpha_channel_blend_node + '.blender'
        )

        # Allow user to load the image, or not.
        lib_utils.force_connect_attr(
            shp + '.imageLoadEnable', image_load_invert_boolean_node + '.inputX'
        )

        # Color Exposure control.
        lib_utils.force_connect_attr(shp + '.exposure', file_node + '.exposure')

        # Color Gamma control.
        lib_utils.force_connect_attr(shp + '.gamma', color_gamma_node + '.gammaX')
        lib_utils.force_connect_attr(shp + '.gamma', color_gamma_node + '.gammaY')
        lib_utils.force_connect_attr(shp + '.gamma', color_gamma_node + '.gammaZ')

        # Control file color multiplier
        lib_utils.force_connect_attr(shp + '.colorGain', file_node + '.colorGain')

        # Control the alpha gain when 'imageUseAlphaChannel' is disabled.
        lib_utils.force_connect_attr(shp + '.alphaGain', file_node + '.alphaGain')
        lib_utils.force_connect_attr(
            shp + '.alphaGain', alpha_channel_reverse_node + '.inputX'
        )
        lib_utils.force_connect_attr(
            shp + '.alphaGain', alpha_channel_reverse_node + '.inputY'
        )
        lib_utils.force_connect_attr(
            shp + '.alphaGain', alpha_channel_reverse_node + '.inputZ'
        )

        # Default color for the image plane, when nothing is loaded.
        lib_utils.force_connect_attr(
            shp + '.imageDefaultColor', file_node + '.defaultColor'
        )

    # Mesh Resolution attr drives the plane sub-divisions.
    node_attr = shp + '.meshResolution'
    lib_utils.force_connect_attr(node_attr, poly_creator + '.subdivisionsWidth')
    lib_utils.force_connect_attr(node_attr, poly_creator + '.subdivisionsHeight')

    # Mesh doesn't need to be visible to drive the image plane shape
    # node drawing.
    maya.cmds.setAttr(img_plane_poly_shp + '.intermediateObject', 1)

    # Add extra message attributes for finding nodes during callbacks.
    if shader_node_network is not None:
        maya.cmds.addAttr(shp, longName='shaderFileNode', attributeType='message')
        lib_utils.force_connect_attr(file_node + '.message', shp + '.shaderFileNode')

    # Logic to calculate the frame number.
    node = maya.cmds.createNode('mmImageSequenceFrameLogic')
    lib_utils.force_connect_attr(shp + '.imageSequenceFrame', node + '.inFrame')
    lib_utils.force_connect_attr(shp + '.imageSequenceFirstFrame', node + '.firstFrame')
    lib_utils.force_connect_attr(shp + '.imageSequenceStartFrame', node + '.startFrame')
    lib_utils.force_connect_attr(shp + '.imageSequenceEndFrame', node + '.endFrame')
    lib_utils.force_connect_attr(node + '.outFrame', shp + '.imageSequenceFrameOutput')

    # Only show the users the final frame number, no editing.
    maya.cmds.setAttr(shp + '.imageSequenceFrameOutput', lock=True)

    return shp


def set_image_sequence(shp, image_sequence_path, attr_name, version=None):
    assert isinstance(shp, pycompat.TEXT_TYPE)
    assert isinstance(image_sequence_path, pycompat.TEXT_TYPE)
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    result = None
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        result = lib_mmimageplane_v1.set_image_sequence(
            shp, image_sequence_path, attr_name
        )
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        result = lib_mmimageplane_v2.set_image_sequence(
            shp, image_sequence_path, attr_name
        )
    else:
        assert False
    return result


def get_shape_node(image_plane_tfm, version=None):
    assert isinstance(image_plane_tfm, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(image_plane_tfm)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    result = None
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        result = lib_mmimageplane_v1.get_shape_node(image_plane_tfm)
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        result = lib_mmimageplane_v2.get_shape_node(image_plane_tfm)
    else:
        assert False
    return result


def get_transform_node(image_plane_shp, version=None):
    assert isinstance(image_plane_shp, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(image_plane_shp)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    result = None
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        result = lib_mmimageplane_v1.get_transform_node(image_plane_shp)
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        result = lib_mmimageplane_v2.get_transform_node(image_plane_shp)
    else:
        assert False
    return result


def get_image_plane_node_pair(node, version=None):
    assert isinstance(node, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(node)
    assert version in lib_const.MM_IMAGE_PLANE_VERSION_LIST
    result = None
    if version == lib_const.MM_IMAGE_PLANE_VERSION_ONE:
        result = lib_mmimageplane_v1.get_image_plane_node_pair(node)
    elif version == lib_const.MM_IMAGE_PLANE_VERSION_TWO:
        result = lib_mmimageplane_v2.get_image_plane_node_pair(node)
    else:
        assert False
    return result
