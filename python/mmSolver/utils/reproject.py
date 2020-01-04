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
Re-Projection utilities - converting a 3D transform into a 2D point.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils


LOG = mmSolver.logger.get_logger()


def get_camera_direction_to_point(camera_node, point_node):
    """
    Get the direction of the camera toward a given point.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param point_node: Transform node to aim at.
    :type point_node: str

    :return: Direction from camera to point.
    :rtype: (float, float, float)
    """
    obj = maya.cmds.xform(
        point_node,
        query=True,
        worldSpace=True,
        translation=True)
    cam = maya.cmds.xform(
        camera_node,
        query=True,
        worldSpace=True,
        translation=True)
    cam_vec = maya.OpenMaya.MVector(*cam)
    obj_vec = maya.OpenMaya.MVector(*obj)
    distance = obj_vec - cam_vec
    length = maya.OpenMaya.MVector(distance).length()
    direction = distance / length
    x, y, z = direction.x, direction.y, direction.z
    return x, y, z


def create_reprojection_on_camera(cam_tfm, cam_shp):
    """
    Create a mmReprojection node, then connect it up as needed.
    """
    try:
        node = maya.cmds.createNode('mmReprojection')
    except RuntimeError:
        # Do not force loading the plug-in each time the tool is
        # run, only if an error happens.
        mmapi.load_plugin()
        try:
            node = maya.cmds.createNode('mmReprojection')
        except RuntimeError:
            raise

    # Connect camera attributes
    maya.cmds.connectAttr(cam_tfm + '.worldMatrix', node + '.cameraWorldMatrix')
    maya.cmds.connectAttr(cam_shp + '.focalLength', node + '.focalLength')
    maya.cmds.connectAttr(cam_shp + '.cameraAperture', node + '.cameraAperture')
    maya.cmds.connectAttr(cam_shp + '.filmOffset', node + '.filmOffset')
    maya.cmds.connectAttr(cam_shp + '.filmFit', node + '.filmFit')
    maya.cmds.connectAttr(cam_shp + '.nearClipPlane', node + '.nearClipPlane')
    maya.cmds.connectAttr(cam_shp + '.farClipPlane', node + '.farClipPlane')
    maya.cmds.connectAttr(cam_shp + '.cameraScale', node + '.cameraScale')

    # Connect render settings attributes
    resolution_factor = 10000.0
    mult_node = maya.cmds.createNode('multiplyDivide')
    maya.cmds.setAttr(mult_node + '.input2X', resolution_factor)
    maya.cmds.setAttr(mult_node + '.input2Y', resolution_factor)
    maya.cmds.connectAttr(cam_shp + '.horizontalFilmAperture', mult_node + '.input1X')
    maya.cmds.connectAttr(cam_shp + '.verticalFilmAperture', mult_node + '.input1Y')
    maya.cmds.connectAttr(mult_node + '.outputX', node + '.imageWidth')
    maya.cmds.connectAttr(mult_node + '.outputY', node + '.imageHeight')

    # Connect Pan to camera.pan
    maya.cmds.connectAttr(node + '.outPan', cam_shp + '.pan')

    # Turn on 'Pan/Zoom'
    plug = cam_shp + '.panZoomEnabled'
    locked = maya.cmds.getAttr(plug, lock=True)
    if locked is False:
        maya.cmds.setAttr(plug, True)
    return node


def find_reprojection_nodes(cam_tfm, cam_shp):
    """
    Find all the reprojection nodes on the camera.
    """
    nodes = maya.cmds.listConnections(
        cam_shp + '.pan',
        source=True,
        destination=False,
        type='mmReprojection',
        exactType=True,
        skipConversionNodes=True
    ) or []
    # Get connected MultiplyDivide nodes connected.
    for node in list(nodes):
        mult_nodes = maya.cmds.listConnections(
            node + '.imageWidth',
            node + '.imageHeight',
            source=True,
            destination=False,
            type='multiplyDivide',
            exactType=True,
            skipConversionNodes=True
        ) or []
        nodes += mult_nodes
    return nodes


def remove_reprojection_from_camera(cam_tfm, cam_shp):
    """
    Find the mmReprojection node and delete it.
    """
    nodes = find_reprojection_nodes(cam_tfm, cam_shp)
    for node in reversed(nodes):
        if maya.cmds.objExists(node) is True:
            maya.cmds.delete(node)
    return


def reset_pan_zoom(cam_tfm, cam_shp):
    """
    Reset the Pan/Zoom camera settings.

    :param cam_tfm: Camera transform node
    :type cam_tfm: str

    :param cam_shp: Camera shape node.
    :type cam_shp: str

    :rtype: None
    """
    plugs = [
        (cam_shp + '.horizontalPan', 0.0),
        (cam_shp + '.verticalPan', 0.0),
        (cam_shp + '.zoom', 1.0),
        (cam_shp + '.panZoomEnabled', False),
    ]
    for plug, value in plugs:
        node_utils.set_attr(plug, value, relock=True)
    return


def connect_transform_to_reprojection(tfm, reproj):
    src = tfm + '.worldMatrix'
    dst = reproj + '.transformWorldMatrix'
    maya.cmds.connectAttr(src, dst)
    return