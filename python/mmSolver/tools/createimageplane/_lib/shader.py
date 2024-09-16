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

import collections

import maya.cmds

import mmSolver.logger
import mmSolver.utils.constant as const_utils
import mmSolver.utils.imageseq as imageseq_utils
import mmSolver.tools.createimageplane._lib.utilities as lib_utils

LOG = mmSolver.logger.get_logger()


ShaderNetworkNodes = collections.namedtuple(
    'ShaderNetworkNodes',
    [
        'sg_node',
        'shd_node',
        'file_node',
        'color_gamma_node',
        'alpha_channel_blend_node',
        'image_load_invert_boolean_node',
        'alpha_channel_reverse_node',
    ],
)


def set_file_path(file_node, image_sequence_path):
    format_style = const_utils.IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME
    (
        file_pattern,
        start,
        end,
        pad_num,
        is_seq,
    ) = imageseq_utils.expand_image_sequence_path(image_sequence_path, format_style)

    maya.cmds.setAttr(
        file_node + '.fileTextureName', image_sequence_path, type='string'
    )

    # Set useFrameExtension temporarily. Setting useFrameExtension to
    # False causes frameOffset to be locked (but we need to edit it).
    maya.cmds.setAttr(file_node + '.useFrameExtension', True)

    settable = maya.cmds.getAttr(file_node + '.frameOffset', settable=True)
    if settable is True:
        maya.cmds.setAttr(file_node + '.frameOffset', 0)
        maya.cmds.setAttr(file_node + '.frameOffset', lock=True)

    maya.cmds.setAttr(file_node + '.useFrameExtension', is_seq)

    # Cache the image sequence.
    maya.cmds.setAttr(file_node + '.useHardwareTextureCycling', is_seq)
    maya.cmds.setAttr(file_node + '.startCycleExtension', start)
    maya.cmds.setAttr(file_node + '.endCycleExtension', end)
    return


def create_network(name_shader, image_plane_tfm):
    """Create an image plane shader, to display an image sequence in Maya
    on a Polygon image plane.
    """
    obj_nodes = [image_plane_tfm]

    file_place2d = maya.cmds.shadingNode(
        'place2dTexture', name=name_shader + '_place2dTexture', asUtility=True
    )
    file_node = maya.cmds.shadingNode(
        'file', name=name_shader + '_file', asTexture=True, isColorManaged=True
    )
    color_gamma_node = maya.cmds.shadingNode(
        'gammaCorrect', name=name_shader + '_colorGamma', asUtility=True
    )
    alpha_channel_blend_node = maya.cmds.shadingNode(
        'blendColors', name=name_shader + '_alphaChannelBlend', asUtility=True
    )
    image_load_invert_boolean_node = maya.cmds.shadingNode(
        'reverse', name=name_shader + '_imageLoadInvertBoolean', asUtility=True
    )
    alpha_channel_reverse_node = maya.cmds.shadingNode(
        'reverse', name=name_shader + '_alphaChannelReverse', asUtility=True
    )
    shd_node = maya.cmds.shadingNode('surfaceShader', asShader=True, name=name_shader)
    sg_node = maya.cmds.sets(
        name=name_shader + 'SG', renderable=True, noSurfaceShader=True, empty=True
    )

    # Pixel filter (how the texture is interpolated between pixels).
    filter_type = 0  # 0 = Nearest Pixel / Unfiltered
    maya.cmds.setAttr(file_node + '.filterType', filter_type)

    lib_utils.force_connect_attr(
        alpha_channel_reverse_node + '.output', alpha_channel_blend_node + '.color2'
    )

    # Add Gamma Control
    lib_utils.force_connect_attr(file_node + '.outColor', color_gamma_node + '.value')
    lib_utils.force_connect_attr(color_gamma_node + '.outValue', shd_node + '.outColor')

    # Enable/Disable alpha channel.
    lib_utils.force_connect_attr(
        file_node + '.outTransparency', alpha_channel_blend_node + '.color1'
    )
    lib_utils.force_connect_attr(
        alpha_channel_blend_node + '.output', shd_node + '.outTransparency'
    )

    # Enable/Disable Loading the File
    lib_utils.force_connect_attr(
        image_load_invert_boolean_node + '.outputX', file_node + '.disableFileLoad'
    )

    # Connect all needed 2D Placement attributes to the File node.
    conns = [
        ['coverage', 'coverage'],
        ['translateFrame', 'translateFrame'],
        ['rotateFrame', 'rotateFrame'],
        ['mirrorU', 'mirrorU'],
        ['mirrorV', 'mirrorV'],
        ['stagger', 'stagger'],
        ['wrapU', 'wrapU'],
        ['wrapV', 'wrapV'],
        ['repeatUV', 'repeatUV'],
        ['offset', 'offset'],
        ['rotateUV', 'rotateUV'],
        ['noiseUV', 'noiseUV'],
        ['vertexUvOne', 'vertexUvOne'],
        ['vertexUvTwo', 'vertexUvTwo'],
        ['vertexUvThree', 'vertexUvThree'],
        ['vertexCameraOne', 'vertexCameraOne'],
        ['outUV', 'uvCoord'],
        ['outUvFilterSize', 'uvFilterSize'],
    ]
    for src_attr, dst_attr in conns:
        src = file_place2d + '.' + src_attr
        dst = file_node + '.' + dst_attr
        lib_utils.force_connect_attr(src, dst)

    # Connect shader to shading group
    lib_utils.force_connect_attr(shd_node + '.outColor', sg_node + '.surfaceShader')

    # Assign shader.
    maya.cmds.sets(obj_nodes, edit=True, forceElement=sg_node)

    shd_network = ShaderNetworkNodes(
        sg_node=sg_node,
        shd_node=shd_node,
        file_node=file_node,
        color_gamma_node=color_gamma_node,
        alpha_channel_blend_node=alpha_channel_blend_node,
        image_load_invert_boolean_node=image_load_invert_boolean_node,
        alpha_channel_reverse_node=alpha_channel_reverse_node,
    )
    return shd_network
