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

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat

import mmSolver.tools.createimageplane.constant as const
import mmSolver.tools.createimageplane.lib.utilities as lib_utils
import mmSolver.tools.createimageplane.lib.shader as lib_shader
import mmSolver.tools.createimageplane.lib.mmimageplane as lib_mmimageplane
import mmSolver.tools.createimageplane.lib.polyplane as lib_polyplane
import mmSolver.tools.createimageplane.lib.nativeimageplane as lib_nativeimageplane

LOG = mmSolver.logger.get_logger()


def create_image_plane_on_camera(cam, name=None):
    """Create an Image Plane that can be distorted in Maya's viewport
    (realtime).
    """
    if name is None:
        name = 'mmImagePlane1'
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(name, pycompat.TEXT_TYPE)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    mm_ip_tfm = lib_mmimageplane.create_transform_node(name, cam_tfm, cam_shp)

    poly_plane_name = name + 'MeshShape'
    poly_plane_network = lib_polyplane.create_poly_plane(
        poly_plane_name,
        mm_ip_tfm,
        cam_shp)

    name_shade = name + 'Shader'
    shader_network = lib_shader.create_network(name_shade, mm_ip_tfm)

    name_img_shp = name + 'Shape'
    mm_ip_shp = lib_mmimageplane.create_shape_node(
        name_img_shp,
        mm_ip_tfm,
        cam_shp,
        poly_plane_network,
        shader_network
    )

    # Shortcut connections to nodes.
    lib_utils.force_connect_attr(
        shader_network.file_node + '.message',
        mm_ip_tfm + '.shaderFileNode')

    # Logic to calculate the frame number.
    frame_expr = const.FRAME_EXPRESSION.format(node=mm_ip_shp)
    frame_expr = frame_expr.replace('{{', '{')
    frame_expr = frame_expr.replace('}}', '}')
    frame_expr_node = maya.cmds.expression(string=frame_expr)

    # Show the users the final frame number.
    shp_node_attr = mm_ip_shp + '.imageSequenceFrameOutput'
    maya.cmds.setAttr(shp_node_attr, lock=True)

    # Set useFrameExtension temporarily. Setting useFrameExtension to
    # False causes frameOffset to be locked (but we need to edit it).
    is_seq = maya.cmds.getAttr(shader_network.file_node + '.useFrameExtension')
    maya.cmds.setAttr(shader_network.file_node + '.useFrameExtension', True)

    file_node_attr = shader_network.file_node + '.frameExtension'
    lib_utils.force_connect_attr(shp_node_attr, file_node_attr)
    maya.cmds.setAttr(file_node_attr, lock=True)

    maya.cmds.setAttr(shader_network.file_node + '.useFrameExtension', is_seq)

    # Image sequence.
    image_sequence_path = lib_utils.get_default_image()
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
    image_planes = camera_utils.get_image_plane_shapes_from_camera(
        cam_tfm, cam_shp)

    ip_node_pairs = []
    for native_ip_shp in image_planes:
        # Convert Maya image plane into a polygon image plane.
        name = 'mmImagePlane1'
        mm_ip_tfm = lib_mmimageplane.create_transform_node(
            name, cam_tfm, cam_shp)

        poly_plane_name = name + 'MeshShape'
        poly_plane_network = lib_polyplane.create_poly_plane(
            poly_plane_name,
            mm_ip_tfm,
            cam_shp)

        lib_nativeimageplane.copy_depth_value(
            mm_ip_tfm,
            native_ip_shp)

        name_shader = name + 'Shader'
        shader_network = lib_shader.create_network(name_shader, mm_ip_tfm)

        name_img_shp = name + 'Shape'
        mm_ip_shp = lib_mmimageplane.create_shape_node(
            name_img_shp,
            mm_ip_tfm,
            cam_shp,
            poly_plane_network,
            shader_network)

        # Disable/hide the Maya image plane.
        maya.cmds.setAttr(native_ip_shp + '.displayMode', 0)  # 0 = 'None' mode
        maya.cmds.setAttr(native_ip_shp + '.type', 1)  # 1 = 'Texture' mode.
        maya.cmds.setAttr(native_ip_shp + '.visibility', False)

        ip_node_pairs.append((mm_ip_tfm, mm_ip_shp))

    return ip_node_pairs


def set_image_sequence(mm_ip_tfm, image_sequence_path):
    shp = lib_mmimageplane.get_shape_node(mm_ip_tfm)
    if shp is None:
        LOG.warn('mmImagePlaneShape node could not be found.')
    file_node = lib_mmimageplane.get_file_node(mm_ip_tfm)
    if file_node is None:
        LOG.warn('mmImagePlane shader file node is invalid.')

    if shp is not None:
        lib_mmimageplane.set_image_sequence(shp, image_sequence_path)
    if file_node is not None:
        lib_shader.set_file_path(file_node, image_sequence_path)
    return


# Stop users from accessing the internal functions of this sub-module.
__all__ = [
    'create_image_plane_on_camera',
    'convert_image_planes_on_camera',
    'set_image_sequence'
]