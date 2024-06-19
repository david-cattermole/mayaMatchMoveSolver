# Copyright (C) 2020, 2022, 2024 David Cattermole.
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
import mmSolver.utils.constant as const_utils
import mmSolver.utils.imageseq as imageseq_utils
import mmSolver.utils.node as node_utils
import mmSolver.tools.createimageplane._lib.constant as lib_const
import mmSolver.tools.createimageplane._lib.utilities as lib_utils


LOG = mmSolver.logger.get_logger()


def create_transform_attrs(image_plane_tfm):
    assert maya.cmds.nodeType(image_plane_tfm) == lib_const.MM_IMAGE_PLANE_TRANSFORM

    # Depth attribute
    attr = 'depth'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=1.0,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Focal Length attribute
    attr = 'focalLength'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.1,
        defaultValue=35.0,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Horizontal Film Aperture attribute
    attr = 'horizontalFilmAperture'
    value = 36.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Vertical Film Aperture attribute
    attr = 'verticalFilmAperture'
    value = 24.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Pixel Aspect Ratio attribute
    attr = 'pixelAspect'
    value = 1.0
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Horizontal Film Offset attribute
    attr = 'horizontalFilmOffset'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=0.0,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Vertical Film Offset attribute
    attr = 'verticalFilmOffset'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=0.0,
    )
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)
    return


def create_image_plane_shape_attrs(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2

    # Choose which image sequence path to use. This is only visible in
    # the Attribute Editor, because this attribute must trigger a
    # callback when changed to update the underlying 'file' node.
    attr = 'imageSequenceSlot'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='enum',
        enumName="main=0:alternate1=1:alternate2=2:alternate3=3",
    )
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=False)

    # Image Sequence attribute
    attr = 'imageSequence'
    nice_name = 'Image Sequence'
    attr_suffix_list = ['Main', 'Alternate1', 'Alternate2', 'Alternate3']
    nice_suffix_list = [' (Main)', ' (Alt 1)', ' (Alt 2)', ' (Alt 3)']
    for attr_suffix, nice_suffix in zip(attr_suffix_list, nice_suffix_list):
        maya.cmds.addAttr(
            image_plane_shp,
            longName=attr + attr_suffix,
            niceName=nice_name + nice_suffix,
            dataType='string',
        )

    # Image Sequence Frame attribute
    attr = 'imageSequenceFrame'
    maya.cmds.addAttr(
        image_plane_shp, longName=attr, attributeType='double', defaultValue=0.0
    )
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    lib_utils.force_connect_attr('time1.outTime', node_attr)

    attr = 'imageSequenceFirstFrame'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        niceName='First Frame',
        attributeType='long',
        defaultValue=0,
    )
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=False)
    maya.cmds.setAttr(node_attr, channelBox=True)

    attr = 'imageSequenceFrameOutput'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        niceName='Frame Output',
        attributeType='double',
        defaultValue=0.0,
    )
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    dst_node_attr = image_plane_shp + '.imageFrameNumber'
    lib_utils.force_connect_attr(node_attr, dst_node_attr)

    # Image Sequence details.
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequenceStartFrame',
        niceName='Start Frame',
        attributeType='long',
        defaultValue=0,
    )
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequenceEndFrame',
        niceName='End Frame',
        attributeType='long',
        defaultValue=0,
    )
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequencePadding',
        niceName='Padding',
        attributeType='long',
        defaultValue=0,
    )

    # Mesh Resolution attribute
    attr = 'meshResolution'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='long',
        minValue=1,
        maxValue=256,
        defaultValue=32,
    )
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    return


