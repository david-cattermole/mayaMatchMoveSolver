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
