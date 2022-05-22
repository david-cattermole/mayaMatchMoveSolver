# Copyright (C) 2020, 2022 Kazuma Tonegawa, David Cattermole
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
Library functions for removing solver nodes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds as cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def _collect_markers(node_categories):
    nodes_to_delete = node_categories.get(mmapi.OBJECT_TYPE_MARKER, [])
    return list(sorted(set(nodes_to_delete)))


def _collect_bundles(node_categories):
    # If a non-bundle node is found under the bundles, then we should
    # take special care because by deleting the bundle we will also
    # delete other nodes.
    unknown_node_found = False
    nodes_to_delete = set()
    for node in node_categories[mmapi.OBJECT_TYPE_BUNDLE]:
        if cmds.objectType(node) != 'transform':
            continue
        nodes_to_delete.add(node)
        children = cmds.listRelatives(
            node,
            type='transform',
            children=True,
            fullPath=True) or []
        for child in children:
            if mmapi.get_object_type(child) != mmapi.OBJECT_TYPE_BUNDLE:
                unknown_node_found = True
    return list(sorted(nodes_to_delete)), unknown_node_found


def _collect_marker_groups(node_categories):
    nodes_to_delete = node_categories.get(mmapi.OBJECT_TYPE_MARKER_GROUP, [])
    return list(sorted(set(nodes_to_delete)))


def _collect_lines(node_categories):
    nodes_to_delete = node_categories.get(mmapi.OBJECT_TYPE_LINE, [])
    return list(sorted(set(nodes_to_delete)))


def _collect_lenses(node_categories):
    nodes_to_delete = set(node_categories.get(mmapi.OBJECT_TYPE_LENS, set()))

    node_types_to_delete = ['mmLensDeformer', 'mmLensEvaluate']
    other_nodes = node_categories.get('other', [])
    for node in other_nodes:
        if cmds.nodeType(node) in node_types_to_delete:
            nodes_to_delete.add(node)
    return list(sorted(nodes_to_delete))


def _collect_image_planes(node_categories):
    nodes_to_delete = node_categories.get(mmapi.OBJECT_TYPE_IMAGE_PLANE, [])
    return list(sorted(set(nodes_to_delete)))


def _collect_display_nodes(node_categories):
    nodes_to_delete = set()
    node_types_to_delete = ['mmSkyDomeShape', 'mmRenderGlobals']
    other_nodes = node_categories.get('other', [])
    for node in other_nodes:
        if cmds.nodeType(node) in node_types_to_delete:
            nodes_to_delete.add(node)
    return list(sorted(nodes_to_delete))


def _collect_collections(node_categories):
    nodes_to_delete = node_categories.get('collection', [])
    return list(sorted(set(nodes_to_delete)))


def _collect_misc_nodes():
    misc_nodes = cmds.ls(
        long=True,
        type=[
            'mmMarkerScale',
            'mmReprojection',
            'mmMarkerGroupTransform',
            'mmLineIntersect',
            'mmCameraCalibrate'
        ]
    )
    other_nodes = cmds.ls('mmSolver*', long=True)
    combined_set = set(misc_nodes+other_nodes)
    return list(sorted(combined_set))


def filter_nodes(what_to_delete_dict):
    nodes = cmds.ls(long=True) or []
    cmds.select(clear=True)
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    unknown_node_found = False
    found_nodes_map = dict()

    what_type = 'markers'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_markers(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'bundles'
    if what_to_delete_dict.get(what_type) is True:
        delete_list, unknown_node_found = _collect_bundles(node_categories)
        found_nodes_map[what_type] = delete_list

    what_type = 'marker_groups'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_marker_groups(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'lenses'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_lenses(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'lines'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_lines(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'imageplanes'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_image_planes(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'collections'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_collections(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'display_nodes'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes = _collect_display_nodes(node_categories)
        found_nodes_map[what_type] = found_nodes

    what_type = 'other_nodes'
    if what_to_delete_dict.get(what_type) is True:
        found_nodes_map[what_type] = _collect_misc_nodes()

    return found_nodes_map, unknown_node_found


def delete_nodes(nodes_to_delete):
    for node in nodes_to_delete:
        if cmds.objExists(node):
            cmds.delete(node)
