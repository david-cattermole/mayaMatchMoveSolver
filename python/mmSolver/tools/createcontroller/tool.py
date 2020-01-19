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
Create a controller transform node.

Usage::

  1) Select transform node.

  2) Run 'create' tool, new world-space transform is created at same
     position as input transform nodes.

  3) New nodes are selected.

  4) User manipulates newly created nodes.

  5) Run 'bake' tool, selected transform nodes are deleted and
      animation is transfered back onto original nodes.

Ideas::

  - Have a flag to allow maintaining the relative hierarchy of the
    input transforms.

"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.viewport as viewport
import mmSolver.tools.createcontroller.lib as lib


LOG = mmSolver.logger.get_logger()


def create():
    """
    Create a controller for selected nodes.
    """
    nodes = maya.cmds.ls(selection=True, long=True) or []
    frame = maya.cmds.currentTime(query=True)
    try:
        viewport.viewport_turn_off()
        ctrls = lib.create(nodes)
        if len(ctrls) > 0:
            maya.cmds.select(ctrls, replace=True)
    finally:
        viewport.viewport_turn_on()
    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, edit=True, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return


def remove():
    """
    Remove selected controllers and bake data on controlled nodes.
    """
    nodes = maya.cmds.ls(selection=True, long=True) or []
    frame = maya.cmds.currentTime(query=True)
    try:
        viewport.viewport_turn_off()
        orig_nodes = lib.remove(nodes)
        if len(orig_nodes) > 0:
            maya.cmds.select(orig_nodes, replace=True)
    finally:
        viewport.viewport_turn_on()
    # Trigger Maya to refresh.
    maya.cmds.currentTime(frame, edit=True, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return
