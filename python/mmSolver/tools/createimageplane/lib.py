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

import os

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.createimageplane.constant as const

LOG = mmSolver.logger.get_logger()


def create_image_poly_plane(name=None):
    """
    Create a default polygon image plane under camera.
    """
    assert name is None or isinstance(name, pycompat.TEXT_TYPE)
    name_shp = name + 'Shape'
    tfm = maya.cmds.createNode('mmImagePlaneTransform', name=name)
    shp = maya.cmds.createNode('mesh', name=name_shp, parent=tfm)
    creator = maya.cmds.createNode('polyPlane')
    maya.cmds.connectAttr(creator + '.output', shp + '.inMesh')

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

    # Depth attribute
    attr = 'depth'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.0,
        defaultValue=1.0)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)
    maya.cmds.setAttr(tfm + '.' + attr, 10.0)

    # MeshResolution attribute
    attr = 'meshResolution'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='long',
        minValue=1,
        maxValue=256,
        defaultValue=32)
    node_attr = tfm + '.' + attr
    maya.cmds.setAttr(node_attr, keyable=True)
    maya.cmds.connectAttr(node_attr, creator + '.subdivisionsWidth')
    maya.cmds.connectAttr(node_attr, creator + '.subdivisionsHeight')

    # Focal Length attribute
    attr = 'focalLength'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.1,
        defaultValue=35.0)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Horizontal Film Aperture attribute
    attr = 'horizontalFilmAperture'
    value = 36.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Vertical Film Aperture attribute
    attr = 'verticalFilmAperture'
    value = 24.0 / 25.4  # 35mm film in inches.
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Pixel Aspect Ratio attribute
    attr = 'pixelAspect'
    value = 1.0
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.001,
        defaultValue=value)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Horizontal Film Offset attribute
    attr = 'horizontalFilmOffset'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.0,
        defaultValue=0.0)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Vertical Film Offset attribute
    attr = 'verticalFilmOffset'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        at='double',
        minValue=0.0,
        defaultValue=0.0)
    maya.cmds.setAttr(tfm + '.' + attr, keyable=True)

    # Image Sequence attribute
    attr = 'imageSequence'
    maya.cmds.addAttr(
        tfm,
        longName=attr,
        dataType='string')

    # Display Mode
    maya.cmds.addAttr(
        tfm,
        longName='displayMode',
        attributeType='enum',
        enumName='Live:Baked:')
    maya.cmds.setAttr(
        tfm + '.displayMode',
        edit=True, keyable=True)

    # Add message attributes
    maya.cmds.addAttr(
        tfm,
        longName='shaderFileNode',
        attributeType='message')
    maya.cmds.addAttr(
        tfm,
        longName='imagePlaneShapeNode',
        attributeType='message')

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
        maya.cmds.connectAttr(tfm + '.' + attr, mkr_scl + '.' + attr)

    attrs = [
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'pixelAspect',
        'horizontalFilmOffset',
        'verticalFilmOffset'
    ]
    for attr in attrs:
        maya.cmds.connectAttr(tfm + '.' + attr, deform_node + '.' + attr)

    # Connect marker scale to transform node.
    maya.cmds.connectAttr(mkr_scl + '.outScale', tfm + '.scale')
    maya.cmds.connectAttr(mkr_scl + '.outTranslateX', tfm + '.translateX')
    maya.cmds.connectAttr(mkr_scl + '.outTranslateY', tfm + '.translateY')

    # Connect inverted depth to the transform TZ.
    maya.cmds.connectAttr(mkr_scl + '.depth', inv_mult + '.input1Z')
    maya.cmds.connectAttr(inv_mult + '.outputZ', tfm + '.translateZ')
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
    return tfm, shp, deform_node


def set_image_plane_values(cam, baked_shp, live_tfm, deform_node):
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
        maya.cmds.connectAttr(src, dst)

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
            maya.cmds.connectAttr(src, dst)

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


def _expand_image_sequence_path(image_sequence_path, format_style):
    start = None
    end = None
    file_pattern = image_sequence_path
    if format_style == const.FORMAT_STYLE_MAYA:
        # file.<f>.png
        pass
    elif format_style == const.FORMAT_STYLE_STANDARD:
        # file.####.png
        pass
    is_seq = start is not None or end is not None
    return file_pattern, start, end, is_seq


def create_baked_image_plane_node(cam_tfm):
    name = 'bakedImagePlane1'
    img_pl_tfm, img_pl_shp = maya.cmds.imagePlane(
        camera=cam_tfm,
        name=name)
    return img_pl_tfm, img_pl_shp


