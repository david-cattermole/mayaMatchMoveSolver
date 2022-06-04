# Copyright (C) 2019 David Cattermole.
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
import mmSolver.logger
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent.lib as lib

LOG = mmSolver.logger.get_logger()


def reparent_under_node():
    """
    Re-parent the selection under the last selected node.
    """
    frame = maya.cmds.currentTime(query=True)
    nodes = maya.cmds.ls(selection=True, long=True, type='transform') or []

    if len(nodes) < 2:
        msg = (
            'Not enough objects selected, ' 'select at least 1 child and 1 parent node.'
        )
        LOG.warn(msg)
        return
    with tools_utils.tool_context(
        disable_viewport=True,
        use_undo_chunk=False,
        use_dg_evaluation_mode=False,
        restore_current_frame=False,
        pre_update_frame=False,
    ):
        children = nodes[:-1]
        parent = nodes[-1]
        children_tfm_nodes = [tfm_utils.TransformNode(node=n) for n in children]
        parent_tfm_node = tfm_utils.TransformNode(node=parent)
        lib.reparent(children_tfm_nodes, parent_tfm_node, sparse=True)
        children = [tn.get_node() for tn in children_tfm_nodes]
        maya.cmds.select(children, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return


def unparent_to_world():
    """
    Un-parent the selected nodes into world space.
    """
    frame = maya.cmds.currentTime(query=True)
    nodes = maya.cmds.ls(selection=True, long=True, type='transform') or []

    if len(nodes) == 0:
        msg = 'Not enough objects selected, ' 'select at least 1 transform node.'
        LOG.warn(msg)
        return
    with tools_utils.tool_context(
        disable_viewport=True,
        use_undo_chunk=True,
        use_dg_evaluation_mode=False,
        restore_current_frame=False,
        pre_update_frame=False,
    ):
        tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]
        lib.reparent(tfm_nodes, None, sparse=True)
        nodes = [tn.get_node() for tn in tfm_nodes]
        maya.cmds.select(nodes, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return
