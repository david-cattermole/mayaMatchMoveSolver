# Copyright (C) 2024 David Cattermole.
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
Functions to control the image cache.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import mmSolver.logger

LOG = mmSolver.logger.get_logger()
CapacityValue = collections.namedtuple('CapacityValue', ['size_bytes', 'percent'])


def convert_to_capacity_value(percent, total_bytes):
    assert isinstance(percent, float)
    ratio = percent / 100.0
    size_bytes = int(total_bytes * ratio)
    return CapacityValue(size_bytes, percent)
