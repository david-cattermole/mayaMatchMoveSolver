# Copyright (C) 2021, 2022 Patcha Saheb Binginapalli.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.channelboxutils as channelbox_utils
import mmSolver.tools.attributebake.lib as fastbake_lib
import mmSolver.tools.createcontroller2.constant as const

LOG = mmSolver.logger.get_logger()

IDENTIFIER_ATTR_NAME = 'mmsolver_cc_identifier'
WORLD_SPACE_RIG_ZERO_SUFFIX = '_worldSpaceZero'
OBJECT_SPACE_RIG_ZERO_SUFFIX = '_objectSpaceZero'
SCREEN_SPACE_RIG_SUFFIX = '_screenSpace'
SCREEN_SPACE_RIG_ZERO_SUFFIX = '_screenSpaceZero'
MAIN_DRIVER_SUFFIX_NAME = '_mainDriver'
TRANSFORM_ATTRS = [
    'translateX',
    'translateY',
    'translateZ',
    'rotateX',
    'rotateY',
    'rotateZ',
    'scaleX',
    'scaleY',
    'scaleZ',
]


def _is_rig_node(node):
    """Check if the node is a rig node."""
    if node_utils.attribute_exists(IDENTIFIER_ATTR_NAME, node):
        return True
    return False


def _get_rig_node_identifier(node):
    """Get custom attribute value to identify rig node."""
    if _is_rig_node(node):
        plug = node + '.' + IDENTIFIER_ATTR_NAME
        attr_value = maya.cmds.getAttr(plug)
        return attr_value
    return None


def _get_selected_channel_box_attrs():
    channel_box = channelbox_utils.get_ui_name()
    attrs = (
        maya.cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
    )
    return attrs


def _skip_translate_attributes(node):
    attr_list = ['x', 'y', 'z']

    plug = node + '.translateX'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('x')

    plug = node + '.translateY'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('y')

    plug = node + '.translateZ'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('z')
    return attr_list


def _skip_rotate_attributes(node):
    attr_list = ['x', 'y', 'z']

    plug = node + '.rotateX'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('x')

    plug = node + '.rotateY'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('y')

    plug = node + '.rotateZ'
    if maya.cmds.getAttr(plug, keyable=True) and maya.cmds.getAttr(plug, settable=True):
        attr_list.remove('z')
    return attr_list


def _set_keyframes_at_source_node_key_times(src_node, dst_node, start_frame, end_frame):
    """
    Set keyframes on dst_node at times based on src_node.

    Start frame and end frame are always copied.
    """
    all_keys = (
        maya.cmds.keyframe(src_node, query=True, time=(start_frame, end_frame)) or []
    )
    keys = {start_frame, end_frame} | set(all_keys)
    for frame in sorted(keys):
        maya.cmds.currentTime(frame, edit=True)
        maya.cmds.setKeyframe(dst_node)
    return


def _set_lod_visibility(node, visibility=False):
    """Sets shape node LOD visibility on/off."""
    assert isinstance(visibility, bool)
    shape = maya.cmds.listRelatives(node, shapes=True) or []
    if len(shape) > 0:
        node_attr = shape[0] + '.lodVisibility'
        settable = maya.cmds.getAttr(node_attr, settable=True)
        if settable is True:
            maya.cmds.setAttr(node_attr, visibility)
    return


