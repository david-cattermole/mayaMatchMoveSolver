# Copyright (C) 2021 David Cattermole, Kazuma Tonegawa.
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
Extra mathematical functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def lerp(min_value, max_value, mix):
    """
    Return 'min_value' to 'max_value' linearly, for a 'mix' value
    between 0.0 and 1.0.

    :type min_value: float
    :type max_value: float
    :type mix: float

    :rtype: float
    """
    return (1.0 - mix) * min_value + mix * max_value


def inverse_lerp(min_value, max_value, mix):
    """
    Return 0.0 to 1.0 linearly, for a 'mix' value between 'min_value'
    and 'max_value'.

    :type min_value: float
    :type max_value: float
    :type mix: float

    :rtype: float
    """
    return (mix - min_value) / (max_value - min_value)


def remap(old_min, old_max, new_min, new_max, mix):
    """
    Remap from the 'old_*' values to 'new_*' values, using a 'mix'
    value between 0.0 and 1.0;

    :type old_min: float
    :type old_max: float
    :type new_min: float
    :type new_max: float
    :type mix: float

    :rtype: float
    """
    blend = inverse_lerp(old_min, old_max, mix)
    return lerp(new_min, new_max, blend)
