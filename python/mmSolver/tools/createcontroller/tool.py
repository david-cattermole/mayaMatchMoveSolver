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

import mmSolver.tools.createcontroller.lib as lib


def create():
    nodes = maya.cmds.ls(selection=True, long=True) or []
    ctrls = lib.create(nodes, sparse=True)
    if len(ctrls) > 0:
        maya.cmds.select(ctrls, replace=True)
    # Trigger Maya to refresh.
    frame = maya.cmds.currentTime(query=True)
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return


def remove():
    nodes = maya.cmds.ls(selection=True, long=True) or []
    orig_nodes = lib.remove(nodes)
    if len(orig_nodes) > 0:
        maya.cmds.select(orig_nodes, replace=True)
    # Trigger Maya to refresh.
    frame = maya.cmds.currentTime(query=True)
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)
    return
