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

import maya.cmds
import mmSolver.logger
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def get_camera(node):
    """
    Get both transform and shape node of a camera.

    :param node: Part of the camera node, must be either a transform
                 or shape node.
    :type node: str

    :returns: Two nodes in a tuple, transform then shape node.
    :rtype: (str, str)
    """
    cam_tfm = None
    cam_shp = None
    node_type = maya.cmds.nodeType(node)
    if node_type == 'camera':
        cam_shp = node_utils.get_long_name(node)
        nodes = maya.cmds.listRelatives(
            cam_shp,
            parent=True,
            fullPath=True
        ) or []
        cam_tfm = nodes[0]
    elif node_type == 'transform':
        cam_tfm = node_utils.get_long_name(node)
        nodes = maya.cmds.listRelatives(
            cam_tfm,
            shapes=True,
            fullPath=True
        ) or []
        cam_shp = nodes[0]
    else:
        msg = 'Node type not recognised as a camera! node_type=%r'
        LOG.error(msg, node_type)
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
