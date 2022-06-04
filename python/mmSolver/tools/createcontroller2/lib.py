# Copyright (C) 2021 Patcha Saheb Binginapalli.
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

import random

import maya.cmds as cmds
import maya.mel as mel

import mmSolver.logger
import mmSolver.tools.attributebake.lib as fastbake_lib
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()

IDENTIFIER_ATTR_NAME = "mmsolver_cc_identifier"
WORLD_SPACE_RIG_ZERO_SUFFIX = "_worldSpaceZero"
OBJECT_SPACE_RIG_ZERO_SUFFIX = "_objectSpaceZero"
SCREEN_SPACE_RIG_SUFFIX = "_screenSpace"
SCREEN_SPACE_RIG_ZERO_SUFFIX = "_screenSpaceZero"
MAIN_DRIVER_SUFFIX_NAME = "_mainDriver"
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
        attr_value = cmds.getAttr(plug)
        return attr_value
    return None


def _get_selected_channel_box_attrs():
    cmd = 'global string $gChannelBoxName; $temp=$gChannelBoxName;'
    channel_box = mel.eval(cmd)
    attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
    return attrs


def _skip_translate_attributes(node):
    attr_list = ["x", "y", "z"]

    plug = node + ".translateX"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("x")

    plug = node + ".translateY"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("y")

    plug = node + ".translateZ"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("z")
    return attr_list


def _skip_rotate_attributes(node):
    attr_list = ["x", "y", "z"]

    plug = node + ".rotateX"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("x")

    plug = node + ".rotateY"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("y")

    plug = node + ".rotateZ"
    if cmds.getAttr(plug, keyable=True) and cmds.getAttr(plug, settable=True):
        attr_list.remove("z")
    return attr_list


def _set_keyframes_at_source_node_key_times(src_node, dst_node, start_frame, end_frame):
    """
    Set keyframes on dst_node at times based on src_node.

    Start frame and end frame are always copied.
    """
    all_keys = cmds.keyframe(src_node, query=True, time=(start_frame, end_frame)) or []
    keys = {start_frame, end_frame} | set(all_keys)
    for frame in sorted(keys):
        cmds.currentTime(frame, edit=True)
        cmds.setKeyframe(dst_node)
    return


def _set_lod_visibility(node, visibility=False):
    """Sets shape node LOD visibility on/off."""
    shape = cmds.listRelatives(node, shapes=True)
    if shape:
        cmds.setAttr(shape[0] + ".lodVisibility", visibility)
    return


def _world_bake(pivot, main, loc_grp, start, end, smart_bake=False):
    attrs = []
    if "vtx" in pivot:
        current_time = cmds.currentTime(query=True)
        for frame in range(start, end + 1):
            cmds.currentTime(frame, edit=True)
            point_pos = cmds.pointPosition(pivot, world=True)
            cmds.xform(loc_grp, worldSpace=True, translation=point_pos)
            cmds.setKeyframe(loc_grp)
        cmds.currentTime(current_time, edit=True)
    else:
        # point constraint, parent is pivot and child is loc_grp
        point_con = cmds.pointConstraint(pivot, loc_grp, maintainOffset=False)
        fastbake_lib.bake_attributes(loc_grp, attrs, start, end, smart_bake=smart_bake)
        cmds.delete(point_con)

    # orient constraint, parent is main and child is loc_grp
    orient_con = cmds.orientConstraint(main, loc_grp, maintainOffset=False)

    fastbake_lib.bake_attributes(loc_grp, attrs, start, end, smart_bake)
    cmds.delete(orient_con)
    return loc_grp


def _create_main_driver(parent, main):
    start, end = time_utils.get_maya_timeline_range_inner()
    main_driver_loc = cmds.duplicate(parent)
    cmds.setAttr(main_driver_loc[0] + ".visibility", 0)
    cmds.parent(main_driver_loc, parent)
    parent_con = cmds.parentConstraint(main, main_driver_loc)
    # bake attributes
    attrs = []
    fastbake_lib.bake_attributes(main_driver_loc, attrs, start, end, smart_bake=False)
    cmds.delete(parent_con)
    # hide in outliner
    cmds.setAttr(main_driver_loc[0] + ".hiddenInOutliner", 1)
    return main_driver_loc


def _find_constraints_from_node(node):
    constraints = (
        cmds.listConnections(
            node + ".parentMatrix[0]", destination=True, source=False, type="constraint"
        )
        or []
    )
    constraints = [n for n in constraints if node_utils.node_is_referenced(n) is False]
    constraints = list(set(constraints))
    return constraints


