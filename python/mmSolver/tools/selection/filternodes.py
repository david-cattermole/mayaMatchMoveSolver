"""
"""

import maya.cmds

import mmSolver.api as mmapi


def get_nodes(nodes):
    """
    Return nodes sorted into mmSolver-specific categories.
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
        if obj_type == 'marker':
            result['marker'].append(node)
        elif obj_type == 'markergroup':
            result['markergroup'].append(node)
        elif obj_type == 'bundle':
            result['bundle'].append(node)
        elif obj_type == 'camera':
            result['camera'].append(node)
        elif obj_type == 'attribute':
            result['attribute'].append(node)
        elif obj_type == 'collection':
            result['collection'].append(node)
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


# def get_attribute_nodes(nodes):
#     filter_nodes = get_nodes(nodes)
#     return filter_nodes.get('attribute', [])

def get_collection_nodes(nodes):
    filter_nodes = get_nodes(nodes)
    return filter_nodes.get('collection', [])

