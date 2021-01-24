# Copyright (C) 2019, 2020 David Cattermole.
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
Query DG relationship information.

Use the Maya DG graph structure to determine the sparsity structure,
a relation of cause and effect; which attributes affect which
markers.

Answer this question: 'for each marker, determine which attributes
can affect it's bundle.'

Detect inputs and outputs for marker-bundle relationships. For each
marker, get the bundle, then find all the attributes that affect the
bundle (and it's parent nodes). If the bundle cannot be affected by
any attribute in the solver, print a warning and remove it from the
solve list.

This relationship building will be the basis for the mmSolver
residual/parameter block creation. Note we do not need to worry
about time in our relationship building, connections cannot be made
at different times (and if they did, that would be stupid). This
relationship building could mean we only need to measure a limited
number of bundles, hence improving performance.

There are special cases for detecting inputs/outputs between markers
and attributes.

- Any transform node/attribute above the marker in the DAG that
  affects the world transform.

- Cameras; transform attributes and focal length will affect all
  markers

.. todo:: Calculating node affect relationships is too slow. We need
    to find a way of caching the calculation, so that batches of
    functions that do not change connections can re-use exist
    computations, leading to greater speed ups, at the cost of memory.

"""

from __future__ import absolute_import

import time
import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils

import traceback

LOG = mmSolver.logger.get_logger()

VALID_ATTR_TYPES = set([
    'double',
    'doubleLinear',
    'doubleAngle',
    'time',
    'float',
])

CAMERA_ATTRS = set([
    'nearClipPlane',
    'farClipPlane',
    'focalLength',
    'horizontalFilmAperture',
    'verticalFilmAperture',
    'cameraScale',
    'filmFitOffset',
    'horizontalFilmOffset',
    'verticalFilmOffset',
    'lensSqueezeRatio',
])


def _get_full_path_plug(plug):
    """
    Get convert a 'name.attr' string into the long name equal.

    :param plug: Name and attribute as a dot-separated string.
    :type plug: str

    :returns: Long name for the given plug.
    :rtype: str
    """
    node = plug.partition('.')[0]
    attr = plug.partition('.')[-1]
    # the line below has been commented out due to issues
    # we were seeing in GitHub Issue-183, leaving it here
    # for future reference in case we need this again...
    # attr = maya.cmds.attributeName(plug, long=True)
    node = maya.cmds.ls(node, long=True)[0]
    full_path = node + '.' + attr
    return str(full_path)


def _get_upstream_nodes(node_name):
    node_types = maya.cmds.nodeType(node_name, inherited=True)
    out_nodes = []
    if 'dagNode' in node_types:
        # DAG upstream
        out_nodes = maya.cmds.listConnections(
            node_name, source=True, destination=False,
            plugs=False, shapes=False, connections=False,
            skipConversionNodes=False) or []
    else:
        # DG upstream
        out_nodes = maya.cmds.listHistory(
            node_name,
            allConnections=True,
            leaf=False,
            levels=0,
            pruneDagObjects=False) or []
    out_nodes = [str(node_utils.get_long_name(n)) for n in out_nodes]
    return out_nodes


def _get_connected_nodes(tfm_node):
    all_nodes = []
    node_name = tfm_node
    out_nodes = _get_upstream_nodes(node_name)
    all_nodes += out_nodes
    max_iter_count = 9
    iter_count = 0
    while len(out_nodes) > 0:
        iter_count += 1
        for node_name in list(out_nodes):
            out_nodes = _get_upstream_nodes(node_name)
            out_nodes = list(set(out_nodes).difference(all_nodes))
            all_nodes += out_nodes
        if iter_count > max_iter_count:
            msg = ('Gathering connected nodes exceeded %r iterations,'
                   ' stopping.')
            LOG.warn(msg, max_iter_count)
            break
    return sorted(list(set(all_nodes)))


def __get_and_fill_cache_value(cache, key, func):
    if cache is None:
        return func()
    value = cache.get(key)
    if value is None:
        value = func()
        cache[key] = value
    return value


def _convert_node_to_plugs(node, attr, node_type,
                           worldspace_cache=None,
                           type_cache=None):
    """Logic to decide if this attribute will affect the node."""
    plugs = set()
    node_type_plug = '{0}.{1}'.format(node_type, attr)

    if node_type == 'camera':
        # If the attribute affects the camera projection matrix, then
        # it's important to us.
        if attr not in CAMERA_ATTRS:
            return plugs
    else:
        # All other nodes, skip if world space is not affected
        ws = __get_and_fill_cache_value(
            worldspace_cache,
            node_type_plug,
            lambda: maya.cmds.attributeQuery(attr, node=node, affectsWorldspace=True))
        if ws is False:
            return plugs

    node_attr = '{0}.{1}'.format(node, attr)
    settable = maya.cmds.getAttr(node_attr, settable=True)
    if settable is True:
        typ = __get_and_fill_cache_value(
            type_cache,
            node_type_plug,
            lambda: maya.cmds.getAttr(node_attr, type=True))
        if typ in VALID_ATTR_TYPES:
            plugs.add(node_attr)
        return plugs

    # Get plugs connected to this attribute, recursively
    conn_attrs = maya.cmds.listConnections(
        node_attr,
        source=True,
        destination=False,
        plugs=True) or []
    while len(conn_attrs) > 0:
        node_attr = conn_attrs.pop()
        node_attr = _get_full_path_plug(node_attr)
        settable = maya.cmds.getAttr(node_attr, settable=True)
        if settable is True:
            attr = node_attr.rpartition('.')[-1]
            node_type = maya.cmds.nodeType(node)
            node_type_plug = '{0}.{1}'.format(node_type, attr)
            typ = __get_and_fill_cache_value(
                type_cache,
                node_type_plug,
                lambda: maya.cmds.getAttr(node_attr, type=True))
            if typ in VALID_ATTR_TYPES:
                plugs.add(node_attr)
            continue

        # Get the plugs that affect this plug.
        tmp_list = maya.cmds.listConnections(
            node_attr,
            source=True,
            destination=False,
            plugs=True) or []

        # Filter by valid plug types.
        for tmp in tmp_list:
            node_ = tmp.partition('.')[0]
            attr_ = tmp.partition('.')[-1]

            affects_this_plug = maya.cmds.affects(attr_, node_) or []
            for attr__ in affects_this_plug:
                if not node_utils.attribute_exists(attr__, node_):
                    continue
                node_attr = node_ + '.' + attr__
                # this block below was implemented to address
                # GitHub Issue-183
                compound_attrs = maya.cmds.listAttr(node_attr, multi=True)
                if compound_attrs > 1:
                    for array_item in compound_attrs:
                        node_attr = node_ + '.' + array_item
                        node_attr = _get_full_path_plug(node_attr)
                        conn_attrs += [node_attr]
                else:
                    node_attr = _get_full_path_plug(node_attr)
                    conn_attrs += [node_attr]
        # Only unique attributes.
        conn_attrs = list(set(conn_attrs))
    return plugs


def _get_attribute_plugs(nodes):
    node_type_attrs_cache = dict()
    worldspace_cache = dict()
    type_cache = dict()
    plugs = set()
    for node in nodes:
        node_type = maya.cmds.nodeType(node)
        attrs = __get_and_fill_cache_value(
            node_type_attrs_cache,
            node_type,
            lambda: maya.cmds.listAttr(node, leaf=True, userDefined=False) or [])
        attrs = set(attrs)
        for attr in attrs:
            plugs |= _convert_node_to_plugs(
                node, attr, node_type,
                worldspace_cache=worldspace_cache,
                type_cache=type_cache)
        user_attrs = maya.cmds.listAttr(node, leaf=True, userDefined=True) or []
        user_attrs = set(user_attrs).difference(set(attrs))
        for attr in user_attrs:
            plugs |= _convert_node_to_plugs(node, attr, node_type)
    return plugs


def find_plugs_affecting_transform(tfm_node, cam_tfm):
    """
    Find plugs that affect the world-matrix transform of the node.

    The 'cam_tfm' argument is for nodes that may be impacted by the
    screen-space matrix that views the 'tfm_node'.

    :param tfm_node: The input node to query.
    :type tfm_node: str

    :param cam_tfm: The camera that should be considered (optional).
    :type cam_tfm: str or None

    :returns:
        An unordered list of Maya attributes in 'node.attr' string
        format.
    :rtype: [str, ..]
    """
    tfm_node = maya.cmds.ls(tfm_node, long=True)[0]

    # Get camera related to the given bundle.
    camera_nodes = []
    if cam_tfm is not None:
        assert maya.cmds.objExists(cam_tfm) is True
        cam_tfm_node = maya.cmds.ls(cam_tfm, long=True)[0]
        cam_shp_node = maya.cmds.listRelatives(
            cam_tfm,
            shapes=True,
            fullPath=True)[0]
        if cam_tfm_node not in camera_nodes:
            camera_nodes.append(cam_tfm_node)
        if cam_shp_node not in camera_nodes:
            camera_nodes.append(cam_shp_node)

    # Get all the parents above the nodes.
    parent_nodes = []
    get_parent_nodes = camera_nodes + [tfm_node]
    for node in get_parent_nodes:
        parents = maya.cmds.listRelatives(
            node,
            parent=True,
            fullPath=True) or []
        parent_nodes += parents
        while len(parents) > 0:
            parents = maya.cmds.listRelatives(
                parents,
                parent=True,
                fullPath=True) or []
            parent_nodes += parents
    nodes = [tfm_node] + camera_nodes + parent_nodes

    conn_nodes = set()
    for node in list(nodes):
        conn_nodes |= set(_get_connected_nodes(node))
    nodes = nodes + list(conn_nodes)

    plugs = _get_attribute_plugs(nodes)
    plugs = list(set(plugs))  # Only unique plugs.
    return plugs


def find_marker_attr_mapping_raw(mkr_list, attr_list):
    """
    Get a mapping of markers to attributes, as a matrix.

    :param mkr_list: Tuple of marker node, bundle node and camera
                     shape node in a list; each list of nodes
                     represent a single Marker relationship and will
                     be considered in mapping.
    :type mkr_list: [(str, str, str), ..]

    :param attr_list: Maya attributes to consider in mapping, in the
                      familiar 'node.attr' string representation.
    :type attr_list: [str, ..]

    :returns: Boolean matrix of size 'markers x attrs'. Matrix index
              is 'mapping[marker_index][attr_index]', based on the
              index of the mkr_cam_node_frm_list and attr_list given.
    :rtype: [[bool, .. ]]
    """
    mapping = []
    for i, mkr in enumerate(mkr_list):
        # Initialise mapping list size.
        tmp = [False] * len(attr_list)
        mapping.append(tmp)

        mkr_node = mkr[0]
        bnd_node = mkr[2]
        cam_node = maya.cmds.listRelatives(mkr[1], parent=True)[0]
        mkr_plugs = []
        bnd_plugs = find_plugs_affecting_transform(bnd_node, None)
        plugs = list(set(mkr_plugs + bnd_plugs))
        for j, attr_name in enumerate(attr_list):
            attr_name = _get_full_path_plug(attr_name)
            mapping[i][j] = attr_name in plugs
    return mapping


def sort_into_hierarchy_groups(mkr_list, attr_list):
    """
    Create blocks of Markers and Attributes, sorted by hierarchy.

    This will allow us to solve top-level objects (ie, root level)
    first, before solving children. This will ensure we minimise the
    base before attempting to solve the children.
    """
    # TODO: Write this.
    raise NotImplementedError