def _world_bake(
    pivot, main, loc_grp, start, end, smart_bake=False, dynamic_pivot=False
):
    assert isinstance(smart_bake, bool)
    assert isinstance(dynamic_pivot, bool)

    attrs = []
    if 'vtx' in pivot:
        current_time = maya.cmds.currentTime(query=True)
        for frame in range(start, end + 1):
            maya.cmds.currentTime(frame, edit=True)
            point_pos = maya.cmds.pointPosition(pivot, world=True)
            maya.cmds.xform(loc_grp, worldSpace=True, translation=point_pos)
            maya.cmds.setKeyframe(loc_grp)
        maya.cmds.currentTime(current_time, edit=True)
    else:
        # point constraint, parent is pivot and child is loc_grp
        if dynamic_pivot is True:
            con = maya.cmds.pointConstraint(pivot, loc_grp, maintainOffset=False)
        else:
            point_con = maya.cmds.pointConstraint(pivot, loc_grp, maintainOffset=False)
            orient_con = maya.cmds.orientConstraint(main, loc_grp, maintainOffset=False)
            maya.cmds.delete(point_con, orient_con)
            con = maya.cmds.parentConstraint(main, loc_grp, maintainOffset=True)
        fastbake_lib.bake_attributes(loc_grp, attrs, start, end, smart_bake=smart_bake)
        maya.cmds.delete(con)

    # orient constraint, parent is main and child is loc_grp
    orient_con = maya.cmds.orientConstraint(main, loc_grp, maintainOffset=False)

    fastbake_lib.bake_attributes(loc_grp, attrs, start, end, smart_bake)
    maya.cmds.delete(orient_con)
    return loc_grp


def _create_main_driver(parent, main):
    start, end = time_utils.get_maya_timeline_range_inner()
    main_driver_loc = maya.cmds.duplicate(parent)
    maya.cmds.setAttr(main_driver_loc[0] + '.visibility', 0)
    maya.cmds.parent(main_driver_loc, parent)
    parent_con = maya.cmds.parentConstraint(main, main_driver_loc)

    # bake attributes
    attrs = []
    fastbake_lib.bake_attributes(main_driver_loc, attrs, start, end, smart_bake=False)
    maya.cmds.delete(parent_con)

    maya.cmds.setAttr(main_driver_loc[0] + '.hiddenInOutliner', 1)
    return main_driver_loc


def _find_constraints_from_node(node):
    constraints = (
        maya.cmds.listConnections(
            node + '.parentMatrix[0]', destination=True, source=False, type='constraint'
        )
        or []
    )
    constraints = [n for n in constraints if node_utils.node_is_referenced(n) is False]
    constraints = list(set(constraints))
    return constraints


def _remove_constraint_blend_attr_from_nodes(nodes):
    for node in nodes:
        attr_list = maya.cmds.listAttr(node)
        for attr in attr_list:
            if 'blendPoint' in attr or 'blendOrient' in attr or 'blendParent' in attr:
                node_attr = '{}.{}'.format(node, attr)
                maya.cmds.deleteAttr(node_attr)
    return


def _create_controller_world_space(
    name,
    pivot_node,
    main_node,
    loc_grp_node,
    start_frame,
    end_frame,
    smart_bake,
    current_frame,
    dynamic_pivot=False,
):
    assert isinstance(dynamic_pivot, bool)
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    loc_grp_node = _world_bake(
        pivot_node,
        main_node,
        loc_grp_node,
        start_frame,
        end_frame,
        smart_bake=smart_bake,
        dynamic_pivot=dynamic_pivot,
    )

    main_driver_loc = _create_main_driver(loc_grp_node, main_node)

    maya.cmds.parentConstraint(
        main_driver_loc,
        main_node,
        maintainOffset=True,
        skipTranslate=skip_translate_attr,
        skipRotate=skip_rotate_attr,
    )

    if current_frame is True:
        maya.cmds.cutKey(loc_grp_node, time=(end_frame, end_frame))
        inner_start_frame, inner_end_frame = time_utils.get_maya_timeline_range_inner()
        maya.cmds.cutKey(main_driver_loc, time=(inner_start_frame, inner_end_frame))
        maya.cmds.setKeyframe(main_driver_loc)

    # LOD visibility
    _set_lod_visibility(loc_grp_node, True)
    _set_lod_visibility(main_driver_loc, False)

    maya.cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
    return loc_grp_node


