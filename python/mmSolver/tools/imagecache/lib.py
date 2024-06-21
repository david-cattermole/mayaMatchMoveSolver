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
import mmSolver.tools.createimageplane._lib.constant as imageplane_const
import mmSolver.tools.createimageplane._lib.mmimageplane_v2 as imageplane_lib

LOG = mmSolver.logger.get_logger()

# Shorter alias.
_MM_IMAGE_PLANE_SHAPE_V2 = imageplane_const.MM_IMAGE_PLANE_SHAPE_V2

# Memory Conversion
_BYTES_TO_KILOBYTES = 1024  # int(pow(2, 10))
_BYTES_TO_MEGABYTES = 1048576  # int(pow(2, 20))
_BYTES_TO_GIGABYTES = 1073741824  # int(pow(2, 30))
_KILOBYTES_TO_MEGABYTES = 1024  # int(pow(2, 10))
_KILOBYTES_TO_GIGABYTES = 1048576  # int(pow(2, 20))


def format_image_sequence_size(image_plane_shp):
    """
    Look up node values and format as text.

    Example output:
    '2,346.1MB (23.7MB x 102 frames)'
    """
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.debug(
        'format_image_sequence_size: image_plane_shp=%r',
        image_plane_shp,
    )

    frame_size_bytes = imageplane_lib.get_frame_size_bytes(image_plane_shp)
    frame_count = imageplane_lib.get_frame_count(image_plane_shp)
    image_sequence_size_bytes = imageplane_lib.get_image_sequence_size_bytes(
        image_plane_shp
    )

    frame_size_mb = frame_size_bytes / _BYTES_TO_MEGABYTES
    seq_size_mb = image_sequence_size_bytes / _BYTES_TO_MEGABYTES
    text = '{seq_size_mb:0,.1f} MB ({frame_size_mb:0,.1f} MB x {frame_count} frames)'
    return text.format(
        seq_size_mb=seq_size_mb, frame_size_mb=frame_size_mb, frame_count=frame_count
    )


def _format_cache_used(used_bytes, capacity_bytes):
    """
    Look up node values and format as text.

    Example text:
    ' 42.1% (3.53 GB) of 8.00 GB'
    """
    assert isinstance(used_bytes, int)
    assert isinstance(capacity_bytes, int)

    usage_percent = 0
    usage_gigabytes = 0
    capacity_gigabyte = 0
    if capacity_bytes > 0:
        usage_percent = (used_bytes / capacity_bytes) * 100.0
        usage_gigabytes = used_bytes / _BYTES_TO_GIGABYTES
        capacity_gigabyte = capacity_bytes / _BYTES_TO_GIGABYTES

    text = '{usage_percent:3.1f}% ({usage_gigabytes:0,.2f} GB) of {capacity_gigabyte:0,.2f} GB'
    return text.format(
        usage_percent=usage_percent,
        usage_gigabytes=usage_gigabytes,
        capacity_gigabyte=capacity_gigabyte,
    )


def format_cache_gpu_used(image_plane_shp):
    """
    Look up node values and format text.

    Example text:
    ' 42.1% (3.53GB) of 8.00GB'
    """
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.debug(
        'format_cache_gpu_used: image_plane_shp=%r',
        image_plane_shp,
    )

    used_bytes = get_gpu_cache_used_bytes()
    capacity_bytes = get_gpu_cache_capacity_bytes()
    return _format_cache_used(int(used_bytes), int(capacity_bytes))


def format_cache_cpu_used(image_plane_shp):
    """
    Look up node values and format as text.

    Example text:
    ' 23.1% (34.24 GB) of 240.00 GB'
    """
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.debug(
        'format_cache_cpu_used: image_plane_shp=%r',
        image_plane_shp,
    )

    used_bytes = get_cpu_cache_used_bytes()
    capacity_bytes = get_cpu_cache_capacity_bytes()
    return _format_cache_used(int(used_bytes), int(capacity_bytes))


