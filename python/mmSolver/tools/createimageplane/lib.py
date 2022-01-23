# Copyright (C) 2020 David Cattermole.
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

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as utils_camera
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def create_image_poly_plane(name=None):
    """
    Create a default polygon image plane under camera.
    """
    assert name is None or isinstance(name, pycompat.TEXT_TYPE)
    tfm, creator = maya.cmds.polyPlane(
        axis=(0.0, 0.0, 1.0),
        subdivisionsWidth=32,
        subdivisionsHeight=32,
        name=name,
    )

    # Make the polygon image plane non-selectable.
    display_type = 2  # 2 = 'Reference'
    maya.cmds.setAttr(tfm + '.overrideEnabled', 1)
    maya.cmds.setAttr(tfm + '.overrideDisplayType', display_type)

    shp = maya.cmds.listRelatives(tfm, shapes=True)[0]
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
    return tfm, deform_node


def set_image_plane_values(cam, image_plane_shp, img_poly_plane_tfm, deform_node):
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
        dst = img_poly_plane_tfm + '.' + attr
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)

    # Copy the image plane 'depth' attribute value to the poly image
    # plane.
    if image_plane_shp is not None:
        src = image_plane_shp + '.depth'
        dst = img_poly_plane_tfm + '.depth'
        value = maya.cmds.getAttr(src)
        maya.cmds.setAttr(dst, value)

    # Parent the transform under the camera.
    img_poly_plane_tfm_uuid = maya.cmds.ls(img_poly_plane_tfm, uuid=True)[0]
    maya.cmds.parent(img_poly_plane_tfm, cam_tfm, relative=True)
    img_poly_plane_tfm = maya.cmds.ls(img_poly_plane_tfm_uuid, long=True)[0]
    return img_poly_plane_tfm


def create_image_plane_shader(tfm, image_plane_shp):
    """Create an image plane shader, to display an image sequence in Maya
    on a Polygon image plane.
    """
    # TODO: Create a shader network to display an image sequence.
    sg_node = None
    shd_node = None
    file_node = None
    return sg_node, shd_node, file_node


def create_poly_image_plane_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_plane_shps = utils_camera.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    image_plane_shp = None
    if len(image_plane_shps) > 0:
        image_plane_shp = image_plane_shps[0]

    # Convert Maya image plane into a polygon image plane.
    img_poly_plane, deform_node = create_image_poly_plane(name='imagePlane1')
    img_poly_plane = set_image_plane_values(cam, image_plane_shp, img_poly_plane, deform_node)

    # Get file path and create new shader assignment for poly image
    # plane.
    # TODO: Get the file path.
    sg_node, shd_node, file_node = create_image_plane_shader(img_poly_plane, image_plane_shp)
    return img_poly_plane


def convert_image_planes_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)

    # Find image plane currently on the camera.
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_planes = utils_camera.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    for image_plane_shp in image_planes:
        # Convert Maya image plane into a polygon image plane.
        img_poly_plane, deform_node = create_image_poly_plane()
        set_image_plane_values(cam, image_plane_shp, img_poly_plane, deform_node)

        # Get file path and create new shader assignment for poly image
        # plane.
        sg_node, shd_node, file_node = create_image_plane_shader(img_poly_plane)

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(image_plane_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(image_plane_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(image_plane_shp + '.visibility', False)
    return
