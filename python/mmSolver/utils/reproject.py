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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()


def get_camera_direction_to_world_position(camera_node, world_position):
    """
    Get the direction of the camera toward a given world space position.

    The direction vector is normalised.

    The camera position is evaluated at the current frame only.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param world_position: World position; X, Y and Z values.
    :type world_position: (float, float, float)

    :return: Direction from camera to point.
    :rtype: (float, float, float)
    """
    assert len(world_position) == 3
    cam = maya.cmds.xform(camera_node, query=True, worldSpace=True, translation=True)
    cam_vec = maya.OpenMaya.MVector(*cam)
    obj_vec = maya.OpenMaya.MVector(*world_position)
    distance = obj_vec - cam_vec
    length = maya.OpenMaya.MVector(distance).length()
    direction = distance / length
    x, y, z = direction.x, direction.y, direction.z
    return x, y, z


def get_camera_direction_to_point(camera_node, point_node):
    """
    Get the direction of the camera toward a given point.

    The direction vector is normalised.

    The camera position is evaluated at the current frame only.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param point_node: Transform node to aim at.
    :type point_node: str

    :return: Direction from camera to point.
    :rtype: (float, float, float)
    """
    assert isinstance(camera_node, pycompat.TEXT_TYPE)
    assert isinstance(point_node, pycompat.TEXT_TYPE)
    world_position = maya.cmds.xform(
        point_node, query=True, worldSpace=True, translation=True
    )
    return get_camera_direction_to_world_position(camera_node, world_position)


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


def _find_auxiliary_set_nodes(point_from_set_node):
    """
    Find all the reprojection nodes on the camera.
    """
    nodes = []

    object_set_nodes = (
        maya.cmds.listConnections(
            point_from_set_node + '.set',
            source=True,
            destination=False,
            type='objectSet',
            exactType=True,
            skipConversionNodes=True,
        )
        or []
    )
    nodes += object_set_nodes

    # transform_plugs = (
    #     maya.cmds.listConnections(
    #         point_from_set_node + '.matrix',
    #         source=True,
    #         destination=False,
    #         plugs=True,
    #         type='transform',
    #         exactType=False,
    #         skipConversionNodes=True,
    #     )
    #     or []
    # )
    # # nodes += transform_nodes

    # mesh_plugs = (
    #     maya.cmds.listConnections(
    #         point_from_set_node + '.mesh',
    #         source=True,
    #         destination=False,
    #         plugs=True,
    #         type='mesh',
    #         exactType=True,
    #         skipConversionNodes=True,
    #     )
    #     or []
    # )
    # # nodes += mesh_nodes

    return nodes


def _find_auxiliary_reprojection_nodes(reprojection_node):
    """
    Find all the reprojection nodes on the camera.
    """
    nodes = []

    # Get connected MultiplyDivide nodes connected.
    mult_nodes = (
        maya.cmds.listConnections(
            reprojection_node + '.imageWidth',
            reprojection_node + '.imageHeight',
            source=True,
            destination=False,
            type='multiplyDivide',
            exactType=True,
            skipConversionNodes=True,
        )
        or []
    )
    nodes += mult_nodes

    # Get connected offset PlusMinusAverage nodes.
    offset_plusminus_nodes = (
        maya.cmds.listConnections(
            reprojection_node + '.outPan',
            source=False,
            destination=True,
            type='plusMinusAverage',
            exactType=True,
            skipConversionNodes=True,
        )
        or []
    )
    nodes += offset_plusminus_nodes

    # Get connected mmPointFromObjectSet nodes.
    point_from_set_nodes = (
        maya.cmds.listConnections(
            reprojection_node + '.transformWorldMatrix',
            source=True,
            destination=False,
            type='mmPointFromObjectSet',
            exactType=True,
            skipConversionNodes=True,
        )
        or []
    )
    nodes += point_from_set_nodes

    return nodes


def _find_object_set_nodes(reproj_node):
    reproj_aux_nodes = _find_auxiliary_reprojection_nodes(reproj_node)
    point_from_set_nodes = [
        x for x in reproj_aux_nodes if maya.cmds.nodeType(x) == 'mmPointFromObjectSet'
    ]
    set_nodes = []
    for point_from_set_node in point_from_set_nodes:
        set_nodes += _find_auxiliary_set_nodes(point_from_set_node)

    return list(sorted(set(set_nodes + point_from_set_nodes)))


def find_reprojection_nodes(cam_tfm, cam_shp):
    """
    Find all the reprojection nodes on the camera.
    """
    nodes = (
        maya.cmds.listConnections(
            cam_shp + '.focalLength',
            source=False,
            destination=True,
            type='mmReprojection',
            exactType=True,
            skipConversionNodes=True,
        )
        or []
    )
    if not nodes:
        return nodes
    reprojection_node = nodes[0]

    # Get the other nodes.
    nodes += _find_auxiliary_reprojection_nodes(reprojection_node)
    nodes += _find_object_set_nodes(reprojection_node)
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


def _cleanup_object_set_nodes(reproj_node):
    old_nodes = _find_object_set_nodes(reproj_node)
    if len(old_nodes) > 0:
        maya.cmds.delete(old_nodes)
    return len(old_nodes)


def connect_transform_to_reprojection(tfm, reproj_node):
    """
    Connect 'tfm' to the reprojection node, 'reproj_node'.

    :param tfm: Transform node name to be connected.
    :type tfm: str

    :param reproj_node: The re-projection node.
    :type reproj_node: str
    """
    _cleanup_object_set_nodes(reproj_node)

    src = tfm + '.worldMatrix'
    dst = reproj_node + '.transformWorldMatrix'
    maya.cmds.connectAttr(src, dst, force=True)
    return


def connect_objects_to_reprojection(objects, reproj_node):
    """
    Connect all the objects and components in 'objects' to the
    reprojection node, 'reproj_node'.

    :param objects:
    :type objects: str

    :param reproj_node: The re-projection node.
    :type reproj_node: str

    """
    _cleanup_object_set_nodes(reproj_node)

    point_from_set_node = maya.cmds.createNode('mmPointFromObjectSet')
    set_node = maya.cmds.sets(objects, name=reproj_node + '_center_objectSet')
    maya.cmds.connectAttr(
        set_node + '.message', point_from_set_node + '.set', force=True
    )

    nodes = maya.cmds.ls(objects, objectsOnly=True, long=True)
    for i, node in enumerate(nodes):
        if not node.startswith('|'):
            # Only DAG objects can be connected.
            continue

        # Both shapes and transforms should always contain a
        # worldMatrix attribute.
        src = node + '.worldMatrix[0]'
        dst = point_from_set_node + '.matrix[{}]'.format(i)
        maya.cmds.connectAttr(src, dst, force=True)

        node_type = maya.cmds.nodeType(node)
        if node_type == 'mesh':
            src = node + '.worldMesh[0]'
            dst = point_from_set_node + '.mesh[{}]'.format(i)
            maya.cmds.connectAttr(src, dst, force=True)

    src = point_from_set_node + '.outMatrix'
    dst = reproj_node + '.transformWorldMatrix'
    maya.cmds.connectAttr(src, dst, force=True)
    return
