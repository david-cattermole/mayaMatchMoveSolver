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
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils


LOG = mmSolver.logger.get_logger()

VALID_ATTR_TYPES = set(
    [
        'double',
        'doubleLinear',
        'doubleAngle',
        'time',
        'float',
    ]
)

CAMERA_ATTRS = set(
    [
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
    ]
)


LENS_ATTRS = set(
    [
        'k1',
        'k2',
        'tdeClassic_distortion',
        'tdeClassic_anamorphicSqueeze',
        'tdeClassic_curvatureX',
        'tdeClassic_curvatureY',
        'tdeClassic_quarticDistortion',
        'tdeRadialStdDeg4_degree2_distortion',
        'tdeRadialStdDeg4_degree2_u',
        'tdeRadialStdDeg4_degree2_v',
        'tdeRadialStdDeg4_degree4_distortion',
        'tdeRadialStdDeg4_degree4_u',
        'tdeRadialStdDeg4_degree4_v',
        'tdeRadialStdDeg4_cylindricDirection',
        'tdeRadialStdDeg4_cylindricBending',
        'tdeAnamorphicStdDeg4_degree2_cx02',
        'tdeAnamorphicStdDeg4_degree2_cy02',
        'tdeAnamorphicStdDeg4_degree2_cx22',
        'tdeAnamorphicStdDeg4_degree2_cy22',
        'tdeAnamorphicStdDeg4_degree4_cx04',
        'tdeAnamorphicStdDeg4_degree4_cy04',
        'tdeAnamorphicStdDeg4_degree4_cx24',
        'tdeAnamorphicStdDeg4_degree4_cy24',
        'tdeAnamorphicStdDeg4_degree4_cx44',
        'tdeAnamorphicStdDeg4_degree4_cy44',
        'tdeAnamorphicStdDeg4_lensRotation',
        'tdeAnamorphicStdDeg4_squeeze_x',
        'tdeAnamorphicStdDeg4_squeeze_y',
    ]
)


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
    node = maya.cmds.ls(node, long=True)[0]
    full_path = node + '.' + attr
    return str(full_path)


def _get_upstream_nodes(node_name):
    node_types = maya.cmds.nodeType(node_name, inherited=True)
    out_nodes = []
    if 'dagNode' in node_types:
        # DAG upstream
        out_nodes = (
            maya.cmds.listConnections(
                node_name,
                source=True,
                destination=False,
                plugs=False,
                shapes=False,
                connections=False,
                skipConversionNodes=False,
            )
            or []
        )
    else:
        # DG upstream
        out_nodes = (
            maya.cmds.listHistory(
                node_name,
                allConnections=True,
                leaf=False,
                levels=0,
                pruneDagObjects=False,
            )
            or []
        )
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
            msg = 'Gathering connected nodes exceeded %r iterations,' ' stopping.'
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


def _convert_node_to_plugs(
    node, attr, node_type, worldspace_cache=None, type_cache=None
):
    """
    Logic to decide if this attribute will affect the node.

    :returns: Set of plugs that the input node will affect.
    :rtype: {str, ..}
    """
    # The 'attr' attribute may never be a compound attribute, such as
    # 'renderLayerInfo.renderLayerRenderable', because if so
    # 'maya.cmds.attributeQuery' will not work.
    assert '.' not in attr

    plugs = set()
    node_type_plug = '{0}.{1}'.format(node_type, attr)

    if node_type == 'camera':
        # If the attribute affects the camera projection matrix, then
        # it's important to us.
        if attr not in CAMERA_ATTRS:
            return plugs
    elif node_type.startswith('mmLensModel'):
        if attr not in LENS_ATTRS:
            return plugs
    else:
        # All other nodes, skip if world space is not affected.
        ws = __get_and_fill_cache_value(
            worldspace_cache,
            node_type_plug,
            lambda: maya.cmds.attributeQuery(attr, node=node, affectsWorldspace=True),
        )
        if ws is False:
            return plugs

    node_attr = '{0}.{1}'.format(node, attr)
    settable = maya.cmds.getAttr(node_attr, settable=True)
    if settable is True:
        typ = __get_and_fill_cache_value(
            type_cache, node_type_plug, lambda: maya.cmds.getAttr(node_attr, type=True)
        )
        if typ in VALID_ATTR_TYPES:
            plugs.add(node_attr)
        return plugs

    # Get plugs connected to this attribute, recursively.
    conn_attrs = (
        maya.cmds.listConnections(node_attr, source=True, destination=False, plugs=True)
        or []
    )
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
                lambda: maya.cmds.getAttr(node_attr, type=True),
            )
            if typ in VALID_ATTR_TYPES:
                plugs.add(node_attr)
            continue

        # Get the plugs that affect this plug.
        tmp_list = (
            maya.cmds.listConnections(
                node_attr, source=True, destination=False, plugs=True
            )
            or []
        )

        # Filter by valid plug types.
        for tmp in tmp_list:
            node_ = tmp.partition('.')[0]
            attr_ = tmp.partition('.')[-1]

            affects_this_plug = maya.cmds.affects(attr_, node_) or []
            for attr__ in affects_this_plug:
                if not node_utils.attribute_exists(attr__, node_):
                    continue
                node_attr = node_ + '.' + attr__
                compound_attrs = maya.cmds.listAttr(node_attr, multi=True)
                if len(compound_attrs) > 1:
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