def _create_controller_object_space(
    name,
    pivot_node,
    main_node,
    loc_grp_node,
    start_frame,
    end_frame,
    smart_bake,
    current_frame,
    dynamic_pivot=False,
):
    assert isinstance(smart_bake, bool)
    assert isinstance(dynamic_pivot, bool)
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    # World bake
    loc_grp_node = _world_bake(
        pivot_node,
        main_node,
        loc_grp_node,
        start_frame,
        end_frame,
        smart_bake=False,
        dynamic_pivot=dynamic_pivot,
    )
    zero_loc = maya.cmds.duplicate(loc_grp_node)
    maya.cmds.parent(zero_loc, loc_grp_node)
    maya.cmds.xform(
        zero_loc,
        translation=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        objectSpace=True,
    )

    main_driver_loc = _create_main_driver(zero_loc, main_node)

    # Smart bake
    if smart_bake is True:
        _set_keyframes_at_source_node_key_times(
            main_node, zero_loc, start_frame, end_frame
        )

    # Current frame
    if current_frame is True:
        maya.cmds.setKeyframe(zero_loc, time=(start_frame, start_frame))
        maya.cmds.cutKey(loc_grp_node, zero_loc, time=(end_frame, end_frame))
        inner_start_frame, inner_end_frame = time_utils.get_maya_timeline_range_inner()
        maya.cmds.cutKey(main_driver_loc, time=(inner_start_frame, inner_end_frame))
        maya.cmds.setKeyframe(main_driver_loc)
    maya.cmds.parentConstraint(
        main_driver_loc,
        main_node,
        maintainOffset=True,
        skipTranslate=skip_translate_attr,
        skipRotate=skip_rotate_attr,
    )

    # LOD visibility
    _set_lod_visibility(loc_grp_node, False)
    _set_lod_visibility(zero_loc, True)
    _set_lod_visibility(main_driver_loc, False)

    # Rename
    maya.cmds.rename(zero_loc, str(name) + OBJECT_SPACE_RIG_ZERO_SUFFIX)
    maya.cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
    return loc_grp_node


def _create_controller_screen_space(
    name,
    pivot_node,
    main_node,
    loc_grp_node,
    start_frame,
    end_frame,
    smart_bake,
    current_frame,
    camera,
    dynamic_pivot=False,
):
    skip_translate_attr = _skip_translate_attributes(main_node)
    if len(skip_translate_attr) != 0:
        LOG.error(
            ('Main object all translation attributes(tx,ty,tz)' ' are not available.')
        )
        # TODO: Should the locator be deleted?
        maya.cmds.delete(loc_grp_node)
        return

    # World bake
    loc_grp_node = _world_bake(
        pivot_node,
        main_node,
        loc_grp_node,
        start_frame,
        end_frame,
        smart_bake=False,
        dynamic_pivot=dynamic_pivot,
    )
    screen_loc = maya.cmds.duplicate(loc_grp_node)
    maya.cmds.parent(screen_loc, loc_grp_node)
    maya.cmds.xform(
        screen_loc,
        translation=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        objectSpace=True,
    )

    # Bake attributes
    attrs = []
    fastbake_lib.bake_attributes(
        screen_loc, attrs, start_frame, end_frame, smart_bake=False
    )
    aim_con = maya.cmds.aimConstraint(camera, screen_loc, aimVector=(0.0, 0.0, 1.0))

    # Bake attributes
    fastbake_lib.bake_attributes(
        screen_loc, attrs, start_frame, end_frame, smart_bake=False
    )
    maya.cmds.delete(aim_con)
    zero_loc = maya.cmds.duplicate(screen_loc)
    maya.cmds.parent(zero_loc, screen_loc)
    maya.cmds.xform(
        zero_loc,
        translation=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        objectSpace=True,
    )

    main_driver_loc = _create_main_driver(zero_loc, main_node)

    # Smart bake
    if smart_bake is True:
        _set_keyframes_at_source_node_key_times(
            main_node, zero_loc, start_frame, end_frame
        )

    # Current frame
    if current_frame is True:
        maya.cmds.setKeyframe(screen_loc, zero_loc, time=(start_frame, start_frame))
        maya.cmds.cutKey(
            loc_grp_node, screen_loc, zero_loc, time=(end_frame, end_frame)
        )
        inner_start_frame, inner_end_frame = time_utils.get_maya_timeline_range_inner()
        maya.cmds.cutKey(main_driver_loc, time=(inner_start_frame, inner_end_frame))
        maya.cmds.setKeyframe(main_driver_loc)

    maya.cmds.pointConstraint(main_driver_loc, main_node, maintainOffset=True)

    # LOD visibility
    _set_lod_visibility(loc_grp_node, False)
    _set_lod_visibility(screen_loc, False)
    _set_lod_visibility(zero_loc, True)
    _set_lod_visibility(main_driver_loc, False)

    # Rename
    maya.cmds.rename(screen_loc, name + SCREEN_SPACE_RIG_SUFFIX)
    maya.cmds.rename(zero_loc, name + SCREEN_SPACE_RIG_ZERO_SUFFIX)
    maya.cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
    return loc_grp_node


