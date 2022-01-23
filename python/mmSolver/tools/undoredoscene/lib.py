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
Library functions for undo/redo.

This module should not have any UI code.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.viewport as viewport


LOG = mmSolver.logger.get_logger()


def undo():
    try:
        if maya.cmds.about(apiVersion=True) >= 201700:
            viewport.set_viewport2_active_state(False)
        else:
            viewport.viewport1_turn_off()
        undo_state = maya.cmds.undoInfo(query=True, state=True)
        if undo_state is True:
            maya.cmds.undo()
    finally:
        if maya.cmds.about(apiVersion=True) >= 201700:
            viewport.set_viewport2_active_state(True)
        else:
            viewport.viewport1_turn_on()
    return


def redo():
    try:
        if maya.cmds.about(apiVersion=True) >= 201700:
            viewport.set_viewport2_active_state(False)
        else:
            viewport.viewport1_turn_off()
        undo_state = maya.cmds.undoInfo(query=True, state=True)
        if undo_state is True:
            maya.cmds.redo()
    finally:
        if maya.cmds.about(apiVersion=True) >= 201700:
            viewport.set_viewport2_active_state(True)
        else:
            viewport.viewport1_turn_on()
    return
