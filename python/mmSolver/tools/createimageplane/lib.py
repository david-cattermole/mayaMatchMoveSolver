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


Idea - Create wrapper image plane node
- The node should adjust either 'live' or 'baked' nodes.


Idea - Allow users to change the image sequence.
- Both 'live' and 'baked' image planes are updated as needed.
- Users can choose to auto-convert to Maya IFF format (for speed).


Idea - Bake images into .iff files using Maya 'imgcvt' utility.
- Experiment with .dds files to see if it's faster in the Maya viewport or not.
- Write to local 'sourceimages/mmSolver_temp' directory, by default.


Idea - Apply image processing templates to images.
- Allow the use of OIIO, Natron or Nuke (if installed)
- Features
  - Reformat / down-res plates.
    - Scale (50%)
    - Maximum width (2048)
    - Maximum height (2048)
  - Lens undistort (for baked image planes)
  - Converting to different formats (such as Maya 'iff')


Tool - Set Image Plane File Path


Tool - Toggle the Live/Baked image plane state.


Idea - Create a custom image plane shape node.
- Pipe the deforming polygon plane into the shape node and draw it with
  an image sequence on it.
- This allows us to hide the polygons in a viewport but still show the
  image plane.
- We can control the depth of the image plane with this method.
- When the OCG Image Plane is fully developed we can easily replace this
  shape node with the 'ocgImagePlane'.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.createimageplane.constant as const

LOG = mmSolver.logger.get_logger()
# Enables/disables the use of a 'baked' image plane feature.
BAKED_IMAGE_PLANE = False


def _add_attr_float3_color(node, attr_name, default_value):
    min_value = 0.0
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        usedAsColor=True,
        attributeType='float3')

    maya.cmds.addAttr(
        node,
        longName=attr_name + 'R',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)
    maya.cmds.addAttr(
        node,
        longName=attr_name + 'G',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)
    maya.cmds.addAttr(
        node,
        longName=attr_name + 'B',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)

    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr + 'R', keyable=True)
    maya.cmds.setAttr(node_attr + 'G', keyable=True)
    maya.cmds.setAttr(node_attr + 'B', keyable=True)
    return


def _create_image_plane_transform_attrs(image_plane_tfm):
    # Depth attribute
    attr = 'depth'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=1.0)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, 10.0)

    # Focal Length attribute
    attr = 'focalLength'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.1,
        defaultValue=35.0)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Horizontal Film Aperture attribute
    attr = 'horizontalFilmAperture'
    value = 36.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Vertical Film Aperture attribute
    attr = 'verticalFilmAperture'
    value = 24.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Pixel Aspect Ratio attribute
    attr = 'pixelAspect'
    value = 1.0
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Horizontal Film Offset attribute
    attr = 'horizontalFilmOffset'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=0.0)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)

    # Vertical Film Offset attribute
    attr = 'verticalFilmOffset'
    maya.cmds.addAttr(
        image_plane_tfm,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        defaultValue=0.0)
    maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=True)
    return


