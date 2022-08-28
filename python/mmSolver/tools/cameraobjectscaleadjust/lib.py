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

import maya.mel
import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.utils.time as time_utils
import mmSolver.tools.cameraobjectscaleadjust.constant as const
import mmSolver.tools.attributebake.lib as fastbake_lib
import mmSolver.tools.createcontroller2.lib as createcontroller_lib
import mmSolver.tools.createcontroller2.constant as createcontroller_const
import mmSolver.tools.reparent2.constant as reparent_const
import mmSolver.tools.reparent2.lib as reparent_lib

LOG = mmSolver.logger.get_logger()

# Should be upper-case, if used like this.
suffix = const.SCALE_RIG_SUFFIX
main_grp_suffix = const.SCALE_RIG_MAIN_GRP_SUFFIX

# TODO: Make these arguments.
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
        attr_value = maya.cmds.getAttr(plug)
        return attr_value
    return None


def _create_scale_rig_main_grp(
    scale_rig_name, scene=None, rig_controls=None, rig_type=None
):
    main_grp = maya.cmds.group(name=scale_rig_name, empty=True)
    attrs = [
        const.SCALE_RIG_IDENTIFIER_ATTR_NAME,
        const.SCALE_RIG_TYPE_ATTR_NAME,
        const.SCALE_RIG_SCENE_ATTR_NAME,
        const.SCALE_RIG_OBJECT_TRACK_CONTROLS_ATTR_NAME,
    ]
    for attr in attrs:
        maya.cmds.addAttr(main_grp, longName=attr, dataType="string", keyable=False)
    maya.cmds.setAttr(
        main_grp + '.' + const.SCALE_RIG_SCENE_ATTR_NAME,
        str(scene),
        type="string",
        lock=True,
    )
    text = ''
    for control_name in rig_controls:
        text += str(control_name) + ', '
    text = text.strip(' ').strip(',')
    maya.cmds.setAttr(
        main_grp + '.' + const.SCALE_RIG_OBJECT_TRACK_CONTROLS_ATTR_NAME,
        text,
        type="string",
        lock=True,
    )
    if rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
        maya.cmds.setAttr(
            main_grp + '.' + const.SCALE_RIG_TYPE_ATTR_NAME,
            const.SCALE_RIG_TYPE_CAMERA_TRACK,
            type="string",
            lock=True,
        )
    else:
        maya.cmds.setAttr(
            main_grp + '.' + const.SCALE_RIG_TYPE_ATTR_NAME,
            const.SCALE_RIG_TYPE_OBJECT_TRACK,
            type="string",
            lock=True,
        )
    return main_grp


def _break_scale_attributes(tfm_nodes):
    attrs = ['sx', 'sy', 'sz']
    for tfm_node in tfm_nodes:
        node = tfm_node.get_node()
        if node is None:
            continue
        for attr in attrs:
            node_attr = node + '.' + attr
            # TODO: Replace this will a explicit 'maya.cmds.disconnectAttr'
            #  calls.
            cmd = 'source channelBoxCommand; CBdeleteConnection "{}"'
            maya.mel.eval(cmd.format(node_attr))


