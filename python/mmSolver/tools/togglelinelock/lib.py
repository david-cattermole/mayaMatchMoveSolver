# Copyright (C) 2022 David Cattermole.
# Copyright (C) 2019 Anil Reddy.
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
This tool toggles selected line lock state
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.togglelinelock.constant as const

LOG = mmSolver.logger.get_logger()


def get_line_attrs(line_nodes):
    """
    Get the Line attributes to lock/unlock.
    """
    node_attrs = []
    for line_node in line_nodes:
        for attr_name in const.LINE_ATTRS:
            node_attr = '{}.{}'.format(line_node, attr_name)
            node_attrs.append(node_attr)

        line = mmapi.Line(node=line_node)
        mkr_list = line.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            for attr_name in const.MARKER_ATTRS:
                node_attr = '{}.{}'.format(mkr_node, attr_name)
                node_attrs.append(node_attr)
    return node_attrs


def lines_lock_toggle(line_nodes):
    """
    Performs a toggle lock for the given Line nodes.
    """
    line_node_attrs = get_line_attrs(line_nodes)

    # Determine the lock state to toggle.
    is_locked = False
    for node_attr in line_node_attrs:
        if maya.cmds.getAttr(node_attr, lock=True):
            is_locked = True

    # Lock the Line attributes.
    lock_value = not is_locked
    lines_lock_set(line_nodes, lock_value)
    return


def lines_lock_set(line_nodes, lock_value):
    """
    Set the lock value for the given Line nodes.
    """
    line_node_attrs = get_line_attrs(line_nodes)

    # Lock the Line attributes.
    for node_attr in line_node_attrs:
        maya.cmds.setAttr(node_attr, lock=lock_value)
    return
