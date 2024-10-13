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
Selection utilities.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.utils.python_compat as pycompat
import mmSolver.logger


LOG = mmSolver.logger.get_logger()

# Magic numbers for the component masks in Maya.
_COMPONENT_MASK_POLYGON_VERTEX = 31
_COMPONENT_MASK_POLYGON_EDGE = 32
_COMPONENT_MASK_POLYGON_FACE = 34


def filter_mesh_vertex_selection(selection):
    component_selection = (
        maya.cmds.filterExpand(
            selection,
            expand=True,
            fullPath=True,
            selectionMask=_COMPONENT_MASK_POLYGON_VERTEX,
        )
        or []
    )
    return component_selection


def filter_mesh_edge_selection(selection):
    component_selection = (
        maya.cmds.filterExpand(
            selection,
            expand=True,
            fullPath=True,
            selectionMask=_COMPONENT_MASK_POLYGON_EDGE,
        )
        or []
    )
    return component_selection


def filter_mesh_face_selection(selection):
    component_selection = (
        maya.cmds.filterExpand(
            selection,
            expand=True,
            fullPath=True,
            selectionMask=_COMPONENT_MASK_POLYGON_FACE,
        )
        or []
    )
    return component_selection


def get_mesh_vertex_selection():
    selection = maya.cmds.ls(selection=True, long=True) or []
    return filter_mesh_vertex_selection(selection)


def get_mesh_edge_selection():
    selection = maya.cmds.ls(selection=True, long=True) or []
    return filter_mesh_edge_selection(selection)


def get_mesh_face_selection():
    selection = maya.cmds.ls(selection=True, long=True) or []
    return filter_mesh_face_selection(selection)


def get_soft_selection_weights(only_shape_node=None):
    """
    Get the currently 'soft' selected components.

    Soft selection may return a list for multiple different nodes.

    If 'only_shape_node' is given, then soft selections on only that node
    will be returned, all else will be ignored.

    :returns: List of object mappings of soft selection vertex index
        to weights, or an empty list.
    :rtype: [] or [{int: float}, ..]
    """
    soft_select_enabled = maya.cmds.softSelect(query=True, softSelectEnabled=True)
    if not soft_select_enabled:
        return []

    rich_selection = OpenMaya.MRichSelection()
    try:
        # Get currently active soft selection
        OpenMaya.MGlobal.getRichSelection(rich_selection)
    except RuntimeError as e:
        LOG.error(str(e))
        LOG.error('Error getting soft selection.')
        return []

    rich_selection_list = OpenMaya.MSelectionList()
    rich_selection.getSelection(rich_selection_list)
    selection_count = rich_selection_list.length()

    all_weights = []
    for i in range(selection_count):
        shape_dag_path = OpenMaya.MDagPath()
        shape_component = OpenMaya.MObject()
        try:
            rich_selection_list.getDagPath(i, shape_dag_path, shape_component)
        except RuntimeError:
            continue

        if only_shape_node is not None:
            if shape_dag_path.fullPathName() != only_shape_node:
                continue

        # Get weight value.
        component_weights = {}
        component_fn = OpenMaya.MFnSingleIndexedComponent(shape_component)
        try:
            for i in range(component_fn.elementCount()):
                weight = component_fn.weight(i)
                component_weights[component_fn.element(i)] = weight.influence()
        except RuntimeError as e:
            LOG.error(str(e))
            short_name = shape_dag_path.partialPathName()
            msg = 'Soft selection appears invalid, skipping for shape "%s".'
            LOG.error(msg, short_name)

        all_weights.append(component_weights)

    return all_weights


def get_selection_center_3d_point(nodes_or_components):
    """
    Return a 3D point that is the average position for the given
    nodes/components.

    :param nodes_or_components:
        List of nodes or components, or a single node or component.
    :type nodes_or_components: [str, ] or str

    :returns: Tuple of 3 floats; 3D Point representing the average position.
    :rtype: (float, float, float)
    """
    assert len(nodes_or_components) > 0

    # Get position from the node/nodes or component/components.
    #
    # NOTE: maya.cmds.xform, with a Mesh 'vertex' component as the input, the returned
    # positions will be a list of 3 float numbers; with a 'face'
    # component the number of numbers will 3 float numbers of each
    # vertex in the face.
    positions = []
    if isinstance(nodes_or_components, pycompat.TEXT_TYPE):
        assert maya.cmds.objExists(nodes_or_components)
        positions += (
            maya.cmds.xform(
                nodes_or_components, query=True, worldSpace=True, translation=True
            )
            or []
        )
    else:
        for node_or_component in nodes_or_components:
            assert maya.cmds.objExists(node_or_component)
            positions += (
                maya.cmds.xform(
                    node_or_component, query=True, worldSpace=True, translation=True
                )
                or []
            )

    # Get average position from all selected nodes (or components).
    sum_x = 0.0
    sum_y = 0.0
    sum_z = 0.0
    positions_count = len(positions) // 3
    for i in range(positions_count):
        index = i * 3
        sum_x += positions[index + 0]
        sum_y += positions[index + 1]
        sum_z += positions[index + 2]
    sum_x /= positions_count
    sum_y /= positions_count
    sum_z /= positions_count
    average_position = (sum_x, sum_y, sum_z)
    return average_position
