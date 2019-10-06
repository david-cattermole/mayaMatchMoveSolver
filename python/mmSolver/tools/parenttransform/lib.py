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
Mimic the parent and unparent tool in Maya.

.. todo:: Unlike the native Maya parent/unparent tools, this tool will
   maintain the world-space position for all keyframes across time.
"""

import collections

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.transform as tfm_utils

import mmSolver.api as mmapi

import mmSolver.tools.parenttransform.constant as const

LOG = mmSolver.logger.get_logger()


def parent(src_nodes, dst_node,
           current_frame=None,
           eval_mode=None):
    """
    Parent nodes under a new parent node.

    :param src_nodes: List of nodes to reparent.
    :type src_nodes: [str, ..]

    :param dst_node: The new parent node for the given source nodes.
    :type dst_node: str

    :param current_frame: What frame number is considered to be
                          'current' when evaluating transforms without
                          any keyframes.
    :type current_frame: float or int

    :param eval_mode: What type of transform evaluation method to use?
    :type eval_mode: mmSolver.utils.constant.EVAL_MODE_*

    """
    assert len(src_nodes) > 0
    assert len(dst_node) > 0
    if current_frame is None:
        current_frame = maya.cmds.currentTime(query=True)
    assert current_frame is not None
    
    src_tfm_nodes = [tfm_utils.TransformNode(node=n)
                     for n in src_nodes]
    tfm_dst_node = tfm_utils.TransformNode(node=dst_node)

    # Query keyframe times on each node attribute
    key_times_map = time_utils.get_keyframe_times_for_node_attrs(
        src_nodes,
        const.TFM_ATTRS
    )

    # Create Transform Cache, add and process cache.
    times = []
    cache = tfm_utils.TransformMatrixCache()
    for src_tfm_node in src_tfm_nodes:
        src_node = src_tfm_node.get_node()
        times = key_times_map.get(src_node, [current_frame])
        cache.add_node(src_tfm_node, times)
    cache.process(eval_mode=eval_mode)

    # Re-parent the nodes.
    dst_node = tfm_dst_node.get_node()
    src_nodes = [tfm_node.get_node()
                 for tfm_node in src_tfm_nodes]
    maya.cmds.parent(src_nodes, dst_node, relative=True)

    # Set transforms for all source nodes.
    # anim_curves = []
    for src_tfm_node in src_tfm_nodes:
        src_node = src_tfm_node.get_node()
        src_times = key_times_map.get(src_node, [current_frame])
        assert len(src_times) > 0
        tfm_utils.set_transform_values(
            cache,
            src_times,
            src_tfm_node,
            src_tfm_node,
            delete_static_anim_curves=False
        )

    src_nodes = [tfm_node.get_node()
                 for tfm_node in src_tfm_nodes]
    return src_nodes


def unparent(src_nodes,
             current_frame=None,
             eval_mode=None):
    """
    Un-parent nodes into world space.

    :param src_nodes: List of nodes to unparent.
    :type src_nodes: [str, ..]

    :param current_frame: What frame number is considered to be
                          'current' when evaluating transforms without
                          any keyframes.
    :type current_frame: float or int

    :param eval_mode: What type of transform evaluation method to use?
    :type eval_mode: mmSolver.utils.constant.EVAL_MODE_*

    """
    if current_frame is None:
        current_frame = maya.cmds.currentTime(query=True)
    assert current_frame is not None

    assert len(src_nodes) > 0
    src_tfm_nodes = [tfm_utils.TransformNode(node=n)
                     for n in src_nodes]

    # Query keyframe times on each node attribute
    key_times_map = time_utils.get_keyframe_times_for_node_attrs(
        src_nodes,
        const.TFM_ATTRS
    )

    # Create Transform Cache, add and process cache.
    times = []
    cache = tfm_utils.TransformMatrixCache()
    for src_tfm_node in src_tfm_nodes:
        src_node = src_tfm_node.get_node()
        times = key_times_map.get(src_node, [current_frame])
        cache.add_node(src_tfm_node, times)
    cache.process(eval_mode=eval_mode)

    # Perform the re-parent operation
    src_nodes = [tfm_node.get_node()
                 for tfm_node in src_tfm_nodes]
    maya.cmds.parent(src_nodes, world=True, relative=True)

    # Set transforms for all source nodes.
    for src_tfm_node in src_tfm_nodes:
        src_node = src_tfm_node.get_node()
        src_times = key_times_map.get(src_node, [current_frame])
        assert len(src_times) > 0
        tfm_utils.set_transform_values(
            cache,
            src_times,
            src_tfm_node,
            src_tfm_node,
            delete_static_anim_curves=False
        )

    src_nodes = [tfm_node.get_node()
                 for tfm_node in src_tfm_nodes]
    return src_nodes