def _create_image_plane_shape_attrs(image_plane_shp):
    # Display Mode
    if BAKED_IMAGE_PLANE is True:
        maya.cmds.addAttr(
            image_plane_shp,
            longName='displayMode',
            attributeType='enum',
            enumName='Live:Baked:')
        maya.cmds.setAttr(
            image_plane_shp + '.displayMode',
            edit=True, keyable=True)

    # Exposure attribute
    attr = 'exposure'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='double',
        softMinValue=-5.0,
        softMaxValue=5.0,
        defaultValue=0.0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Gamma attribute
    attr = 'gamma'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        softMaxValue=3.0,
        defaultValue=1.0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Color Gain attribute
    attr = 'colorGain'
    default_value = 1.0
    _add_attr_float3_color(image_plane_shp, attr, default_value)

    # Alpha Gain attribute
    attr = 'alphaGain'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='double',
        minValue=0.0,
        softMaxValue=1.0,
        defaultValue=1.0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Use Image Alpha Channel attribute
    attr = 'imageUseAlphaChannel'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='bool',
        defaultValue=0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Default Image Color attribute, display a dark-red color when an
    # image is not found.
    attr = 'imageDefaultColor'
    default_value = 0.0
    _add_attr_float3_color(image_plane_shp, attr, default_value)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr + 'R', 0.3)
    maya.cmds.setAttr(node_attr + 'G', 0.0)
    maya.cmds.setAttr(node_attr + 'B', 0.0)

    # Image Load Enable attribute
    attr = 'imageLoadEnable'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='bool',
        defaultValue=1)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Image Sequence attribute
    attr = 'imageSequence'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        dataType='string')

    # Image Sequence Frame attribute
    attr = 'imageSequenceFrame'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='double',
        defaultValue=0.0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    _force_connect_attr('time1.outTime', node_attr)

    attr = 'imageSequenceFirstFrame'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        niceName='First Frame',
        attributeType='long',
        defaultValue=0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=False)
    maya.cmds.setAttr(node_attr, channelBox=True)

    attr = 'imageSequenceFrameOutput'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        niceName='Frame Output',
        attributeType='double',
        defaultValue=0.0)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)

    # Image Sequence details.
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequenceStartFrame',
        niceName='Start Frame',
        attributeType='long',
        defaultValue=0)
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequenceEndFrame',
        niceName='End Frame',
        attributeType='long',
        defaultValue=0)
    maya.cmds.addAttr(
        image_plane_shp,
        longName='imageSequencePadding',
        niceName='Padding',
        attributeType='long',
        defaultValue=0)

    # Mesh Resolution attribute
    attr = 'meshResolution'
    maya.cmds.addAttr(
        image_plane_shp,
        longName=attr,
        attributeType='long',
        minValue=1,
        maxValue=256,
        defaultValue=32)
    node_attr = image_plane_shp + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    return


