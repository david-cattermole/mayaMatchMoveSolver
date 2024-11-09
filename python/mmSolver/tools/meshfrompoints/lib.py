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

import maya.api.OpenMaya as OpenMaya
import maya.cmds

import mmSolver.api as mmapi

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.tools.meshfrompoints.constant as const
import mmSolver.tools.meshfrompoints.delaunator as delaunator


LOG = mmSolver.logger.get_logger()


MeshData = collections.namedtuple(
    'MeshData',
    ['world_positions', 'full_mesh_indices', 'border_mesh_indices'],
)


def _delaunator_indices(world_positions, flat_positions):
    """
    Uses transforms and active camera view to compute delaunay
    indices in the proper order to create mesh.

    NOTE: This function uses the active view camera! This is hidden

    :param transform_nodes:
    :type transform_nodes: list

    """
    assert len(flat_positions) == len(world_positions)
    assert len(flat_positions) >= const.MINIMUM_NUMBER_OF_POINTS

    # Compute once, and reuse the result.
    computation = delaunator.Delaunator(flat_positions)
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

    mesh_data = MeshData(
        world_positions=world_positions,
        full_mesh_indices=full_mesh_indices,
        border_mesh_indices=border_mesh_indices,
    )
    return mesh_data


def _best_fit_plane_matrix_from_3d_points(world_positions):
    assert world_positions.len() >= const.MINIMUM_NUMBER_OF_POINTS

    # Our plug-in must be loaded to access the mmBestFitPlane command.
    mmapi.load_plugin()

    # The data structure that the mmBestFitPlane command expects.
    points_components = []
    for point in world_positions:
        points_components.append(point.x)
        points_components.append(point.y)
        points_components.append(point.z)

    OUTPUT_VALUES_AS_MATRIX_4X4 = "matrix_4x4"
    plane_fit_result = maya.cmds.mmBestFitPlane(
        pointComponent=points_components,
        outputValuesAs=OUTPUT_VALUES_AS_MATRIX_4X4,
        outputRmsError=False,
    )

    plane_mmatrix = OpenMaya.MMatrix()
    if plane_fit_result is not None:
        plane_mmatrix = OpenMaya.MMatrix(
            (
                # Row 0
                plane_fit_result[0],
                plane_fit_result[1],
                plane_fit_result[2],
                plane_fit_result[3],
                # Row 1
                plane_fit_result[4],
                plane_fit_result[5],
                plane_fit_result[6],
                plane_fit_result[7],
                # Row 2
                plane_fit_result[8],
                plane_fit_result[9],
                plane_fit_result[10],
                plane_fit_result[11],
                # Row 3
                plane_fit_result[12],
                plane_fit_result[13],
                plane_fit_result[14],
                plane_fit_result[15],
            )
        )

    return plane_mmatrix


def _convert_transform_nodes_to_positions(transform_nodes):
    assert len(transform_nodes) >= const.MINIMUM_NUMBER_OF_POINTS

    world_positions = []
    for transform_node in transform_nodes:
        transform_pos = maya.cmds.xform(
            transform_node, query=True, worldSpace=True, translation=True
        )
        transform_mpoint = OpenMaya.MPoint(
            transform_pos[0], transform_pos[1], transform_pos[2]
        )
        world_positions.append(transform_mpoint)

    plane_mmatrix = _best_fit_plane_matrix_from_3d_points(world_positions)
    if plane_mmatrix is None:
        return None

    flat_positions = []
    for world_position in world_positions:
        # Essentially this will parent the given point under the plane
        # fit matrix.
        plane_position = plane_mmatrix * world_position

        # The plane matrix is oriented to Y-up, so X and Z should
        # represent the 2D position.
        flat_positions.append((plane_position.x, plane_position.z))
    assert len(world_positions) == len(flat_positions)

    return world_positions, flat_positions


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

    :returns: The name of the created mesh node.
    :rtype: str
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

    (world_positions, flat_positions) = _convert_transform_nodes_to_positions(
        transform_nodes
    )

    mesh_data = _delaunator_indices(world_positions, flat_positions)
    positions = mesh_data.world_positions

    # Set face count and indices
    if mesh_type == const.MESH_TYPE_FULL_MESH_VALUE:
        indices = mesh_data.full_mesh_indices
        face_counts = [3] * (len(indices) // 3)
    else:
        indices = mesh_data.border_mesh_indices
        face_counts = [len(indices)]

    # Create the mesh.
    mesh_fn = OpenMaya.MFnMesh()
    mesh = mesh_fn.create(positions, face_counts, indices)

    # Set mesh name.
    dag_node = OpenMaya.MFnDagNode(mesh)
    dag_node.setName(mesh_name)
    mesh_node = dag_node.name()

    # Set lambert
    maya.cmds.sets(mesh_node, edit=True, forceElement='initialShadingGroup')

    # Create border edge strip mesh
    if mesh_type == const.MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE:
        maya.cmds.polyExtrudeFacet(mesh_node, offset=offset_value)
        face_0 = '{}.f[0]'.format(mesh_node)
        face_1 = '{}.f[1]'.format(mesh_node)
        maya.cmds.delete(face_0, face_1)

    return node_utils.get_long_name(mesh_node)
