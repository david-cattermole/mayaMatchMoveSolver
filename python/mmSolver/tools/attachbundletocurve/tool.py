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
Attach Bundle to Curve tool. Attaches a bundle node to a NURBs curve.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.attachbundletocurve.constant as const
import mmSolver.tools.attachbundletocurve.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Renames selected markers and bundles (and the connected nodes).
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    bnd_nodes = mmapi.filter_bundle_nodes(selection)
    crv_shp_nodes = lib.get_nurbs_curve_nodes(selection)
    if len(bnd_nodes) == 0 and len(crv_shp_nodes) != 1:
        msg = 'Please select at least one Bundle and only one NURBS curve.'
        LOG.warning(msg)
        return
    if len(bnd_nodes) > 0 and len(crv_shp_nodes) != 1:
        msg = 'Please select one NURBS curve.'
        LOG.warning(msg)
        return
    if len(bnd_nodes) == 0 and len(crv_shp_nodes) == 1:
        msg = 'Please select at least one Bundle.'
        LOG.warning(msg)
        return

    attr_name = const.ATTR_NAME
    crv_shp_node = crv_shp_nodes[0]
    for bnd_node in bnd_nodes:
        lib.attach_bundle_to_curve(bnd_node, crv_shp_node, attr_name)
    maya.cmds.select(bnd_nodes)
    return
