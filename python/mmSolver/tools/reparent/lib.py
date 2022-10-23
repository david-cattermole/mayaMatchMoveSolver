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

import mmSolver.utils.time as time_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.utils.node as node_utils
import mmSolver.tools.reparent.keytimeutils as keytime_utils

LOG = mmSolver.logger.get_logger()

TRANSLATE_ATTRS = ['translateX', 'translateY', 'translateZ']

ROTATE_ATTRS = ['rotateX', 'rotateY', 'rotateZ']

SCALE_ATTRS = ['scaleX', 'scaleY', 'scaleZ']

TFM_ATTRS = []
TFM_ATTRS += TRANSLATE_ATTRS
TFM_ATTRS += ROTATE_ATTRS
TFM_ATTRS += SCALE_ATTRS


def reparent(children, parent, sparse=True, delete_static_anim_curves=False):
    """
    Reparent the children under the given parent.

    :param children: List of child nodes to be modified.
    :type children: [TransformNode, ..]

    :param parent: The new parent node for children, or None means
                   un-parent.
    :type parent: TransformNode or None

    :param sparse: Keyframe animation on the children each frame
                   (dense) or sparse (only at keyframes).
    :type sparse: bool

    :param delete_static_anim_curves: Delete any animCurves that all
                                      have the same values.
    :type delete_static_anim_curves: bool

    :returns: List of 'children' TransformNodes modified, will not
              contain child nodes if the child is already parented under
              'parent'.
    :rtype: [TransformNode, ..]
    """
    assert len(children) > 0
    assert isinstance(children[0], tfm_utils.TransformNode)
    assert parent is None or isinstance(parent, tfm_utils.TransformNode)
    assert isinstance(sparse, bool)
    assert isinstance(delete_static_anim_curves, bool)
    children_nodes = [tn.get_node() for tn in children]

    parent_parent_nodes = []
    if parent is not None:
        parent_node = parent.get_node()
        parent_parent_nodes = [parent_node]
        parent_parent_nodes += node_utils.get_node_parents(parent_node) or []

    # Query keyframe times on each node attribute
    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    keytime_obj = keytime_utils.KeyframeTimes()
    for child_node in children_nodes:
        child_parent_nodes = list(parent_parent_nodes)
        child_parent_nodes += node_utils.get_node_parents(child_node) or []
        keytime_obj.add_node_attrs(
            child_node, TFM_ATTRS, start_frame, end_frame, parents=child_parent_nodes
        )
    fallback_frame_range = keytime_obj.sum_frame_range_for_nodes(children_nodes)
    fallback_times = list(range(fallback_frame_range[0], fallback_frame_range[1] + 1))

    # Query current transforms
    tfm_cache = tfm_utils.TransformMatrixCache()
    for tfm_node, node in zip(children, children_nodes):
        times = keytime_obj.get_times(node, sparse) or fallback_times
        tfm_cache.add_node_attr(tfm_node, 'worldMatrix[0]', times)
    tfm_cache.process()

    # Apply parenting logic for the children nodes.
    changed_list = [False] * len(children)
    if parent is not None:
        parent_node = parent.get_node()
        assert maya.cmds.objExists(parent_node)
        for i, tfm_node in enumerate(children):
            node = tfm_node.get_node()
            current_parent = tfm_node.get_parent()
            if current_parent == parent:
                continue
            maya.cmds.parent(node, parent_node, absolute=True)
            changed_list[i] = True
    else:
        for i, (tfm_node, node) in enumerate(zip(children, children_nodes)):
            current_parent = tfm_node.get_parent()
            if current_parent is None:
                continue
            maya.cmds.parent(node, world=True, absolute=True)
            changed_list[i] = True
    assert len(changed_list) == len(children)

    # Set transforms again.
    changed_tfm_nodes = [tn for tn, c in zip(children, changed_list) if c is True]
    for tfm_node in changed_tfm_nodes:
        node = tfm_node.get_node()
        times = keytime_obj.get_times(node, sparse) or []
        if len(times) > 0:
            tfm_utils.set_transform_values(
                tfm_cache,
                times,
                tfm_node,
                tfm_node,
                delete_static_anim_curves=delete_static_anim_curves,
            )
    return changed_tfm_nodes
