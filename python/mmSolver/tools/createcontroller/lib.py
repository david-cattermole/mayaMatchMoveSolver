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
        settable = maya.cmds.getAttr(plug, settable=True)
        if settable is True and keyable is True:
            keyable_attrs.add(plug)
    return keyable_attrs


def _get_skip_attrs(node, attrs):
    assert len(attrs) == 3
    axis_list = ['x', 'y', 'z']
    skip_attrs = set(axis_list)
    for axis, attr in zip(axis_list, attrs):
        plug = node + '.' + attr
        keyable = maya.cmds.getAttr(plug, keyable=True)
        settable = maya.cmds.getAttr(plug, settable=True)
        if settable is True and keyable is True:
            skip_attrs.remove(axis)
    return skip_attrs


def _get_keyframe_times_for_each_node_attr(nodes, attrs, start_frame, end_frame):
    """
    Query keyframe times on each node attribute (sparse keys)
    """
    frame_ranges_map = {}
    key_times_map = {}
    total_start = 9999999
    total_end = -9999999
    for node in nodes:
        start = start_frame
        end = end_frame
        for attr in attrs:
            plug = node + '.' + attr
            attr_exists = node_utils.attribute_exists(attr, node)
            if attr_exists is False:
                continue
            settable = maya.cmds.getAttr(plug, settable=True)
            if settable is False:
                continue
            times = maya.cmds.keyframe(
                plug,
                query=True,
                timeChange=True
            ) or []
            if len(times) == 0:
                continue
            if node not in key_times_map:
                key_times_map[node] = set()
            times = [int(t) for t in times]
            key_times_map[node] |= set(times)
            node_key_times = key_times_map.get(node)
            key_start = min(node_key_times)
            key_end = max(node_key_times)
            start = min(key_start, start)
            end = max(key_end, end)
        frame_ranges_map[node] = (start, end)
        total_start = min(total_start, start)
        total_end = max(total_end, end)
    return total_start, total_end, frame_ranges_map, key_times_map


def _get_constraints_from_ctrls(input_node):
    """
    Get Constraints 'input_node' is connected to.
    """
    constraints = maya.cmds.listConnections(
        input_node,
        type='constraint',
        source=False,
        destination=True) or []
    constraints = [n for n in constraints
                   if node_utils.node_is_referenced(n) is False]
    constraints = set(constraints)
    if len(constraints) == 0:
        LOG.warn('node is not controlling anything: %r', input_node)
        return set()
    return constraints


def _get_destination_nodes_from_ctrls(constraints):
    """
    Get nodes connected to constraints.
    """
    dest_nodes = set()
    attr = 'constraintParentInverseMatrix'
    for constraint in constraints:
        plug = constraint + '.' + attr
        temp = maya.cmds.listConnections(
            plug,
            type='transform',
            source=True,
            destination=False,
        ) or []
        dest_nodes |= set(temp)
    if len(dest_nodes) != 1:
        return []
    return list(dest_nodes)


