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


def get_soft_selection_weights(only_node=None):
    """
    Get the currently 'soft' selected components.

    Soft selection may return a list for multiple different nodes.

    If 'only_node' is given, then soft selections on only that node
    will be returned, all else will be ignored.
    """
    all_weights = []

    soft_select_enabled = maya.cmds.softSelect(query=True, softSelectEnabled=True)
    if not soft_select_enabled:
        return all_weights

    rich_selection = OpenMaya.MRichSelection()
    try:
        # get currently active soft selection
        OpenMaya.MGlobal.getRichSelection(rich_selection)
    except RuntimeError as e:
        LOG.error(str(e))
        LOG.error('Error getting soft selection.')
        return all_weights

    rich_selection_list = OpenMaya.MSelectionList()
    rich_selection.getSelection(rich_selection_list)
    selection_count = rich_selection_list.length()

    for i in range(selection_count):
        shape_dag_path = OpenMaya.MDagPath()
        shape_component = OpenMaya.MObject()
        try:
            rich_selection_list.getDagPath(i, shape_dag_path, shape_component)
        except RuntimeError:
            continue

        if only_node is not None:
            if shape_dag_path.fullPathName() != only_node:
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
