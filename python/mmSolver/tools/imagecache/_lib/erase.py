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
import mmSolver.utils.imageseq as imageseq_utils
import mmSolver.utils.constant as const_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.imagecache.constant as const
import mmSolver.tools.imagecache._lib.imagecache_cmd as imagecache_cmd
import mmSolver.tools.createimageplane._lib.constant as imageplane_const
import mmSolver.tools.createimageplane._lib.mmimageplane_v2 as imageplane_lib

LOG = mmSolver.logger.get_logger()

# Shorter alias.
_IMAGE_PLANE_SHAPE = imageplane_const.MM_IMAGE_PLANE_SHAPE_V2


def _make_group_name_consistent(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0

    # The ImageCache stores all file paths with UNIX
    # forward-slashes convention.
    group_name = group_name.replace('\\', '/')

    return group_name


def erase_gpu_group_items(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0
    group_name = _make_group_name_consistent(group_name)
    return maya.cmds.mmImageCache([group_name], edit=True, gpuEraseGroupItems=True)


def erase_cpu_group_items(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
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


def erase_all_images_on_image_plane_slots(cache_type, shape_node):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(shape_node) == _IMAGE_PLANE_SHAPE

    file_patterns = imageplane_lib.get_file_pattern_for_all_slots(shape_node)
    file_patterns = [
        x for x in file_patterns if isinstance(x, pycompat.TEXT_TYPE) and len(x) > 0
    ]
    if len(file_patterns) == 0:
        LOG.warn('mmImagePlane unused slots are all invalid; node=%r', shape_node)
        return

    if cache_type == const.CACHE_TYPE_GPU:
        return erase_gpu_groups_items(file_patterns)
    elif cache_type == const.CACHE_TYPE_CPU:
        return erase_cpu_groups_items(file_patterns)
    assert False


def erase_images_in_active_image_plane_slot(cache_type, shape_node):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(shape_node) == _IMAGE_PLANE_SHAPE

    file_pattern = imageplane_lib.get_file_pattern_for_active_slot(shape_node)
    if file_pattern is None or len(file_pattern) == 0:
        LOG.warn('mmImagePlane active slot is invalid=%r', file_pattern)
        return

    if cache_type == const.CACHE_TYPE_GPU:
        return erase_gpu_group_items(file_pattern)
    elif cache_type == const.CACHE_TYPE_CPU:
        return erase_cpu_group_items(file_pattern)
    raise NotImplementedError


def erase_images_in_unused_image_plane_slots(cache_type, shape_node):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(shape_node) == _IMAGE_PLANE_SHAPE

    file_patterns = imageplane_lib.get_file_pattern_for_unused_slots(shape_node)
    file_patterns = [
        x for x in file_patterns if isinstance(x, pycompat.TEXT_TYPE) and len(x) > 0
    ]
    if len(file_patterns) == 0:
        LOG.warn('mmImagePlane unused slots are all invalid; node=%r', shape_node)
        return

    if cache_type == const.CACHE_TYPE_GPU:
        return erase_gpu_groups_items(file_patterns)
    elif cache_type == const.CACHE_TYPE_CPU:
        return erase_cpu_groups_items(file_patterns)
    raise NotImplementedError


def erase_image_sequence(
    cache_type, file_pattern, format_style, start_frame, end_frame
):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert format_style in const_utils.IMAGE_SEQ_FORMAT_STYLE_VALUES
    assert isinstance(file_pattern, pycompat.TEXT_TYPE)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)

    item_count = None
    if cache_type == const.CACHE_TYPE_GPU:
        item_count = imagecache_cmd.get_gpu_cache_group_item_count(file_pattern)
    elif cache_type == const.CACHE_TYPE_CPU:
        item_count = imagecache_cmd.get_cpu_cache_group_item_count(file_pattern)
    assert item_count is not None

    if item_count == 0:
        LOG.warn('File pattern does not have any items. item_count=%r', item_count)
        return

    item_names = set(imagecache_cmd.get_gpu_group_item_names(cache_type, file_pattern))
    assert len(item_names) > 0

    # Evaluate the file_pattern for start_frame to end_frame.
    image_file_paths = set()
    for frame in range(start_frame, end_frame + 1):
        format_style = const_utils.IMAGE_SEQ_FORMAT_STYLE_EXACT_FRAME
        file_path = imageseq_utils.resolve_file_pattern_to_file_path(
            file_pattern, format_style, exact_frame=start_frame
        )
        image_file_paths.add(file_path)

    # If the evaluated file path is in the image cache, add it to the
    # list to be removed.
    #
    # This assumes both lists use the same representation of the same
    # file; the file is absolute and both use forward-slashes (which
    # is expected).
    common_file_paths = item_names & image_file_paths

    # Remove named items from the cache.
    if cache_type == const.CACHE_TYPE_GPU:
        return erase_gpu_image_items(list(common_file_paths))
    elif cache_type == const.CACHE_TYPE_CPU:
        return erase_cpu_image_items(list(common_file_paths))
    else:
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
    """
    Clear image cache completely.
    """
    assert cache_type in const.CACHE_TYPE_VALUES

    # Remove named items from the cache.
    before_item_count = None
    after_item_count = None
    if cache_type == const.CACHE_TYPE_GPU:
        before_item_count = imagecache_cmd.get_gpu_cache_item_count()
        capacity_bytes = imagecache_cmd.get_gpu_cache_capacity_bytes()

        # Because setting the capacity to zero will automatically
        # evict "all" images (except the minimum number allowed) from
        # the cache.
        imagecache_cmd.set_gpu_cache_capacity_bytes(0)

        imagecache_cmd.set_gpu_cache_capacity_bytes(capacity_bytes)
        after_item_count = imagecache_cmd.get_gpu_cache_item_count()
    elif cache_type == const.CACHE_TYPE_CPU:
        before_item_count = imagecache_cmd.get_cpu_cache_item_count()
        capacity_bytes = imagecache_cmd.get_cpu_cache_capacity_bytes()

        # Because setting the capacity to zero will automatically
        # evict "all" images (except the minimum number allowed) from
        # the cache.
        imagecache_cmd.set_cpu_cache_capacity_bytes(0)

        imagecache_cmd.set_cpu_cache_capacity_bytes(capacity_bytes)
        after_item_count = imagecache_cmd.get_cpu_cache_item_count()
    else:
        raise NotImplementedError

    LOG.debug(
        '%s ImageCache items before clearing: %r', cache_type.upper(), before_item_count
    )
    LOG.debug(
        '%s ImageCache items after clearing: %r', cache_type.upper(), after_item_count
    )

    removed_count = before_item_count - after_item_count
    LOG.info(
        'Erased %r images from the %s Image Cache', removed_count, cache_type.upper()
    )
    return
