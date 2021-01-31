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

import maya.cmds as cmds
import maya.mel as mel

import mmSolver.utils.node as node_utils
import mmSolver.tools.fastbake.lib as fastbake_lib
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


ATTRIBUTE_IDENTIFIER_NAME = "mmsolver_cc_identifier"
ATTRIBUTE_IDENTIFIER_VALUE = "mmSolver_create_controller_identifier"
WORLD_SPACE_RIG_ZERO_SUFFIX = "_worldSpaceZero"
OBJECT_SPACE_RIG_ZERO_SUFFIX = "_objectSpaceZero"
SCREEN_SPACE_RIG_SUFFIX = "_screenSpace"
SCREEN_SPACE_RIG_ZERO_SUFFIX = "_screenSpaceZero"


def _get_selected_channel_box_attrs():
    cmd = 'global string $gChannelBoxName; $temp=$gChannelBoxName;'
    channel_box = mel.eval(cmd)
    attrs = cmds.channelBox(
        channel_box, query=True, selectedMainAttributes=True) or []
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


def _copy_parent_keys_to_child(parent, child, start_frame, end_frame):
    """Copy parent keys to child. start frame and end frame are mandatory."""
    all_keys = cmds.keyframe(parent, query=True, time=(start_frame, end_frame))
    keys = [start_frame, end_frame]
    for key in all_keys:
        if key not in keys:
            keys.append(key)
    cmds.setKeyframe(child, time=keys)


def _set_lod_visibility(node, visibility=False):
    """Sets shape node LOD visibility on/off"""
    shape = cmds.listRelatives(node, shapes=True)
    if shape:
        cmds.setAttr(shape[0] + ".lodVisibility", visibility)
    return


def _world_bake(pivot, main, loc_grp, start, end, smart_bake=False):
    # xform pivot node world position to loc_grp_node
    pivot_translate = cmds.xform(
        pivot, query=True, worldSpace=True, translation=True)
    cmds.xform(loc_grp, worldSpace=True, translation=pivot_translate)

    # xform main node world rotation to loc_grp_node
    main_rotate = cmds.xform(
        main, query=True, worldSpace=True, rotation=True)
    cmds.xform(loc_grp, worldSpace=True, rotation=main_rotate)
    parent_con = cmds.parentConstraint(main, loc_grp, maintainOffset=True)

    # bake attributes
    attrs = []
    fastbake_lib.bake_attributes(loc_grp, attrs, start, end, smart_bake)
    cmds.delete(parent_con)
    return loc_grp


def _find_constraints_from_node(node):
    constraints = cmds.listConnections(
        node + ".parentMatrix[0]",
        destination=True, source=False, type="constraint")
    constraints = [n for n in constraints
                   if node_utils.node_is_referenced(n) is False]
    constraints = list(set(constraints))
    return constraints


def _remove_constraint_blend_attr_from_nodes(nodes):
    for node in nodes:
        attr_list = cmds.listAttr(node)
        for attr in attr_list:
            if ("blendPoint" in attr
                    or "blendOrient" in attr
                    or "blendParent" in attr):
                cmds.deleteAttr(str(node) + "." + str(attr))
    return


def _create_controller_world_space(pivot_node,
                                   main_node,
                                   loc_grp_node,
                                   start_frame,
                                   end_frame,
                                   smart_bake,
                                   current_frame):
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    loc_grp_node = _world_bake(
        pivot_node, main_node, loc_grp_node,
        start_frame, end_frame, smart_bake=smart_bake)

    cmds.parentConstraint(
        loc_grp_node, main_node,
        maintainOffset=True,
        skipTranslate=skip_translate_attr,
        skipRotate=skip_rotate_attr)
    if current_frame is True:
        cmds.cutKey(loc_grp_node, time=(end_frame, end_frame))

    return loc_grp_node


def _create_controller_object_space(name,
                                    pivot_node,
                                    main_node,
                                    loc_grp_node,
                                    start_frame,
                                    end_frame,
                                    smart_bake,
                                    current_frame):
    skip_translate_attr = _skip_translate_attributes(main_node)
    skip_rotate_attr = _skip_rotate_attributes(main_node)

    # World bake
    loc_grp_node = _world_bake(
        pivot_node, main_node, loc_grp_node,
        start_frame, end_frame, smart_bake=False)
    zero_loc = cmds.duplicate(loc_grp_node)
    cmds.parent(zero_loc, loc_grp_node)

    # Smart bake
    if smart_bake is True:
        _copy_parent_keys_to_child(main_node, zero_loc, start_frame, end_frame)

    # Current frame
    if current_frame is True:
        cmds.setKeyframe(zero_loc, time=(start_frame, start_frame))
        cmds.cutKey(loc_grp_node, zero_loc, time=(end_frame, end_frame))
    cmds.parentConstraint(
        zero_loc, main_node,
        maintainOffset=True,
        skipTranslate=skip_translate_attr,
        skipRotate=skip_rotate_attr)

    # LOD visibility
    _set_lod_visibility(loc_grp_node, False)
    _set_lod_visibility(zero_loc, True)

    # Rename
    cmds.rename(zero_loc, str(name)+OBJECT_SPACE_RIG_ZERO_SUFFIX)
    return loc_grp_node