def create_controller(
    name,
    pivot_node,
    main_node,
    loc_grp_node,
    start_frame,
    end_frame,
    controller_type,
    smart_bake=False,
    camera=None,
    dynamic_pivot=False,
):
    """
    Create Controller of a node.

    :param name: The name of the rig.
    :type name: str

    :param pivot_node:
        The controller uses the pivot node's transform as the parent
        of the controller.
    :type pivot_node: str

    :param main_node: The node to be controlled
    :type main_node: str

    :param loc_grp_node: The nodes for the Locator or Group node that
        will be used to create rig. If a Locator is used, a list of
        both transform and shape nodes should be provided. If a Group
        is provided, just use a list with the transform node.
    :type loc_grp_node: [str]

    :param start_frame: bake range start frame
    :type start_frame: int

    :param end_frame: bake range end frame
    :type end_frame: int

    :param controller_type: In which space rig to be created? A value in
        mmSolver.tools.createcontroller2.constant.CONTROLLER_TYPE_LIST.
    :type: str

    :param smart_bake: Enable or disable baking only "smart" keyframe times.
    :type: bool

    :param camera: Camera transform node for screen space rig
    :type: str or None

    :param dynamic_pivot: When True, the pivot_node is considered animated.
    :type: bool

    :returns: The controller node locator/group created. This should
        be the same as 'loc_grp_node' given to the function.
    :rtype: [str, ..]
    """
    current_frame = False
    if start_frame == end_frame:
        current_frame = True
        end_frame = start_frame + 1

    # Handle group node
    if not maya.cmds.listRelatives(loc_grp_node, shapes=True):
        loc_grp_node = [loc_grp_node]

    # Add custom identify attribute
    maya.cmds.addAttr(
        loc_grp_node[0], longName=IDENTIFIER_ATTR_NAME, dataType='string', keyable=False
    )
    maya.cmds.setAttr(
        str(loc_grp_node[0]) + '.' + IDENTIFIER_ATTR_NAME,
        str(loc_grp_node[0] + str(random.randint(1, 100000000))),
        type='string',
        lock=True,
    )

    if controller_type == const.CONTROLLER_TYPE_WORLD_SPACE:
        loc_grp_node = _create_controller_world_space(
            name,
            pivot_node,
            main_node,
            loc_grp_node,
            start_frame,
            end_frame,
            smart_bake,
            current_frame,
            dynamic_pivot=dynamic_pivot,
        )

    elif controller_type == const.CONTROLLER_TYPE_OBJECT_SPACE:
        loc_grp_node = _create_controller_object_space(
            name,
            pivot_node,
            main_node,
            loc_grp_node,
            start_frame,
            end_frame,
            smart_bake,
            current_frame,
            dynamic_pivot=dynamic_pivot,
        )

    elif controller_type == const.CONTROLLER_TYPE_SCREEN_SPACE:
        loc_grp_node = _create_controller_screen_space(
            name,
            pivot_node,
            main_node,
            loc_grp_node,
            start_frame,
            end_frame,
            smart_bake,
            current_frame,
            camera,
            dynamic_pivot=dynamic_pivot,
        )

    else:
        LOG.error('Invalid space.')

    return loc_grp_node


