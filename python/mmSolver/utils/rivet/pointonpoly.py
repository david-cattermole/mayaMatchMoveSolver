# Copyright (C) 2014, 2022, 2023 David Cattermole.
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
Create a Rivet using a Point-On-Poly Constraint.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds

import mmSolver.utils.node as node_utils
import mmSolver.utils.rivet.nearestpointonmesh as nearestpointonmesh_utils
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def _create_locator(name, parent=None):
    tfm = maya.cmds.createNode('transform', name=name, parent=parent)
    tfm = node_utils.get_long_name(tfm)

    name_shp = tfm.split('|')[-1] + 'Shape'
    shp = maya.cmds.createNode('locator', name=name_shp, parent=tfm)
    shp = node_utils.get_long_name(shp)
    return tfm, shp


def _lock_node_attrs(node, attrs, lock=None, keyable=None, channelBox=None):
    assert lock is None or isinstance(lock, bool)
    assert keyable is None or isinstance(keyable, bool)
    assert channelBox is None or isinstance(channelBox, bool)

    kwargs = {}
    if lock is not None:
        kwargs['lock'] = lock
    if keyable is not None:
        kwargs['keyable'] = keyable
    if channelBox is not None:
        kwargs['channelBox'] = channelBox

    for attr in attrs:
        if node_utils.attribute_exists(attr, node):
            node_attr = node + '.' + attr
            maya.cmds.setAttr(node_attr, **kwargs)
    return


def _lock_constraint_offset_attrs(node, lock=None, keyable=None, channelBox=None):
    attrs = ['ox', 'oy', 'oz', 'otx', 'oty', 'otz', 'orx', 'ory', 'orz']
    return _lock_node_attrs(
        node, attrs, lock=lock, keyable=keyable, channelBox=channelBox
    )


def _lock_transform_attrs(node, lock=None, keyable=None, channelBox=None):
    attrs = [
        'tx',
        'ty',
        'tz',
        'rx',
        'ry',
        'rz',
        'sx',
        'sy',
        'sz',
        'shxy',
        'shxz',
        'shyz',
    ]
    return _lock_node_attrs(
        node, attrs, lock=lock, keyable=keyable, channelBox=channelBox
    )


class PointOnPolyConstraintNode(object):
    def __init__(self, node):
        super(PointOnPolyConstraintNode, self).__init__()
        self._node = node

    def get_node(self):
        return self._node

    def get_attr_name_target_u(self):
        attr_name = maya.cmds.connectionInfo(
            self._node + '.target[0].targetU', sourceFromDestination=True
        )
        return attr_name

    def get_attr_name_target_v(self):
        attr_name = maya.cmds.connectionInfo(
            self._node + '.target[0].targetV', sourceFromDestination=True
        )
        return attr_name

    def get_attr_name_target_weight(self):
        attr_name = maya.cmds.connectionInfo(
            self._node + '.target[0].targetWeight', sourceFromDestination=True
        )
        return attr_name


def _create_point_on_poly_constraint(mesh_tfm, rivet_tfm):
    constraint = maya.cmds.pointOnPolyConstraint(mesh_tfm, rivet_tfm, weight=1)
    if len(constraint) == 0:
        msg = 'Could not create point on poly constraint.'
        LOG.error(msg)
        return None

    constraint = constraint[0]
    point_on_poly = PointOnPolyConstraintNode(constraint)

    _lock_constraint_offset_attrs(constraint, lock=True)
    node_attr = constraint + '.target[0].targetUseNormal'
    maya.cmds.setAttr(node_attr, 1)

    _lock_transform_attrs(rivet_tfm, lock=True)

    return point_on_poly


RivetPointOnPoly = collections.namedtuple(
    'RivetPointOnPoly', ['rivet_transform', 'rivet_shape', 'point_on_poly_constraint']
)


def create(
    mesh_transform,
    mesh_shape,
    name=None,
    parent=None,
    coordinate_uv=None,
    in_position=None,
):
    """
    Create a Point-on-Poly Rivet.

    :param name: Name of the Rivet to create.
    :type name: None or str

    :param parent: The parent node of the newly created Rivet.
    :type parent: None or str

    :param coordinate_uv: The default UV Coordinate of the newly created Rivet.
    :type coordinate_uv: None or (float, float)

    :param in_position: The world-space position of the created Rivet,
        if None, fall back to the default coordinate_uv.
    :type in_position: None or (float, float, float)

    :returns: Rivet data structure containing all nodes for rivet.
    :rtype: RivetPointOnPoly
    """
    if name is None:
        name = 'mmRivetPointOnPoly1'
    assert isinstance(name, str)
    assert parent is None or maya.cmds.objExists(parent)
    assert in_position is None or (
        isinstance(in_position, (tuple, list)) and len(in_position) == 3
    )
    if coordinate_uv is None:
        coordinate_uv = (0.5, 0.5)
    assert isinstance(in_position, (tuple, list)) and len(coordinate_uv) == 2

    rivet_tfm, rivet_shp = _create_locator(name, parent=parent)

    point_on_poly = _create_point_on_poly_constraint(mesh_transform, rivet_tfm)
    assert point_on_poly is not None

    coordinate_u = coordinate_uv[0]
    coordinate_v = coordinate_uv[1]
    if in_position is not None:
        nearest_point_data = nearestpointonmesh_utils.get_nearest_point_on_mesh(
            mesh_shape, in_position
        )
        coordinate_u = nearest_point_data.coords[0]
        coordinate_v = nearest_point_data.coords[1]

    # Add attributes and create connections for locator control.
    coord_u_attr_name = 'coordinateU'
    coord_v_attr_name = 'coordinateV'
    maya.cmds.addAttr(
        rivet_tfm,
        longName=coord_u_attr_name,
        shortName='crdu',
        niceName='U',
        at='double',
        defaultValue=coordinate_u,
        keyable=True,
    )
    maya.cmds.addAttr(
        rivet_tfm,
        longName=coord_v_attr_name,
        shortName='crdv',
        niceName='V',
        at='double',
        defaultValue=coordinate_v,
        keyable=True,
    )
    rivet_attr_name_u = point_on_poly.get_attr_name_target_u()
    rivet_attr_name_v = point_on_poly.get_attr_name_target_v()
    rivet_tfm_coord_u_attr = '{}.{}'.format(rivet_tfm, coord_u_attr_name)
    rivet_tfm_coord_v_attr = '{}.{}'.format(rivet_tfm, coord_v_attr_name)
    maya.cmds.connectAttr(rivet_tfm_coord_u_attr, rivet_attr_name_u)
    maya.cmds.connectAttr(rivet_tfm_coord_v_attr, rivet_attr_name_v)
    _lock_node_attrs(
        point_on_poly.get_node(), [rivet_attr_name_u, rivet_attr_name_v], lock=True
    )

    rivet = RivetPointOnPoly(
        rivet_transform=rivet_tfm,
        rivet_shape=rivet_shp,
        point_on_poly_constraint=point_on_poly,
    )
    return rivet
