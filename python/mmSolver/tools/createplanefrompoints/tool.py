# Copyright (C) 2024 David Cattermole.
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
Mesh From Points main.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger

import mmSolver.tools.createplanefrompoints.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_selection():
    transform_nodes = maya.cmds.ls(selection=True, transforms=True) or []
    if len(transform_nodes) < 3:
        LOG.warn('Please select least three transform nodes.')
        return None
    return transform_nodes


def main():
    transform_nodes = _get_selection()
    if transform_nodes is None:
        return

    world_points = lib.convert_transform_nodes_to_3d_points(transform_nodes)

    node = lib.create_plane_from_points(world_points)
    if node is None:
        LOG.error('Could not calculate best fit plane matrix from 3D points.')
        return

    if node is not None and maya.cmds.objExists(node):
        maya.cmds.select(node, replace=True)
    return
