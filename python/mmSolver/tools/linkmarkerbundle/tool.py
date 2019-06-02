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
The 'Link / Unlink Marker Bundles' tool.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.linkmarkerbundle.lib as lib


LOG = mmSolver.logger.get_logger()


def link_marker_bundle():
    """
    Select a marker node, and a bundle node, run to link both nodes.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    mkr_nodes = filternodes.get_marker_nodes(sel)
    bnd_nodes = filternodes.get_bundle_nodes(sel)

    if len(mkr_nodes) != 1 and len(bnd_nodes) != 1:
        msg = 'Please select only one Marker and one Bundle.'
        LOG.warning(msg)
        return
    if len(mkr_nodes) != 1:
        msg = 'Please select only one Marker.'
        LOG.warning(msg)
    if len(bnd_nodes) != 1:
        msg = 'Please select only one Bundle.'
        LOG.warning(msg)
    if len(mkr_nodes) != 1 or len(bnd_nodes) != 1:
        return

    lib.link_marker_bundle(mkr_nodes[0], bnd_nodes[0])
    return


def unlink_marker_bundle():
    """
    All selected markers are disconnected from their respective bundle.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    mkr_nodes = filternodes.get_marker_nodes(sel)

    if len(mkr_nodes) == 0:
        msg = 'Please select one or more Markers.'
        LOG.warning(msg)
        return

    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(node=mkr_node)
        mkr.set_bundle(None)
    return
