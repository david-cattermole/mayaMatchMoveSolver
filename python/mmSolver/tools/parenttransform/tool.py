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
Mimic the parent and unparent tool in Maya.

.. todo:: Unlike the native Maya parent/unparent tools, this tool will
   maintain the world-space position for all keyframes across time.
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.parenttransform.lib as lib

import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def parent():
    """
    Parent selected nodes under the last selected node.
    """
    sel = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform') or []
    if len(sel) < 2:
        msg = 'Please select at least two objects.'
        LOG.warn(msg)
        return
    src_nodes = sel[:-1]
    dst_node = sel[-1]
    out_nodes = lib.parent(src_nodes, dst_node)
    maya.cmds.select(out_nodes, replace=True)
    return


def unparent():
    """
    Un-parent selected nodes into world space.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    if len(sel) == 0:
        msg = 'Please select at least one objects.'
        LOG.warn(msg)
        return
    out_nodes = lib.unparent(sel)
    maya.cmds.select(out_nodes, replace=True)
    return