def _create_image_poly_plane(name):
    """
    Create a default polygon image plane under camera.
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    mmapi.load_plugin()

    name_mesh_shp = name + 'MeshShape'
    tfm = maya.cmds.createNode('mmImagePlaneTransform', name=name)
    mesh_shp = maya.cmds.createNode('mesh', name=name_mesh_shp, parent=tfm)
    creator = maya.cmds.createNode('polyPlane')
    maya.cmds.connectAttr(creator + '.output', mesh_shp + '.inMesh')

    maya.cmds.setAttr(creator + '.subdivisionsWidth', 32)
    maya.cmds.setAttr(creator + '.subdivisionsHeight', 32)
    maya.cmds.setAttr(creator + '.axisX', 0.0)
    maya.cmds.setAttr(creator + '.axisY', 0.0)
    maya.cmds.setAttr(creator + '.axisZ', 1.0)

    # Make the polygon image plane non-selectable.
    display_type = 2  # 2 = 'Reference'
    maya.cmds.setAttr(tfm + '.overrideEnabled', 1)
    maya.cmds.setAttr(tfm + '.overrideDisplayType', display_type)

    deform_node = maya.cmds.deformer(tfm, type='mmLensDeformer')[0]
    mkr_scl = maya.cmds.createNode('mmMarkerScale')
    inv_mult = maya.cmds.createNode('multiplyDivide')

    # Get the intermediate mesh shape, so we can re-order the nodes
    # later and ensure the mmImagePlaneShape is first, so that users
    # will see the mmImagePlaneShape first in the Attribute Editor.
    shapes = maya.cmds.listRelatives(
        tfm,
        shapes=True,
        noIntermediate=False,
        type='mesh') or []
    shapes = [x for x in shapes
              if maya.cmds.getAttr(x + '.intermediateObject') == 1]
    assert len(shapes) == 1
    mesh_shp_original = shapes[0]

    # Create (dynamic) attributes.
    _create_image_plane_transform_attrs(tfm)

    # Connect Image Plane dummy attrs to Marker Scale node.
    attrs = [
        'depth',
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'horizontalFilmOffset',
        'verticalFilmOffset'
    ]
    for attr in attrs:
        src = tfm + '.' + attr
        dst = mkr_scl + '.' + attr
        _force_connect_attr(src, dst)

    attrs = [
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'pixelAspect',
        'horizontalFilmOffset',
        'verticalFilmOffset'
    ]
    for attr in attrs:
        src = tfm + '.' + attr
        dst = deform_node + '.' + attr
        _force_connect_attr(src, dst)

    # Connect marker scale to transform node.
    _force_connect_attr(mkr_scl + '.outScale', tfm + '.scale')
    _force_connect_attr(mkr_scl + '.outTranslateX', tfm + '.translateX')
    _force_connect_attr(mkr_scl + '.outTranslateY', tfm + '.translateY')

    # Connect inverted depth to the transform TZ.
    _force_connect_attr(mkr_scl + '.depth', inv_mult + '.input1Z')
    _force_connect_attr(inv_mult + '.outputZ', tfm + '.translateZ')
    maya.cmds.setAttr(inv_mult + '.operation', 1)  # Multiply operation
    maya.cmds.setAttr(inv_mult + '.input2Z', -1.0)

    # Lock and hide all the attributes
    attrs = ['tx', 'ty', 'tz',
             'rx', 'ry', 'rz',
             'sx', 'sy', 'sz',
             'shearXY', 'shearXZ', 'shearYZ', 'rotateOrder',
             'rotateAxisX', 'rotateAxisY', 'rotateAxisZ']
    for attr in attrs:
        maya.cmds.setAttr(tfm + '.' + attr, lock=True)
        maya.cmds.setAttr(tfm + '.' + attr, keyable=False, channelBox=False)
    return tfm, mesh_shp, mesh_shp_original, creator, deform_node


def _set_image_plane_values(cam, baked_shp, live_tfm, deform_node):
    """Set the values of a polygon image plane with a regular Maya image
    plane.

    This function is intended to match/sync the exact same image plane
    settings on the polygon image plane.

    The camera is also set to whatever camera is given.

    """
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    # Drive the Deformer node with the camera lens.
    src = cam_shp + '.outLens'
    dst = deform_node + '.inLens'
    if not maya.cmds.isConnected(src, dst):
        _force_connect_attr(src, dst)

    # Connect camera attributes
    attrs = [
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'horizontalFilmOffset',
        'verticalFilmOffset'
    ]
    for attr in attrs:
        src = cam_shp + '.' + attr
        dst = live_tfm + '.' + attr
        if not maya.cmds.isConnected(src, dst):
            _force_connect_attr(src, dst)

    # Copy the image plane 'depth' attribute value to the poly image
    # plane.
    if baked_shp is not None:
        src = baked_shp + '.depth'
        dst = live_tfm + '.depth'
        value = maya.cmds.getAttr(src)
        maya.cmds.setAttr(dst, value)

    # Parent the transform under the camera.
    img_poly_plane_tfm_uuid = maya.cmds.ls(live_tfm, uuid=True)[0]
    maya.cmds.parent(live_tfm, cam_tfm, relative=True)
    live_tfm = maya.cmds.ls(img_poly_plane_tfm_uuid, long=True)[0]
    return live_tfm


def _get_default_image():
    base_install_location = os.environ.get('MMSOLVER_LOCATION', None)
    assert base_install_location is not None
    fallback = os.path.join(base_install_location, 'resources')

    dir_path = os.environ.get('MMSOLVER_RESOURCE_PATH', fallback)
    assert isinstance(dir_path, pycompat.TEXT_TYPE)

    file_name = 'default_mmSolver_1920x1080_hd.iff'
    file_path = os.path.join(dir_path, file_name)
    return os.path.abspath(file_path)


def _get_image_plane_mm_shape_node(image_plane_tfm):
    shape = None
    shapes = maya.cmds.listRelatives(
        image_plane_tfm,
        shapes=True,
        type='mmImagePlaneShape'
    ) or []
    if len(shapes) > 0:
        shape = shapes[0]
    return shape


def _get_image_plane_file_node(image_plane_tfm):
    file_node = None
    conns = maya.cmds.listConnections(
        image_plane_tfm + '.shaderFileNode',
        destination=False,
        source=True,
        plugs=False,
        type='file',
    ) or []
    if len(conns) > 0:
        file_node = conns[0]
    return file_node


def _get_image_plane_baked_shape_node(image_plane_tfm):
    file_node = None
    conns = maya.cmds.listConnections(
        image_plane_tfm + '.imagePlaneShapeNode',
        destination=False,
        source=True,
        plugs=False,
        type='imagePlane',
    ) or []
    if len(conns) > 0:
        file_node = conns[0]
    return file_node


def _get_string_numbers_at_end(string_value):
    numbers = []
    for i in range(1, len(string_value)):
        char = string_value[-i]
        if char.isdigit():
            numbers.insert(0, char)
        else:
            break
    return ''.join(numbers)


def _split_image_sequence_path(file_path):
    head, tail = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(tail)

    seq_num_int = 0
    seq_num_str = _get_string_numbers_at_end(file_name)
    if len(seq_num_str) > 0:
        file_name = file_name[:-len(seq_num_str)]
        seq_num_int = int(seq_num_str)
    return head, file_name, seq_num_int, seq_num_str, file_extension


def _get_image_sequence_start_end_frames(base_dir, file_name, file_extension):
    join_file_name = '{}*{}'.format(file_name, file_extension)
    glob_path = os.path.join(base_dir, join_file_name)
    all_paths = glob.iglob(glob_path)

    padding_num = 99
    start_frame = 9999999
    end_frame = 0
    count = 0
    for path in all_paths:
        path_base_dir, \
            path_file_name, \
            path_seq_num_int, \
            path_seq_num_str, \
            path_file_extension = _split_image_sequence_path(path)
        start_frame = min(path_seq_num_int, start_frame)
        end_frame = max(path_seq_num_int, end_frame)
        padding_num = min(padding_num, len(path_seq_num_str))
        count = count + 1

    if count <= 1:
        start_frame = 0
        end_frame = 0
        padding_num = 0

    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    assert isinstance(padding_num, int)
    return start_frame, end_frame, padding_num


def _expand_image_sequence_path(image_sequence_path, format_style):
    image_sequence_path = os.path.abspath(image_sequence_path)

    base_dir, \
        file_name, \
        seq_num_int, \
        seq_num_str, \
        file_extension = _split_image_sequence_path(image_sequence_path)

    start_frame, end_frame, padding_num = \
        _get_image_sequence_start_end_frames(
            base_dir,
            file_name,
            file_extension)

    is_seq = start_frame != end_frame and padding_num > 0
    if is_seq is False:
        file_pattern = image_sequence_path
    else:
        image_seq_num = ''
        if format_style == const.FORMAT_STYLE_MAYA:
            # file.<f>.png
            if padding_num > 0:
                image_seq_num = '<f>'
        elif format_style == const.FORMAT_STYLE_HASH_PADDED:
            # file.####.png
            image_seq_num = '#' * padding_num
        elif format_style == const.FORMAT_STYLE_PRINTF:
            # file.%04d.png
            if padding_num > 0:
                image_seq_num = '%0{}d'.format(padding_num)
        elif format_style == const.FORMAT_STYLE_FIRST_FRAME:
            # file.1001.png
            image_seq_num = str(start_frame).zfill(padding_num)
        else:
            raise NotImplementedError
        file_pattern = '{}{}{}'.format(
            file_name,
            image_seq_num,
            file_extension)
        file_pattern = os.path.join(base_dir, file_pattern)

    return file_pattern, start_frame, end_frame, padding_num, is_seq


def _create_baked_image_plane_node(cam_tfm):
    name = 'bakedImagePlane1'
    img_pl_tfm, img_pl_shp = maya.cmds.imagePlane(
        camera=cam_tfm,
        name=name)
    return img_pl_tfm, img_pl_shp


def set_image_sequence(tfm, image_sequence_path):
    _set_main_image_sequence(tfm, image_sequence_path)
    _set_shader_file_path(tfm, image_sequence_path)
    _set_image_plane_file_path(tfm, image_sequence_path)


def _set_main_image_sequence(tfm, image_sequence_path):
    shp = _get_image_plane_mm_shape_node(tfm)
    if shp is None:
        LOG.warn('mmImagePlaneShape node could not be found.')
        return

    assert maya.cmds.nodeType(shp) == 'mmImagePlaneShape'
    format_style = const.FORMAT_STYLE_HASH_PADDED
    file_pattern, start_frame, end_frame, pad_num, is_seq = \
        _expand_image_sequence_path(
            image_sequence_path,
            format_style)

    format_style = const.FORMAT_STYLE_FIRST_FRAME
    first_frame_file_seq, _, _, _, _ = \
        _expand_image_sequence_path(
            image_sequence_path,
            format_style)

    mmapi.load_plugin()
    try:
        first_frame_file_seq = first_frame_file_seq.replace('\\', '/')
        image_width_height = maya.cmds.mmReadImage(
            first_frame_file_seq,
            query=True,
            widthHeight=True)
    except RuntimeError:
        image_width_height = None
        LOG.warn('Failed to read file: %r', first_frame_file_seq)
    if image_width_height is not None:
        image_width = image_width_height[0]
        image_height = image_width_height[1]

        if not node_utils.node_is_referenced(shp):
            maya.cmds.setAttr(shp + '.imageWidth', lock=False)
            maya.cmds.setAttr(shp + '.imageHeight', lock=False)

        maya.cmds.setAttr(shp + '.imageWidth', image_width)
        maya.cmds.setAttr(shp + '.imageHeight', image_height)

        if not node_utils.node_is_referenced(shp):
            maya.cmds.setAttr(shp + '.imageWidth', lock=True)
            maya.cmds.setAttr(shp + '.imageHeight', lock=True)

    maya.cmds.setAttr(
        shp + '.imageSequence',
        file_pattern,
        type='string')

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


def _set_shader_file_path(image_plane_tfm, image_sequence_path):
    file_node = _get_image_plane_file_node(image_plane_tfm)
    if file_node is None:
        LOG.warn('image plane shader file node is invalid.')
        return

    mm_image_plane_shape = _get_image_plane_mm_shape_node(image_plane_tfm)
    if mm_image_plane_shape is None:
        LOG.warn('image plane shape node.')

    format_style = const.FORMAT_STYLE_FIRST_FRAME
    file_pattern, start, end, pad_num, is_seq = _expand_image_sequence_path(
        image_sequence_path,
        format_style)

    maya.cmds.setAttr(
        file_node + '.fileTextureName',
        image_sequence_path,
        type='string')

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


def _set_image_plane_file_path(image_plane_tfm, image_sequence_path):
    if BAKED_IMAGE_PLANE is False:
        return
    image_plane_shp = _get_image_plane_baked_shape_node(image_plane_tfm)
    if image_plane_shp is None:
        LOG.warn('image plane baked shape node is invalid.')
        return

    format_style = const.FORMAT_STYLE_HASH_PADDED
    file_pattern, start, end, pad_num, is_seq = _expand_image_sequence_path(
        image_sequence_path,
        format_style)

    maya.cmds.setAttr(
        image_plane_shp + '.imageName',
        image_sequence_path,
        type='string')
    maya.cmds.setAttr(image_plane_shp + '.useFrameExtension', is_seq)

    settable = maya.cmds.getAttr(image_plane_shp + '.frameOffset', settable=True)
    if settable is True:
        maya.cmds.setAttr(image_plane_shp + '.frameOffset', 0)

    # The image plane can query the loaded image pixel width/height.
    image_width, image_height = maya.cmds.imagePlane(
        image_plane_shp,
        query=True,
        imageSize=True)

    # image_width/image_height will be wrong if the image file could
    # not be loaded successfully.
    if (image_width > 0) and (image_height > 0):
        # With Maintain ratio ("mr") enabled, Maya will calculate the
        # image height for us.
        previous_maintain_ratio = maya.cmds.getAttr(image_plane_shp + '.mr')
        maya.cmds.setAttr(image_plane_shp + '.mr', True)
        plane_width = image_width / 100.0
        maya.cmds.imagePlane(image_plane_shp, edit=True, width=plane_width)
        maya.cmds.setAttr(image_plane_shp + '.mr', previous_maintain_ratio)

    minimum_cache_size = 99
    if is_seq is False:
        sequence_length = minimum_cache_size
    else:
        sequence_length = min(minimum_cache_size, end - start)
    maya.cmds.setAttr(image_plane_shp + '.frameCache', sequence_length)
    return


def _create_image_plane_shader(image_plane_tfm):
    """Create an image plane shader, to display an image sequence in Maya
    on a Polygon image plane.
    """
    obj_nodes = [image_plane_tfm]

    file_place2d = maya.cmds.shadingNode('place2dTexture', asUtility=True)
    file_node = maya.cmds.shadingNode('file', asTexture=True, isColorManaged=True)
    gamma_node = maya.cmds.shadingNode('gammaCorrect', asUtility=True)
    blend_colors_node = maya.cmds.shadingNode('blendColors', asUtility=True)
    reverse1_node = maya.cmds.shadingNode('reverse', asUtility=True)
    reverse2_node = maya.cmds.shadingNode('reverse', asUtility=True)
    shd_node = maya.cmds.shadingNode('surfaceShader', asShader=True)
    sg_node = maya.cmds.sets(renderable=True, noSurfaceShader=True, empty=True)

    # Pixel filter (how the texture is interpolated between pixels).
    filter_type = 0  # 0 = Nearest Pixel / Unfiltered
    maya.cmds.setAttr(file_node + '.filterType', filter_type)

    _force_connect_attr(
        reverse2_node + '.output',
        blend_colors_node + '.color2')

    # Add Gamma Control
    _force_connect_attr(
        file_node + '.outColor',
        gamma_node + '.value')
    _force_connect_attr(
        gamma_node + '.outValue',
        shd_node + '.outColor')

    # Enable/Disable alpha channel.
    _force_connect_attr(
        file_node + '.outTransparency',
        blend_colors_node + '.color1')
    _force_connect_attr(
        blend_colors_node + '.output',
        shd_node + '.outTransparency')

    # Enable/Disable Loading the File
    _force_connect_attr(
        reverse1_node + '.outputX',
        file_node + '.disableFileLoad')

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
    for (src_attr, dst_attr) in conns:
        src = file_place2d + '.' + src_attr
        dst = file_node + '.' + dst_attr
        _force_connect_attr(src, dst)

    # Connect shader to shading group
    _force_connect_attr(
        shd_node + '.outColor',
        sg_node + '.surfaceShader')

    # Assign shader.
    maya.cmds.sets(obj_nodes, edit=True, forceElement=sg_node)

    nodes = {
        'sg_node': sg_node,
        'shd_node': shd_node,
        'file_node': file_node,
        'gamma_node': gamma_node,
        'blend_colors_node': blend_colors_node,
        'reverse1_node': reverse1_node,
        'reverse2_node': reverse2_node
    }
    return nodes


def _force_connect_attr(src_attr, dst_attr):
    """Disconnect attribute that is already connected to dst_attr, before
    creating the connection.
    """
    dst_lock_state = maya.cmds.getAttr(dst_attr, lock=True)

    if dst_lock_state is True:
        maya.cmds.setAttr(dst_attr, lock=False)

    conns = maya.cmds.listConnections(
        dst_attr,
        source=True,
        plugs=True,
        skipConversionNodes=True) or []
    conns = [x for x in conns if maya.cmds.isConnected(x, dst_attr)]
    for conn in conns:
        maya.cmds.disconnectAttr(conn, dst_attr)
    maya.cmds.connectAttr(src_attr, dst_attr, force=True)

    if dst_lock_state is True:
        maya.cmds.setAttr(dst_attr, lock=True)
    return


def _convert_mesh_to_mm_image_plane_shape(name,
                                          cam_shp,
                                          img_plane_poly_tfm,
                                          img_plane_poly_shp,
                                          img_plane_poly_shp_original,
                                          poly_creator,
                                          shd_node,
                                          file_node,
                                          gamma_node,
                                          blend_colors_node,
                                          reverse1_node,
                                          reverse2_node):
    """Convert mesh to a mmImagePlaneShape."""
    name_img_shp = name + 'Shape'
    img_plane_shp = maya.cmds.createNode(
        'mmImagePlaneShape',
        name=name_img_shp,
        parent=img_plane_poly_tfm)

    maya.cmds.setAttr(img_plane_shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.localScaleZ', channelBox=False)

    maya.cmds.setAttr(img_plane_shp + '.cameraWidthInch', channelBox=False)
    maya.cmds.setAttr(img_plane_shp + '.cameraHeightInch', channelBox=False)

    # Image plane hash will be used to stop updating the Viewport 2.0
    # shape when the lens distortion values stay the same.
    lens_eval_node = maya.cmds.createNode('mmLensEvaluate')
    _force_connect_attr(img_plane_shp + '.outLens', lens_eval_node + '.inLens')
    _force_connect_attr(lens_eval_node + '.outHash', img_plane_shp + '.lensHashCurrent')

    maya.cmds.reorder(img_plane_shp, back=True)
    maya.cmds.reorder(img_plane_poly_shp_original, back=True)
    maya.cmds.reorder(img_plane_poly_shp, back=True)

    _create_image_plane_shape_attrs(img_plane_shp)

    # Nodes to drive the image plane shape.
    _force_connect_attr(
        img_plane_poly_shp + '.outMesh',
        img_plane_shp + '.geometryNode')
    _force_connect_attr(
        shd_node + '.outColor',
        img_plane_shp + '.shaderNode')

    # The image drives the pixel aspect ratio of the image plane.
    _force_connect_attr(
        img_plane_shp + '.imagePixelAspect',
        img_plane_poly_tfm + '.pixelAspect')

    # Use the image alpha channel, or not
    _force_connect_attr(
        img_plane_shp + '.imageUseAlphaChannel',
        blend_colors_node + '.blender')

    # Allow user to load the image, or not.
    _force_connect_attr(
        img_plane_shp + '.imageLoadEnable',
        reverse1_node + '.inputX')

    # Color Exposure control.
    _force_connect_attr(
        img_plane_shp + '.exposure',
        file_node + '.exposure')

    # Color Gamma control.
    _force_connect_attr(
        img_plane_shp + '.gamma',
        gamma_node + '.gammaX')
    _force_connect_attr(
        img_plane_shp + '.gamma',
        gamma_node + '.gammaY')
    _force_connect_attr(
        img_plane_shp + '.gamma',
        gamma_node + '.gammaZ')

    # Control file color multiplier
    _force_connect_attr(
        img_plane_shp + '.colorGain',
        file_node + '.colorGain')

    # Control the alpha gain when 'imageUseAlphaChannel' is disabled.
    _force_connect_attr(
        img_plane_shp + '.alphaGain',
        file_node + '.alphaGain')
    _force_connect_attr(
        img_plane_shp + '.alphaGain',
        reverse2_node + '.inputX')
    _force_connect_attr(
        img_plane_shp + '.alphaGain',
        reverse2_node + '.inputY')
    _force_connect_attr(
        img_plane_shp + '.alphaGain',
        reverse2_node + '.inputZ')

    # Set the camera size of the image plane shape HUD.
    _force_connect_attr(
        img_plane_poly_tfm + '.horizontalFilmAperture',
        img_plane_shp + '.cameraWidthInch')
    _force_connect_attr(
        img_plane_poly_tfm + '.verticalFilmAperture',
        img_plane_shp + '.cameraHeightInch')

    # Default color for the image plane, when nothing is loaded.
    _force_connect_attr(
        img_plane_shp + '.imageDefaultColor',
        file_node + '.defaultColor')

    # Mesh Resolution attr drives the plane sub-divisions.
    node_attr = img_plane_shp + '.meshResolution'
    _force_connect_attr(node_attr, poly_creator + '.subdivisionsWidth')
    _force_connect_attr(node_attr, poly_creator + '.subdivisionsHeight')

    # Mesh doesn't need to be visible to drive the image plane shape
    # node drawing.
    maya.cmds.setAttr(img_plane_poly_shp + '.intermediateObject', 1)

    # Add extra message attributes for finding nodes during callbacks.
    maya.cmds.addAttr(
        img_plane_shp,
        longName='shaderFileNode',
        attributeType='message')
    maya.cmds.addAttr(
        img_plane_shp,
        longName='imagePlaneShapeNode',
        attributeType='message')
    return img_plane_shp


def create_image_plane_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_plane_shps = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    baked_tfm = None
    baked_shp = None
    if len(image_plane_shps) > 0:
        baked_shp = image_plane_shps[0]
    if BAKED_IMAGE_PLANE is True and baked_shp is None:
        baked_tfm, baked_shp = \
            _create_baked_image_plane_node(cam_tfm)

    # If the pixel aspect ratio of the input plate is non-zero, the
    # image plane must scale 'to size' to break the confines of the
    # input image width/height.
    image_plane_fit = 4  # 4 = 'To Size'
    if BAKED_IMAGE_PLANE is True:
        maya.cmds.setAttr(baked_shp + '.fit', image_plane_fit)

    # Convert Maya image plane into a polygon image plane.
    name = 'mmImagePlane1'
    poly_tfm, poly_shp, poly_shp_original, poly_creator, deform_node = \
        _create_image_poly_plane(name)
    poly_tfm = _set_image_plane_values(
        cam,
        baked_shp,
        poly_tfm,
        deform_node)

    image_plane_shader_nodes = _create_image_plane_shader(poly_tfm)

    shd_node = image_plane_shader_nodes['shd_node']
    file_node = image_plane_shader_nodes['file_node']
    img_plane_shp = _convert_mesh_to_mm_image_plane_shape(
        name,
        cam_shp,
        poly_tfm,
        poly_shp,
        poly_shp_original,
        poly_creator,
        shd_node,
        file_node,
        image_plane_shader_nodes['gamma_node'],
        image_plane_shader_nodes['blend_colors_node'],
        image_plane_shader_nodes['reverse1_node'],
        image_plane_shader_nodes['reverse2_node']
    )

    # Connect Display mode to live/baked nodes.
    if BAKED_IMAGE_PLANE is True:
        display_mode_expr = const.DISPLAY_MODE_EXPRESSION.format(
            image_plane_tfm=poly_tfm,
            baked_image_plane_shape=baked_shp,
            live_image_plane_shape=img_plane_shp)
        display_mode_expr = display_mode_expr.replace('{{', '{')
        display_mode_expr = display_mode_expr.replace('}}', '}')
        display_mode_expr_node = maya.cmds.expression(string=display_mode_expr)

    # Shortcut connections to nodes.
    _force_connect_attr(file_node + '.message', poly_tfm + '.shaderFileNode')
    if BAKED_IMAGE_PLANE is True:
        _force_connect_attr(baked_shp + '.message', poly_tfm + '.imagePlaneShapeNode')

    # Logic to calculate the frame number.
    frame_expr = const.FRAME_EXPRESSION.format(node=img_plane_shp)
    frame_expr = frame_expr.replace('{{', '{')
    frame_expr = frame_expr.replace('}}', '}')
    frame_expr_node = maya.cmds.expression(string=frame_expr)

    # Show the users the final frame number.
    shp_node_attr = img_plane_shp + '.imageSequenceFrameOutput'
    maya.cmds.setAttr(shp_node_attr, lock=True)

    # Set useFrameExtension temporarily. Setting useFrameExtension to
    # False causes frameOffset to be locked (but we need to edit it).
    is_seq = maya.cmds.getAttr(file_node + '.useFrameExtension')
    maya.cmds.setAttr(file_node + '.useFrameExtension', True)

    file_node_attr = file_node + '.frameExtension'
    _force_connect_attr(shp_node_attr, file_node_attr)
    maya.cmds.setAttr(file_node_attr, lock=True)

    maya.cmds.setAttr(file_node + '.useFrameExtension', is_seq)

    if BAKED_IMAGE_PLANE is True:
        baked_node_attr = baked_shp + '.frameExtension'
        _force_connect_attr(shp_node_attr, baked_node_attr)
        maya.cmds.setAttr(baked_node_attr, lock=True)

    # Keep attributes in sync.
    if BAKED_IMAGE_PLANE is True:
        _force_connect_attr(poly_tfm + '.depth', baked_shp + '.depth')
        _force_connect_attr(cam_shp + '.horizontalFilmAperture', baked_shp + '.sizeX')
        _force_connect_attr(cam_shp + '.verticalFilmAperture', baked_shp + '.sizeY')
        _force_connect_attr(cam_shp + '.horizontalFilmOffset', baked_shp + '.offsetX')
        _force_connect_attr(cam_shp + '.verticalFilmOffset', baked_shp + '.offsetY')

    # Image sequence.
    image_sequence_path = _get_default_image()
    set_image_sequence(poly_tfm, image_sequence_path)
    return poly_tfm


def convert_image_planes_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)

    # Find image plane currently on the camera.
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_planes = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    for image_plane_shp in image_planes:
        # Convert Maya image plane into a polygon image plane.
        name = 'mmImagePlane1'
        poly_tfm, poly_shp, poly_shp_original, poly_creator, deform_node = \
            _create_image_poly_plane(name)

        _set_image_plane_values(cam, image_plane_shp, poly_tfm, deform_node)

        image_plane_shader_nodes = _create_image_plane_shader(poly_tfm)

        _convert_mesh_to_mm_image_plane_shape(
            name,
            cam_shp,
            poly_tfm,
            poly_shp,
            poly_shp_original,
            poly_creator,
            image_plane_shader_nodes['shd_node'],
            image_plane_shader_nodes['file_node'],
            image_plane_shader_nodes['gamma_node'],
            image_plane_shader_nodes['blend_colors_node'],
            image_plane_shader_nodes['reverse1_node'],
            image_plane_shader_nodes['reverse2_node']
        )

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(image_plane_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(image_plane_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(image_plane_shp + '.visibility', False)
    return