def set_image_sequence(tfm, image_sequence_path):
    # format_style = const.FORMAT_STYLE_STANDARD
    # file_pattern, start, end, is_seq = _expand_image_sequence_path(
    #     image_sequence_path,
    #     format_style)

    maya.cmds.setAttr(
        tfm + '.imageSequence',
        image_sequence_path,
        type='string')
    return


def set_shader_file_path(image_plane_tfm, image_sequence_path):
    file_node = _get_image_plane_file_node(image_plane_tfm)
    if file_node is None:
        LOG.warn('file node is invalid.')
        return

    format_style = const.FORMAT_STYLE_STANDARD
    file_pattern, start, end, is_seq = _expand_image_sequence_path(
        image_sequence_path,
        format_style)

    maya.cmds.setAttr(
        file_node + '.fileTextureName',
        image_sequence_path,
        type='string')
    maya.cmds.setAttr(file_node + '.useFrameExtension', is_seq)
    return


def set_image_plane_file_path(image_plane_tfm, image_sequence_path):
    image_plane_shp = _get_image_plane_baked_shape_node(image_plane_tfm)
    if image_plane_shp is None:
        LOG.warn('file node is invalid.')
        return

    format_style = const.FORMAT_STYLE_STANDARD
    file_pattern, start, end, is_seq = _expand_image_sequence_path(
        image_sequence_path,
        format_style)

    maya.cmds.setAttr(
        image_plane_shp + '.imageName',
        image_sequence_path,
        type='string')
    maya.cmds.setAttr(image_plane_shp + '.useFrameExtension', is_seq)
    return


def create_image_plane_shader(image_plane_tfm):
    """Create an image plane shader, to display an image sequence in Maya
    on a Polygon image plane.
    """
    obj_nodes = [image_plane_tfm]

    file_place2d = maya.cmds.shadingNode('place2dTexture', asUtility=True)
    file_node = maya.cmds.shadingNode('file', asTexture=True, isColorManaged=True)
    shd_node = maya.cmds.shadingNode('surfaceShader', asShader=True)
    sg_node = maya.cmds.sets(renderable=True, noSurfaceShader=True, empty=True)

    src = file_node + '.outColor'
    dst = shd_node + '.outColor'
    maya.cmds.connectAttr(src, dst, force=True)

    src = shd_node + '.outColor'
    dst = sg_node + '.surfaceShader'
    maya.cmds.connectAttr(src, dst, force=True)

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
        maya.cmds.connectAttr(src, dst, force=True)

    # Assign shader.
    maya.cmds.sets(obj_nodes, edit=True, forceElement=sg_node)
    return sg_node, shd_node, file_node


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
    if baked_shp is None:
        baked_tfm, baked_shp = \
            create_baked_image_plane_node(cam_tfm)

    # Convert Maya image plane into a polygon image plane.
    poly_tfm, poly_shp, deform_node = create_image_poly_plane(name='imagePlane1')
    poly_tfm = set_image_plane_values(
        cam,
        baked_shp,
        poly_tfm,
        deform_node)

    # Connect Display mode to live/baked nodes.
    display_mode_expr = const.DISPLAY_MODE_EXPRESSION.format(
        image_plane_tfm=poly_tfm,
        baked_image_plane_shape=baked_shp,
        live_image_plane_shape=poly_shp)
    display_mode_expr = display_mode_expr.replace('{{', '{')
    display_mode_expr = display_mode_expr.replace('}}', '}')
    display_mode_expr_node = maya.cmds.expression(string=display_mode_expr)

    # Get file path and create new shader assignment for poly image
    # plane.
    sg_node, shd_node, file_node = create_image_plane_shader(poly_tfm)

    # Shortcut connections to nodes.
    maya.cmds.connectAttr(file_node + '.message', poly_tfm + '.shaderFileNode')
    maya.cmds.connectAttr(baked_shp + '.message', poly_tfm + '.imagePlaneShapeNode')

    # Image sequence.
    image_sequence_path = _get_default_image()
    set_image_sequence(poly_tfm, image_sequence_path)
    set_shader_file_path(poly_tfm, image_sequence_path)
    set_image_plane_file_path(poly_tfm, image_sequence_path)
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
        img_poly_plane_tfm, img_poly_plane_shp, deform_node = create_image_poly_plane()
        set_image_plane_values(cam, image_plane_shp, img_poly_plane_tfm, deform_node)

        # Get file path and create new shader assignment for poly
        # image plane.
        sg_node, shd_node, file_node = create_image_plane_shader(img_poly_plane_tfm)

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(image_plane_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(image_plane_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(image_plane_shp + '.visibility', False)
    return