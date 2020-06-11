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
Library functions for navigating the root frames defined
in the active Collection.

This module should not have any UI code.
"""

import maya.cmds

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def get_next_frame_maya():
    """
    Get the next keyframe from the timeslider.

    This function uses the current Maya scene state, for example
    selection and current frame.
    
    :rtype: int
    """
    frame = maya.cmds.findKeyframe(timeSlider=True, which='next')
    return frame


def get_prev_frame_maya():
    """
    Get the previous keyframe from the timeslider.

    This function uses the current Maya scene state, for example
    selection and current frame.
    
    :rtype: int
    """
    frame = maya.cmds.findKeyframe(timeSlider=True, which='previous')
    return frame


def get_next_frame(cur_frame, int_list):
    """
    Get the next frame in the frame number sequence given.
    
    :param cur_frame: The current time number.
    :type cur_frame: int or float

    :param int_list: The frames number sequence as a list.
    :type int_list: [int, ..]

    :returns: The next frame number, or None if no next frame can be 
              found.
    :rtype: int or None
    """
    assert isinstance(int_list, (list, tuple))
    assert isinstance(cur_frame, (float, int, long))
    future_frames = [int(f) for f in int_list
                     if float(f) > float(cur_frame)]
    future_frames = list(sorted(future_frames))
    next_frame = cur_frame
    if len(future_frames) == 0:
        if len(int_list) > 0:
            # Wrap-around the frame values.
            next_frame = list(sorted(int_list))[0]
        else:
            next_frame = None
    else:
        # The next future frame.
        next_frame = future_frames[0]
    return next_frame


def get_prev_frame(cur_frame, int_list):
    """
    Get the previous frame in the frame number sequence given.
    
    :param cur_frame: The current time number.
    :type cur_frame: int or float

    :param int_list: The frames number sequence as a list.
    :type int_list: [int, ..]

    :returns: The previous frame number, or None if no previous frame 
              can be found.
    :rtype: int or None
    """
    assert isinstance(int_list, (list, tuple))
    assert isinstance(cur_frame, (float, int, long))
    past_frames = [f for f in int_list
                   if float(f) < float(cur_frame)]
    past_frames = list(sorted(past_frames))
    previous_frame = cur_frame
    if len(past_frames) == 0:
        if len(int_list) > 0:
            # Wrap-around the frame values.
            previous_frame = list(sorted(int_list))[-1]
        else:
            previous_frame = None
    else:
        # The last previous frame.
        previous_frame = past_frames[-1]
    return previous_frame

