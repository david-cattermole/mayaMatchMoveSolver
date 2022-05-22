# Copyright (C) 2020 Kazuma Tonegawa.
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
Remove Solver Nodes - user facing.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import maya.cmds as cmds


LOG = mmSolver.logger.get_logger()


def main():
    """
    Open the 'Remove Solver Nodes' window.
    """
    import mmSolver.tools.removesolvernodes.ui.removesolvernodes_window as window
    window.main()
