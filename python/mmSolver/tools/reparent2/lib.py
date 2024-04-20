# Copyright (C) 2021 David Cattermole.
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

This script will re-parent objects, keeping the world space position
the same except moving the objects in to a different hierarchy. This
will work with animation data, not just a single frame, like the
native Maya command "parent".
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import maya.cmds

import mmSolver.logger

import mmSolver.utils.constant as const_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent2.constant as const


LOG = mmSolver.logger.get_logger()

# Used as placeholders for Constraint command arguments for 'skip'.
#
# If SKIP_ALL, then all attributes will be skipped from the
# constraint, and therefore the constraint should not be created. If
# SKIP_NONE, then no skipping occurs and all components of the
# constraint are created.
SKIP_ALL = 'all'
SKIP_NONE = 'none'


def _bake_nodes(nodes, frame_range, smart_bake=False):
    assert isinstance(smart_bake, bool)
    assert len(frame_range) == 2
    if smart_bake is True:
        maya.cmds.bakeResults(
            nodes,
            time=frame_range,
            smart=1,
            sparseAnimCurveBake=smart_bake,
            minimizeRotation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            controlPoints=False,
            shape=False,
        )
    else:
        maya.cmds.bakeResults(
            nodes,
            time=frame_range,
            sampleBy=1,
            sparseAnimCurveBake=False,
            minimizeRotation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            controlPoints=False,
            shape=False,
        )
    return


def _get_node_attr_skip(node, attr_base):
    axis_list = ['x', 'y', 'z']
    attr_list = []
    for axis in axis_list:
        attr = '{}{}'.format(attr_base, axis.upper())
        attr_list.append(attr)

    skip_list = []
    for axis, attr in zip(axis_list, attr_list):
        node_attr = node + '.' + attr
        settable = maya.cmds.getAttr(node_attr, settable=True)
        if settable is False:
            skip_list.append(axis)

    skip = None
    if len(skip_list) == 0:
        skip = SKIP_NONE
    elif len(skip_list) == 3:
        skip = SKIP_ALL
    else:
        skip = skip_list
    return skip


def nodes_attrs_settable(node_list, attr_list):
    """
    Returns a dict of the settable status for each attribute on each node.

    :rtype: ({str: str, ..}, int, int)
    """
    settable_map = {}
    settable_count = 0
    non_settable_count = 0
    for node in node_list:
        for attr in attr_list:
            node_attr = node + '.' + attr
            settable = maya.cmds.getAttr(node_attr, settable=True)
            settable_map[node_attr] = settable
            if settable:
                settable_count += 1
            else:
                non_settable_count += 1
    return settable_map, settable_count, non_settable_count


def _constrain_objects(
    target, node, translate_skip=None, rotate_skip=None, scale_skip=None
):
    if translate_skip is None:
        translate_skip = SKIP_NONE
    if rotate_skip is None:
        rotate_skip = SKIP_NONE
    if scale_skip is None:
        scale_skip = SKIP_NONE

    constraints = set()
    if translate_skip != SKIP_ALL:
        nodes = maya.cmds.pointConstraint(target, node, skip=translate_skip) or []
        constraints |= set(nodes)

    if rotate_skip != SKIP_ALL:
        nodes = maya.cmds.orientConstraint(target, node, skip=rotate_skip) or []
        constraints |= set(nodes)

    if scale_skip != SKIP_ALL:
        nodes = maya.cmds.scaleConstraint(target, node, skip=scale_skip) or []
        constraints |= set(nodes)

    return constraints


