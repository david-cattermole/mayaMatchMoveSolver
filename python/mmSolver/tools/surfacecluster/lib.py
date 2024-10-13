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
Functions to create and edit Surface Clusters.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.rivet.nearestpointonmesh as nearestpointonmesh
import mmSolver.utils.rivet.pointonpoly as rivet_pointonpoly
import mmSolver.utils.selection as selection_utils


LOG = mmSolver.logger.get_logger()
OPEN_PAINT_EDITOR_MEL_CMD = (
    'artSetToolAndSelectAttr("artAttrCtx", "cluster.{node}.weights");'
    # Show Widow
    'toolPropertyWindow;'
    'toolPropertyShow;'
    # Set weight slider to 1.0.
    'artAttrPaintOperation artAttrCtx Replace;'
    'artAttrCtx -e -value 1.0 `currentCtx`;'
    'artAttrValues artAttrContext;'
)


def _lock_node_attr(nodeAttr, lock=True, keyable=False, channelBox=False):
    node = nodeAttr.split('.')[0]
    attr = nodeAttr[len(node) + 1 :]
    if node_utils.attribute_exists(attr, node):
        return maya.cmds.setAttr(
            nodeAttr, lock=lock, keyable=keyable, channelBox=channelBox
        )
    return False


def _lock_node_attrs(node, attrs, lock=True, keyable=False, channelBox=False):
    for attr in attrs:
        if node_utils.attribute_exists(attr, node):
            maya.cmds.setAttr(
                node + '.' + attr, lock=lock, keyable=keyable, channelBox=channelBox
            )
            pass
    return True


def _lock_transform_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node,
        ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'shxy', 'shxz', 'shyz'],
        lock=lock,
        keyable=keyable,
        channelBox=channelBox,
    )


def _lock_translate_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node, ['tx', 'ty', 'tz'], lock=lock, keyable=keyable, channelBox=channelBox
    )


def _lock_rotate_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node, ['rx', 'ry', 'rz'], lock=lock, keyable=keyable, channelBox=channelBox
    )


def _lock_scale_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node, ['sx', 'sy', 'sz'], lock=lock, keyable=keyable, channelBox=channelBox
    )


def _lock_shear_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node,
        ['shxy', 'shxz', 'shyz'],
        lock=lock,
        keyable=keyable,
        channelBox=channelBox,
    )


def _lock_constraint_offset_attrs(node, lock=True, keyable=False, channelBox=False):
    return _lock_node_attrs(
        node,
        ['ox', 'oy', 'oz', 'otx', 'oty', 'otz', 'orx', 'ory', 'orz'],
        lock=lock,
        keyable=keyable,
        channelBox=channelBox,
    )


def _reset_transform_values(node):
    maya.cmds.xform(node, objectSpace=True, translation=(0.0, 0.0, 0.0))
    maya.cmds.xform(node, objectSpace=True, rotation=(0.0, 0.0, 0.0))
    maya.cmds.xform(node, objectSpace=True, scale=(1.0, 1.0, 1.0))
    maya.cmds.xform(node, objectSpace=True, shear=(0.0, 0.0, 0.0))
    maya.cmds.xform(node, objectSpace=True, shear=(0.0, 0.0, 0.0))
    maya.cmds.xform(node, objectSpace=True, pivots=(0.0, 0.0, 0.0))
    return True


def _create_constraint_to(
    targetTransform,
    objectTransform,
    lockAttrs=True,
    lock=True,
    keyable=False,
    channelBox=False,
):
    constPoint = maya.cmds.pointConstraint(targetTransform, objectTransform)[0]
    constOrient = maya.cmds.orientConstraint(targetTransform, objectTransform)[0]
    constScale = maya.cmds.scaleConstraint(targetTransform, objectTransform)[0]
    if lockAttrs:
        _lock_constraint_offset_attrs(
            constPoint, lock=lock, keyable=keyable, channelBox=channelBox
        )
        _lock_constraint_offset_attrs(
            constOrient, lock=lock, keyable=keyable, channelBox=channelBox
        )
        _lock_constraint_offset_attrs(
            constScale, lock=lock, keyable=keyable, channelBox=channelBox
        )
    return constPoint, constOrient, constScale


