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
User facing root frame navigation functions.

This function may be called in a UI context.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.ui.converttypes as convert_types
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.navigaterootframes.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_root_frames_string():
    """
    Get the Root Frames string, from the currently active Collection.

    Not to be called by users, used internally only.

    :rtype: str or None
    """
    col = lib_state.get_active_collection()
    if col is None:
        return None
    root_frames_str = lib_col_state.get_solver_root_frames_from_collection(col)
    if root_frames_str is None or len(root_frames_str) == 0:
        return None
    return root_frames_str


def _get_next_frame():
    """
    Get the next frame number from Root Frames.

    :rtype: int or None
    """
    root_frames_str = _get_root_frames_string()
    if root_frames_str is None:
        return None
    int_list = convert_types.stringToIntList(root_frames_str)
    if len(int_list) == 0:
        return None
    cur_frame = maya.cmds.currentTime(query=True)
    frame = lib.get_next_frame(cur_frame, int_list)
    return frame


def _get_prev_frame():
    """
    Get the previous frame number from Root Frames.

    :rtype: int or None
    """
    root_frames_str = _get_root_frames_string()
    if root_frames_str is None:
        return None
    int_list = convert_types.stringToIntList(root_frames_str)
    if len(int_list) == 0:
        return None
    cur_frame = maya.cmds.currentTime(query=True)
    frame = lib.get_prev_frame(cur_frame, int_list)
    return frame


def main_next_frame():
    """
    Move the current time to the next root frame.

    If no Root Frames are available, use Maya's native "Next Keyframe"
    tool.
    """
    frame = _get_next_frame()
    if frame is None:
        frame = lib.get_next_frame_maya()
    maya.cmds.currentTime(frame, edit=True)
    return


def main_prev_frame():
    """
    Move the current time to the previous root frame.

    If no Root Frames are available, use Maya's native "Previous Keyframe"
    tool.
    """
    frame = _get_prev_frame()
    if frame is None:
        frame = lib.get_prev_frame_maya()
    maya.cmds.currentTime(frame, edit=True)
    return
