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
Re-parent transform node to a new parent, across time.
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.transform as tfm_utils

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


def __are_nodes_the_same(tfm_node_a, tfm_node_b):
    """
    Test if two TransformNode objects point to the same underlying node.
    """
    if tfm_node_a is None and tfm_node_b is not None:
        return False
    if tfm_node_a is not None and tfm_node_b is None:
        return False
    if tfm_node_a is None and tfm_node_b is None:
        return True
    node_a = tfm_node_a.get_node()
    node_b = tfm_node_b.get_node()
    return node_a == node_b


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


def reparent(children, parent,
             sparse=True,
             delete_static_anim_curves=True):
    """
    Reparent the children under the given parent.

    :param children: List of child nodes to be modified.
    :type children: [TransformNode, ..]

    :param parent: The new parent node for children, or None means 
                   unparent.
    :type parent: TransformNode or None

    :param sparse: Keyframe animation on the children each frame 
                   (dense) or sparse (only at keyframes).
    :type sparse: bool

    :returns: List of 'children' TransformNodes modified, will not 
              contain child nodes if the child is already parented under
              'parent'.
    :rtype: [TransformNode, ..]
    """
    children_nodes = [tn.get_node() for tn in children]
    dont_allow_empty = False
    allow_empty = True

    # Query keyframe times on each node attribute
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    frame_range = list(range(start_frame, end_frame+1))
    # total_start, total_end, frame_ranges_map, key_times_map = _get_keyframe_times_for_each_node_attr(
    #     children_nodes,
    #     TFM_ATTRS,
    #     start_frame,
    #     end_frame)


    # Query current transforms
    tfm_cache = tfm_utils.TransformMatrixCache()
    for tfm_node, node in zip(children, children_nodes):
        # frame_range = _get_times(node,
        #                          key_times_map, frame_ranges_map,
        #                          total_start, total_end,
        #                          sparse, dont_allow_empty)
        tfm_cache.add_node_attr(tfm_node, 'worldMatrix[0]', frame_range)
    tfm_cache.process()

    # Apply parenting logic for the children nodes.
    changed_list = [False] * len(children)
    if parent is not None:
        parent_node = parent.get_node()
        assert maya.cmds.objExists(parent_node)
        for i, tfm_node in enumerate(children):
            node = tfm_node.get_node()
            current_parent = tfm_node.get_parent()
            same =  __are_nodes_the_same(current_parent, parent)
            if same is True:
                continue
            maya.cmds.parent(node, parent_node)
            changed_list[i] = True
    else:
        for i, (tfm_node, node) in enumerate(zip(children, children_nodes)):
            current_parent = tfm_node.get_parent()
            same = __are_nodes_the_same(current_parent, None)
            if same is True:
                continue
            maya.cmds.parent(node, world=True)
            changed_list[i] = True

    # Set transforms again.
    changed_tfm_nodes = [tn for tn, c in zip(children, changed_list)
                         if c is True]
    for tfm_node in changed_tfm_nodes:
        # node = tfm_node.get_node()
        # frame_range = _get_times(node,
        #                          key_times_map, frame_ranges_map,
        #                          total_start, total_end,
        #                          sparse, dont_allow_empty)
        tfm_utils.set_transform_values(
            tfm_cache, frame_range,
            tfm_node, tfm_node,
            delete_static_anim_curves=delete_static_anim_curves,
        )
    return changed_tfm_nodes
