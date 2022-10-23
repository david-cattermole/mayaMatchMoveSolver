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
Toggle the visibility of motion trails on selected objects.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.tools.toggleobjectmotiontrail.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggle motion trails on the selected transform nodes.
    """
    tfm_nodes = maya.cmds.ls(sl=True, long=True, type='transform') or []
    if len(tfm_nodes) == 0:
        LOG.warn('Please select transform nodes.')
        return

    lib.motion_trails_lock_toggle(tfm_nodes)
    maya.cmds.select(tfm_nodes, replace=True)
    return
