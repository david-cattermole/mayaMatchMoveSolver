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
The Create Bundle tool.
"""

import warnings

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.linkmarkerbundle.lib as linkmarkerbundle_lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Create a new Bundle, attached to the selected Marker (if a Marker
    is selected)
    """
    sel = maya.cmds.ls(sl=True, long=True)
    mkr_nodes = mmapi.filter_marker_nodes(sel)

    bnd_name = mmapi.get_new_bundle_name('bundle1')
    bnd = mmapi.Bundle().create_node(name=bnd_name)

    bnd_node = bnd.get_node()
    for mkr_node in mkr_nodes:
        linkmarkerbundle_lib.link_marker_bundle(mkr_node, bnd_node)

    maya.cmds.select(bnd.get_node(), replace=True)
    return


def create_bundle():
    warnings.warn("Use 'main' function instead.", DeprecationWarning)
    main()
