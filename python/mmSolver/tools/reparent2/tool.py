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
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import collections

import maya.cmds
import maya.OpenMaya

import mmSolver.logger
import mmSolver.utils.constant as const_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.utils.configmaya as configmaya

import mmSolver.tools.reparent2.lib as lib
import mmSolver.tools.reparent2.constant as const


LOG = mmSolver.logger.get_logger()


def __get_node_settable_data(settable_map):
    non_settable_nodes = set()
    non_settable_node_axis_t = collections.defaultdict(set)
    non_settable_node_axis_r = collections.defaultdict(set)
    non_settable_node_axis_s = collections.defaultdict(set)
    for key, settable in settable_map.items():
        if settable is False:
            key_split = key.split('.')
            node_name = key_split[0]
            attr_name = key_split[1]
            axis_name = attr_name
            axis_name = axis_name.replace('translate', '')
            axis_name = axis_name.replace('rotate', '')
            axis_name = axis_name.replace('scale', '')
            if 'translate' in attr_name:
                non_settable_node_axis_t[node_name].add(axis_name)
            elif 'rotate' in attr_name:
                non_settable_node_axis_r[node_name].add(axis_name)
            elif 'scale' in attr_name:
                non_settable_node_axis_s[node_name].add(axis_name)
            else:
                pass
            non_settable_nodes.add(node_name)
    settable_data = (
        non_settable_nodes,
        non_settable_node_axis_t,
        non_settable_node_axis_r,
        non_settable_node_axis_s
    )
    return settable_data


def __format_node_status(node,
                         non_settable_node_axis_t,
                         non_settable_node_axis_r,
                         non_settable_node_axis_s):
    axis_t = list(sorted(non_settable_node_axis_t[node]))
    axis_r = list(sorted(non_settable_node_axis_r[node]))
    axis_s = list(sorted(non_settable_node_axis_s[node]))
    if len(axis_t) > 0:
        axis_t = 'T' + ''.join(axis_t)
    else:
        axis_t = ''
    if len(axis_r) > 0:
        axis_r = 'R' + ''.join(axis_r)
    else:
        axis_r = ''
    if len(axis_s) > 0:
        axis_s = 'S' + ''.join(axis_s)
    else:
        axis_s = ''
    attrs = "{} {} {}".format(axis_t, axis_r, axis_s)
    attrs = attrs.replace('  ', ' ').strip()

    node_status = "{} {}".format(node, attrs)
    return node_status


def __check_modify_nodes(node_list):
    """
    Detect if the re-parent children nodes have locked attributes.

    If so, prompt the user what to do...
    1) Cancel operation?
    2) Continue operation with limited features?
    """
    prompt_user = False

    attr_list = [
        'translateX', 'translateY', 'translateZ',
        'rotateX', 'rotateY', 'rotateZ',
        'scaleX', 'scaleY', 'scaleZ'
    ]
    settable_map, \
        settable_count, \
        non_settable_count = lib.nodes_attrs_settable(
            node_list,
            attr_list)

    full_msg = ''
    confirm_msg = ''
    if non_settable_count > 0:
        prompt_user = True
        non_settable_nodes, \
            non_settable_node_axis_t, \
            non_settable_node_axis_r, \
            non_settable_node_axis_s = __get_node_settable_data(settable_map)

        non_settable_nodes = list(sorted(non_settable_nodes))
        non_settable_node_count = len(non_settable_nodes)
        max_display_count = 9

        msg = ("The following nodes have locked or "
               "connected attributes and cannot be modified "
               "during re-parenting.\n\n")
        msg += "Cannot modify {} nodes:\n".format(non_settable_node_count)
        full_msg = msg
        confirm_msg = msg

        for i, node in enumerate(non_settable_nodes):
            node_status = __format_node_status(
                node,
                non_settable_node_axis_t,
                non_settable_node_axis_r,
                non_settable_node_axis_s)

            node_msg = "  {}\n".format(node_status)
            full_msg += node_msg
            if i < max_display_count:
                confirm_msg += node_msg

        if non_settable_node_count > len(non_settable_nodes):
            confirm_msg += "  ... see Script Editor for full list.\n"

        confirm_msg += "\nWould you like to continue?"
    return prompt_user, settable_map, full_msg, confirm_msg


def _reparent_under_node_selection():
    """
    Get selection for Re-parenting the selection under the last selected node.
    """
    nodes = maya.cmds.ls(selection=True, long=True,
                         type='transform') or []
    if len(nodes) < 2:
        msg = ('Not enough objects selected, '
               'select at least 1 child and 1 parent node.')
        LOG.warn(msg)
        return None
    children = nodes[:-1]
    parent = nodes[-1]
    return children, parent


