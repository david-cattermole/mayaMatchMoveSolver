# Copyright (C) 2022 Patcha Saheb Binginapalli.

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

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import maya.mel as mel
import maya.cmds as cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.utils.time as time_utils
import mmSolver.tools.createcamerabodytrackscalerigbake.constant as const
import mmSolver.tools.attributebake.lib as fastbake_lib
import mmSolver.tools.createcontroller3.lib as createcontroller_lib
import mmSolver.tools.createcontroller3.constant as createcontroller_const
import mmSolver.tools.reparent2.lib as reparent_lib

LOG = mmSolver.logger.get_logger()


suffix = const.SCALE_RIG_SUFFIX
main_grp_suffix = const.SCALE_RIG_MAIN_GRP_SUFFIX

frame_start, frame_end = time_utils.get_maya_timeline_range_inner()

def _is_rig_node(node):
    """Check if the node is a rig node."""
    if node_utils.attribute_exists(const.SCALE_RIG_IDENTIFIER_ATTR_NAME, node):
        return True
    return False

def _get_rig_node_identifier(node, attr):
    """Get custom attribute value to identify rig node."""
    if _is_rig_node(node):
        plug = node + '.' + attr
        attr_value = cmds.getAttr(plug)
        return attr_value
    return None

def _create_scale_rig_main_grp(scale_rig_name,
                               scene=None,
                               rig_controls=None,
                               rig_type=None):
    main_grp = cmds.group(name=scale_rig_name, empty=True)
    attrs = [const.SCALE_RIG_IDENTIFIER_ATTR_NAME,
             const.SCALE_RIG_TYPE_ATTR_NAME,
             const.SCALE_RIG_SCENE_ATTR_NAME,
             const.SCALE_RIG_BODY_TRACK_CONTROLS_ATTR_NAME]
    for attr in attrs:
        cmds.addAttr(main_grp, longName=attr, dataType="string", keyable=False)        
    cmds.setAttr(main_grp+'.'+const.SCALE_RIG_SCENE_ATTR_NAME, str(scene),
                                                  type="string", lock=True)    
    text = ''
    for control_name in rig_controls:
        text += str(control_name) + ', '
    text = text.strip(' ').strip(',')      
    cmds.setAttr(main_grp+'.'+const.SCALE_RIG_BODY_TRACK_CONTROLS_ATTR_NAME,
                                            text, type="string", lock=True)
    if rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
        cmds.setAttr(main_grp+'.'+const.SCALE_RIG_TYPE_ATTR_NAME,
                     const.SCALE_RIG_TYPE_CAMERA_TRACK,
                     type="string", lock=True)
    else:
        cmds.setAttr(main_grp+'.'+const.SCALE_RIG_TYPE_ATTR_NAME,
                     const.SCALE_RIG_TYPE_BODY_TRACK,
                     type="string", lock=True)      
    return main_grp  

def _break_scale_attributes(nodes):
    attrs = ['sx', 'sy', 'sz']
    for node in nodes:
        for count,i in enumerate(attrs):
            attr = str(node.get_node())+'.'+attrs[count]
            mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\""%attr)

