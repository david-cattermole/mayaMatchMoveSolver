# Copyright (C) 2019 Anil Reddy, David Cattermole.
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
This tool renames selected markers and bundles (and the connected nodes).
"""
import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.markerbundlerename.constant as const
import mmSolver.tools.markerbundlerename.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Renames selected markers and bundles (and the connected nodes).
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    sel_mkr_nodes = mmapi.filter_marker_nodes(selection)
    sel_bnd_nodes = mmapi.filter_bundle_nodes(selection)
    if len(sel_mkr_nodes) == 0 and len(sel_bnd_nodes) == 0:
        LOG.warning('Please select markers or bundles to rename.')
        return

    title = const.TITLE
    message = const.MESSAGE
    text = const.MARKER_NAME
    mkr_name = lib.prompt_for_new_node_name(title, message, text)
    if mkr_name is None:
        # If user clicks cancel on prompt window it returns None.
        LOG.warning('User canceled rename.')
        return

    number_format = const.NUMBER_FORMAT
    mkr_suffix = const.MARKER_SUFFIX
    bnd_suffix = const.BUNDLE_SUFFIX
    if mkr_name == text:
        bnd_name = const.BUNDLE_NAME
    else:
        bnd_name = mkr_name
    nodes = lib.rename_markers_and_bundles(
        sel_mkr_nodes,
        sel_bnd_nodes,
        mkr_name,
        bnd_name,
        number_format,
        mkr_suffix,
        bnd_suffix,
    )
    maya.cmds.select(nodes, replace=True)
    return
