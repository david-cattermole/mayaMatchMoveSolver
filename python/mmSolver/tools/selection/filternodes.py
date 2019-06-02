# Copyright (C) 2018 David Cattermole.
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
Helpful tools to filter a list of nodes into pre-defined categories.
"""

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def get_nodes(nodes):
    """
    Return nodes sorted into mmSolver-specific object type categories.

    Supported categories are:

    - 'camera'
    - 'marker'
    - 'markergroup'
    - 'bundle'
    - 'attribute'
    - 'collection'
    - 'other'

    :param nodes: Maya nodes to categorise.
    :type nodes: list of str

    :returns: Dictionary with lists for each object type.
    :rtype: dict
    """
    assert isinstance(nodes, (list, tuple))
    result = {
        'camera': [],
        'marker': [],
        'markergroup': [],
        'bundle': [],
        'attribute': [],
        'collection': [],
        'other': []
    }
    for node in nodes:
        obj_type = mmapi.get_object_type(node)
        if obj_type == mmapi.OBJECT_TYPE_MARKER:
            result['marker'].append(node)
        elif obj_type == mmapi.OBJECT_TYPE_MARKER_GROUP:
            result['markergroup'].append(node)
        elif obj_type == mmapi.OBJECT_TYPE_BUNDLE:
            result['bundle'].append(node)
        elif obj_type == mmapi.OBJECT_TYPE_CAMERA:
            result['camera'].append(node)
        elif obj_type == mmapi.OBJECT_TYPE_ATTRIBUTE:
            result['attribute'].append(node)
        elif obj_type == mmapi.OBJECT_TYPE_COLLECTION:
            result['collection'].append(node)
        else:
            result['other'].append(node)
    return result


def get_marker_nodes(nodes):
    """
    Filter the given 'nodes' by only the Marker nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Marker nodes, or empty list if no Marker nodes.
    :rtype: list
    """
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('marker', [])


def get_marker_group_nodes(nodes):
    """
    Filter the given 'nodes' by only the MarkerGroup nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of MarkerGroup nodes, or empty list if no MarkerGroup nodes.
    :rtype: list
    """
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('markergroup', [])


def get_bundle_nodes(nodes):
    """
    Filter the given 'nodes' by only the Bundle nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Bundle nodes, or empty list if no Bundle nodes.
    :rtype: list
    """
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('bundle', [])


def get_camera_nodes(nodes):
    """
    Filter the given 'nodes' by only the camera nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of camera nodes, or empty list if no camera nodes.
    :rtype: list
    """
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('camera', [])


def get_collection_nodes(nodes):
    """
    Filter the given 'nodes' by only the Collection nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Collection nodes, or empty list if no Collection nodes.
    :rtype: list
    """
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('collection', [])
