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


TFM_ATTRS = [
    'translateX', 'translateY', 'translateZ',
    'rotateX', 'rotateY', 'rotateZ',
    'scaleX', 'scaleY', 'scaleZ',
]


def create(nodes, maintain_hierarchy=True, sparse=True):
    # Get selected nodes.
    nodes = maya.cmds.ls(selection=True, long=True) or []
    tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]

    # Ensure node attributes are unlocked
    keyable_attrs = set()
    for node in nodes:
        for attr in TFM_ATTRS:
            plug = node + '.' + attr
            keyable = maya.cmds.getAttr(plug, keyable=True)
            if keyable is True:
                keyable_attrs.add(plug)

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
        if maintain_hierarchy is True:
            # TODO: Allow maintaining relative hierarchy of nodes.
            pass
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
            times = list(key_times.get(node))
        tfm_utils.set_transform_values(cache, times, tfm_node, ctrl)

    # Delete all keyframes for non-keyed times (sparse)
    if sparse is True:
        # TODO: Use a sparse-to-dense Maya animCurve solver.
        pass

    # Delete all keyframes on controlled nodes
    anim_curves = anim_utils.get_anim_curves_from_nodes(nodes)
    anim_curves = [n for n in anim_curves
                   if node_utils.node_is_referenced(n) is False]
    maya.cmds.delete(anim_curves)

    # Create constraint(s) to previous nodes.
    # - Create point, orient and scale constraints.
    for tfm_node, ctrl in zip(tfm_nodes, ctrl_tfm_nodes):
        src_node = tfm_node.get_node()
        dst_node = ctrl.get_node()
        # TODO: ensure we actually can connect to the respective
        # translate, rotate and scale attributes.
        maya.cmds.pointConstraint(src_node, dst_node)
        maya.cmds.orientConstraint(src_node, dst_node)
        maya.cmds.scaleConstraint(src_node, dst_node)
    return ctrl_list


def remove(nodes):
    # Get selected nodes

    # detect if these are 'controllers'

    # find controlled nodes from controller nodes

    # query transform matrix on controlled nodes.

    # query keyframe times on controller nodes.

    # delete constraints on controlled nodes.

    # set keyframes (per-frame) on controlled nodes

    # Delete keyframes for non-keyed times (sparse)

    # delete controller nodes
    pass