def set_image_sequence(shp, image_sequence_path, attr_name):
    assert isinstance(image_sequence_path, str)
    assert maya.cmds.nodeType(shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2
    assert node_utils.attribute_exists(attr_name, shp) is True

    format_style = const_utils.IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME
    (
        file_pattern,
        _,
        _,
        _,
        _,
    ) = imageseq_utils.expand_image_sequence_path(image_sequence_path, format_style)
    first_frame_file_seq = file_pattern.replace('\\', '/')

    mmapi.load_plugin()
    try:
        image_data_header = maya.cmds.mmReadImage(
            first_frame_file_seq, query=True, dataHeader=True
        )
    except RuntimeError:
        image_data_header = None
        LOG.warn('Failed to read file: %r', first_frame_file_seq)

    image_width = 1
    image_height = 1
    image_num_channels = 0
    image_bytes_per_channel = 0
    image_data_size_as_bytes = 0
    if image_data_header is not None:
        image_width = int(image_data_header[0])
        image_height = int(image_data_header[1])
        image_num_channels = int(image_data_header[2])
        image_bytes_per_channel = int(image_data_header[3])
        image_data_size_as_bytes = image_data_header[4]

    if not node_utils.node_is_referenced(shp):
        maya.cmds.setAttr(shp + '.imageWidth', lock=False)
        maya.cmds.setAttr(shp + '.imageHeight', lock=False)
        maya.cmds.setAttr(shp + '.imageNumChannels', lock=False)
        maya.cmds.setAttr(shp + '.imageBytesPerChannel', lock=False)
        maya.cmds.setAttr(shp + '.imageSizeBytes', lock=False)

    maya.cmds.setAttr(shp + '.imageWidth', image_width)
    maya.cmds.setAttr(shp + '.imageHeight', image_height)
    maya.cmds.setAttr(shp + '.imageNumChannels', image_num_channels)
    maya.cmds.setAttr(shp + '.imageBytesPerChannel', image_bytes_per_channel)
    maya.cmds.setAttr(shp + '.imageSizeBytes', image_data_size_as_bytes, type='string')

    if not node_utils.node_is_referenced(shp):
        maya.cmds.setAttr(shp + '.imageWidth', lock=True)
        maya.cmds.setAttr(shp + '.imageHeight', lock=True)
        maya.cmds.setAttr(shp + '.imageNumChannels', lock=True)
        maya.cmds.setAttr(shp + '.imageBytesPerChannel', lock=True)
        maya.cmds.setAttr(shp + '.imageSizeBytes', lock=True)

    format_style = const_utils.IMAGE_SEQ_FORMAT_STYLE_HASH_PADDED
    (
        file_pattern,
        start_frame,
        end_frame,
        pad_num,
        is_seq,
    ) = imageseq_utils.expand_image_sequence_path(image_sequence_path, format_style)

    maya.cmds.setAttr(shp + '.' + attr_name, file_pattern, type='string')

    if not node_utils.node_is_referenced(shp):
        maya.cmds.setAttr(shp + '.imageSequenceStartFrame', lock=False)
        maya.cmds.setAttr(shp + '.imageSequenceEndFrame', lock=False)
        maya.cmds.setAttr(shp + '.imageSequencePadding', lock=False)

    maya.cmds.setAttr(shp + '.imageSequenceFirstFrame', start_frame)
    maya.cmds.setAttr(shp + '.imageSequenceStartFrame', start_frame)
    maya.cmds.setAttr(shp + '.imageSequenceEndFrame', end_frame)
    maya.cmds.setAttr(shp + '.imageSequencePadding', pad_num)

    if not node_utils.node_is_referenced(shp):
        maya.cmds.setAttr(shp + '.imageSequenceStartFrame', lock=True)
        maya.cmds.setAttr(shp + '.imageSequenceEndFrame', lock=True)
        maya.cmds.setAttr(shp + '.imageSequencePadding', lock=True)
    return


def get_frame_size_bytes(shp):
    assert isinstance(shp, str)
    assert maya.cmds.nodeType(shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2
    image_size_bytes = maya.cmds.getAttr(shp + '.imageSizeBytes')
    return int(image_size_bytes)


def get_frame_count(shp):
    assert isinstance(shp, str)
    assert maya.cmds.nodeType(shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2
    start_frame = maya.cmds.getAttr(shp + '.imageSequenceStartFrame')
    end_frame = maya.cmds.getAttr(shp + '.imageSequenceEndFrame')
    frame_count = end_frame - start_frame
    return frame_count


def get_image_sequence_size_bytes(shp):
    assert isinstance(shp, str)
    assert maya.cmds.nodeType(shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2
    image_size_bytes = get_frame_size_bytes(shp)
    frame_count = get_frame_count(shp)
    return image_size_bytes * frame_count


def get_shape_node(image_plane_tfm):
    assert maya.cmds.nodeType(image_plane_tfm) == lib_const.MM_IMAGE_PLANE_TRANSFORM

    shape = None
    shapes = (
        maya.cmds.listRelatives(
            image_plane_tfm,
            shapes=True,
            fullPath=True,
            type=lib_const.MM_IMAGE_PLANE_SHAPE_V2,
        )
        or []
    )
    if len(shapes) > 0:
        shape = shapes[0]
    return shape


def get_transform_node(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == lib_const.MM_IMAGE_PLANE_SHAPE_V2

    tfm = None
    tfms = (
        maya.cmds.listRelatives(
            image_plane_shp,
            parent=True,
            fullPath=True,
            type=lib_const.MM_IMAGE_PLANE_TRANSFORM,
        )
        or []
    )
    if len(tfms) > 0:
        tfm = tfms[0]
    return tfm


def get_image_plane_node_pair(node):
    node_type = maya.cmds.nodeType(node)
    assert node_type in [
        lib_const.MM_IMAGE_PLANE_SHAPE_V2,
        lib_const.MM_IMAGE_PLANE_TRANSFORM,
    ]
    tfm = None
    shp = None
    if node_type == lib_const.MM_IMAGE_PLANE_TRANSFORM:
        shp = get_shape_node(node)
        tfm = node
    else:
        # Given a shape, we can look at our parent node to find the
        # transform.
        tfm = get_transform_node(node)
        shp = node
    return tfm, shp
