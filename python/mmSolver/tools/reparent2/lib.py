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


def _bake_nodes(nodes, frame_range, smart_bake=False):
    if smart_bake:
        maya.cmds.bakeResults(
            nodes,
            time=frame_range,
            smart=1,
            sparseAnimCurveBake=smart_bake,
            minimizeRotation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            controlPoints=False,
            shape=False)
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
            shape=False)
    return


def reparent(children_nodes, parent_node,
             frame_range_mode=None,
             start_frame=None,
             end_frame=None,
             bake_mode=None,
             rotate_order_mode=None,
             delete_static_anim_curves=None):
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
        frame_range_mode = FRAME_RANGE_MODE_TIMELINE_INNER_VALUE
    if bake_mode is None:
        bake_mode = BAKE_MODE_FULL_BAKE_VALUE
    if rotate_order_mode is None:
        rotate_order_mode = ROTATE_ORDER_MODE_USE_EXISTING_VALUE
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES
    assert bake_mode in const.BAKE_MODE_VALUES
    assert rotate_order_mode in const.ROTATE_ORDER_MODE_VALUES
    assert isinstance(delete_static_anim_curves, bool)

    # Get frame range
    if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
        assert start_frame is not None
        assert end_frame is not None
    else:
        assert False
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    frame_range = (start_frame, end_frame)
    frames = range(int(start_frame), int(end_frame)+1)

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

    # Sort nodes by depth, deeper nodes first, so we do do not remove
    # parents before children.
    children = [tn.get_node() for tn in children_nodes]
    children = node_utils.sort_nodes_by_depth(children, reverse=True)
    children_nodes = [tfm_utils.TransformNode(node=n) for n in children]

    loc_tfms = []
    for i, child in enumerate(children):
        tfm_name = 'dummy' + str(i + 1)
        shp_name = 'dummy' + str(i + 1) + 'Shape'
        loc_tfm = maya.cmds.createNode('transform', name=tfm_name)
        maya.cmds.createNode('locator', name=shp_name, parent=loc_tfm)

        # Constrain the locator to the child, in translate, rotate and
        # scale.
        maya.cmds.pointConstraint(child, loc_tfm)
        maya.cmds.orientConstraint(child, loc_tfm)
        maya.cmds.scaleConstraint(child, loc_tfm)

        loc_tfms.append(loc_tfm)

    # Bake the locator results
    _bake_nodes(loc_tfms, frame_range, smart_bake=True)
    maya.cmds.delete(loc_tfms, constraints=True)

    for child, child_node in zip(children, children_nodes):
        # Remove keyframes from child transform
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
            maya.cmds.pointConstraint(parent, child)
            maya.cmds.orientConstraint(parent, child)
            maya.cmds.scaleConstraint(parent, child)
            maya.cmds.delete(child, constraints=True)

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

        # Constrain the child to the locator,
        maya.cmds.pointConstraint(loc_tfm, child)
        maya.cmds.orientConstraint(loc_tfm, child)
        maya.cmds.scaleConstraint(loc_tfm, child)

    # Bake the children's results.
    children = [tn.get_node() for tn in children_nodes]
    _bake_nodes(children, frame_range, smart_bake=smart_bake)
    maya.cmds.delete(children, constraints=True)
    maya.cmds.filterCurve(children)
    if delete_static_anim_curves is True:
        maya.cmds.delete(children, staticChannels=True)

    # Clean up redundant nodes.
    maya.cmds.delete(loc_tfms)
    return