def _check_node_is_enabled_on_frames(node, attrs, frames):
    assert len(node) > 0
    assert isinstance(frames, (set, list))
    assert len(frames) > 0
    assert isinstance(attrs, (set, list))
    assert len(attrs) > 0

    node_attr_enable = None
    node_attr_weight = None
    if 'enable' in attrs:
        node_attr_enable = node + '.enable'
    if 'weight' in attrs:
        node_attr_weight = node + '.weight'

    if node_attr_enable is None and node_attr_weight is None:
        # If the attributes do not exist, we assume the node is
        # enabled on all frames.
        return set(frames)

    enabled_frames = set()
    for frame in sorted(frames):
        enable = True
        weight = 1.0
        if node_attr_enable:
            # TODO: We may be able to use a cache here, to avoid
            # calling Maya multiple times for the same value.
            enable = maya.cmds.getAttr(node_attr_enable, time=frame)

        if node_attr_weight:
            # TODO: We may be able to use a cache here, to avoid
            # calling Maya multiple times for the same value.
            weight = maya.cmds.getAttr(node_attr_weight, time=frame)

        enabled = enable * weight
        if enabled > 0.00001:
            enabled_frames.add(frame)

    return enabled_frames


def _get_attribute_plugs_dict(nodes, frames):
    assert frames is None or len(frames) > 0

    node_plugs_dict = dict()
    worldspace_cache = dict()
    type_cache = dict()
    for node in nodes:
        node_type = maya.cmds.nodeType(node)

        attrs = maya.cmds.listAttr(node, leaf=True) or []
        attrs = set(attrs)

        enabled_frames = set()
        if frames is not None:
            enabled_frames = _check_node_is_enabled_on_frames(node, attrs, frames)
            if len(enabled_frames) == 0:
                # This node is not valid on any frames given, skip it.
                continue

        node_plugs = set()
        for attr in attrs:
            node_plugs |= _convert_node_to_plugs(
                node,
                attr,
                node_type,
                worldspace_cache=worldspace_cache,
                type_cache=type_cache,
            )

        if frames is None:
            for node_plug in node_plugs:
                node_plugs_dict[node_plug] = None
        else:
            for node_plug in node_plugs:
                if node_plug not in node_plugs_dict:
                    node_plugs_dict[node_plug] = set(enabled_frames)
                    assert len(node_plugs_dict[node_plug]) <= len(frames)
                else:
                    node_plugs_dict[node_plug] |= enabled_frames
                    assert len(node_plugs_dict[node_plug]) <= len(frames)

    return node_plugs_dict


def find_plugs_affecting_bundle(bnd_tfm, mkr_tfm, cam_tfms, frames=None):
    """
    Find plugs that affect the world-matrix transform of the
    bundle transform node for the given frames.

    The 'cam_tfms' argument is for bundles that may be impacted by the
    screen-space matrix that views the 'bnd_tfm'.

    :param bnd_tfm: The input bundle (transform) node to query.
    :type bnd_tfm: str

    :param mkr_tfm: The connected marker node to this bundle.
    :type mkr_tfm: str

    :param cam_tfms: Not yet supported. The cameras that should be
        considered.
    :type cam_tfms: None

    :param frames: Sequence of frame numbers (optional).
    :type frames: [int, ..] or None

    :returns:
        An unordered list of Maya attributes in 'node.attr' string
        format.
    :rtype: [str, ..]
    """
    # TODO: Support multiple camera transforms passed to this
    # function.
    assert cam_tfms is None
    assert frames is None or len(frames) > 0

    mkr_enabled_frames = frames
    if frames is None:
        mkr_enabled_frames = []

    if frames is not None and mkr_tfm is not None:
        mkr_tfm = maya.cmds.ls(mkr_tfm, long=True)[0]
        attrs = maya.cmds.listAttr(mkr_tfm, leaf=True) or []
        mkr_enabled_frames = _check_node_is_enabled_on_frames(
            mkr_tfm, set(attrs), frames
        )
    if len(mkr_enabled_frames) == 0:
        return []

    bnd_tfm = maya.cmds.ls(bnd_tfm, long=True)[0]
    return find_plugs_affecting_transform(bnd_tfm, cam_tfms, frames=mkr_enabled_frames)


