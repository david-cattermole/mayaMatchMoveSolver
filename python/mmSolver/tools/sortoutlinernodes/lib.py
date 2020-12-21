# Copyright (C) 2020 David Cattermole.
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
Sort nodes alphabetically.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.sort as sort

LOG = mmSolver.logger.get_logger()


def sort_nodes(nodes):
    """
    Sort the list of nodes.

    .. note:: The nodes are expected to be full-paths to nodes.
    """
    sorted_nodes = sort.sort_strings_with_digits(nodes)
    for node in sorted_nodes:
        maya.cmds.reorder(node, back=True)
    return
