# Copyright (C) 2019 David Cattermole.
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
Create a controller transform node.

Ideas::

  - Have a flag to allow maintaining the relative hierarchy of the
    input transforms.

"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.transform as tfm_utils

import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()

TRANSLATE_ATTRS = [
    'translateX', 'translateY', 'translateZ'
]

ROTATE_ATTRS = [
    'rotateX', 'rotateY', 'rotateZ'
]

SCALE_ATTRS = [
    'scaleX', 'scaleY', 'scaleZ'
]

TFM_ATTRS = []
TFM_ATTRS += TRANSLATE_ATTRS
TFM_ATTRS += ROTATE_ATTRS
TFM_ATTRS += SCALE_ATTRS


def _get_keyable_attrs(node, attrs):
    keyable_attrs = set()
    for attr in attrs:
        plug = node + '.' + attr
        keyable = maya.cmds.getAttr(plug, keyable=True)
        if keyable is True:
            keyable_attrs.add(plug)
    return keyable_attrs


def _get_skip_attrs(node, attrs):
    assert len(attrs) == 3
    axis_list = ['x', 'y', 'z']
    skip_attrs = set(axis_list)
    for axis, attr in zip(axis_list, attrs):
        plug = node + '.' + attr
        keyable = maya.cmds.getAttr(plug, keyable=True)
        if keyable is True:
            skip_attrs.remove(axis)
    return skip_attrs


def create(nodes, sparse=True):
    tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]

    # Ensure node attributes are editable.
    keyable_attrs = set()
    for node in nodes:
        keyable_attrs |= _get_keyable_attrs(node, TFM_ATTRS)

    # Query keyframe times on each node attribute (sparse keys)
    frame_ranges = {}
    key_times = {}
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    total_start = 999999
    total_end = -999999
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        start = start_frame
        end = end_frame
        for attr in TFM_ATTRS:
            plug = node + '.' + attr
            times = maya.cmds.keyframe(
                plug,
                query=True,
                timeChange=True
            ) or []
            if node not in key_times:
                key_times[node] = set()
            if len(times) == 0:
                continue
            times = [int(t) for t in times]
            key_times[node] |= set(times)
            node_key_times = key_times.get(node)
            key_start = min(node_key_times)
            key_end = max(node_key_times)
            start = min(key_start, start)
            end = max(key_end, end)
        frame_ranges[node] = (start, end)
        total_start = min(total_start, start)
        total_end = max(total_end, end)

    # Query the transform matrix for the nodes
    fallback_frame_range = (total_start, total_end)
    cache = tfm_utils.TransformMatrixCache()
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        start, end = frame_ranges.get(node, fallback_frame_range)
        times = list(range(start, end + 1))
        cache.add(tfm_node, 'worldMatrix[0]', times)
    cache.process()

    # Create new (locator) node for each input node
    ctrl_list = []
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        name = node + '_CTRL'
        name = mmapi.find_valid_maya_node_name(name)
        # # TODO: Allow maintaining relative hierarchy of nodes.
        # if maintain_hierarchy is True:
        #     pass
        # TODO: How to workout what rotation order to use?
        tfm = maya.cmds.createNode('transform', name=name)
        maya.cmds.createNode('locator', parent=tfm)
        ctrl_list.append(tfm)
    ctrl_tfm_nodes = [tfm_utils.TransformNode(node=tfm)
                      for tfm in ctrl_list]

    # Set transform matrix on new node
    for tfm_node, ctrl in zip(tfm_nodes, ctrl_tfm_nodes):
        node = tfm_node.get_node()
        start, end = frame_ranges.get(node, fallback_frame_range)
        times = list(range(start, end + 1))
        if sparse is True:
            temp = list(key_times.get(node))
            if len(temp) > 0:
                times = temp
        tfm_utils.set_transform_values(cache, times, tfm_node, ctrl)

    # # TODO: Use a sparse-to-dense Maya animCurve solver.
    # if sparse is True:
    #     pass

    # Delete all keyframes on controlled nodes
    anim_curves = anim_utils.get_anim_curves_from_nodes(
        list(keyable_attrs),
    )
    anim_curves = [n for n in anim_curves
                   if node_utils.node_is_referenced(n) is False]
    if len(anim_curves) > 0:
        maya.cmds.delete(anim_curves)

    # Create constraint(s) to previous nodes.
    for tfm_node, ctrl in zip(tfm_nodes, ctrl_tfm_nodes):
        src_node = tfm_node.get_node()
        dst_node = ctrl.get_node()
        skip = _get_skip_attrs(node, TRANSLATE_ATTRS)
        if len(skip) != 3:
            maya.cmds.pointConstraint(dst_node, src_node, skip=tuple(skip))
        skip = _get_skip_attrs(node, ROTATE_ATTRS)
        if len(skip) != 3:
            maya.cmds.orientConstraint(dst_node, src_node, skip=tuple(skip))
        skip = _get_skip_attrs(node, SCALE_ATTRS)
        if len(skip) != 3:
            maya.cmds.scaleConstraint(dst_node, src_node, skip=tuple(skip))
    return ctrl_list


