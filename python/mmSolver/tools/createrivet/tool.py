# Copyright (C) 2014, 2023 David Cattermole.
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
The Create Rivet tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.rivet.meshtwoedge as utils_rivet_meshtwoedge
import mmSolver.utils.rivet.pointonpoly as utils_rivet_pointonpoly
import mmSolver.utils.selection as utils_selection


LOG = mmSolver.logger.get_logger()


def _create_mesh_two_edge_rivet(edges):
    assert len(edges) == 2
    edge_a = edges[0]
    edge_b = edges[1]
    mesh_shape = edges[0].partition('.')[0]
    assert maya.cmds.objExists(mesh_shape)
    rivet = utils_rivet_meshtwoedge.create(mesh_shape, edge_a, edge_b)
    return [rivet.rivet_transform]


def _create_point_on_poly_rivets(vertices):
    assert len(vertices) > 0
    select_nodes = []
    for vertex in vertices:
        mesh_shape = vertex.partition('.')[0]
        mesh_transform = maya.cmds.listRelatives(
            mesh_shape, parent=True, fullPath=True, type='transform'
        )[0]
        vertex_world_position = maya.cmds.xform(
            vertex, query=True, worldSpace=True, translation=True
        )
        rivet = utils_rivet_pointonpoly.create(
            mesh_transform, mesh_shape, in_position=vertex_world_position
        )
        select_nodes.append(rivet.rivet_transform)
    return select_nodes


def main():
    """
    Create Rivet(s) from the selected mesh components.

    If 2 edges are selected, this tool will create a two-edge rivet,
    like the 'rivet.mel'.
    """
    error_msg = 'Please select Mesh Vertices or 2 Mesh Edges.'
    selection = maya.cmds.ls(selection=True, long=True) or []
    if len(selection) == 0:
        LOG.error(error_msg)
        return

    vertices = utils_selection.filter_mesh_vertex_selection(selection)
    edges = utils_selection.filter_mesh_edge_selection(selection)
    if len(vertices + edges) == 0:
        LOG.error(error_msg)
        return

    if len(vertices) > 0:
        select_nodes = _create_point_on_poly_rivets(vertices)
        maya.cmds.select(select_nodes, replace=True)
    elif len(edges) == 2:
        select_nodes = _create_mesh_two_edge_rivet(edges)
        maya.cmds.select(select_nodes, replace=True)
    else:
        LOG.error(error_msg)
    return