def _create_controller_screen_space(name,
                                    pivot_node, main_node, loc_grp_node,
                                    start_frame, end_frame, smart_bake,
                                    current_frame, camera):
    skip_translate_attr = _skip_translate_attributes(main_node)
    if not len(skip_translate_attr) == 0:
        LOG.error((
            "Main object all translation attributes(tx,ty,tz)"
            " are not available."
        ))
        # TODO: Should the locator be deleted?
        cmds.delete(loc_grp_node)
        return

    # World bake
    loc_grp_node = _world_bake(
        pivot_node, main_node, loc_grp_node,
        start_frame, end_frame, smart_bake=False)
    screen_loc = cmds.duplicate(loc_grp_node)
    cmds.parent(screen_loc, loc_grp_node)

    # Bake attributes
    attrs = []
    fastbake_lib.bake_attributes(
        screen_loc, attrs, start_frame, end_frame, smart_bake=False)
    aim_con = cmds.aimConstraint(camera, screen_loc, aimVector=(0.0, 0.0, 1.0))

    # Bake attributes
    fastbake_lib.bake_attributes(
        screen_loc, attrs, start_frame, end_frame, smart_bake=False)
    cmds.delete(aim_con)
    zero_loc = cmds.duplicate(screen_loc)
    cmds.parent(zero_loc, screen_loc)

    # Smart bake
    if smart_bake is True:
        _copy_parent_keys_to_child(main_node, zero_loc, start_frame, end_frame)

    # Current frame
    if current_frame is True:
        cmds.setKeyframe(screen_loc, zero_loc,
                         time=(start_frame, start_frame))
        cmds.cutKey(loc_grp_node, screen_loc, zero_loc,
                    time=(end_frame, end_frame))
    cmds.pointConstraint(zero_loc, main_node, maintainOffset=True)

    # LOD visibility
    _set_lod_visibility(loc_grp_node, False)
    _set_lod_visibility(screen_loc, False)
    _set_lod_visibility(zero_loc, True)

    # Rename
    cmds.rename(screen_loc, name + SCREEN_SPACE_RIG_SUFFIX)
    cmds.rename(zero_loc, name + SCREEN_SPACE_RIG_ZERO_SUFFIX)
    return loc_grp_node


def create_controller(name,
                      pivot_node,
                      main_node,
                      loc_grp_node,
                      start_frame,
                      end_frame,
                      controller_type,
                      smart_bake=False,
                      camera=None):
    """
    Create Controller of a node.

    :param name: rig name
    :type name: string

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
        loc_grp_node[0],
        longName=ATTRIBUTE_IDENTIFIER_NAME,
        dataType="string", keyable=False)
    cmds.setAttr(
        str(loc_grp_node[0]) + "." + ATTRIBUTE_IDENTIFIER_NAME,
        ATTRIBUTE_IDENTIFIER_VALUE,
        type="string", lock=True)

    if controller_type == const.CONTROLLER_TYPE_WORLD_SPACE:
        loc_grp_node = _create_controller_world_space(
            pivot_node, main_node, loc_grp_node,
            start_frame, end_frame, smart_bake, current_frame)

    elif controller_type == const.CONTROLLER_TYPE_OBJECT_SPACE:
        loc_grp_node = _create_controller_object_space(
            name,
            pivot_node, main_node, loc_grp_node,
            start_frame, end_frame, smart_bake, current_frame)

    elif controller_type == const.CONTROLLER_TYPE_SCREEN_SPACE:
        loc_grp_node = _create_controller_screen_space(
            name,
            pivot_node, main_node, loc_grp_node,
            start_frame, end_frame, smart_bake, current_frame, camera)

    else:
        LOG.error("Invalid space.")

    return loc_grp_node


def remove_controller(controller_node, frame_start, frame_end):
    """
    Bake the affects of the controller node, and delete the controller.

    :returns: The transform node that was controlled by the given controller.
    :rtype: str
    """
    attrs = _get_selected_channel_box_attrs()

    constraints = _find_constraints_from_node(controller_node)
    if not constraints:
        LOG.warn("Selected controller is not driving any object.")
        return

    # Get Driven nodes
    driven_nodes = []
    for constraint in constraints:
        driven_nodes += cmds.listConnections(
            constraints + '.constraintParentInverseMatrix',
            destination=False, source=True) or []

    if driven_nodes and len(driven_nodes) > 0:
        # Bake attributes
        fastbake_lib.bake_attributes(
            driven_nodes, attrs, frame_start, frame_end, smart_bake=True)
        cmds.delete(constraints)
        _remove_constraint_blend_attr_from_nodes(driven_nodes)

        # Delete controller node and its parents
        attr_list = cmds.listAttr(controller_node)
        if ATTRIBUTE_IDENTIFIER_NAME in attr_list:
            parent_nodes = cmds.listRelatives(
                controller_node, fullPath=True, parent=True)
            if parent_nodes:
                parent_nodes = parent_nodes[0]
                parent_nodes = parent_nodes.split("|")
                del(parent_nodes[0])
                cmds.delete(parent_nodes)
        if cmds.objExists(controller_node):
            cmds.delete(controller_node)
    return driven_nodes
