# Copyright (C) 2022 David Cattermole.
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
Functions for sub-dividing a line with more markers.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def subdivide_line(line):
    """
    Set the lock value for the given Marker nodes.
    """
    mkr_list = line.get_marker_list()
    num_mkrs = len(mkr_list)

    sel = []
    new_mkr_list = []
    line_tfm = line.get_node()
    mkr_grp = line.get_marker_group()
    if num_mkrs == 0:
        mkr_name_a = mmapi.get_new_marker_name('marker1')
        mkr_a = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_a)
        mkr_name_b = mmapi.get_new_marker_name('marker1')
        mkr_b = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_b)
        new_mkr_list = [mkr_a, mkr_b]

        mkr_node_a = mkr_a.get_node()
        mkr_node_b = mkr_b.get_node()
        maya.cmds.setAttr(mkr_node_a + '.tx', -0.25)
        maya.cmds.setAttr(mkr_node_b + '.tx', 0.25)
        maya.cmds.setAttr(mkr_node_a + '.ty', -0.15)
        maya.cmds.setAttr(mkr_node_b + '.ty', 0.15)
        sel = [mkr_a, mkr_b]

    elif num_mkrs == 2:
        mkr_name_b = mmapi.get_new_marker_name('marker1')
        mkr_a = mkr_list[0]
        mkr_b = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_b)
        mkr_c = mkr_list[1]
        new_mkr_list = [mkr_a, mkr_b, mkr_c]

        mkr_node_a = mkr_a.get_node()
        mkr_node_b = mkr_b.get_node()
        mkr_node_c = mkr_c.get_node()

        tx_b = maya.cmds.getAttr(mkr_node_a + '.tx')
        tx_b += maya.cmds.getAttr(mkr_node_c + '.tx')
        tx_b = tx_b * 0.5

        ty_b = maya.cmds.getAttr(mkr_node_a + '.ty')
        ty_b += maya.cmds.getAttr(mkr_node_c + '.ty')
        ty_b = ty_b * 0.5

        maya.cmds.setAttr(mkr_node_b + '.tx', tx_b)
        maya.cmds.setAttr(mkr_node_b + '.ty', ty_b)
        maya.cmds.parent(mkr_node_b, line_tfm, relative=True)
        sel = [mkr_b]

    elif num_mkrs == 3:
        mkr_a = mkr_list[0]
        mkr_name_b = mmapi.get_new_marker_name('marker1')
        mkr_b = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_b)
        mkr_c = mkr_list[1]
        mkr_name_d = mmapi.get_new_marker_name('marker1')
        mkr_d = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_d)
        mkr_e = mkr_list[2]
        new_mkr_list = [mkr_a, mkr_b, mkr_c, mkr_d, mkr_e]

        mkr_node_a = mkr_a.get_node()
        mkr_node_b = mkr_b.get_node()
        mkr_node_c = mkr_c.get_node()
        mkr_node_d = mkr_d.get_node()
        mkr_node_e = mkr_e.get_node()

        tx_b = maya.cmds.getAttr(mkr_node_a + '.tx')
        tx_b += maya.cmds.getAttr(mkr_node_c + '.tx')
        tx_b = tx_b * 0.5

        ty_b = maya.cmds.getAttr(mkr_node_a + '.ty')
        ty_b += maya.cmds.getAttr(mkr_node_c + '.ty')
        ty_b = ty_b * 0.5

        tx_d = maya.cmds.getAttr(mkr_node_c + '.tx')
        tx_d += maya.cmds.getAttr(mkr_node_e + '.tx')
        tx_d = tx_d * 0.5

        ty_d = maya.cmds.getAttr(mkr_node_c + '.ty')
        ty_d += maya.cmds.getAttr(mkr_node_e + '.ty')
        ty_d = ty_d * 0.5

        maya.cmds.setAttr(mkr_node_b + '.tx', tx_b)
        maya.cmds.setAttr(mkr_node_b + '.ty', ty_b)
        maya.cmds.setAttr(mkr_node_d + '.tx', tx_d)
        maya.cmds.setAttr(mkr_node_d + '.ty', ty_d)
        maya.cmds.parent(mkr_node_b, line_tfm, relative=True)
        maya.cmds.parent(mkr_node_d, line_tfm, relative=True)
        sel = [mkr_b, mkr_d]

    else:
        LOG.warn('Not supported yet.')

    line.set_marker_list(new_mkr_list)
    return sel
