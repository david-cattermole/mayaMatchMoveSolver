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
Disable Hold-Outs for selected meshes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds as cmds
import mmSolver.logger
import mmSolver.tools.holdoutsenableselectedmeshes.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Disable Hold-Outs for all meshes.
    """
    all_meshes = cmds.ls(dag=True, type="mesh") or []
    if not all_meshes:
        LOG.warn("Mesh not found.")
        return
    lib.set_holdout(all_meshes, False)