def reparent(
    children_nodes,
    parent_node,
    frame_range_mode=None,
    start_frame=None,
    end_frame=None,
    bake_mode=None,
    rotate_order_mode=None,
    delete_static_anim_curves=None,
):
    """
    Reparent the children under the given parent.

    :param children_nodes: List of child nodes to be modified.
    :type children_nodes: [TransformNode, ..]

    :param parent_node: The new parent node for children, or None means
        un-parent.
    :type parent_node: TransformNode or None

    :param frame_range_mode: What frame range to use for baking.
    :type frame_range_mode: FRAME_RANGE_MODE_VALUES

    :param start_frame: First frame of custom frame range.
    :type start_frame: int or None

    :param end_frame: Last frame of custom frame range.
    :type end_frame: int or None

    :param bake_mode: How to bake the object? Where to place keyframes.
    :type bake_mode: BAKE_MODE_VALUES

    :param rotate_order_mode:
    :type rotate_order_mode: ROTATE_ORDER_MODE_VALUES

    :param delete_static_anim_curves:
        Delete any animCurves that all have the same values.
    :type delete_static_anim_curves: bool

    :returns: List of 'children' TransformNodes modified, will not
              contain child nodes if the child is already parented
              under 'parent'.
    :rtype: [TransformNode, ..]
    """
    assert len(children_nodes) > 0
    assert isinstance(children_nodes[0], tfm_utils.TransformNode)
    assert parent_node is None or isinstance(parent_node, tfm_utils.TransformNode)
    if isinstance(parent_node, tfm_utils.TransformNode):
        assert maya.cmds.objExists(parent_node.get_node())
    if frame_range_mode is None:
        frame_range_mode = const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE
    if bake_mode is None:
        bake_mode = const.BAKE_MODE_FULL_BAKE_VALUE
    if rotate_order_mode is None:
        rotate_order_mode = const.ROTATE_ORDER_MODE_USE_EXISTING_VALUE
    assert start_frame is None or isinstance(start_frame, int)
    assert end_frame is None or isinstance(end_frame, int)
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES
    assert bake_mode in const.BAKE_MODE_VALUES
    assert rotate_order_mode in const.ROTATE_ORDER_MODE_VALUES
    assert isinstance(delete_static_anim_curves, bool)

    # Get frame range
    frame_range = time_utils.get_frame_range(
        frame_range_mode, start_frame=start_frame, end_frame=end_frame
    )

    # Get bake mode.
    sparse = None
    if bake_mode == const.BAKE_MODE_FULL_BAKE_VALUE:
        sparse = False
    elif bake_mode == const.BAKE_MODE_SMART_BAKE_VALUE:
        sparse = True
    else:
        assert False
    smart_bake = sparse is True

    # Get rotate order mode.
    rotate_order = None
    if rotate_order_mode == const.ROTATE_ORDER_MODE_USE_EXISTING_VALUE:
        rotate_order = None
    else:
        order_str = str(rotate_order_mode)
        rotate_order = const_utils.ROTATE_ORDER_STR_TO_INDEX[order_str]

    # Filter out invalid nodes.
    #
    # There is no need to un-parent to the world, if the node is
    # already parented to the world.
    msg = 'Skipping Re-Parent! Node is already parented to world: node=%r'
    if parent_node is None:
        tmp_children_nodes = children_nodes
        children_nodes = []
        for child_node in tmp_children_nodes:
            node = child_node.get_node()
            current_parent = maya.cmds.listRelatives(node, parent=True)
            if not current_parent:
                LOG.warn(msg, node)
            else:
                children_nodes.append(child_node)
    if len(children_nodes) == 0:
        return

    # Sort nodes by depth, deeper nodes first, so we do do not remove
    # parents before children.
    children = [tn.get_node() for tn in children_nodes]
    children = node_utils.sort_nodes_by_depth(children, reverse=True)
    children_nodes = [tfm_utils.TransformNode(node=n) for n in children]

    loc_tfms = []
    constraints = set()
    for i, child in enumerate(children):
        tfm_name = 'dummy' + str(i + 1)
        shp_name = 'dummy' + str(i + 1) + 'Shape'
        loc_tfm = maya.cmds.createNode('transform', name=tfm_name)
        maya.cmds.createNode('locator', name=shp_name, parent=loc_tfm)

        # Constrain the locator to the child, in translate, rotate and
        # scale.
        constraints |= _constrain_objects(child, loc_tfm)

        loc_tfms.append(loc_tfm)

    # Bake the locator results
    _bake_nodes(loc_tfms, frame_range, smart_bake=smart_bake)
    if len(constraints) > 0:
        maya.cmds.delete(constraints)

    constraints = set()
    for child, child_node, loc_tfm in zip(children, children_nodes, loc_tfms):
        # Find which attributes are partially locked, so we can avoid
        # modifying the attributes.
        translate_skip = _get_node_attr_skip(child, 'translate')
        rotate_skip = _get_node_attr_skip(child, 'rotate')
        scale_skip = _get_node_attr_skip(child, 'scale')

        # Warn if the child transform is completely locked.
        if (
            translate_skip == SKIP_ALL
            and rotate_skip == SKIP_ALL
            and scale_skip == SKIP_ALL
        ):
            msg = 'Skipping Re-Parent! Cannot modify any attributes: node=%r'
            LOG.warn(msg, child)
            continue

        # Warn the user if some values cannot be modified.
        msg_base = 'Cannot modify attributes: node=%r attrs={} skip=%r'
        if translate_skip != 'none':
            msg = msg_base.format('translate')
            LOG.warn(msg, child, translate_skip)
        if rotate_skip != 'none':
            msg = msg_base.format('rotate')
            LOG.warn(msg, child, rotate_skip)
        if scale_skip != 'none':
            msg = msg_base.format('scale')
            LOG.warn(msg, child, scale_skip)

        # Remove keyframes from child transform.
        maya.cmds.cutKey(child, time=frame_range, attribute='translateX')
        maya.cmds.cutKey(child, time=frame_range, attribute='translateY')
        maya.cmds.cutKey(child, time=frame_range, attribute='translateZ')
        maya.cmds.cutKey(child, time=frame_range, attribute='rotateX')
        maya.cmds.cutKey(child, time=frame_range, attribute='rotateY')
        maya.cmds.cutKey(child, time=frame_range, attribute='rotateZ')
        maya.cmds.cutKey(child, time=frame_range, attribute='scaleX')
        maya.cmds.cutKey(child, time=frame_range, attribute='scaleY')
        maya.cmds.cutKey(child, time=frame_range, attribute='scaleZ')
        maya.cmds.cutKey(child, time=frame_range, attribute='rotateOrder')

        # If the parent is empty, parent to the world...
        if parent_node is None:
            maya.cmds.parent(child, world=True)
        else:
            # Else, constrain the child to the parent,
            # delete the history, and parent the child under
            # the parent.
            parent = parent_node.get_node()
            temp_constraints = _constrain_objects(
                parent,
                child,
                translate_skip=translate_skip,
                rotate_skip=rotate_skip,
                scale_skip=scale_skip,
            )
            if len(temp_constraints) > 0:
                maya.cmds.delete(temp_constraints)

            maya.cmds.parent(child, parent)
        child = child_node.get_node()

        # Change Rotate order.
        if rotate_order is not None:
            node_attr = child + '.rotateOrder'
            settable = maya.cmds.getAttr(node_attr, settable=True)
            if settable:
                maya.cmds.setAttr(node_attr, rotate_order)
            else:
                LOG.warn('Cannot change rotate order: %r', child)

        # Constrain the child to match the locator.
        constraints |= _constrain_objects(
            loc_tfm,
            child,
            translate_skip=translate_skip,
            rotate_skip=rotate_skip,
            scale_skip=scale_skip,
        )

    # Bake the children's results.
    children = [tn.get_node() for tn in children_nodes]
    _bake_nodes(children, frame_range, smart_bake=smart_bake)
    if len(constraints) > 0:
        maya.cmds.delete(constraints)
    maya.cmds.filterCurve(children)
    if delete_static_anim_curves is True:
        maya.cmds.delete(children, staticChannels=True)

    # Clean up redundant nodes.
    maya.cmds.delete(loc_tfms)
    return
