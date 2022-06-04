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
This tool renames selected markers and bundles with the internal
metadata names stored on the markers.
"""
import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.markerbundlerenamewithmetadata.constant as const
import mmSolver.tools.markerbundlerenamewithmetadata.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    This tool renames selected markers and bundles with the internal
    metadata names stored on the markers.
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    sel_mkr_nodes = mmapi.filter_marker_nodes(selection)
    sel_bnd_nodes = mmapi.filter_bundle_nodes(selection)
    if len(sel_mkr_nodes) == 0 and len(sel_bnd_nodes) == 0:
        LOG.warning('Please select markers or bundles to rename.')
        return

    number_format = const.NUMBER_FORMAT
    mkr_prefix = const.MARKER_PREFIX
    mkr_suffix = const.MARKER_SUFFIX
    bnd_prefix = const.BUNDLE_PREFIX
    bnd_suffix = const.BUNDLE_SUFFIX
    nodes = lib.rename_markers_and_bundles_with_metadata(
        sel_mkr_nodes, sel_bnd_nodes, mkr_prefix, bnd_prefix, mkr_suffix, bnd_suffix
    )
    if len(nodes) == 0:
        maya.cmds.select(selection, replace=True)
    else:
        maya.cmds.select(nodes, replace=True)
    return
