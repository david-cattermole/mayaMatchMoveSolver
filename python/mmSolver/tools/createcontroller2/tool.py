# Copyright (C) 2021 Patcha Saheb Binginapalli.
# Copyright (C) 2022 David Cattermole.

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

import maya.cmds

import mmSolver.logger

import mmSolver.utils.time as time_utils
import mmSolver.utils.constant as const_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.createcontroller2.constant as const
import mmSolver.tools.createcontroller2.lib as lib


LOG = mmSolver.logger.get_logger()


def create_world_controllers():
    """
    Create controllers for all selected nodes.

    Usage::

      1) Select transform node(s).

      2) Run 'create_world_controllers' tool, new world-space
         transform is created at same position as input transform
         nodes.

      3) New nodes are selected.

      4) User manipulates newly created nodes.

      5) Run 'remove_controllers' tool, selected transform nodes are
          deleted and animation is transfered back onto original
          nodes.

    This is to provide a simple tool to select many nodes and create
    (world-space) controllers for each node. The user may then do
    whatever is needed to transform and re-parent the controllers.

    :rtype: None
    """
    nodes = maya.cmds.ls(selection=True, long=True) or []
    if len(nodes) == 0:
        LOG.warn('Please select transform nodes.')
        return

    start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
    controller_type = const.CONTROLLER_SPACE_WORLD
    smart_bake = False
    dynamic_pivot = False
    camera = None

    ctrl_nodes = []
    with tools_utils.tool_context(
        use_undo_chunk=True,
        pre_update_frame=True,
        post_update_frame=True,
        restore_current_frame=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
    ):

        for node in nodes:
            name_tfm = '{}_CTRL'.format(node.rpartition('|')[-1])

            # This node is used as the controller.
            loc_grp_nodes = maya.cmds.spaceLocator(name=name_tfm)

            pivot_node = node
            main_node = node
            ctrl_node = lib.create_controller(
                name_tfm,
                pivot_node,
                main_node,
                loc_grp_nodes,
                start_frame,
                end_frame,
                controller_type,
                smart_bake=smart_bake,
                camera=camera,
                dynamic_pivot=dynamic_pivot,
            )
            if ctrl_node and maya.cmds.objExists(ctrl_node[0]):
                ctrl_nodes.append(ctrl_node[0])

    if len(ctrl_nodes) > 0:
        maya.cmds.select(ctrl_nodes, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.refresh(currentView=True, force=False)
    return


def open_window():
    import mmSolver.tools.createcontroller2.ui.createcontroller_window as window

    window.main()
