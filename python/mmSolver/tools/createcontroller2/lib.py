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

import mmSolver.tools.fastbake.lib as fastbake_lib

import mmSolver.logger
LOG = mmSolver.logger.get_logger()

import maya.cmds as cmds
import maya.mel as mel

ATTRIBUTE_IDENTIFIER_NAME = "mmsolverccidentifier"
ATTRIBUTE_IDENTIFIER_VALUE = "mmSolver_createcontroller_identifier"
OBJECT_SPACE_RIG_ZERO_SUFFIX = "_objectSpaceZero"
SCREEN_SPACE_RIG_SUFFIX = "_screenSpace"
SCREEN_SPACE_RIG_ZERO_SUFFIX = "_screenSpaceZero"


def skip_attributes(node):
    attr_list = [["x","y","z"],["x","y","z"]]
    if cmds.getAttr(node+".translateX", keyable=True) and cmds.getAttr(node+".translateX", settable=True):
        attr_list[0].remove("x")
    if cmds.getAttr(node+".translateY", keyable=True) and cmds.getAttr(node+".translateY", settable=True):
        attr_list[0].remove("y")
    if cmds.getAttr(node+".translateZ", keyable=True) and cmds.getAttr(node+".translateZ", settable=True):
        attr_list[0].remove("z")
    if cmds.getAttr(node+".rotateX", keyable=True) and cmds.getAttr(node+".rotateX", settable=True):
        attr_list[1].remove("x")
    if cmds.getAttr(node+".rotateY", keyable=True) and cmds.getAttr(node+".rotateY", settable=True):
        attr_list[1].remove("y")
    if cmds.getAttr(node+".rotateZ", keyable=True) and cmds.getAttr(node+".rotateZ", settable=True):
        attr_list[1].remove("z")
    return attr_list


def set_keys(parent, child, frame_start, frame_end):
    #copy parent keys to child. start frame and end frame are mandatory
    all_keys = cmds.keyframe(parent, query=True, time=(frame_start, frame_end))
    keys = [frame_start, frame_end]
    for key in all_keys:
        if key not in keys:
            keys.append(key)
    cmds.setKeyframe(child, time=keys)


def set_lod_visibility(node, visibility=False):
    #sets shape node LOD visibility on/off
    shape = cmds.listRelatives(node, shapes=True)
    if shape:
        cmds.setAttr(shape[0]+".lodVisibility",visibility)


def _world_bake(pivot, main, loc_grp, start, end, smart=False):
    # xform pivot node world position to loc_grp_node
    cmds.xform(loc_grp, worldSpace=True, translation=(cmds.xform(pivot, query=True, worldSpace=True, translation=True)))
    # xform main node world rotation to loc_grp_node
    cmds.xform(loc_grp, worldSpace=True, rotation=(cmds.xform(main, query=True, worldSpace=True, rotation=True)))
    parent_con = cmds.parentConstraint(main, loc_grp, maintainOffset=True)
    # bake attributes
    fastbake_lib.bake_attributes(loc_grp, [], start, end, smart)
    cmds.delete(parent_con)
    return loc_grp


