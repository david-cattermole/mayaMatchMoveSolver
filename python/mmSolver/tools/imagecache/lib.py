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

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


CACHE_TYPE_ALL = 'all'
CACHE_TYPE_GPU = 'gpu'
CACHE_TYPE_CPU = 'cpu'
CACHE_TYPE_VALUES = [
    CACHE_TYPE_ALL,
    CACHE_TYPE_GPU,
    CACHE_TYPE_CPU,
]


def cache_remove_image_plane_contents(cache_type):
    pass


def cache_remove_image_sequence(file_pattern, start_frame, end_frame, cache_type):
    pass


def cache_remove_all(cache_type):
    pass


def cache_remove_all_inactive(cache_type):
    # Removes all the items in the cache that cannot be 'reached' by
    # any of the image planes.
    pass


def function():
    pass