def create_scale_rig(name, camera, scene, object_track_controls, scale_rig_type):
    """
    Create a camera track scale rig.

    :param name: Scale rig name.
    :type name: str

    :param camera: Camera node.
    :type camera: Transform node

    :param scene: Scene node.
    :type scene: Transform node or None

    :param object_track_controls: Object track controls transforms.
    :type object_track_controls: Transforms list or []

    :param scale_rig_type: Which type of scale rig to be created?
        mmSolver.tools.cameraobjectscaleadjust.constant.SCALE_RIG_LIST.
    :type: str

    :rtype: [str]
    """
    # Create camera witness
    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    controller_type = createcontroller_const.CONTROLLER_TYPE_WORLD_SPACE
    camera_witness = None
    if scale_rig_type == const.SCALE_RIG_TYPE_OBJECT_TRACK:
        camera_witness = _create_scale_rig_main_grp(
            name + suffix + main_grp_suffix,
            str(scene),
            object_track_controls,
            const.SCALE_RIG_TYPE_OBJECT_TRACK,
        )
    if scale_rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
        camera_witness = maya.cmds.group(name=name + suffix, empty=True)
    assert camera_witness is not None

    parent_con = maya.cmds.parentConstraint(
        camera, camera_witness, maintainOffset=False
    )
    camera_witness = maya.cmds.ls(camera_witness)
    fastbake_lib.bake_attributes(
        camera_witness, attrs, frame_start, frame_end, smart_bake=False
    )
    maya.cmds.delete(parent_con)

    # Create rig controls witness
    object_track_controls_witness = []
    for control in object_track_controls:
        null_node = maya.cmds.createNode('transform')
        control_witness = createcontroller_lib.create_controller(
            name,
            control,
            control,
            null_node,
            frame_start,
            frame_end,
            controller_type,
            smart_bake=False,
            camera=None,
        )
        object_track_controls_witness.append(control_witness[0])

    # Reparent
    children_nodes = [
        tfm_utils.TransformNode(node=n) for n in object_track_controls_witness
    ]
    parent_node = tfm_utils.TransformNode(node=camera_witness[0])
    reparent_lib.reparent(
        children_nodes,
        parent_node,
        frame_range_mode=reparent_const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE,
        start_frame=frame_start,
        end_frame=frame_end,
        bake_mode=reparent_const.BAKE_MODE_FULL_BAKE_VALUE,
        rotate_order_mode=reparent_const.ROTATE_ORDER_MODE_USE_EXISTING_VALUE,
        delete_static_anim_curves=False,
    )
    _break_scale_attributes(children_nodes)

    # Object track scale rig
    if scale_rig_type == const.SCALE_RIG_TYPE_OBJECT_TRACK:
        # Break object track controls witness scale attributes
        object_track_control_nodes = [
            tfm_utils.TransformNode(node=n) for n in object_track_controls
        ]
        _break_scale_attributes(object_track_control_nodes)
        # Scale constraint to object track controls
        for node in object_track_control_nodes:
            maya.cmds.scaleConstraint(
                parent_node.get_node(), node.get_node(), maintainOffset=True
            )
        maya.cmds.select(parent_node.get_node(), replace=True)

    # Camera track scale rig
    if scale_rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
        grand_parent = _create_scale_rig_main_grp(
            name + suffix + main_grp_suffix,
            str(scene),
            object_track_controls,
            const.SCALE_RIG_TYPE_CAMERA_TRACK,
        )
        con = maya.cmds.parentConstraint(
            parent_node.get_node(), grand_parent, maintainOffset=False
        )
        maya.cmds.delete(con)
        grand_parent_node = tfm_utils.TransformNode(node=grand_parent)
        reparent_lib.reparent(
            [parent_node],
            grand_parent_node,
            frame_range_mode=reparent_const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE,
            start_frame=frame_start,
            end_frame=frame_end,
            bake_mode=reparent_const.BAKE_MODE_FULL_BAKE_VALUE,
            rotate_order_mode=reparent_const.ROTATE_ORDER_MODE_USE_EXISTING_VALUE,
            delete_static_anim_curves=False,
        )
        _break_scale_attributes([parent_node])

        # Break scene scale attributes
        node = maya.cmds.ls(scene, long=True, type='transform')
        scene_node = tfm_utils.TransformNode(node=node[0])
        _break_scale_attributes([scene_node])
        maya.cmds.parentConstraint(grand_parent, scene, maintainOffset=True)
        maya.cmds.scaleConstraint(grand_parent, scene, maintainOffset=True)

        # Create scale expression
        attrs = ['sx', 'sy', 'sz']
        parent = parent_node.get_node()
        for attr in attrs:
            exp = (
                str(str(parent) + '.' + attr)
                + '='
                + '1'
                + '/'
                + str(grand_parent)
                + '.'
                + attr
            )
            maya.cmds.expression(
                string=exp,
                object=str(parent),
                alwaysEvaluate=True,
                unitConversion='all',
            )
        maya.cmds.select(grand_parent, replace=True)
    return


def remove_scale_rig(rigs_list):
    """
    Bake and remove scale rig(s).

    :param rigs_list: Scale rig(s).
    :type rigs_list: list
    """
    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    for node in rigs_list:
        object_track_attr_value = _get_rig_node_identifier(
            node, const.SCALE_RIG_OBJECT_TRACK_CONTROLS_ATTR_NAME
        )
        if object_track_attr_value is None:
            LOG.warn('Please select scale rig(s) only.')
            return
        nodes_to_be_baked = object_track_attr_value.split(',')
        rig_type = _get_rig_node_identifier(node, const.SCALE_RIG_TYPE_ATTR_NAME)
        camera_attr_value = _get_rig_node_identifier(
            node, const.SCALE_RIG_SCENE_ATTR_NAME
        )
        if rig_type == const.SCALE_RIG_TYPE_CAMERA_TRACK:
            nodes_to_be_baked.append(camera_attr_value)
        fastbake_lib.bake_attributes(
            nodes_to_be_baked, attrs, frame_start, frame_end, smart_bake=False
        )
        maya.cmds.delete(node)
    return