def reparent_under_node():
    """
    Re-parent the selection under the last selected node.

    All settings are taken from the UI's defaults. To change these,
    please use the UI (or 'configmaya' module)
    """
    result = _reparent_under_node_selection()
    if result is None:
        return
    children, parent = result
    reparent(children, parent)
    return


def _unparent_to_world_selection():
    """
    Get selection for Un-parenting the selected nodes into world space.
    """
    children = maya.cmds.ls(selection=True, long=True,
                            type='transform') or []
    if len(children) == 0:
        msg = ('Not enough objects selected, '
               'select at least 1 transform node.')
        LOG.warn(msg)
        return None
    parent = None
    return children, parent


def unparent_to_world():
    """
    Un-parent the selected nodes into world space.

    All settings are taken from the UI's defaults. To change these,
    please use the UI (or 'configmaya' module)
    """
    result = _unparent_to_world_selection()
    if result is None:
        return
    children, parent = result
    reparent(children, parent)
    return


def reparent(children, parent):
    """
    Reparent 'children' nodes under 'parent' node.

    If 'parent' is None, the children are unparented to world.

    All settings are taken from the UI's defaults. To change these,
    please use the UI (or 'configmaya' module)
    """
    children_nodes = [tfm_utils.TransformNode(node=n) for n in children]
    parent_node = None
    if parent is not None:
        parent_node = tfm_utils.TransformNode(node=parent)

    # Get all saved re-parent options.
    frame_range_mode = configmaya.get_scene_option(
        const.CONFIG_FRAME_RANGE_MODE_KEY,
        default=const.DEFAULT_FRAME_RANGE_MODE)
    start_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_START_KEY,
        default=const.DEFAULT_FRAME_START)
    end_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_END_KEY,
        default=const.DEFAULT_FRAME_END)
    bake_mode = configmaya.get_scene_option(
        const.CONFIG_BAKE_MODE_KEY,
        default=const.DEFAULT_BAKE_MODE)
    rotate_order = configmaya.get_scene_option(
        const.CONFIG_ROTATE_ORDER_MODE_KEY,
        default=const.DEFAULT_ROTATE_ORDER_MODE)
    delete_static_anim_curves = configmaya.get_scene_option(
        const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY,
        default=const.DEFAULT_DELETE_STATIC_ANIM_CURVES)
    viewport_mode = const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE

    # Check the children nodes and prompt the user what to do
    prompt_user, settable_map, full_msg, confirm_msg = \
        __check_modify_nodes(children)
    if prompt_user is True:
        LOG.warn(full_msg)
        cancel_button = 'Cancel'
        continue_button = 'Continue'
        button = maya.cmds.confirmDialog(
            title='Warning: Cannot Modify Nodes.',
            message=confirm_msg,
            button=[continue_button, cancel_button],
            defaultButton=continue_button,
            cancelButton=cancel_button,
            dismissString=cancel_button)
        if button == cancel_button:
            LOG.warn('User canceled Re-parent.')
            return

    with tools_utils.tool_context(disable_viewport=True,
                                  use_undo_chunk=True,
                                  use_dg_evaluation_mode=False,
                                  restore_current_frame=True,
                                  pre_update_frame=False,
                                  disable_viewport_mode=viewport_mode):
        lib.reparent(
            children_nodes, parent_node,
            frame_range_mode=frame_range_mode,
            start_frame=start_frame,
            end_frame=end_frame,
            bake_mode=bake_mode,
            rotate_order_mode=rotate_order,
            delete_static_anim_curves=bool(delete_static_anim_curves),
        )
        nodes = [tn.get_node() for tn in children_nodes]
        maya.cmds.select(nodes, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.refresh(currentView=True, force=False)
    return


def reparent_under_node_open_window():
    import mmSolver.tools.reparent2.ui.reparent2_window as window
    win = window.main()

    result = _reparent_under_node_selection()
    if result is None:
        return
    children, parent = result
    sub_form = win.getSubForm()
    sub_form.setChildrenNodes(children)
    sub_form.setParentNode([parent])


def unparent_to_world_open_window():
    import mmSolver.tools.reparent2.ui.reparent2_window as window
    win = window.main()

    result = _unparent_to_world_selection()
    if result is None:
        return
    children, parent = result
    sub_form = win.getSubForm()
    sub_form.setChildrenNodes(children)
    sub_form.setParentNode([])


def open_window():
    import mmSolver.tools.reparent2.ui.reparent2_window as window
    window.main()