def find_plugs_affected_by_marker(mkr_tfm, cam_tfm, frames=None):
    """
    Find plugs that are affected by the given marker transform
    node for the given frames.

    The 'cam_tfm' argument is the camera transform node owns the
    ('mkr_tfm') marker transform.

    :param mkr_tfm: The input marker (transform) node to query.
    :type mkr_tfm: str

    :param cam_tfm: The camera that should be considered (optional).
    :type cam_tfm: str or None

    :param frames: Sequence of frame numbers (optional).
    :type frames: [int, ..] or None

    :returns:
        An unordered list of Maya attributes in 'node.attr' string
        format.
    :rtype: [str, ..]
    """
    assert frames is None or len(frames) > 0

    mkr_enabled_frames = frames
    if frames is None:
        mkr_enabled_frames = []

    mkr_tfm = maya.cmds.ls(mkr_tfm, long=True)[0]
    if frames is not None:
        attrs = maya.cmds.listAttr(mkr_tfm, leaf=True) or []
        mkr_enabled_frames = _check_node_is_enabled_on_frames(
            mkr_tfm, set(attrs), frames
        )
    if len(mkr_enabled_frames) == 0:
        return []

    cam_tfm = maya.cmds.ls(cam_tfm, long=True)[0]
    return find_plugs_affecting_transform(mkr_tfm, cam_tfm, frames=mkr_enabled_frames)


def find_plugs_affecting_transform(tfm_node, cam_tfm, frames=None):
    """
    Find plugs that affect the world-matrix transform of the node
    for the given frames.

    The 'cam_tfm' argument is for nodes that may be impacted by the
    screen-space matrix that views the 'tfm_node'.

    :param tfm_node: The input node to query.
    :type tfm_node: str

    :param cam_tfm: The camera that should be considered (optional).
    :type cam_tfm: str or None

    :param frames: Sequence of frame numbers (optional).
    :type frames: [int, ..] or None

    :returns:
        An unordered list of Maya attributes in 'node.attr' string
        format.
    :rtype: [str, ..]
    """
    tfm_node = maya.cmds.ls(tfm_node, long=True)[0]
    assert frames is None or len(frames) > 0

    # Get camera related to the given transform.
    #
    # TODO: Can we get a list of camera transform nodes as input?
    camera_nodes = set()
    if cam_tfm is not None:
        assert maya.cmds.objExists(cam_tfm) is True
        cam_tfm_node = maya.cmds.ls(cam_tfm, long=True)[0]
        cam_shp_node = maya.cmds.listRelatives(cam_tfm, shapes=True, fullPath=True)[0]
        if cam_tfm_node not in camera_nodes:
            camera_nodes.add(cam_tfm_node)
        if cam_shp_node not in camera_nodes:
            camera_nodes.add(cam_shp_node)

        # Find all lens nodes.
        if node_utils.attribute_exists('inLens', cam_shp_node):
            lens_in_attr = cam_shp_node + '.inLens'
            conn_nodes = maya.cmds.listConnections(lens_in_attr) or []
            conn_nodes = [
                x for x in conn_nodes if maya.cmds.nodeType(x).startswith('mmLensModel')
            ]
            while len(conn_nodes) > 0:
                lens_node = conn_nodes.pop()
                lens_in_attr = lens_node + '.inLens'
                if node_utils.attribute_exists('inLens', lens_node):
                    tmp_nodes = maya.cmds.listConnections(lens_in_attr) or []
                    conn_nodes += [
                        x
                        for x in tmp_nodes
                        if maya.cmds.nodeType(x).startswith('mmLensModel')
                    ]
                camera_nodes.add(lens_node)

    # Get all the parents above the nodes.
    parent_nodes = []
    get_parent_nodes = list(sorted(camera_nodes)) + [tfm_node]
    for node in get_parent_nodes:
        parents = maya.cmds.listRelatives(node, parent=True, fullPath=True) or []
        parent_nodes += parents
        while len(parents) > 0:
            parents = maya.cmds.listRelatives(parents, parent=True, fullPath=True) or []
            parent_nodes += parents
    nodes = [tfm_node] + list(sorted(camera_nodes)) + parent_nodes

    conn_nodes = set()
    for node in list(nodes):
        conn_nodes |= set(_get_connected_nodes(node))
    nodes = nodes + list(sorted(conn_nodes))

    plugs_dict = _get_attribute_plugs_dict(nodes, frames)
    if frames is None:
        plugs = list(sorted(plugs_dict.keys()))  # Only unique plugs.
    else:
        plugs = []
        for plug_name in plugs_dict.keys():
            valid_frames = plugs_dict[plug_name]
            assert len(valid_frames) > 0
            valid_frames = [str(x) for x in valid_frames]
            valid_frames_str = ','.join(valid_frames)
            assert len(valid_frames_str) > 0
            plug = '{}#{}'.format(plug_name, valid_frames_str)
            plugs.append(plug)

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

        bnd_node = mkr[2]
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
