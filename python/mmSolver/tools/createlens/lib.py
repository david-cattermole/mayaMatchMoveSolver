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
Library functions for creating and modifying Lenses.


Use Case::

1) Select a camera.

2) Add a Lens node to the camera.

   - This will convert the image plane(s) to polygons.

   - This will convert the markers to be undistorted.

3) Solve the lens distortion.

4) Select Camera, switch to 'distorted' mode.

   - The Markers under the camera are now distorted.

   - When solving a lens node, the lens model is always turned on
     before solving.

5) Change the Marker positions however needed.

6) Solve the lens distortion.

   - Lens distortion is automatically turned on before solving.

"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as utils_camera

LOG = mmSolver.logger.get_logger()


def create_image_poly_plane():
    """
    Create a default polygon image plane under camera.
    """
    tfm, creator = maya.cmds.polyPlane(
        axis=(0.0, 0.0, 1.0),
        subdivisionsWidth=32,
        subdivisionsHeight=32,
    )
    # TODO: Make the polygon image plane non-selectable.
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


def set_image_plane_values(cam, img_poly_plane_tfm, deform_node, image_plane):
    """Set the values of a polygon image plane with a regular Maya image
    plane.

    This function is intended to match/sync the exact same image plane
    settings on the polygon image plane.

    The camera is also set to whatever camera is given.

    """
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    maya.cmds.parent(img_poly_plane_tfm, cam_tfm, relative=True)

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

    # TODO: Copy the image plane 'depth' attribute value to the
    #  poly image plane.
    return


def set_lens_mode(cam, mode):
    """
    Sets the plate mode, distort or undistort.
    """
    assert mode in ['distort', 'undistort']
    assert isinstance(cam, mmapi.Camera)

    # Get all markers under the camera.
    mkr_list = cam.get_marker_list()
    mkr_nodes = [mkr.get_node() for mkr in mkr_list]

    # Ensure Marker have connections to the camera lens.
    cam_shp = cam.get_shape_node()
    for mkr_node in mkr_nodes:
        src = cam_shp + '.outLens'
        dst = mkr_node + '.inLens'
        # TODO: Ensure marker transform has an 'inLens' attribute.
        # maya.cmds.connectAttr(src, dst)
        LOG.warn('ConnectAttr: %r %r', src, dst)

    if mode == 'undistort':
        cam.set_lens_enable(True)
    else:
        cam.set_lens_enable(False)
    return


def create_image_plane_shader(tfm):
    """Create an image plane shader, to display an image sequence in Maya
    on a Polygon image plane.
    """
    # TODO: Create a shader network to display an image sequence.
    sg_node = None
    shd_node = None
    file_node = None
    return sg_node, shd_node, file_node


def create_lens_on_camera(cam, force_create_new=None):
    """
    Create a lens node on the given camera.

    Create a mmLensBasic node and connect it to the camera.

    Add a 'lens' attribute to the camera. This 'camera.lens' dynamic
    attribute will fan-out and connect to each Marker as needed.

    """
    assert isinstance(cam, mmapi.Camera)
    if force_create_new is None:
        force_create_new = False
    assert isinstance(force_create_new, bool)
    lens = cam.get_lens()
    if lens is None or force_create_new is True:
        # Create a mmSolver.api.Lens() object, connect lens to the camera.
        lens = mmapi.Lens().create_node()
        cam.set_lens(lens)
    return lens


def create_image_plane_on_camera(cam):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    assert isinstance(cam, mmapi.Camera)

    # Find first image plane currently on the camera.
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    image_planes = utils_camera.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    if len(image_planes) > 0:
        image_plane_shp = image_planes[0]

        # Convert Maya image plane into a polygon image plane.
        img_poly_plane, deform_node = create_image_poly_plane()
        set_image_plane_values(cam, img_poly_plane, deform_node, image_plane_shp)

        # Get file path and create new shader assignment for poly image
        # plane.
        sg_node, shd_node, file_node = create_image_plane_shader(img_poly_plane)

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(image_plane_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(image_plane_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(image_plane_shp + '.visibility', False)
    return
