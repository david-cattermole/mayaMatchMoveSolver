# Copyright (C) 2022 Patcha Saheb Binginapalli.
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

import maya.cmds

import mmSolver.logger
import mmSolver.utils.constant as const_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.createcontroller3.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform') or []
    if len(nodes) == 0:
        LOG.warn("Please select at least 1 transform.")
        return
    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()

    # Sort nodes by depth, deeper nodes first, so we do do not remove
    # parents before children.
    nodes = node_utils.sort_nodes_by_depth(nodes, reverse=True)

    # Channels to bake.
    attrs = lib._get_selected_channel_box_attrs()
    if len(attrs) == 0:
        attrs = lib.TRANSFORM_ATTRS

    baked_nodes = []
    ctx = tools_utils.tool_context(
        use_undo_chunk=True,
        restore_current_frame=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE)
    with ctx:
        for node in nodes:
            if maya.cmds.objExists(node) is False:
                continue
            baked_nodes += lib.remove_controller(
                node, start_frame, end_frame, attrs=attrs)
        maya.cmds.select(baked_nodes, replace=True)
    return
