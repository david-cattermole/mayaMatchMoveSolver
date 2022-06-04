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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils


LOG = mmSolver.logger.get_logger()


def filter_nodes_into_categories(nodes):
    """
    Return nodes sorted into mmSolver-specific object type categories.

    Supported categories are:

    - OBJECT_TYPE_CAMERA
    - OBJECT_TYPE_MARKER
    - OBJECT_TYPE_LINE
    - OBJECT_TYPE_LENS
    - OBJECT_TYPE_IMAGE_PLANE
    - OBJECT_TYPE_MARKER_GROUP
    - OBJECT_TYPE_BUNDLE
    - OBJECT_TYPE_ATTRIBUTE
    - OBJECT_TYPE_COLLECTION
    - 'other'

    :param nodes: Maya nodes to categorise.
    :type nodes: list of str

    :returns: Dictionary with lists for each object type.
    :rtype: dict
    """
    assert isinstance(nodes, (list, tuple))
    result = {
        const.OBJECT_TYPE_CAMERA: [],
        const.OBJECT_TYPE_MARKER: [],
        const.OBJECT_TYPE_LINE: [],
        const.OBJECT_TYPE_LENS: [],
        const.OBJECT_TYPE_IMAGE_PLANE: [],
        const.OBJECT_TYPE_MARKER_GROUP: [],
        const.OBJECT_TYPE_BUNDLE: [],
        const.OBJECT_TYPE_ATTRIBUTE: [],
        const.OBJECT_TYPE_COLLECTION: [],
        'other': [],
    }
    for node in nodes:
        obj_type = api_utils.get_object_type(node)
        if obj_type == const.OBJECT_TYPE_MARKER:
            result[const.OBJECT_TYPE_MARKER].append(node)
        elif obj_type == const.OBJECT_TYPE_LINE:
            result[const.OBJECT_TYPE_LINE].append(node)
        elif obj_type == const.OBJECT_TYPE_LENS:
            result[const.OBJECT_TYPE_LENS].append(node)
        elif obj_type == const.OBJECT_TYPE_IMAGE_PLANE:
            result[const.OBJECT_TYPE_IMAGE_PLANE].append(node)
        elif obj_type == const.OBJECT_TYPE_MARKER_GROUP:
            result[const.OBJECT_TYPE_MARKER_GROUP].append(node)
        elif obj_type == const.OBJECT_TYPE_BUNDLE:
            result[const.OBJECT_TYPE_BUNDLE].append(node)
        elif obj_type == const.OBJECT_TYPE_CAMERA:
            result[const.OBJECT_TYPE_CAMERA].append(node)
        elif obj_type == const.OBJECT_TYPE_ATTRIBUTE:
            result[const.OBJECT_TYPE_ATTRIBUTE].append(node)
        elif obj_type == const.OBJECT_TYPE_COLLECTION:
            result[const.OBJECT_TYPE_COLLECTION].append(node)
        else:
            result['other'].append(node)
    return result


def filter_marker_nodes(nodes):
    """
    Filter the given 'nodes' by only the Marker nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Marker nodes, or empty list if no Marker nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_MARKER, [])


def filter_line_nodes(nodes):
    """
    Filter the given 'nodes' by only the Line nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Line nodes, or empty list if no Line nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_LINE, [])


def filter_lens_nodes(nodes):
    """
    Filter the given 'nodes' by only the lens nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of lens nodes, or empty list if no lens nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_LENS, [])


def filter_image_plane_nodes(nodes):
    """
    Filter the given 'nodes' by only the imagePlane nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of imagePlane nodes, or empty list if no imagePlane nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_IMAGE_PLANE, [])


def filter_marker_group_nodes(nodes):
    """
    Filter the given 'nodes' by only the MarkerGroup nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of MarkerGroup nodes, or empty list if no MarkerGroup nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_MARKER_GROUP, [])


def filter_bundle_nodes(nodes):
    """
    Filter the given 'nodes' by only the Bundle nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Bundle nodes, or empty list if no Bundle nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_BUNDLE, [])


def filter_camera_nodes(nodes):
    """
    Filter the given 'nodes' by only the camera nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of camera nodes, or empty list if no camera nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_CAMERA, [])


def filter_collection_nodes(nodes):
    """
    Filter the given 'nodes' by only the Collection nodes.

    :param nodes: List of nodes to query.
    :type nodes: list or str

    :returns: A list of Collection nodes, or empty list if no Collection nodes.
    :rtype: list
    """
    filter_nodes = filter_nodes_into_categories(nodes)
    return filter_nodes.get(const.OBJECT_TYPE_COLLECTION, [])
