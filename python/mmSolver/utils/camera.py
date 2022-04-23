# Copyright (C) 2019 David Cattermole.
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
Camera related functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def get_camera(node):
    """
    Get both transform and shape node of a camera.

    :param node: Part of the camera node, must be either a transform
                 or shape node.
    :type node: str

    :returns: Two nodes in a tuple, transform then shape node.
    :rtype: (str, str) or (None, None)
    """
    cam_tfm = None
    cam_shp = None
    inherited_node_types = maya.cmds.nodeType(node, inherited=True) or []
    if 'camera' in inherited_node_types:
        cam_shp = node_utils.get_long_name(node)
        nodes = maya.cmds.listRelatives(
            cam_shp,
            parent=True,
            fullPath=True
        ) or []
        cam_tfm = nodes[0]
    elif 'transform' in inherited_node_types:
        cam_tfm = node_utils.get_long_name(node)
        nodes = maya.cmds.listRelatives(
            cam_tfm,
            shapes=True,
            type='camera',
            fullPath=True
        ) or []
        if len(nodes) > 0:
            cam_shp = nodes[0]
        else:
            cam_tfm = None
            cam_shp = None
    else:
        node_type = maya.cmds.nodeType(node)
        msg = ('Node type not recognised as a camera! '
               'node=%r node_type=%r')
        LOG.warn(msg, node, node_type)
    return cam_tfm, cam_shp


def is_startup_cam(node):
    """
    Return True if the given camera node is a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return maya.cmds.camera(node, query=True, startupCamera=True) is True


def is_not_startup_cam(node):
    """
    Return True if the given camera node is NOT a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return is_startup_cam(node) is False


def get_image_plane_shapes_from_camera(cam_tfm, cam_shp):
    """
    Get the list of image plane shape nodes connected to the given camera.

    :param cam_tfm: Camera transform node.
    :type cam_tfm: str

    :param cam_shp: Camera shape node.
    :type cam_shp: str

    :returns: The list of image shape nodes, may be an empty list.
    :rtype: [str, ..]
    """
    assert isinstance(cam_tfm, pycompat.TEXT_TYPE)
    assert len(cam_tfm) > 0
    assert maya.cmds.objExists(cam_tfm)
    assert isinstance(cam_shp, pycompat.TEXT_TYPE)
    assert len(cam_shp) > 0
    assert maya.cmds.objExists(cam_shp)
    assert node_utils.attribute_exists('imagePlane', cam_shp)
    plug = '{0}.imagePlane'.format(cam_shp)
    img_pl_shps = maya.cmds.listConnections(
        plug,
        type='imagePlane',
        shapes=True) or []
    img_pl_shps = [node_utils.get_long_name(n) for n in img_pl_shps]
    img_pl_shps = [n for n in img_pl_shps if n is not None]
    return img_pl_shps