def _create_transform(name=None, parent=None):
    assert isinstance(name, pycompat.TEXT_TYPE)
    node = maya.cmds.createNode("transform", name=name, parent=parent)
    node = node_utils.get_long_name(node)
    return node


def _create_locator(name=None, parent=None):
    assert isinstance(name, pycompat.TEXT_TYPE)
    tfm = maya.cmds.createNode('transform', name=name, parent=parent)
    tfm = node_utils.get_long_name(tfm)

    name_shp = tfm.split('|')[-1] + 'Shape'
    shp = maya.cmds.createNode('locator', name=name_shp, parent=tfm)
    shp = node_utils.get_long_name(shp)
    return tfm, shp


def _find_existing_rivet_shape(mesh_shape):
    """
    Find a mesh shape node with the name 'RivetShape' that has
    previously been created and can be reused.

    :returns: Mesh shape node, or None.
    :rtype: None or str
    """
    rivet_shape = None
    nodes = maya.cmds.listHistory(mesh_shape, allConnections=True, future=False) or []
    for node in nodes:
        conns = (
            maya.cmds.listConnections(
                node, shapes=True, connections=False, destination=True
            )
            or []
        )
        for conn in conns:
            if conn.find('RivetShape') != -1:
                rivet_shape = conn
                break
    return rivet_shape


def _create_rivet_shape(mesh_transform, mesh_shape):
    """
    Creates a new 'RivetShape' mesh shape node on the mesh given.
    """
    # Find attribute.
    original_src_attr = maya.cmds.connectionInfo(
        mesh_shape + '.inMesh', sourceFromDestination=True
    )
    if len(original_src_attr) == 0:
        attr = mesh_shape + '.inMesh'
        LOG.error('No incoming connection to mesh "%s".', attr)
        return None

    # If we could not find a mesh shape, make one.
    duplicate_transform = maya.cmds.duplicate(mesh_shape, returnRootsOnly=True)[0]
    duplicate_shapes = maya.cmds.listRelatives(
        duplicate_transform, shapes=True, noIntermediate=True, fullPath=True
    )
    duplicate_shape = duplicate_shapes[0]
    parented_shape = maya.cmds.parent(
        duplicate_shape, mesh_transform, addObject=True, shape=True
    )[0]
    maya.cmds.delete(duplicate_transform)
    rivet_shape = maya.cmds.rename(parented_shape, mesh_transform + 'RivetShape')

    # Connect up to previous node.
    maya.cmds.connectAttr(original_src_attr, rivet_shape + '.inMesh', force=True)
    return rivet_shape


def _setup_control_attrs(
    control_tfm, cluster_deformer, point_poly_rivet_transform, uv_coordinate
):
    """
    Add attributes and create connections for locator control.
    """
    assert maya.cmds.objExists(control_tfm)
    assert maya.cmds.objExists(cluster_deformer)
    assert maya.cmds.objExists(point_poly_rivet_transform)
    assert len(uv_coordinate) >= 2

    maya.cmds.addAttr(
        control_tfm,
        longName='deformerWeight',
        shortName='dfmwgt',
        at='double',
        defaultValue=1.0,
        keyable=True,
    )
    maya.cmds.addAttr(
        control_tfm,
        longName='coordinateU',
        shortName='crdu',
        niceName='U',
        at='double',
        defaultValue=uv_coordinate[0],
        keyable=True,
    )
    maya.cmds.addAttr(
        control_tfm,
        longName='coordinateV',
        shortName='crdv',
        niceName='V',
        at='double',
        defaultValue=uv_coordinate[1],
        keyable=True,
    )

    rivet_attr_u = point_poly_rivet_transform + '.coordinateU'
    rivet_attr_v = point_poly_rivet_transform + '.coordinateV'
    rivet_attr_weight = point_poly_rivet_transform + '.coordinateWeight'
    maya.cmds.connectAttr(
        control_tfm + '.deformerWeight', cluster_deformer + '.envelope'
    )
    maya.cmds.connectAttr(control_tfm + '.coordinateU', rivet_attr_u)
    maya.cmds.connectAttr(control_tfm + '.coordinateV', rivet_attr_v)

    _lock_node_attr(rivet_attr_u)
    _lock_node_attr(rivet_attr_v)
    _lock_node_attr(rivet_attr_weight)
    return


