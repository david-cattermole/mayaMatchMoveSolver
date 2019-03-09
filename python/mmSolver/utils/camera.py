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

    :param node: Part of the camera node, must be either a transform or
    :return:
    """
    cam_tfm = None
    cam_shp = None
    node_type = maya.cmds.nodeType(node)
    if node_type == 'camera':
        cam_shp = node_utils.get_node_full_path(node)
        nodes = maya.cmds.listRelatives(
            cam_shp,
            parent=True,
            fullPath=True
        ) or []
        cam_tfm = nodes[0]
    elif node_type == 'transform':
        cam_tfm = node_utils.get_node_full_path(node)
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


def is_startup_cam(x):
    """
    Return True if the given camera node is a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return maya.cmds.camera(x, query=True, startupCamera=True) is True


def is_not_startup_cam(x):
    """
    Return True if the given camera node is NOT a 'startupCamera'.

    A startup camera is a camera; 'persp', 'side', 'top', 'front', etc.

    :rtype: bool
    """
    return is_startup_cam(x) is False