def _remove_constraint_blend_attr_from_nodes(nodes):
    for node in nodes:
        attr_list = cmds.listAttr(node)
        for attr in attr_list:
            if "blendPoint" in attr or "blendOrient" in attr or "blendParent" in attr:
                cmds.deleteAttr(str(node) + "." + str(attr))
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
):
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    loc_grp_node = _world_bake(
        pivot_node,
        main_node,
        loc_grp_node,
        start_frame,
        end_frame,
        smart_bake=smart_bake,
    )

    main_driver_loc = _create_main_driver(loc_grp_node, main_node)

    cmds.parentConstraint(
        main_driver_loc,
        main_node,
        maintainOffset=True,
        skipTranslate=skip_translate_attr,
        skipRotate=skip_rotate_attr,
    )

    if current_frame is True:
        cmds.cutKey(loc_grp_node, time=(end_frame, end_frame))

    # LOD visibility
    _set_lod_visibility(loc_grp_node, True)
    _set_lod_visibility(main_driver_loc, False)

    cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
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
):
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    # World bake
    loc_grp_node = _world_bake(
        pivot_node, main_node, loc_grp_node, start_frame, end_frame, smart_bake=False
    )
    zero_loc = cmds.duplicate(loc_grp_node)
    cmds.parent(zero_loc, loc_grp_node)
    cmds.xform(
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
        cmds.setKeyframe(zero_loc, time=(start_frame, start_frame))
        cmds.cutKey(loc_grp_node, zero_loc, time=(end_frame, end_frame))
    cmds.parentConstraint(
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
    cmds.rename(zero_loc, str(name) + OBJECT_SPACE_RIG_ZERO_SUFFIX)
    cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
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
):
    skip_translate_attr = _skip_translate_attributes(main_node)
    if not len(skip_translate_attr) == 0:
        LOG.error(
            ("Main object all translation attributes(tx,ty,tz)" " are not available.")
        )
        # TODO: Should the locator be deleted?
        cmds.delete(loc_grp_node)
        return

    # World bake
    loc_grp_node = _world_bake(
        pivot_node, main_node, loc_grp_node, start_frame, end_frame, smart_bake=False
    )
    screen_loc = cmds.duplicate(loc_grp_node)
    cmds.parent(screen_loc, loc_grp_node)
    cmds.xform(
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
    aim_con = cmds.aimConstraint(camera, screen_loc, aimVector=(0.0, 0.0, 1.0))

    # Bake attributes
    fastbake_lib.bake_attributes(
        screen_loc, attrs, start_frame, end_frame, smart_bake=False
    )
    cmds.delete(aim_con)
    zero_loc = cmds.duplicate(screen_loc)
    cmds.parent(zero_loc, screen_loc)
    cmds.xform(
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
        cmds.setKeyframe(screen_loc, zero_loc, time=(start_frame, start_frame))
        cmds.cutKey(loc_grp_node, screen_loc, zero_loc, time=(end_frame, end_frame))

    cmds.pointConstraint(main_driver_loc, main_node, maintainOffset=True)

    # LOD visibility
    _set_lod_visibility(loc_grp_node, False)
    _set_lod_visibility(screen_loc, False)
    _set_lod_visibility(zero_loc, True)
    _set_lod_visibility(main_driver_loc, False)

    # Rename
    cmds.rename(screen_loc, name + SCREEN_SPACE_RIG_SUFFIX)
    cmds.rename(zero_loc, name + SCREEN_SPACE_RIG_ZERO_SUFFIX)
    cmds.rename(main_driver_loc, str(name) + MAIN_DRIVER_SUFFIX_NAME)
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

    :param loc_grp_node: Transform (locator or group) node that will be
        used to create rig.
    :type loc_grp_node: str

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

    :rtype: [str, ..]
    """
    current_frame = False
    if start_frame == end_frame:
        current_frame = True
        end_frame = start_frame + 1

    # Handle group node
    if not cmds.listRelatives(loc_grp_node, shapes=True):
        loc_grp_node = [loc_grp_node[0]]

    # Add custom identify attribute
    cmds.addAttr(
        loc_grp_node[0], longName=IDENTIFIER_ATTR_NAME, dataType="string", keyable=False
    )
    cmds.setAttr(
        str(loc_grp_node[0]) + '.' + IDENTIFIER_ATTR_NAME,
        str(loc_grp_node[0] + str(random.randint(1, 100000000))),
        type="string",
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
        )

    else:
        LOG.error("Invalid space.")

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
    assert cmds.objExists(controller_node)
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
        children = cmds.ls(controller_node, dag=True, long=True, type='transform') or []
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
        driven_nodes += cmds.listConnections(attr, destination=False, source=True) or []
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
        cmds.delete(constraints)
    _remove_constraint_blend_attr_from_nodes(driven_nodes)
    nodes_to_delete = [n for n in nodes_to_delete if cmds.objExists(n)]
    if len(nodes_to_delete) > 0:
        cmds.delete(nodes_to_delete)

    return driven_nodes
