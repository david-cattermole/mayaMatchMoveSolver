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
Build the mmSolver Hotkey Set.
"""

import maya.mel
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def build_hotkey_set():
    """
    Create the 'mmSolver' Hotkey Set.
    """
    LOG.info('Building mmSolver Hotkey Set...')

    cmd = 'source "mmSolverCreateHotkeySet.mel";'
    maya.mel.eval(cmd)
    return
