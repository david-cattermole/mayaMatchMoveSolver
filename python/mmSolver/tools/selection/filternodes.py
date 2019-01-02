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
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('marker', [])


def get_marker_group_nodes(nodes):
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('markergroup', [])

def get_bundle_nodes(nodes):
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('bundle', [])


def get_camera_nodes(nodes):
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('camera', [])


def get_collection_nodes(nodes):
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('collection', [])
