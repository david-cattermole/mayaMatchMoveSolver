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

from mmSolver.tools.imagecache._lib.initialize import initialize
from mmSolver.tools.imagecache._lib.query_resources import (
    get_gpu_memory_total_bytes,
    get_gpu_memory_used_bytes,
    get_cpu_memory_total_bytes,
    get_cpu_memory_used_bytes,
)
from mmSolver.tools.imagecache._lib.imagecache_cmd import (
    get_gpu_cache_item_count,
    get_cpu_cache_item_count,
    get_gpu_cache_group_names,
    get_cpu_cache_group_names,
    get_gpu_cache_slot_count,
    get_cpu_cache_slot_count,
    get_gpu_cache_group_item_count,
    get_cpu_cache_group_item_count,
    get_gpu_cache_group_item_names,
    get_cpu_cache_group_item_names,
    get_gpu_cache_used_bytes,
    get_cpu_cache_used_bytes,
    get_gpu_cache_capacity_bytes,
    get_cpu_cache_capacity_bytes,
    set_gpu_cache_capacity_bytes,
    set_cpu_cache_capacity_bytes,
)
from mmSolver.tools.imagecache._lib.erase import (
    erase_gpu_group_items,
    erase_cpu_group_items,
    erase_gpu_groups_items,
    erase_cpu_groups_items,
    erase_gpu_image_items,
    erase_cpu_image_items,
    erase_all_images_on_image_plane_slots,
    erase_images_in_active_image_plane_slot,
    erase_images_in_unused_image_plane_slots,
    erase_image_sequence,
    erase_all_inactive_images,
    erase_all_images,
)

# Stop users from accessing the internal functions of this sub-module.
__all__ = [
    'initialize',
    #
    'get_gpu_memory_total_bytes',
    'get_gpu_memory_used_bytes',
    'get_cpu_memory_total_bytes',
    'get_cpu_memory_used_bytes',
    #
    'get_gpu_cache_item_count',
    'get_cpu_cache_item_count',
    'get_gpu_cache_group_names',
    'get_cpu_cache_group_names',
    'get_gpu_cache_slot_count',
    'get_cpu_cache_slot_count',
    'get_gpu_cache_group_item_count',
    'get_cpu_cache_group_item_count',
    'get_gpu_cache_group_item_names',
    'get_cpu_cache_group_item_names',
    'get_gpu_cache_used_bytes',
    'get_cpu_cache_used_bytes',
    'get_gpu_cache_capacity_bytes',
    'get_cpu_cache_capacity_bytes',
    'set_gpu_cache_capacity_bytes',
    'set_cpu_cache_capacity_bytes',
    #
    'erase_gpu_group_items',
    'erase_cpu_group_items',
    'erase_gpu_groups_items',
    'erase_cpu_groups_items',
    'erase_gpu_image_items',
    'erase_cpu_image_items',
    'erase_all_images_on_image_plane_slots',
    'erase_images_in_active_image_plane_slot',
    'erase_images_in_unused_image_plane_slots',
    'erase_image_sequence',
    'erase_all_inactive_images',
    'erase_all_images',
]
