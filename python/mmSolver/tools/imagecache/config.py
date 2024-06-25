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
import mmSolver.tools.imagecache.config_file as config_file
import mmSolver.tools.imagecache.config_scene as config_scene
import mmSolver.tools.createimageplane._lib.constant as imageplane_const


# Shorter alias.
_MM_IMAGE_PLANE_SHAPE_V2 = imageplane_const.MM_IMAGE_PLANE_SHAPE_V2


LOG = mmSolver.logger.get_logger()
CapacityData = collections.namedtuple(
    'CapacityData',
    [
        'gpu_default_capacity',
        'cpu_default_capacity',
        'scene_override',
        'gpu_scene_capacity',
        'cpu_scene_capacity',
        'gpu_resolved_capacity',
        'cpu_resolved_capacity',
    ],
)


def resolve_capacity_data():
    # Open Config file.
    default_gpu_capacity = config_file.get_gpu_capacity_percent()
    default_cpu_capacity = config_file.get_cpu_capacity_percent()

    # Check Maya scene options for image cache overrides.
    scene_override = config_scene.get_cache_scene_override()
    scene_gpu_capacity = config_scene.get_gpu_capacity_percent()
    scene_cpu_capacity = config_scene.get_cpu_capacity_percent()

    # Apply override to 'resolved' values.
    resolved_gpu_capacity = default_gpu_capacity
    resolved_cpu_capacity = default_cpu_capacity
    if scene_override is True:
        resolved_gpu_capacity = scene_gpu_capacity
        resolved_cpu_capacity = scene_cpu_capacity

    return CapacityData(
        default_gpu_capacity,
        default_cpu_capacity,
        scene_override,
        scene_gpu_capacity,
        scene_cpu_capacity,
        resolved_gpu_capacity,
        resolved_cpu_capacity,
    )