def paint_cluster_weights_on_mesh(mesh_tfm, cluster_shp):
    """
    Opens the Paint Editor on a mesh node to allow user painting
    of weights.
    """
    maya.cmds.select(mesh_tfm, replace=True)
    mel_cmd = OPEN_PAINT_EDITOR_MEL_CMD.format(node=cluster_shp)
    maya.mel.eval(mel_cmd)
    return


SurfaceCluster = collections.namedtuple(
    'SurfaceCluster',
    ['control_transform', 'mesh_transform', 'mesh_shape', 'cluster_deformer_node'],
)


def get_surface_cluster_from_control_transform(control_tfm):
    assert maya.cmds.objExists(control_tfm)
    assert maya.cmds.nodeType(control_tfm) == 'transform'

    cluster_deformers = (
        maya.cmds.listConnections(
            control_tfm,
            destination=True,
            source=False,
            skipConversionNodes=True,
            shapes=True,
            type='cluster',
            exactType=True,
        )
        or []
    )
    if len(cluster_deformers) == 0:
        LOG.error(
            'Could not find Cluster Deformer node from Control transform: %r',
            control_tfm,
        )
        return

    mesh_shps = maya.cmds.listHistory(cluster_deformers[0], future=True) or []
    mesh_shps = [
        node_utils.get_long_name(x)
        for x in mesh_shps
        if maya.cmds.nodeType(x) == 'mesh'
    ]
    if len(mesh_shps) == 0:
        LOG.error(
            'Could not find Mesh shape node from Control transform: %r', control_tfm
        )
        return

    mesh_tfms = (
        maya.cmds.listRelatives(
            mesh_shps[0], parent=True, type='transform', fullPath=True
        )
        or []
    )
    if len(mesh_tfms) == 0:
        LOG.error(
            'Could not find Mesh transform node from Control transform: %r', control_tfm
        )
        return

    return SurfaceCluster(
        control_transform=control_tfm,
        mesh_transform=mesh_tfms[0],
        mesh_shape=mesh_shps[0],
        cluster_deformer_node=cluster_deformers[0],
    )


def create_surface_cluster_on_mesh_and_component(
    mesh_tfm, mesh_shp, component, uv_coordinate
):
    """
    Create a Surface Cluster on a mesh component (face, edge or
    vertex), positioned at a UV coordinate on the mesh_shp.

    :rtype: None or SurfaceCluster
    """
    assert len(uv_coordinate) >= 2

    # Group all nodes under a single group.
    main_group = _create_transform(name='mmSurfaceCluster1')
    _lock_transform_attrs(main_group)

    # Duplicate mesh shape node, keep all incoming connections.
    rivet_shp = _find_existing_rivet_shape(mesh_shp)
    if rivet_shp is None:
        rivet_shp = _create_rivet_shape(mesh_tfm, mesh_shp)
    if rivet_shp is None:
        LOG.error('Could not create rivet shape.')
        return None

    # Set non-rivet mesh as intermediate, and set rivet mesh as normal.
    maya.cmds.setAttr(rivet_shp + '.intermediateObject', 0)
    maya.cmds.setAttr(mesh_shp + '.intermediateObject', 1)

    point_on_poly = rivet_pointonpoly.create(
        mesh_tfm,
        mesh_shp,
        parent=main_group,
        as_locator=False,
        uv_coordinate=uv_coordinate,
    )
    if point_on_poly is None:
        LOG.error('Could not create point on poly constraint.')
        return None
    rivet_tfm = point_on_poly.rivet_transform

    # Set rivet mesh as intermediate, and set non-rivet mesh as normal.
    maya.cmds.setAttr(rivet_shp + '.intermediateObject', 1)
    maya.cmds.setAttr(mesh_shp + '.intermediateObject', 0)

    # Create locator controller.
    control_tfm, _control_shp = _create_locator(name='mmControl1', parent=rivet_tfm)
    _reset_transform_values(control_tfm)

    # Create cluster on mesh.
    cluster_deformer, cluster_handle = maya.cmds.cluster(
        mesh_tfm, name='mmSurfaceCluster1'
    )
    maya.cmds.setAttr(cluster_deformer + '.relative', 1)
    maya.cmds.setAttr(cluster_handle + '.visibility', 0)
    cluster_handle = node_utils.get_long_name(
        maya.cmds.parent(cluster_handle, rivet_tfm)[0]
    )
    maya.cmds.disconnectAttr(
        cluster_handle + '.worldMatrix[0]', cluster_deformer + '.matrix'
    )
    _create_constraint_to(control_tfm, cluster_handle)
    _reset_transform_values(cluster_handle)
    _lock_transform_attrs(cluster_handle)

    # Create Object Null,
    object_null = _create_transform(name='objectNull1', parent=main_group)
    _create_constraint_to(mesh_tfm, object_null)
    _lock_transform_attrs(object_null)

    # Create Object Rivet Nulls.
    object_rivet_null = _create_transform(name='objectRivet1', parent=object_null)
    _create_constraint_to(rivet_tfm, object_rivet_null)
    _lock_transform_attrs(object_rivet_null)

    # Connect GeomMatrix Cluster attribute.
    maya.cmds.connectAttr(
        object_rivet_null + '.inverseMatrix',
        cluster_deformer + '.geomMatrix[0]',
        force=True,
    )

    _setup_control_attrs(
        control_tfm,
        cluster_deformer,
        point_on_poly.rivet_transform,
        uv_coordinate,
    )

    return SurfaceCluster(control_tfm, mesh_tfm, mesh_shp, cluster_deformer)


