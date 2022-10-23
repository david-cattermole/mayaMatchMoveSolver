# Copyright (C) 2018 David Cattermole.
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
Provides a base interface for marker import plug-ins.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys


def float_is_equal(x, y):
    """
    Check the two float numbers match.

    :returns: True or False, if float is equal or not.
    :rtype: bool
    """
    # float equality
    if x == y:
        return True

    # float equality, with an epsilon
    eps = sys.float_info.epsilon * 100.0
    if x < (y + eps) and x > (y - eps):
        return True

    # string equality, with nine decimal places.
    x_str = '%.9f' % float(x)
    y_str = '%.9f' % float(y)
    if x_str == y_str:
        return True

    return False


def get_closest_frame(frame, value):
    """
    Get the closest frame in the dictionary value.

    :param frame: An int for the frame to look up.
    :param value: A dict with keys as the frames to look up.

    Returns the closest frame in the dict value.
    """
    keys = value.keys()
    int_keys = list()
    for key in keys:
        int_keys.append(int(key))
    keys = sorted(int_keys)
    diff = int()
    closest_frame = None
    for key in keys:
        if closest_frame is None:
            closest_frame = key
            diff = frame - closest_frame
        if (key <= frame) and (key > closest_frame):
            closest_frame = key
        diff = closest_frame - frame
    keys.reverse()
    closest_frame_rev = None
    for key in keys:
        if closest_frame_rev is None:
            closest_frame_rev = key
            diff = frame - closest_frame_rev
        if (key >= frame) and (key < closest_frame_rev):
            closest_frame_rev = key
        diff = closest_frame_rev - frame
    diffRef = abs(closest_frame_rev - frame)
    diff = abs(closest_frame - frame)
    if diffRef < diff:
        closest_frame = closest_frame_rev
    return closest_frame