def remove_controller(controller_node, frame_start, frame_end, attrs=None):
    """
    Bake the affects of the controller node, and delete the controller.

    :param controller_node: The controller node.
    :type controller_node: str

    :param frame_start: First frame to bake.
    :type frame_start: int

    :param frame_end: Last frame to bake.
    :type frame_end: int

    :param attrs: List of attributes to bake. If None, all transform,
        rotate and scale attributes are baked.
    :type attrs: [str, ..] or None

    :returns: The list of transform nodes that were controlled by the
        given controller.
    :rtype: [str, ..]
    """
    assert isinstance(controller_node, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(controller_node)
    assert isinstance(frame_start, int)
    assert isinstance(frame_end, int)
    if attrs is None:
        attrs = TRANSFORM_ATTRS
    assert isinstance(attrs, list)
    if len(attrs) == 0:
        attrs = TRANSFORM_ATTRS

    # Find controller nodes.
    controller_nodes = []
    is_controller_rig = _is_rig_node(controller_node)
    if is_controller_rig is False:
        controller_nodes = [controller_node]
    else:
        children = (
            maya.cmds.ls(controller_node, dag=True, long=True, type='transform') or []
        )
        controller_nodes = [n for n in children if _is_rig_node(n)]

        # Sort nodes by depth, deeper nodes first, so we do do not
        # remove parents before children.
        controller_nodes = node_utils.sort_nodes_by_depth(
            controller_nodes, reverse=True
        )

    # Find constraints.
    constraints = []
    for node in controller_nodes:
        constraints += _find_constraints_from_node(node)
    if len(constraints) == 0:
        LOG.warn('Selected controller is not driving any object(s).')
        return []

    # Get Driven nodes.
    driven_nodes = []
    for constraint in constraints:
        attr = constraint + '.constraintParentInverseMatrix'
        driven_nodes += (
            maya.cmds.listConnections(attr, destination=False, source=True) or []
        )
    if len(driven_nodes) == 0:
        LOG.warn('Selected controller is not driving any object(s).')
        return []

    # Find nodes to be deleted.
    nodes_to_delete = []
    for node in controller_nodes:
        controller_id = _get_rig_node_identifier(node)
        parent_nodes = node_utils.get_node_parents(node)
        parent_node_ids = [_get_rig_node_identifier(n) for n in parent_nodes]
        nodes_to_delete += [
            n for n, id_ in zip(parent_nodes, parent_node_ids) if id_ == controller_id
        ]
    has_extra_parents = len(nodes_to_delete) == 0

    # Bake driven attributes.
    if is_controller_rig is True and has_extra_parents is False:
        for driven_node in driven_nodes:
            # If the original top-level controller node was "smart
            # baked", then set keys on all the same frames, therefore
            # re-creating the original keyframe times.
            _set_keyframes_at_source_node_key_times(
                controller_node, driven_node, frame_start, frame_end
            )
    else:
        fastbake_lib.bake_attributes(
            driven_nodes, attrs, frame_start, frame_end, smart_bake=True
        )

    # Delete nodes and clean up.
    if len(constraints) > 0:
        maya.cmds.delete(constraints)
    _remove_constraint_blend_attr_from_nodes(driven_nodes)
    nodes_to_delete = [n for n in nodes_to_delete if maya.cmds.objExists(n)]
    if len(nodes_to_delete) > 0:
        maya.cmds.delete(nodes_to_delete)

    return driven_nodes
