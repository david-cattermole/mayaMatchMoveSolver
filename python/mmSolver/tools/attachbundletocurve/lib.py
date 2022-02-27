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
Attach Bundle to Curve tool. Attaches a bundle node to a NURBs curve.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import mmSolver.logger
import mmSolver.tools.attachbundletocurve.constant as const

LOG = mmSolver.logger.get_logger()


def get_nurbs_curve_nodes(nodes):
    """
    Get the NURBS curve shape nodes from the given nodes.

    :param nodes: Nodes to query.
    :type nodes: [str, ..]

    :returns: List of NURBS curve shape nodes.
    :rtype: [str, ..]
    """
    crv_shp_nodes = []
    for node in nodes:
        node_type = maya.cmds.nodeType(node)
        if node_type == 'transform':
            shps = maya.cmds.listRelatives(
                node,
                shapes=True,
                type='nurbsCurve') or []
            crv_shp_nodes += shps
        elif node_type == 'nurbsCurve':
            crv_shp_nodes.append(node)
    crv_shp_nodes = list(set(crv_shp_nodes))
    return crv_shp_nodes


def get_closest_point_on_nurbs_curve(pos, crv_shp_node):
    """
    Get the position along a NURBS curve that is closest to the input position.

    Position is expected to be in world space.

    :param pos: Position of the input to find closest point.
    :type pos: [float, float, float]

    :param crv_shp_node: NURBS curve shape node.
    :type crv_shp_node: str

    :returns: Tuple of world space position and percentage along the NURBS curve.
    :rtype: ([float, float, float], float)
    """
    assert isinstance(pos, (tuple, list))
    assert len(pos) == 3
    assert maya.cmds.objExists(crv_shp_node)

    node = maya.cmds.createNode('nearestPointOnCurve')
    try:
        crv_min = maya.cmds.getAttr(crv_shp_node + '.minValue')
        crv_max = maya.cmds.getAttr(crv_shp_node + '.maxValue')

        src = crv_shp_node + '.worldSpace[0]'
        dst = node + '.inputCurve'
        maya.cmds.connectAttr(src, dst)

        maya.cmds.setAttr(node + '.inPosition', *pos)
        closest_pos = maya.cmds.getAttr(node + '.position')
        closest_param = maya.cmds.getAttr(node + '.parameter')
        closest_param = (closest_param - crv_min) / (crv_max - crv_min)
    finally:
        maya.cmds.delete(node)
    return closest_pos, closest_param


def connect_transform_to_nurbs_curve(tfm_node, crv_shp_node, attr_name):
    """
    Connect a transform node to a NURBS curve.

    The attribute created will range from 0.0 to 1.0, with a default
    value of 0.5.

    :param tfm_node: Transform node to connect to the NURBS curve.
    :type tfm_node: str

    :param crv_shp_node: NURBS curve shape node to connect to.
    :type crv_shp_node: str

    :param attr_name: Attribute name to create on the transform.
    :type attr_name: str

    :returns: A 'pointOnCurveInfo' node name connected between the
              transform and curve.
    :rtype: str
    """
    assert maya.cmds.objExists(tfm_node)
    assert maya.cmds.objExists(crv_shp_node)

    # NOTE: If we add a multipleDivide node to remap the values, the
    # solver will not work. The cause is unknown. We therefore must
    # use only direct connections between the attributes and this
    # seems to work.
    do_remap = const.REMAP_TO_ONE_HUNDRED
    min_value = 0.0
    max_value = 1.0
    default_value = 0.5
    if do_remap is True:
        min_value = 0.0
        max_value = 100.0
        default_value = 50.0

    maya.cmds.addAttr(
        tfm_node,
        longName=attr_name,
        attributeType='double',
        minValue=min_value,
        maxValue=max_value,
        defaultValue=default_value,
        keyable=True)

    info_node = maya.cmds.createNode('pointOnCurveInfo')
    plug = info_node + '.turnOnPercentage'
    maya.cmds.setAttr(plug, 1)
    src = crv_shp_node + '.worldSpace[0]'
    dst = info_node + '.inputCurve'
    maya.cmds.connectAttr(src, dst)

    if do_remap is False:
        src = tfm_node + '.' + attr_name
        dst = info_node + '.parameter'
        maya.cmds.connectAttr(src, dst)
    else:
        mult_node = maya.cmds.createNode('multiplyDivide')
        maya.cmds.setAttr(mult_node + '.input2X', 0.01)
        src = mult_node + '.outputX'
        dst = info_node + '.parameter'
        maya.cmds.connectAttr(src, dst)

        src = tfm_node + '.' + attr_name
        dst = mult_node + '.input1X'
        maya.cmds.connectAttr(src, dst)

    src = info_node + '.position'
    dst = tfm_node + '.translate'
    maya.cmds.connectAttr(src, dst)
    return info_node


def attach_bundle_to_curve(bnd_node, crv_shp_node, attr_name):
    """
    Connect a Bundle node to a NURBS curve, and create an attribute to
    control the position along the curve.

    :param bnd_node: Bundle (transform) node to connect to the NURBS
                     curve.
    :type bnd_node: str

    :param crv_shp_node: NURBS curve shape node to connect to.
    :type crv_shp_node: str

    :param attr_name: Attribute name to create on the bundle node.
    :type attr_name: str

    :returns: The 'node.attr' to be controlled for bundle movement
              along the curve.
    :rtype: str

    """
    pos = maya.cmds.xform(
        bnd_node,
        query=True,
        worldSpace=True,
        translation=True)
    crv_pos, crv_param = get_closest_point_on_nurbs_curve(
        pos,
        crv_shp_node)
    connect_transform_to_nurbs_curve(
        bnd_node,
        crv_shp_node,
        attr_name)
    do_remap = const.REMAP_TO_ONE_HUNDRED
    value = crv_param
    if do_remap is True:
        value = crv_param * 100.0
    plug = bnd_node + '.' + attr_name
    maya.cmds.setAttr(plug, value)
    return plug
