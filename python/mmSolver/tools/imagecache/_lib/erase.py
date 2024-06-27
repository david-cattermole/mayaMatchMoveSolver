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

import maya.cmds

import mmSolver.logger
import mmSolver.tools.imagecache.constant as const
import mmSolver.tools.imagecache._lib.imagecache_cmd as imagecache_cmd
import mmSolver.tools.createimageplane._lib.constant as imageplane_const
import mmSolver.tools.createimageplane._lib.mmimageplane_v2 as imageplane_lib

LOG = mmSolver.logger.get_logger()

# Shorter alias.
_IMAGE_PLANE_SHAPE = imageplane_const.MM_IMAGE_PLANE_SHAPE_V2


def _make_group_name_consistent(group_name):
    assert isinstance(group_name, str)
    assert len(group_name) > 0

    # The ImageCache stores all file paths with UNIX
    # forward-slashes convention.
    group_name = group_name.replace('\\', '/')

    return group_name


def erase_gpu_group_items(group_name):
    assert isinstance(group_name, str)
    assert len(group_name) > 0
    group_name = _make_group_name_consistent(group_name)
    return maya.cmds.mmImageCache([group_name], edit=True, gpuEraseGroupItems=True)


def erase_cpu_group_items(group_name):
    assert isinstance(group_name, str)
    assert len(group_name) > 0
    group_name = _make_group_name_consistent(group_name)
    return maya.cmds.mmImageCache([group_name], edit=True, cpuEraseGroupItems=True)


def erase_gpu_groups_items(group_names):
    assert len(group_names) >= 0
    group_names = [_make_group_name_consistent(x) for x in group_names]
    return maya.cmds.mmImageCache(group_names, edit=True, gpuEraseGroupItems=True)


def erase_cpu_groups_items(group_names):
    assert len(group_names) >= 0
    group_names = [_make_group_name_consistent(x) for x in group_names]
    return maya.cmds.mmImageCache(group_names, edit=True, cpuEraseGroupItems=True)


def erase_gpu_image_items(items):
    assert len(items) >= 0
    return maya.cmds.mmImageCache(items, edit=True, gpuEraseItems=True)


def erase_cpu_image_items(items):
    assert len(items) >= 0
    return maya.cmds.mmImageCache(items, edit=True, cpuEraseItems=True)


def erase_all_images_on_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _IMAGE_PLANE_SHAPE
    LOG.info(
        'erase_all_images_on_image_plane_slots: cache_type=%r, image_plane_shp=%r',
        cache_type,
        image_plane_shp,
    )

    slots = imageplane_lib.get_image_sequence_for_all_slots(image_plane_shp)
    LOG.info('erase_all_images_on_image_plane_slots: slots=%r', slots)

    group_names = None
    if cache_type == const.CACHE_TYPE_GPU:
        group_names = imagecache_cmd.get_gpu_cache_group_names()
    elif cache_type == const.CACHE_TYPE_CPU:
        group_names = imagecache_cmd.get_cpu_cache_group_names()
    assert group_names is not None

    slots_to_erase = []
    for slot in slots:
        if slot not in group_names:
            LOG.warn('Slot not found in groups: group_names=%r', group_names)
            continue
        slots_to_erase.append(slot)

    if cache_type == const.CACHE_TYPE_GPU:
        return erase_gpu_groups_items(slots_to_erase)
    elif cache_type == const.CACHE_TYPE_CPU:
        return erase_cpu_groups_items(slots_to_erase)
    assert False


def erase_images_in_active_image_plane_slot(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _IMAGE_PLANE_SHAPE
    LOG.info(
        'erase_images_in_active_image_plane_slot: cache_type=%r, image_plane_shp=%r',
        cache_type,
        image_plane_shp,
    )

    slot = imageplane_lib.get_image_sequence_for_active_slot(image_plane_shp)
    LOG.info('erase_images_in_active_image_plane_slot: slot=%r', slot)

    return


def erase_images_in_unused_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _IMAGE_PLANE_SHAPE
    LOG.info(
        'erase_images_in_unused_image_plane_slots: cache_type=%r, image_plane_shp=%r',
        cache_type,
        image_plane_shp,
    )
    slots = imageplane_lib.get_image_sequence_for_unused_slots(image_plane_shp)
    LOG.info('erase_images_in_unused_image_plane_slots: slots=%r', slots)
    return


def erase_image_sequence(cache_type, file_pattern, start_frame, end_frame):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert isinstance(file_pattern, str)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    LOG.info(
        'erase_image_sequence: '
        'cache_type=%r, file_pattern=%r, start_frame=%r, end_frame=%r',
        cache_type,
        file_pattern,
        start_frame,
        end_frame,
    )

    item_count = None
    if cache_type == const.CACHE_TYPE_GPU:
        item_count = imagecache_cmd.get_gpu_cache_group_item_count(file_pattern)
    elif cache_type == const.CACHE_TYPE_CPU:
        item_count = imagecache_cmd.get_cpu_cache_group_item_count(file_pattern)
    assert item_count is not None

    if item_count == 0:
        LOG.warn('File pattern does not have any items. item_count=%r', item_count)
        return

    item_names = imagecache_cmd.get_gpu_group_item_names(cache_type, file_pattern)
    assert len(item_names) > 0

    # TODO:
    #
    # 1) Evaluate the file_pattern for start_frame to end_frame.
    #
    # 2) If the evaluated file path is in the image cache, add it to
    #    the list to be removed.
    #
    # 3) Remove named items from the cache.

    raise NotImplementedError


def erase_all_inactive_images(cache_type):
    assert cache_type in const.CACHE_TYPE_VALUES
    # Removes all the items in the cache that cannot be 'reached' by
    # any of the image planes.
    LOG.info(
        'erase_all_inactive_images: cache_type=%r',
        cache_type,
    )

    # TODO:
    #
    # 1) Get all image planes.
    #
    # 2) Get all active slots on all image planes.
    #
    # 3) Get all groups in the image cache.
    #
    # 4) For any group that is not in the active slots, remove it.

    raise NotImplementedError


def erase_all_images(cache_type):
    assert cache_type in const.CACHE_TYPE_VALUES
    LOG.info(
        'erase_images_in_unused_image_plane_slots: cache_type=%r',
        cache_type,
    )

    # TODO: Clear image cache completely.

    # 1) Get the ImageCache capacities (CPU and GPU).
    # 2) Set the ImageCache capacity (CPU and GPU) to zero.
    # 3) Restore the ImageCache capacities (CPU and GPU).

    return
