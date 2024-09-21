# Copyright (C) 2024 Patcha Saheb Binginapalli.
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

import collections

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds

import mmSolver.logger
from mmSolver.tools.meshfrompoints.delaunator import Delaunator
import mmSolver.tools.meshfrompoints.constant as const


LOG = mmSolver.logger.get_logger()


MeshData = collections.namedtuple(
    'MeshData',
    ['world_positions', 'full_mesh_indices', 'border_mesh_indices'],
)


def _delaunator_indices(transform_nodes, viewport):
    """
    Uses transforms and active camera view to compute delaunay
    indices in the proper order to create mesh.

    NOTE: This function uses the active view camera! This is hidden

    :param transform_nodes:
    :type transform_nodes: list

    """
    assert isinstance(viewport, omui.M3dView)
    assert len(transform_nodes) >= const.MINIMUM_NUMBER_OF_POINTS

    world_positions = []
    view_positions = []
    for transform_node in transform_nodes:
        transform_pos = maya.cmds.xform(
            transform_node, query=True, worldSpace=True, translation=True
        )
        transform_mpoint = om.MPoint(
            transform_pos[0], transform_pos[1], transform_pos[2]
        )
        world_positions.append(transform_mpoint)

        # Convert world position to view space.
        view_pos = viewport.worldToView(transform_mpoint)
        view_x, view_y = view_pos[0], view_pos[1]
        view_positions.append([view_x, view_y])

    # Compute once, and reuse the result.
    computation = Delaunator(view_positions)
    mesh_indices = computation.triangles

    # Reverse order
    mesh_indices_reverse = []
    for i in range(0, len(mesh_indices), 3):
        chunk = mesh_indices[i : i + 3]
        mesh_indices_reverse.extend(chunk[::-1])
    full_mesh_indices = mesh_indices_reverse

    # Hull indices
    border_mesh_indices = computation.hull
    border_mesh_indices.reverse()

    assert len(world_positions) == len(view_positions)

    mesh_data = MeshData(
        world_positions=world_positions,
        full_mesh_indices=full_mesh_indices,
        border_mesh_indices=border_mesh_indices,
    )
    return mesh_data


def create_mesh_from_transform_nodes(
    mesh_type, transform_nodes, offset_value=None, mesh_name=None
):
    """
    Creates mesh from transform nodes.

    :param mesh_type: The type of mesh to create.
    :type mesh_type: mmSolver.tools.meshfrompoints.constant.MESH_TYPE_*_VALUE.

    :param transform_nodes: List of transform nodes to get 3D positions from.
    :type transform_nodes: [str, ..]

    :param offset_value: An offset value for MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE.
    :type offset_value: float

    :param mesh_name: The name of the mesh node created.
    :type mesh_name: str
    """
    if offset_value is None:
        offset_value = const.DEFAULT_STRIP_WIDTH
    if mesh_name is None:
        mesh_name = const.DEFAULT_MESH_NAME
    assert mesh_type in const.MESH_TYPE_VALUES
    assert isinstance(mesh_name, str)
    assert len(mesh_name) > 0
    assert isinstance(offset_value, float)
    assert len(transform_nodes) >= const.MINIMUM_NUMBER_OF_POINTS

    active_viewport = omui.M3dView.active3dView()
    mesh_data = _delaunator_indices(transform_nodes, active_viewport)
    positions = mesh_data.world_positions

    # Set face count and indices
    if mesh_type == const.MESH_TYPE_FULL_MESH_VALUE:
        indices = mesh_data.full_mesh_indices
        face_counts = [3] * (len(indices) // 3)
    else:
        indices = mesh_data.border_mesh_indices
        face_counts = [len(indices)]

    # Create the mesh.
    mesh_fn = om.MFnMesh()
    mesh = mesh_fn.create(positions, face_counts, indices)

    # Set mesh name.
    dag_node = om.MFnDagNode(mesh)
    dag_node.setName(mesh_name)
    mesh_name = dag_node.name()

    # Set lambert
    maya.cmds.sets(mesh_name, edit=True, forceElement='initialShadingGroup')

    # Create border edge strip mesh
    if mesh_type == const.MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE:
        maya.cmds.polyExtrudeFacet(mesh_name, offset=offset_value)
        face_0 = '{}.f[0]'.format(mesh_name)
        face_1 = '{}.f[1]'.format(mesh_name)
        maya.cmds.delete(face_0, face_1)
    return
