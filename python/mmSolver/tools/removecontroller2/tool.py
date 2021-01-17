# Copyright (C) 2021 Patcha Saheb Binginapalli.
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

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.tools.createcontroller2.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    selection = maya.cmds.ls(selection=True)
    if not len(selection) == 1:
        LOG.warn("Please select only one controller.")
        return
    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
    lib.remove_controller(selection[0], start_frame, end_frame)

