# Copyright (C) 2022, 2023 David Cattermole.
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
The 'rivet.mel technique' for creating rivets.

'rivet.mel' was written by Michael Bazhutkin in 2001.
https://www.highend3d.com/maya/script/rivet-button-for-maya

This method uses polygon edges converted into NURBS curves, then
placing a point at the average of two different NURBS curves.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


RivetMeshTwoEdge = collections.namedtuple(
    'RivetMeshTwoEdge',
    [
        'rivet_transform',
        'rivet_shape',
        'constraint_node',
        'loft_node',
        'point_on_surface_info_node',
        'curve_from_mesh_edge_a_node',
        'curve_from_mesh_edge_b_node',
    ],
)


def create(mesh_shape, edge_a, edge_b, name=None):
    """
    Create a Rivet position between two edges.

    :param mesh_shape: Mesh shape node.
    :type mesh_shape: str

    :param edge_a: First edge component path.
    :type edge_a: str

    :param edge_b: Second edge component path.
    :type edge_b: str

    :returns: A rivet object containing names to all the nodes.
    :rtype: RivetMeshTwoEdge
    """
    assert maya.cmds.objExists(mesh_shape)
    assert maya.cmds.objExists(edge_a)
    assert maya.cmds.objExists(edge_b)
    if name is None:
        name = 'mmRivetMeshTwoEdge1'
    assert isinstance(name, str)

    edge_index_a = edge_a.split('[')[-1]
    edge_index_b = edge_b.split('[')[-1]
    edge_index_a = int(edge_index_a.split(']')[0])
    edge_index_b = int(edge_index_b.split(']')[0])

    # Create Curve From Edge A.
    curve_from_mesh_edge_a = maya.cmds.createNode(
        'curveFromMeshEdge', name='mmRivetCurveFromMeshEdge_a1'
    )
    maya.cmds.setAttr(curve_from_mesh_edge_a + '.isHistoricallyInteresting', 1)
    maya.cmds.setAttr(curve_from_mesh_edge_a + '.edgeIndex[0]', edge_index_a)

    # Create Curve From Edge B.
    curve_from_mesh_edge_b = maya.cmds.createNode(
        'curveFromMeshEdge', name='mmRivetCurveFromMeshEdge_b1'
    )
    maya.cmds.setAttr(curve_from_mesh_edge_b + '.isHistoricallyInteresting', 1)
    maya.cmds.setAttr(curve_from_mesh_edge_b + '.edgeIndex[0]', edge_index_b)

    # Create Loft node.
    loft_node = maya.cmds.createNode('loft', name='mmRivetLoft1')
    maya.cmds.setAttr(loft_node + '.inputCurve', size=2)
    maya.cmds.setAttr(loft_node + '.uniform', True)
    maya.cmds.setAttr(loft_node + '.reverseSurfaceNormals', True)

    # Create Point On Surface Info.
    surface_info = maya.cmds.createNode(
        'pointOnSurfaceInfo', name='mmRivetPointOnSurfaceInfo1'
    )
    maya.cmds.setAttr(surface_info + '.turnOnPercentage', 1)
    maya.cmds.setAttr(surface_info + '.parameterU', 0.5)
    maya.cmds.setAttr(surface_info + '.parameterV', 0.5)

    maya.cmds.connectAttr(
        loft_node + '.outputSurface',
        surface_info + '.inputSurface',
        force=True,
    )
    output_surface_attr_a = curve_from_mesh_edge_a + '.outputCurve'
    output_surface_attr_b = curve_from_mesh_edge_b + '.outputCurve'
    maya.cmds.connectAttr(output_surface_attr_a, loft_node + '.inputCurve[0]')
    maya.cmds.connectAttr(output_surface_attr_b, loft_node + '.inputCurve[1]')
    mesh_world_mesh_attr = mesh_shape + '.worldMesh'
    maya.cmds.connectAttr(mesh_world_mesh_attr, curve_from_mesh_edge_a + '.inputMesh')
    maya.cmds.connectAttr(mesh_world_mesh_attr, curve_from_mesh_edge_b + '.inputMesh')

    # Create Locator.
    rivet_tfm = maya.cmds.createNode('transform', name=name)
    rivet_shp_name = rivet_tfm.split('|')[-1] + 'Shape'
    rivet_shp = maya.cmds.createNode('locator', name=rivet_shp_name, parent=rivet_tfm)

    # Create Aim Constraint.
    aim_constraint = maya.cmds.createNode(
        'aimConstraint', parent=rivet_tfm, name=(rivet_tfm + '_mmRivetAimConstraint1')
    )
    maya.cmds.setAttr(aim_constraint + '.target[0].targetWeight', 1)
    maya.cmds.setAttr(aim_constraint + '.aimVector', 0.0, 1.0, 0.0, typ='double3')
    maya.cmds.setAttr(aim_constraint + '.upVector', 0.0, 0.0, 1.0, typ='double3')
    # Don't show users the aim constraint internals they should not
    # change anyway.
    maya.cmds.setAttr(aim_constraint + '.v', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.tx', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.ty', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.tz', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.rx', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.ry', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.rz', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.sx', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.sy', keyable=False)
    maya.cmds.setAttr(aim_constraint + '.sz', keyable=False)

    maya.cmds.connectAttr(surface_info + '.position', rivet_tfm + '.translate')
    maya.cmds.connectAttr(
        surface_info + '.normal', aim_constraint + '.target[0].targetTranslate'
    )
    maya.cmds.connectAttr(surface_info + '.tangentV', aim_constraint + '.worldUpVector')
    maya.cmds.connectAttr(aim_constraint + '.constraintRotateX', rivet_tfm + '.rotateX')
    maya.cmds.connectAttr(aim_constraint + '.constraintRotateY', rivet_tfm + '.rotateY')
    maya.cmds.connectAttr(aim_constraint + '.constraintRotateZ', rivet_tfm + '.rotateZ')

    # Do not allow users to disconnect or scale the rivet transform.
    attr_names = [
        'translateX',
        'translateY',
        'translateZ',
        'rotateX',
        'rotateY',
        'rotateZ',
        'scaleX',
        'scaleY',
        'scaleZ',
    ]
    for attr_name in attr_names:
        attr = '{}.{}'.format(rivet_tfm, attr_name)
        maya.cmds.setAttr(attr, lock=True)

    rivet = RivetMeshTwoEdge(
        rivet_transform=rivet_tfm,
        rivet_shape=rivet_shp,
        constraint_node=aim_constraint,
        loft_node=loft_node,
        point_on_surface_info_node=surface_info,
        curve_from_mesh_edge_a_node=curve_from_mesh_edge_a,
        curve_from_mesh_edge_b_node=curve_from_mesh_edge_b,
    )
    return rivet
