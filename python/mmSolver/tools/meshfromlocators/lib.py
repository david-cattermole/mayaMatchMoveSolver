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

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds

import mmSolver.logger
from mmSolver.tools.meshfromlocators.delaunator import Delaunator
import mmSolver.tools.meshfromlocators.constant as const

LOG = mmSolver.logger.get_logger()


def delaunator_indices(locators):
    """
    Returns delaunay indices in the proper order to create mesh.

    :param locators: locatorlist
    :type locators: list
    """
    mesh_data = {
        "world_positions": [],
        "vew_positions": [],
        "full_mesh_indices": [],
        "border_mesh_indices": [],
    }
    for locator_name in locators:
        locator_pos = maya.cmds.xform(
            locator_name, query=True, worldSpace=True, translation=True
        )
        locator_mpoint = om.MPoint(locator_pos[0], locator_pos[1], locator_pos[2])
        mesh_data["world_positions"].append(locator_mpoint)
        # Convert world position to view space
        view = omui.M3dView.active3dView()
        view_pos = view.worldToView(locator_mpoint)
        view_x, view_y = view_pos[0], view_pos[1]
        mesh_data["vew_positions"].append([view_x, view_y])

    # Indices
    mesh_indices = Delaunator(mesh_data["vew_positions"]).triangles

    # Reverse order
    mesh_indices_reverse = []
    for i in range(0, len(mesh_indices), 3):
        chunk = mesh_indices[i : i + 3]
        mesh_indices_reverse.extend(chunk[::-1])
    mesh_data["full_mesh_indices"] = mesh_indices_reverse

    # Hull indices
    hull = Delaunator(mesh_data["vew_positions"]).hull
    hull.reverse()
    mesh_data["border_mesh_indices"] = hull
    return mesh_data


def create_mesh_from_locators(mesh_type=None, offset_value=1.0):
    """
    Creates mesh from locators.

    :param mesh_type: 'fullMesh' 'borderMesh' 'borderEdgeStripMesh'.
    :type mesh_type: str

    :param offset_value: An offset value for borderEdgeStripMesh
    :type offset_value: float
    """
    locators = maya.cmds.ls(selection=True, transforms=True) or []
    if len(locators) < 3:
        LOG.warn('at least three locators must be selected.')
        return

    mesh_data = delaunator_indices(locators)
    positions = mesh_data["world_positions"]

    # Set face count and indices
    if mesh_type == 'fullMesh':
        indices = mesh_data["full_mesh_indices"]
        face_counts = [3] * (len(indices) // 3)
    else:
        indices = mesh_data["border_mesh_indices"]
        face_counts = [len(indices)]

    # Create the mesh
    mesh_fn = om.MFnMesh()
    mesh = mesh_fn.create(positions, face_counts, indices)

    # Set mesh name
    dag_node = om.MFnDagNode(mesh)
    dag_node.setName(const.MESH_NAME)
    mesh_name = dag_node.name()

    # Set lambert
    maya.cmds.sets(mesh_name, edit=True, forceElement='initialShadingGroup')

    # Create border edge strip mesh
    if mesh_type == 'borderEdgeStripMesh':
        maya.cmds.polyExtrudeFacet(mesh_name, offset=offset_value)
        face_0 = '{}.f[0]'.format(mesh_name)
        face_1 = '{}.f[1]'.format(mesh_name)
        maya.cmds.delete(face_0, face_1)
