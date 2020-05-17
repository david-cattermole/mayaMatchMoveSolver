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
Create a controller transform node.

Ideas::

  - Have a flag to allow maintaining the relative hierarchy of the
    input transforms.

.. note:: If no keyframes are set, this tool works on the current
   frame and adds a keyframe to the controller.

"""

import collections

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent.keytimeutils as keytime_utils
import mmSolver.tools.createcontroller.constant as const

import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


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
        LOG.warn('Node is not controlling anything: %r', input_node)
        return set()
    assert input_node not in constraints
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
    """
    Create constraint from source node to destination node.

    :param src_node: Constrain from this node.
    :type src_node: stc

    :param dst_node: Control this node with constraint nodes.
    :type dst_node: str

    :rtype: None
    """
    constraints = []
    skip = _get_skip_attrs(src_node, const.TRANSLATE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.pointConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    skip = _get_skip_attrs(src_node, const.ROTATE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.orientConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    skip = _get_skip_attrs(src_node, const.SCALE_ATTRS)
    if len(skip) != 3:
        constraints += maya.cmds.scaleConstraint(
            dst_node,
            src_node,
            skip=tuple(skip)
        )
    return


def _sort_by_hierarchy(nodes, children_first=False):
    """
    Sort the nodes by hierarchy depth; level 0 first, 1 second,
    until 'n'.
    """
    assert isinstance(nodes, (list, set, tuple))
    depth_to_node_map = collections.defaultdict(list)
    for node in nodes:
        assert isinstance(node, basestring)
        depth = node.count('|')
        depth_to_node_map[depth].append(node)
    nodes = []
    depths = sorted(depth_to_node_map.keys())
    if children_first is True:
        depths = reversed(depths)
    for depth in depths:
        node_list = depth_to_node_map.get(depth)
        assert len(node_list) > 0
        nodes += sorted(node_list)
    return nodes


def _sort_hierarchy_depth_to_nodes(nodes):
    depth_to_node_map = collections.defaultdict(set)
    for node in nodes:
        depth = node.count('|')
        depth_to_node_map[depth].add(node)
    return depth_to_node_map


def _sort_hierarchy_depth_to_tfm_nodes(tfm_nodes):
    depth_to_tfm_node_map = collections.defaultdict(list)
    for tfm_node in tfm_nodes:
        depth = tfm_node.get_node().count('|')
        depth_to_tfm_node_map[depth].append(tfm_node)
    return depth_to_tfm_node_map


def _get_node_parent_map(nodes):
    """
    For each transform node, get the parent transform above it. If no
    parent node exists, get the parent should be None (ie, world or
    root).
    """
    nodes_parent = {}
    for node in nodes:
        parent = None
        parents = node_utils.get_all_parent_nodes(node)
        parents = list(reversed(parents))
        while len(parents) != 0:
            p = parents.pop()
            if p in nodes:
                parent = p
                break
        nodes_parent[node] = parent
    assert len(nodes_parent) == len(nodes)
    return nodes_parent


def create(nodes,
           current_frame=None,
           eval_mode=None):
    """
    Create a Controller for the given nodes.

    :param nodes: The nodes to create Controller for.
    :type nodes: [str, ..]

    :param current_frame: What frame number is considered to be
                          'current' when evaluating transforms without
                          any keyframes.
    :type current_frame: float or int

    :param eval_mode: What type of transform evaluation method to use?
    :type eval_mode: mmSolver.utils.constant.EVAL_MODE_*

    :returns: List of controller transform nodes.
    :rtype: [str, ..]
    """
    if current_frame is None:
        current_frame = maya.cmds.currentTime(query=True)
    assert current_frame is not None
    sparse = False

    tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]

    # Force into long-names.
    nodes = [n.get_node() for n in tfm_nodes]

    # Ensure node attributes are editable.
    keyable_attrs = set()
    for node in nodes:
        keyable_attrs |= _get_keyable_attrs(node, const.TFM_ATTRS)

    # Query keyframe times on each node attribute
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    keytime_obj = keytime_utils.KeyframeTimes()
    for node in nodes:
        keytime_obj.add_node_attrs(node, const.TFM_ATTRS, start_frame, end_frame)
    fallback_frame_range = keytime_obj.sum_frame_range_for_nodes(nodes)
    fallback_times = list(range(fallback_frame_range[0],
                                fallback_frame_range[1]+1))
    key_times_map = time_utils.get_keyframe_times_for_node_attrs(
        nodes,
        const.TFM_ATTRS
    )

    # Query the transform matrix for the nodes
    cache = tfm_utils.TransformMatrixCache()
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        times = key_times_map.get(node, [current_frame])
        cache.add_node(tfm_node, times)
    cache.process(eval_mode=eval_mode)

    depth_to_tfm_node_map = _sort_hierarchy_depth_to_tfm_nodes(tfm_nodes)
    nodes_parent = _get_node_parent_map(nodes)

    # Create new (locator) node for each input node
    ctrl_list = []
    node_to_ctrl_map = {}
    node_to_ctrl_tfm_map = {}
    depths = sorted(depth_to_tfm_node_map.keys())
    for depth in depths:
        depth_tfm_nodes = depth_to_tfm_node_map.get(depth)
        assert depth_tfm_nodes is not None
        sorted_tfm_nodes = sorted(depth_tfm_nodes, key=lambda x: x.get_node())
        for tfm_node in sorted_tfm_nodes:
            node = tfm_node.get_node()
            node_parent = nodes_parent.get(node)
            if node_parent is not None:
                node_parent = node_to_ctrl_map.get(node_parent)
            name = node.rpartition('|')[-1]
            assert '|' not in name
            name = name.replace(':', '_')
            name = name + '_CTRL'
            name = mmapi.find_valid_maya_node_name(name)
            tfm = maya.cmds.createNode(
                'transform',
                name=name,
                parent=node_parent)
            tfm = node_utils.get_long_name(tfm)
            maya.cmds.createNode('locator', parent=tfm)
            rot_order = maya.cmds.xform(node, query=True, rotateOrder=True)
            maya.cmds.xform(tfm, rotateOrder=rot_order, preserve=True)
            ctrl_tfm = tfm_utils.TransformNode(node=tfm)
            ctrl_list.append(tfm)
            node_to_ctrl_map[node] = tfm
            node_to_ctrl_tfm_map[node] = ctrl_tfm

    # Set transform matrix on new node
    anim_curves = []
    for src in tfm_nodes:
        src_node = src.get_node()
        src_times = key_times_map.get(src_node, [current_frame])
        dst = node_to_ctrl_tfm_map.get(src_node)
        assert len(src_times) > 0
        tfm_utils.set_transform_values(
            cache,
            src_times,
            src, dst,
            delete_static_anim_curves=False
        )
        src_had_keys = key_times_map.get(src_node) is not None
        if src_had_keys is True:
            continue
        # Maintain that destination node will not have keyframes now, the
        # same as the source node.
        dst_node = dst.get_node()
        keyable_attrs = _get_keyable_attrs(dst_node, const.TFM_ATTRS)
        anim_curves += anim_utils.get_anim_curves_from_nodes(
            list(keyable_attrs),
        )
    anim_curves = [n for n in anim_curves
                   if node_utils.node_is_referenced(n) is False]
    if len(anim_curves) > 0:
        maya.cmds.delete(anim_curves)

    # Delete all keyframes on controlled nodes
    keyable_attrs = set()
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        keyable_attrs |= _get_keyable_attrs(node, const.TFM_ATTRS)
    anim_curves = anim_utils.get_anim_curves_from_nodes(
        list(keyable_attrs),
    )
    anim_curves = [n for n in anim_curves
                   if node_utils.node_is_referenced(n) is False]
    if len(anim_curves) > 0:
        maya.cmds.delete(anim_curves)

    # Create constraint(s) to previous nodes.
    for tfm_node in tfm_nodes:
        src_node = tfm_node.get_node()
        ctrl = node_to_ctrl_tfm_map.get(src_node)
        dst_node = ctrl.get_node()
        _create_constraint(src_node, dst_node)
    return ctrl_list


def remove(nodes,
           current_frame=None,
           eval_mode=None):
    """
    Remove a controller and push the animation back to the controlled
    object.

    Order the nodes to remove by hierarchy depth. This means that
    children will be removed first, then parents, this ensures we
    don't delete a controller accidentally when a parent controller is
    deleted first.

    :param nodes: The nodes to delete.
    :type nodes: [str, ..]

    :param current_frame: What frame number is considered to be
                          'current' when evaluating transforms without
                          any keyframes.
    :type current_frame: float or int

    :param eval_mode: What type of transform evaluation method to use?
    :type eval_mode: mmSolver.utils.constant.EVAL_MODE_*

    :returns: List of once controlled transform nodes, that are no
              longer controlled.
    :rtype: [str, ..]
    """
    if current_frame is None:
        current_frame = maya.cmds.currentTime(query=True)
    assert current_frame is not None
    sparse = False

    nodes = _sort_by_hierarchy(nodes, children_first=True)
    tfm_nodes = [tfm_utils.TransformNode(node=n)
                 for n in nodes]

    # Find controlled nodes from controller nodes
    ctrl_to_ctrlled_map = {}
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        constraints = _get_constraints_from_ctrls(node)
        dests = _get_destination_nodes_from_ctrls(constraints)
        if len(dests) == 0:
            continue
        dests = _sort_by_hierarchy(dests, children_first=True)
        ctrl_to_ctrlled_map[node] = (constraints, dests)

    # Query keyframe times on controller nodes.
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    keytime_obj = keytime_utils.KeyframeTimes()
    for node in nodes:
        keytime_obj.add_node_attrs(node, const.TFM_ATTRS, start_frame, end_frame)
    fallback_frame_range = keytime_obj.sum_frame_range_for_nodes(nodes)
    fallback_times = list(range(fallback_frame_range[0],
                                fallback_frame_range[1]+1))

    # Query transform matrix on controlled nodes.
    cache = tfm_utils.TransformMatrixCache()
    for ctrl_node, (constraints, dest_nodes) in ctrl_to_ctrlled_map.items():
        times = keytime_obj.get_times(ctrl_node, sparse) or fallback_times
        ctrl = tfm_utils.TransformNode(node=ctrl_node)

    # Query keyframe times on each node attribute
    key_times_map = time_utils.get_keyframe_times_for_node_attrs(
        nodes,
        const.TFM_ATTRS
    )

    # Query transform matrix on controlled nodes.
    cache = tfm_utils.TransformMatrixCache()
    for src_node, (constraints, dst_nodes) in ctrl_to_ctrlled_map.items():
        times = key_times_map.get(src_node, [current_frame])
        assert len(times) > 0
        ctrl = tfm_utils.TransformNode(node=src_node)
        cache.add_node(ctrl, times)
        for dst_node in dst_nodes:
            dst = tfm_utils.TransformNode(node=dst_node)
            cache.add_node(dst, times)
    cache.process(eval_mode=eval_mode)

    # Get Controlled nodes
    ctrlled_nodes = set()
    for src_node, (_, dst_nodes) in ctrl_to_ctrlled_map.items():
        for dst_node in dst_nodes:
            ctrlled_nodes.add(dst_node)

    # Delete constraints on controlled nodes.
    const_nodes = set()
    for src_node, (constraints, _) in ctrl_to_ctrlled_map.items():
        assert src_node not in constraints
        const_nodes |= constraints
    if len(const_nodes) > 0:
        maya.cmds.delete(list(const_nodes))

    # Set keyframes (per-frame) on controlled nodes
    for ctrl_node, (_, ctrlled_nodes) in ctrl_to_ctrlled_map.items():
        times = key_times_map.get(ctrl_node, [current_frame])
        ctrl = tfm_utils.TransformNode(node=ctrl_node)
        for ctrlled_node in ctrlled_nodes:
            ctrlled = tfm_utils.TransformNode(node=ctrlled_node)
            tfm_utils.set_transform_values(cache, times, ctrl, ctrlled,
                                           delete_static_anim_curves=False)

    parent_nodes = []
    anim_curves = []
    for src_node, (_, dst_nodes) in ctrl_to_ctrlled_map.items():
        src_times = key_times_map.get(src_node, [current_frame])
        assert len(src_times) > 0
        ctrl = tfm_utils.TransformNode(node=src_node)
        for dst_node in dst_nodes:
            dst = tfm_utils.TransformNode(node=dst_node)
            tfm_utils.set_transform_values(
                cache, src_times, ctrl, dst,
                delete_static_anim_curves=False
            )

            # Re-parent controller child nodes under controlled node.
            ctrl_children = maya.cmds.listRelatives(
                src_node,
                children=True,
                shapes=False,
                fullPath=True,
                type='transform',
            ) or []
            for child_node in ctrl_children:
                if child_node in nodes:
                    continue
                child = tfm_utils.TransformNode(node=child_node)
                parent_nodes.append((child, dst))

            src_had_keys = key_times_map.get(src_node) is not None
            if src_had_keys is True:
                continue
            # Maintain that destination node will not have keyframes now, the
            # same as the source node.
            dst_node = dst.get_node()
            keyable_attrs = _get_keyable_attrs(dst_node, const.TFM_ATTRS)
            anim_curves += anim_utils.get_anim_curves_from_nodes(
                list(keyable_attrs),
            )

    # Reparent children back to under the controlled.
    for src, dst in parent_nodes:
        src_node = src.get_node()
        dst_node = dst.get_node()
        maya.cmds.parent(src_node, dst_node, absolute=True)

    # Remove animation curves.
    anim_curves = [n for n in anim_curves
                   if node_utils.node_is_referenced(n) is False]
    if len(anim_curves) > 0:
        maya.cmds.delete(anim_curves)

    # Delete controller nodes
    ctrl_nodes = [n.get_node() for n in tfm_nodes]
    if len(ctrl_nodes) > 0:
        maya.cmds.delete(ctrl_nodes)
    return list(ctrlled_nodes)