def remove(nodes):
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()

    # detect if these are 'controllers'

    # find controlled nodes from controller nodes
    ctrl_to_ctrlled_map = {}
    ctrl_to_const_map = {}
    for node in nodes:
        const_nodes = maya.cmds.listConnections(
            node,
            type='constraint',
            source=False,
            destination=True) or []
        const_nodes = set(const_nodes)
        # TODO: Filter by referenced constraints.
        LOG.warn('constraints: %r', const_nodes)
        if len(const_nodes) == 0:
            LOG.warn('node is not controlling anything: %r', node)
            continue

        controlled_nodes = set()
        attr = 'constraintParentInverseMatrix'
        for const_node in const_nodes:
            plug = const_node + '.' + attr
            temp = maya.cmds.listConnections(
                plug,
                type='transform',
                source=True,
                destination=False,
            ) or []
            controlled_nodes |= set(temp)
        LOG.warn('controlled_nodes: %r', controlled_nodes)
        if len(controlled_nodes) != 1:
            continue
        ctrl_to_ctrlled_map[node] = list(controlled_nodes)[0]
        ctrl_to_const_map[node] = const_nodes

    # query transform matrix on controlled nodes.
    times = list(range(start_frame, end_frame + 1))
    cache = tfm_utils.TransformMatrixCache()
    for ctrl_node, ctrlled_node in ctrl_to_ctrlled_map.items():
        ctrl = tfm_utils.TransformNode(node=ctrl_node)
        ctrlled = tfm_utils.TransformNode(node=ctrlled_node)
        cache.add(ctrlled, 'worldMatrix[0]', times)
        cache.add(ctrl, 'worldMatrix[0]', times)
    cache.process()

    # TODO: query keyframe times on controller nodes.

    # delete constraints on controlled nodes.
    ctrlled_nodes = set()
    const_nodes = set()
    for ctrl_node, ctrlled_node in ctrl_to_ctrlled_map.items():
        const_nodes |= set(ctrl_to_const_map.get(ctrl_node))
        ctrlled_nodes.add(ctrlled_node)
    LOG.warn('const_nodes: %r', list(const_nodes))
    if len(const_nodes) > 0:
        maya.cmds.delete(list(const_nodes))

    # set keyframes (per-frame) on controlled nodes
    for ctrl_node, ctrlled_node in ctrl_to_ctrlled_map.items():
        ctrl = tfm_utils.TransformNode(node=ctrl_node)
        ctrlled = tfm_utils.TransformNode(node=ctrlled_node)
        tfm_utils.set_transform_values(cache, times, ctrl, ctrlled)

    # TODO: Delete keyframes for non-keyed times (sparse)

    # delete controller nodes
    ctrl_nodes = ctrl_to_ctrlled_map.keys()
    LOG.warn('ctrl_nodes: %r', list(ctrl_nodes))
    if len(ctrl_nodes) > 0:
        maya.cmds.delete(ctrl_nodes)
    LOG.warn('ctrlled_nodes: %r', list(ctrlled_nodes))
    
    return list(ctrlled_nodes)
