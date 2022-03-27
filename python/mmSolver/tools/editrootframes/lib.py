# Copyright (C) 2020 David Cattermole.
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
Library functions for editing the user frames defined
in the active Collection.

This module should not have any UI code.
"""

import mmSolver.logger
import mmSolver.ui.converttypes as convert_types
import mmSolver.tools.solver.lib.collectionstate as lib_col_state


LOG = mmSolver.logger.get_logger()


def get_user_frames_list(col):
    """
    Get the User Frames string, from the currently active Collection.

    :rtype: [int, ..] or None
    """
    if col is None:
        return None
    user_frames_str = lib_col_state.get_solver_user_frames_from_collection(col)
    if user_frames_str is None or len(user_frames_str) == 0:
        return None
    user_frames = convert_types.stringToIntList(user_frames_str)
    return user_frames


def set_user_frames_list(col, user_frames_list):
    """
    Set the User Frames on the currently active Collection.
    """
    if col is None:
        return None
    if user_frames_list is None:
        return None
    assert isinstance(user_frames_list, list)
    user_frames_string = convert_types.intListToString(user_frames_list)
    lib_col_state.set_solver_user_frames_on_collection(col, user_frames_string)
    return None
