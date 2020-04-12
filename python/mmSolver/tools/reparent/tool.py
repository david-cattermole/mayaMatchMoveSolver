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
import mmSolver.utils.viewport as viewport
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent.lib as lib

LOG = mmSolver.logger.get_logger()


def reparent_under_node():
    """
    Re-parent the selection under the last selected node.
    """
    frame = maya.cmds.currentTime(query=True)
    nodes = maya.cmds.ls(selection=True, long=True,
                         type='transform') or []
    current_eval_manager_mode = maya.cmds.evaluationManager(
        query=True,
        mode=True
    )

    if len(nodes) < 2:
        msg = ('Not enough objects selected, '
               'select at least 1 child and 1 parent node.')
        LOG.warn(msg)
        return
    try:
        viewport.viewport_turn_off()

        # Force DG mode, because it evaluates with DG Context faster
        # (in Maya 2017).
        #
        # TODO: Test that DG mode is actually faster in Maya versions
        # other than 2017.
        maya.cmds.evaluationManager(mode='off')

        children = nodes[:-1]
        parent = nodes[-1]
        children_tfm_nodes = [tfm_utils.TransformNode(node=n) for n in children]
        parent_tfm_node = tfm_utils.TransformNode(node=parent)
        lib.reparent(children_tfm_nodes, parent_tfm_node, sparse=True)
        children = [tn.get_node() for tn in children_tfm_nodes]
        maya.cmds.select(children, replace=True)
    finally:
        maya.cmds.evaluationManager(
            mode=current_eval_manager_mode[0]
        )
        viewport.viewport_turn_on()
    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return


def unparent_to_world():
    """
    Un-parent the selected nodes into world space.
    """
    frame = maya.cmds.currentTime(query=True)
    nodes = maya.cmds.ls(selection=True, long=True,
                         type='transform') or []
    current_eval_manager_mode = maya.cmds.evaluationManager(
        query=True,
        mode=True
    )

    if len(nodes) == 0:
        msg = ('Not enough objects selected, '
               'select at least 1 transform node.')
        LOG.warn(msg)
        return
    try:
        viewport.viewport_turn_off()

        # Force DG mode, because it evaluates with DG Context faster
        # (in Maya 2017).
        #
        # TODO: Test that DG mode is actually faster in Maya versions
        # other than 2017.
        maya.cmds.evaluationManager(mode='off')

        tfm_nodes = [tfm_utils.TransformNode(node=n) for n in nodes]
        lib.reparent(tfm_nodes, None, sparse=True)
        nodes = [tn.get_node() for tn in tfm_nodes]
        maya.cmds.select(nodes, replace=True)
    finally:
        maya.cmds.evaluationManager(
            mode=current_eval_manager_mode[0]
        )
        viewport.viewport_turn_on()

    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return
