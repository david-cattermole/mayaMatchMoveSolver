# Copyright (C) 2024 Patcha Saheb Binginapalli.
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

import mmSolver.tools.meshfrompoints.constant as const
import mmSolver.tools.meshfrompoints.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_selection():
    transform_nodes = maya.cmds.ls(selection=True, transforms=True) or []
    if len(transform_nodes) < 3:
        LOG.warn('Please select least three transform nodes.')
        return None
    return transform_nodes


def create_full_mesh():
    transform_nodes = _get_selection()
    if transform_nodes is None:
        return

    node = lib.create_mesh_from_transform_nodes(
        const.MESH_TYPE_FULL_MESH_VALUE, transform_nodes
    )

    if node is not None and maya.cmds.objExists(node):
        maya.cmds.select(node, replace=True)
    return


def create_border_mesh():
    transform_nodes = _get_selection()
    if transform_nodes is None:
        return

    node = lib.create_mesh_from_transform_nodes(
        const.MESH_TYPE_BORDER_MESH_VALUE, transform_nodes
    )

    if node is not None and maya.cmds.objExists(node):
        maya.cmds.select(node, replace=True)
    return


def main():
    """
    Open the 'Mesh From Points' window.
    """
    import mmSolver.tools.meshfrompoints.ui.meshfrompoints_window as window

    window.main()