def create_controller(name,
                      pivot_node,
                      main_node,
                      loc_grp_node,
                      start_frame,
                      end_frame,
                      space,
                      smart_bake=False,
                      camera=None):
    """
    Create Controller of a node.

    :param name: rig name
    :type name: string

    :param pivot_node: pivot node for rig
    :type pivot_node: pivot node

    :param main_node: main node for rig
    :type main_node: transform node

    :param loc_grp_node: node that will be used to create rig
    :type loc_grp_node: transform node(ex:locator or group)

    :param start_frame: bake range start frame
    :type start_frame: int

    :param end_frame: bake range end frame
    :type end_frame: int 

    :param space: in which space rig to be created?
    :type: string
           'worldSpace', 'objectSpace', 'screenSpace'

    :param smart_bake: enable/disable smart bake
    :type: bool

    :param camera: camera node for screen space rig
    :type: camera node
    """
    attrs = []

    skip_attrs = skip_attributes(main_node)
    skip_translate_attr = skip_attrs[0]
    skip_rotate_attr = skip_attrs[1]

    current_frame = False
    if start_frame == end_frame:
        current_frame = True
        end_frame = start_frame + 1

    #handle group node
    if not cmds.listRelatives(loc_grp_node, shapes=True):
        loc_grp_node = [loc_grp_node[0]]

    #add custom identify attribute
    cmds.addAttr(loc_grp_node[0], longName=ATTRIBUTE_IDENTIFIER_NAME, dataType="string", keyable=False)
    cmds.setAttr(str(loc_grp_node[0])+"."+ATTRIBUTE_IDENTIFIER_NAME, ATTRIBUTE_IDENTIFIER_VALUE, type="string", lock=True)

    if space == "worldSpace":
        loc_grp_node = _world_bake(pivot_node, main_node, loc_grp_node, start_frame, end_frame, smart_bake)
        cmds.parentConstraint(loc_grp_node, main_node, maintainOffset=True, st=skip_translate_attr, sr=skip_rotate_attr)
        if current_frame is True:
            cmds.cutKey(loc_grp_node, time=(end_frame,end_frame))

    if space == "objectSpace":
        #world bake
        loc_grp_node = _world_bake(pivot_node, main_node, loc_grp_node, start_frame, end_frame, False)
        zero_loc = cmds.duplicate(loc_grp_node)
        cmds.parent(zero_loc, loc_grp_node)
        #smart bake
        if smart_bake is True:
            set_keys(main_node, zero_loc, start_frame, end_frame)
        #current frame
        if current_frame is True:
            cmds.setKeyframe(zero_loc, time=(start_frame,start_frame))
            cmds.cutKey(loc_grp_node, zero_loc,time=(end_frame,end_frame))
        cmds.parentConstraint(zero_loc, main_node, maintainOffset=True, st=skip_translate_attr, sr=skip_rotate_attr)
        #LOD visibility
        set_lod_visibility(loc_grp_node, False)
        set_lod_visibility(zero_loc, True)
        #rename
        cmds.rename(zero_loc, str(name)+OBJECT_SPACE_RIG_ZERO_SUFFIX)

    if space == "screenSpace":
        if not len(skip_translate_attr) == 0:
            LOG.warn("Error, Main object all translation attributes(tx,ty,tz) are not available.")
            cmds.delete(loc_grp_node)
            return
        #world bake
        loc_grp_node = _world_bake(pivot_node, main_node, loc_grp_node, start_frame, end_frame, False)
        screen_loc = cmds.duplicate(loc_grp_node)
        cmds.parent(screen_loc, loc_grp_node)
        #bake attributes
        fastbake_lib.bake_attributes(screen_loc, attrs, start_frame, end_frame, False)
        aim_con = cmds.aimConstraint(camera, screen_loc, aimVector=(0.0,0.0,1.0))
        #bake attributes
        fastbake_lib.bake_attributes(screen_loc, attrs, start_frame, end_frame, False)
        cmds.delete(aim_con)
        zero_loc = cmds.duplicate(screen_loc)
        cmds.parent(zero_loc, screen_loc)
        #smart bake
        if smart_bake is True:
            set_keys(main_node, zero_loc, start_frame, end_frame)
        #current frame
        if current_frame is True:
            cmds.setKeyframe(screen_loc, zero_loc, time=(start_frame,start_frame))
            cmds.cutKey(loc_grp_node, screen_loc, zero_loc, time=(end_frame,end_frame))
        cmds.pointConstraint(zero_loc, main_node, maintainOffset=True)
        #LOD visibility
        set_lod_visibility(loc_grp_node, False)
        set_lod_visibility(screen_loc, False)
        set_lod_visibility(zero_loc, True)
        #rename
        cmds.rename(screen_loc, name+SCREEN_SPACE_RIG_SUFFIX)
        cmds.rename(zero_loc, name+SCREEN_SPACE_RIG_ZERO_SUFFIX)


def remove_controller(controllerNode, frame_start, frame_end):
    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
    attrs = cmds.channelBox(channelBox, query=True, sma=True) or []
    constraint = cmds.listConnections(controllerNode+".parentMatrix[0]",
                                      destination=True, source=False, type="constraint")
    if not constraint:
        LOG.warn("Selected controller is not driving any object.")
        return
    constraint = constraint[0]
    driven_node = cmds.listConnections(constraint+'.constraintParentInverseMatrix', destination=False, source=True)
    if driven_node:
        #bake attributes
        fastbake_lib.bake_attributes(driven_node, attrs, frame_start, frame_end, True)
        cmds.delete(constraint)
        attr_list = cmds.listAttr(driven_node)
        for attr in attr_list:
            if "blendPoint" in attr or "blendOrient" in attr or "blendParent" in attr:
                cmds.deleteAttr(str(driven_node[0])+"."+str(attr))
        #delete controller node and its parents
        attr_list = cmds.listAttr(controllerNode)
        if ATTRIBUTE_IDENTIFIER_NAME in attr_list:
            parent_nodes = cmds.listRelatives(controllerNode, fullPath=True, parent=True)
            if parent_nodes:
                parent_nodes = parent_nodes[0]
                parent_nodes = parent_nodes.split("|")
                del(parent_nodes[0])
                cmds.delete(parent_nodes)
        if cmds.objExists(controllerNode):
            cmds.delete(controllerNode)
    return