def _create_constraint(src_node, dst_node):
    constraints = []
    skip = _get_skip_attrs(src_node, TRANSLATE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.pointConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    skip = _get_skip_attrs(src_node, ROTATE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.orientConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    skip = _get_skip_attrs(src_node, SCALE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.scaleConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    return


def _get_times(node,
               key_times_map,
               frame_ranges_map,
               total_start,
               total_end,
               sparse, allow_empty):
    """
    The logic to query time for a node, in sparse or dense mode.
    """
    times = []
    fallback_frame_range = (total_start, total_end)
    fallback_times = list(range(total_start, total_end + 1))
    if sparse is True:
        tmp = []
        if allow_empty is False:
            tmp = fallback_times
        times = key_times_map.get(node, tmp)
    else:
        start, end = frame_ranges_map.get(node, fallback_frame_range)
        times = range(start, end + 1)
    times = list(times)
    if allow_empty is False:
        assert len(times) > 0
    return times


def create(nodes, sparse=True):
    dont_allow_empty = False
    allow_empty = True
    tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]

    # Force into long-names.
    nodes = [n.get_node() for n in tfm_nodes]

    # Ensure node attributes are editable.
    keyable_attrs = set()
    for node in nodes:
        keyable_attrs |= _get_keyable_attrs(node, TFM_ATTRS)

    # Query keyframe times on each node attribute
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    total_start, total_end, frame_ranges_map, key_times_map = _get_keyframe_times_for_each_node_attr(
        nodes,
        TFM_ATTRS,
        start_frame,
        end_frame)

    # Query the transform matrix for the nodes
    cache = tfm_utils.TransformMatrixCache()
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        times = _get_times(node,
                           key_times_map, frame_ranges_map,
                           total_start, total_end,
                           sparse, dont_allow_empty)
        cache.add_node(tfm_node, times)
    cache.process()

    # Create new (locator) node for each input node
    ctrl_list = []
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        name = node.rpartition('|')[-1]
        assert '|' not in name
        name = name.replace(':', '_')
        name = name + '_CTRL'
        name = mmapi.find_valid_maya_node_name(name)
        # TODO: Allow maintaining relative hierarchy of nodes.
        tfm = maya.cmds.createNode('transform', name=name)
        maya.cmds.createNode('locator', parent=tfm)
        rot_order = maya.cmds.xform(node, query=True, rotateOrder=True)
        maya.cmds.xform(tfm, rotateOrder=rot_order, preserve=True)
        ctrl_list.append(tfm)
    ctrl_tfm_nodes = [tfm_utils.TransformNode(node=tfm)
                      for tfm in ctrl_list]

    # Set transform matrix on new node
    for src, dst in zip(tfm_nodes, ctrl_tfm_nodes):
        src_node = src.get_node()
        times = _get_times(src_node,
                           key_times_map, frame_ranges_map,
                           total_start, total_end,
                           sparse, dont_allow_empty)
        tfm_utils.set_transform_values(
            cache, times, src, dst,
            delete_static_anim_curves=False
        )
        if sparse is True:
            # Remove keyframes
            src_times = _get_times(src_node,
                                   key_times_map, frame_ranges_map,
                                   total_start, total_end,
                                   sparse, allow_empty)
            dst_node = dst.get_node()
            if len(src_times) == 0:
                time_range = (total_start, total_end)
                maya.cmds.cutKey(
                    dst_node,
                    attribute=TFM_ATTRS,
                    time=time_range,
                    clear=True
                )

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
        _create_constraint(src_node, dst_node)
    return ctrl_list


def remove(nodes, sparse=True):
    """
    Remove a controller and push the animation back to the controlled
    object.

    .. todo:: What should we do with any transforms parented under the
    controller? Should these objects be re-parented under the
    controlled object? Probably yes.

    """
    dont_allow_empty = False
    allow_empty = True
        
    # find controlled nodes from controller nodes
    ctrl_to_ctrlled_map = {}
    for ctrl_node in nodes:
        constraints = _get_constraints_from_ctrls(ctrl_node)
        dests = _get_destination_nodes_from_ctrls(constraints)
        if len(dests) == 0:
            continue
        ctrl_to_ctrlled_map[ctrl_node] = (constraints, dests)

    # Query keyframe times on controller nodes.
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    total_start, total_end, frame_ranges_map, key_times_map = _get_keyframe_times_for_each_node_attr(
        nodes,
        TFM_ATTRS,
        start_frame,
        end_frame)

    # query transform matrix on controlled nodes.
    cache = tfm_utils.TransformMatrixCache()
    for ctrl_node, (constraints, dest_nodes) in ctrl_to_ctrlled_map.items():
        times = _get_times(ctrl_node,
                           key_times_map, frame_ranges_map,
                           total_start, total_end,
                           sparse, dont_allow_empty)
        ctrl = tfm_utils.TransformNode(node=ctrl_node)
        cache.add_node(ctrl, times)
        for dest_node in dest_nodes:
            dest = tfm_utils.TransformNode(node=dest_node)
            cache.add_node(dest, times)
    cache.process()

    # Get Controlled nodes
    ctrlled_nodes = set()
    for ctrl_node, (_, dest_nodes) in ctrl_to_ctrlled_map.items():
        for dest_node in dest_nodes:
            ctrlled_nodes.add(dest_node)

    # Delete constraints on controlled nodes.
    const_nodes = set()
    for ctrl_node, (constraints, _) in ctrl_to_ctrlled_map.items():
        const_nodes |= constraints
    if len(const_nodes) > 0:
        maya.cmds.delete(list(const_nodes))

    # Set keyframes (per-frame) on controlled nodes
    for ctrl_node, (_, ctrlled_nodes) in ctrl_to_ctrlled_map.items():
        times = _get_times(ctrl_node,
                           key_times_map, frame_ranges_map,
                           total_start, total_end,
                           sparse, dont_allow_empty)
        ctrl = tfm_utils.TransformNode(node=ctrl_node)
        for ctrlled_node in ctrlled_nodes:
            ctrlled = tfm_utils.TransformNode(node=ctrlled_node)
            tfm_utils.set_transform_values(cache, times, ctrl, ctrlled,
                                           delete_static_anim_curves=False)

            # Re-parent controller child nodes under controlled node.
            ctrl_children = maya.cmds.listRelatives(
                ctrl_node,
                children=True,
                shapes=False,
                fullPath=True,
                type='transform',
            ) or []
            for child_node in ctrl_children:
                maya.cmds.parent(child_node, ctrlled_node, absolute=True)

    # Delete controller nodes
    ctrl_nodes = ctrl_to_ctrlled_map.keys()
    if len(ctrl_nodes) > 0:
        maya.cmds.delete(ctrl_nodes)
    return list(ctrlled_nodes)