def set_cluster_deformer_weights(cluster_shp, mesh_shp, weights):
    assert maya.cmds.objExists(cluster_shp)
    assert maya.cmds.objExists(mesh_shp)
    assert maya.cmds.nodeType(cluster_shp) == 'cluster'
    assert maya.cmds.nodeType(mesh_shp) == 'mesh'
    assert isinstance(weights, dict)
    vertex_count = maya.cmds.polyEvaluate(mesh_shp, vertex=True)
    for i in range(vertex_count):
        weights_attr = '{}.weightList[0].weights[{}]'.format(cluster_shp, i)
        if i in weights:
            maya.cmds.setAttr(weights_attr, weights[i])
        else:
            maya.cmds.setAttr(weights_attr, 0.0)
    return


def create_surface_cluster_on_component(component):
    """
    Create a Surface Cluster on a mesh component (face, edge or
    vertex).

    :rtype: None or SurfaceCluster
    """
    # Get selection for mesh and locators.
    meshes = maya.cmds.listRelatives(component, parent=True, fullPath=True) or []
    if len(meshes) == 0:
        msg = 'Could not find mesh shape; component=%r meshes=%r.'
        LOG.warn(msg, component, meshes)
        return
    mesh = meshes[0]

    # Get the mesh transform and shape.
    mesh_tfm = None
    mesh_shp = None
    tmp = maya.cmds.listRelatives(mesh, parent=True)
    if len(tmp) > 0:
        mesh_tfm = tmp[0]
        mesh_shp = mesh
    else:
        LOG.warn(
            'Mesh transform and shape could not be found'
            ' for surface cluster; component=%r',
            component,
        )
        return

    sel = maya.cmds.ls(selection=True, long=True) or []
    try:
        # The weights are calculated for the single component only.
        maya.cmds.select(component, replace=True)
        soft_selection_weights = selection_utils.get_soft_selection_weights(
            only_shape_node=mesh_shp
        )
        if len(soft_selection_weights) > 0:
            soft_selection_weights = soft_selection_weights[0]

        in_position = selection_utils.get_selection_center_3d_point(component)

        point_data = nearestpointonmesh.get_nearest_point_on_mesh(mesh_shp, in_position)
        uv_coordinate = point_data.coords

        surface_cluster = create_surface_cluster_on_mesh_and_component(
            mesh_tfm, mesh_shp, component, uv_coordinate
        )
        if surface_cluster is None:
            LOG.error('Could not create surface cluster!')
            return

        if len(soft_selection_weights) > 0:
            set_cluster_deformer_weights(
                surface_cluster.cluster_deformer_node, mesh_shp, soft_selection_weights
            )
    finally:
        maya.cmds.select(sel, replace=True)

    return surface_cluster