def format_memory_gpu_available(image_plane_shp):
    """
    Look up node values and format as text.

    Example text:
    'GPU 8.00 GB'
    """
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.debug(
        'format_memory_available: image_plane_shp=%r',
        image_plane_shp,
    )

    memory_bytes = get_gpu_memory_total_bytes()
    memory_gigabytes = 0.0
    if memory_bytes > 0:
        memory_gigabytes = memory_bytes / _BYTES_TO_GIGABYTES

    text = 'GPU: {memory_gigabytes:0,.2f} GB'
    return text.format(
        memory_gigabytes=memory_gigabytes,
    )


def format_memory_cpu_available(image_plane_shp):
    """
    Look up node values and format as text.

    Example text:
    'CPU: 240.00 GB'
    """
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.debug(
        'format_memory_available: image_plane_shp=%r',
        image_plane_shp,
    )

    memory_bytes = get_cpu_memory_total_bytes()
    memory_gigabytes = 0.0
    if memory_bytes > 0:
        memory_gigabytes = memory_bytes / _BYTES_TO_GIGABYTES

    text = 'CPU: {memory_gigabytes:0,.2f} GB'
    return text.format(
        memory_gigabytes=memory_gigabytes,
    )


def get_gpu_cache_item_count():
    return int(maya.cmds.mmImageCache(query=True, gpuItemCount=True))


def get_cpu_cache_item_count():
    return int(maya.cmds.mmImageCache(query=True, cpuItemCount=True))


def get_gpu_cache_used_bytes():
    return int(maya.cmds.mmImageCache(query=True, gpuUsed=True))


def get_cpu_cache_used_bytes():
    return int(maya.cmds.mmImageCache(query=True, cpuUsed=True))


def get_gpu_cache_capacity_bytes():
    return int(maya.cmds.mmImageCache(query=True, gpuCapacity=True))


def get_cpu_cache_capacity_bytes():
    return int(maya.cmds.mmImageCache(query=True, cpuCapacity=True))


def get_gpu_memory_total_bytes():
    return int(maya.cmds.mmMemoryGPU(query=True, total=True))


def get_gpu_memory_used_bytes():
    return int(maya.cmds.mmMemoryGPU(query=True, used=True))


def get_cpu_memory_total_bytes():
    return int(
        maya.cmds.mmMemorySystem(
            query=True,
            systemPhysicalMemoryTotal=True,
        )
    )


def get_cpu_memory_used_bytes():
    return int(
        maya.cmds.mmMemorySystem(
            query=True,
            systemPhysicalMemoryUsed=True,
        )
    )


def cache_remove_all_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.info(
        'cache_remove_all_image_plane_slots: image_plane_shp=%r, cache_type=%r',
        image_plane_shp,
        cache_type,
    )
    return


def cache_remove_active_image_plane_slot(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.info(
        'cache_remove_active_image_plane_slot: image_plane_shp=%r, cache_type=%r',
        image_plane_shp,
        cache_type,
    )
    return


def cache_remove_unused_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == _MM_IMAGE_PLANE_SHAPE_V2
    LOG.info(
        'cache_remove_unused_image_plane_slots: image_plane_shp=%r, cache_type=%r',
        image_plane_shp,
        cache_type,
    )
    return


def cache_remove_all(cache_type):
    assert cache_type in const.CACHE_TYPE_VALUES
    LOG.info(
        'cache_remove_unused_image_plane_slots: cache_type=%r',
        cache_type,
    )
    return


def cache_remove_image_sequence(file_pattern, start_frame, end_frame, cache_type):
    LOG.info(
        'cache_remove_image_sequence: '
        'file_pattern=%r, start_frame=%r, end_frame=%r, cache_type=%r',
        file_pattern,
        start_frame,
        end_frame,
        cache_type,
    )
    pass


def cache_remove_all_inactive(cache_type):
    # Removes all the items in the cache that cannot be 'reached' by
    # any of the image planes.
    LOG.info(
        'cache_remove_all_inactive: cache_type=%r',
        cache_type,
    )
    pass