def create_camera_body_track_scale_rig(name,
                              camera,
                              scene,
                              body_track_controls,
                              scale_rig_type):
    """
    Create a camera track scale rig.
    
    :param name: Scale rig name.
    :type name: str   
    
    :param camera: Camera node.
    :type camera: Transform node
    
    :param scene: Scene node.
    :type scene: Transform node or None   
    
    :param body_track_controls: Body track controls transforms.
    :type body_track_controls: Transforms list or [] 
    
    :param scale_rig_type: Which type of scale rig to be created?
        mmSolver.tools.camerabodytrackscalerigbake.constant.SCALE_RIG_LIST.
    :type: str 
    
    :rtype: [str]       
    """
    
    # Create camera witness
    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    controller_type = createcontroller_const.CONTROLLER_TYPE_WORLD_SPACE
    if scale_rig_type == const.SCALE_RIG_TYPE_BODY_TRACK:     
        camera_witness = _create_scale_rig_main_grp(name+suffix+main_grp_suffix,
                                                    str(scene),
                                                    body_track_controls,
                                                    const.SCALE_RIG_TYPE_BODY_TRACK)
    if scale_rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK: 
        camera_witness = cmds.group(name=name+suffix, empty=True)    
    
    parent_con = cmds.parentConstraint(camera, camera_witness, maintainOffset=False)
    camera_witness = cmds.ls(camera_witness)
    fastbake_lib.bake_attributes(camera_witness, attrs, frame_start, frame_end,
                                                              smart_bake=False)
    cmds.delete(parent_con)
    
    # Create rig controls witness
    body_track_controls_witness = []
    for control in body_track_controls:
        control_witness = createcontroller_lib.create_controller(name,
                                                control,
                                                control,
                                                cmds.group(empty=True),
                                                frame_start,
                                                frame_end,
                                                controller_type,
                                                smart_bake=False,
                                                camera=None)
        body_track_controls_witness.append(control_witness[0])
        
    # Reparent
    children_nodes = [tfm_utils.TransformNode(node=n) for n in body_track_controls_witness]
    parent_node = tfm_utils.TransformNode(node=camera_witness[0])
    reparent_lib.reparent(children_nodes, parent_node,
                           frame_range_mode='timeline_inner',
                           start_frame=frame_start,
                           end_frame=frame_end,
                           bake_mode='full_bake',
                           rotate_order_mode='use_existing',
                           delete_static_anim_curves=False)
    _break_scale_attributes(children_nodes)

    # Body track scale rig
    if scale_rig_type == const.SCALE_RIG_TYPE_BODY_TRACK:
        # Break body track controls witness scale attributes
        body_track_control_nodes = [tfm_utils.TransformNode(node=n) for n in body_track_controls]
        _break_scale_attributes(body_track_control_nodes)
        # Scale constraint to body track controls
        for node in body_track_control_nodes:
            cmds.scaleConstraint(parent_node.get_node(),
                                 node.get_node(), maintainOffset=True)
        cmds.select(parent_node.get_node(), replace=True)
            
    # Camera track scale rig
    if scale_rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
        grand_parent = _create_scale_rig_main_grp(name+suffix+main_grp_suffix,
                                                  str(scene),
                                                  body_track_controls,
                                                  const.SCALE_RIG_TYPE_CAMERA_TRACK)        
        con = cmds.parentConstraint(parent_node.get_node(), grand_parent,
                                                    maintainOffset=False)
        cmds.delete(con)        
        grand_parent_node = tfm_utils.TransformNode(node=grand_parent)
        reparent_lib.reparent([parent_node], grand_parent_node,
                               frame_range_mode='timeline_inner',
                               start_frame=frame_start,
                               end_frame=frame_end,
                               bake_mode='full_bake',
                               rotate_order_mode='use_existing',
                               delete_static_anim_curves=False) 
        _break_scale_attributes([parent_node])
        
        # Break scene scale attributes
        node = cmds.ls(scene, long=True, type='transform')
        scene_node = tfm_utils.TransformNode(node=node[0])
        _break_scale_attributes([scene_node])        
        cmds.parentConstraint(grand_parent, scene, maintainOffset=True)        
        cmds.scaleConstraint(grand_parent, scene, maintainOffset=True)
        
        # Create scale expression
        attrs = ['sx', 'sy', 'sz']
        parent = parent_node.get_node()
        for attr in attrs:
            exp = str(str(parent)+'.'+attr)+'='+'1'+'/'+str(grand_parent)+'.'+attr
            cmds.expression(string=exp, object=str(parent), alwaysEvaluate=True,
                                                           unitConversion='all')
        cmds.select(grand_parent, replace=True)    
                        
def remove_camera_body_track_scale_rig(rigs_list): 
    """
    Bake and remove scale rig(s).
    
    :param rigs_list: Scale rig(s).
    :type rigs_list: list
    """

    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    for node in rigs_list:
        body_track_attr_value = _get_rig_node_identifier(node,
                                const.SCALE_RIG_BODY_TRACK_CONTROLS_ATTR_NAME)
        if body_track_attr_value == None:
            LOG.warn('Please select scale rig(s) only.')
            return
        nodes_to_be_baked = body_track_attr_value.split(',')
        rig_type = _get_rig_node_identifier(node,
                    const.SCALE_RIG_TYPE_ATTR_NAME)
        camera_attr_value = _get_rig_node_identifier(node,
                            const.SCALE_RIG_SCENE_ATTR_NAME)
        if rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
            nodes_to_be_baked.append(camera_attr_value)
        fastbake_lib.bake_attributes(nodes_to_be_baked,
                                     attrs,
                                     frame_start,
                                     frame_end,
                                     smart_bake=False)
        cmds.delete(node)
