# Copyright (C) 2024 David Cattermole.
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

import maya.api.OpenMaya as OpenMaya
import maya.cmds

import mmSolver.api as mmapi

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.tools.createplanefrompoints.constant as const


LOG = mmSolver.logger.get_logger()


def _set_mesh_transform_matrix(transform_node, matrix):
    maya.cmds.xform(transform_node, worldSpace=True, matrix=matrix)

    # Workaround a bug with the returned Matrix. The scale values for
    # some components may be flipped, so here we just make sure the
    # scale is always positive.
    scale_xyz = maya.cmds.xform(transform_node, query=True, worldSpace=True, scale=True)
    scale_xyz = (abs(scale_xyz[0]), abs(scale_xyz[1]), abs(scale_xyz[2]))
    maya.cmds.xform(transform_node, objectSpace=True, scale=scale_xyz)


def _set_mesh_transform_mmatrix(transform_node, mmatrix):
    matrix = (
        # Row 0
        mmatrix.getElement(0, 0),
        mmatrix.getElement(0, 1),
        mmatrix.getElement(0, 2),
        mmatrix.getElement(0, 3),
        # Row 1
        mmatrix.getElement(1, 0),
        mmatrix.getElement(1, 1),
        mmatrix.getElement(1, 2),
        mmatrix.getElement(1, 3),
        # Row 2
        mmatrix.getElement(2, 0),
        mmatrix.getElement(2, 1),
        mmatrix.getElement(2, 2),
        mmatrix.getElement(2, 3),
        # Row 3
        mmatrix.getElement(3, 0),
        mmatrix.getElement(3, 1),
        mmatrix.getElement(3, 2),
        mmatrix.getElement(3, 3),
    )
    maya.cmds.xform(transform_node, worldSpace=True, matrix=matrix)


def best_fit_plane_matrix_from_3d_points(
    world_positions, with_scale=None, as_mmatrix=None
):
    if with_scale is None:
        with_scale = True
    if as_mmatrix is None:
        as_mmatrix = True
    assert isinstance(with_scale, bool)
    assert isinstance(as_mmatrix, bool)
    assert len(world_positions) >= const.MINIMUM_NUMBER_OF_POINTS

    # Our plug-in must be loaded to access the mmBestFitPlane command.
    mmapi.load_plugin()

    # The data structure that the mmBestFitPlane command expects.
    points_components = []
    for point in world_positions:
        points_components.append(point[0])
        points_components.append(point[1])
        points_components.append(point[2])

    OUTPUT_VALUES_AS_MATRIX_4X4 = "matrix_4x4"
    plane_fit_result = maya.cmds.mmBestFitPlane(
        pointComponent=points_components,
        outputValuesAs=OUTPUT_VALUES_AS_MATRIX_4X4,
        outputRmsError=False,
        withScale=with_scale,
    )

    plane_matrix = (
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
    if as_mmatrix is True:
        plane_mmatrix = OpenMaya.MMatrix()
        if plane_fit_result is not None:
            plane_mmatrix = OpenMaya.MMatrix(plane_matrix)
        return plane_mmatrix

    return plane_matrix


def convert_transform_nodes_to_3d_points(transform_nodes):
    assert len(transform_nodes) >= const.MINIMUM_NUMBER_OF_POINTS

    world_points = []
    for transform_node in transform_nodes:
        transform_pos = maya.cmds.xform(
            transform_node, query=True, worldSpace=True, translation=True
        )
        transform_mpoint = OpenMaya.MPoint(
            transform_pos[0], transform_pos[1], transform_pos[2]
        )
        world_points.append(transform_mpoint)

    return world_points


def create_plane_from_points(world_points, name=None):
    """
    Create Mesh plane aligned to world-space 3D Points.

    :param world_points: List of 3D points to use.
    :type world_points: [maya.api.OpenMaya.MPoint, ..]

    :param name: The name of the mesh node created.
    :type name: str

    :returns: The name of the created node.
    :rtype: str
    """
    if name is None:
        name = const.DEFAULT_PLANE_NAME
    assert isinstance(name, str)
    assert len(name) > 0
    assert len(world_points) >= const.MINIMUM_NUMBER_OF_POINTS

    plane_matrix = best_fit_plane_matrix_from_3d_points(
        world_points, with_scale=True, as_mmatrix=False
    )
    if plane_matrix is None:
        return None

    transform_node, _creator_node = maya.cmds.polyPlane(axis=[0.0, 1.0, 0.0], name=name)

    _set_mesh_transform_matrix(transform_node, plane_matrix)

    # Assign 'lambert1' to mesh.
    maya.cmds.sets(transform_node, edit=True, forceElement='initialShadingGroup')

    return node_utils.get_long_name(transform_node)
