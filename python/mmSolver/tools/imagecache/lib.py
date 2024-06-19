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
import mmSolver.tools.createimageplane._lib.mmimageplane_v2 as imageplane_lib

LOG = mmSolver.logger.get_logger()


# Memory Conversion
BYTES_TO_KILOBYTES = 1024  # int(pow(2, 10))
BYTES_TO_MEGABYTES = 1048576  # int(pow(2, 20))
BYTES_TO_GIGABYTES = 1073741824  # int(pow(2, 30))
KILOBYTES_TO_MEGABYTES = 1024  # int(pow(2, 10))
KILOBYTES_TO_GIGABYTES = 1048576  # int(pow(2, 20))


def format_image_sequence_size(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_image_sequence_size: image_plane_shp=%r',
        image_plane_shp,
    )

    frame_size_bytes = imageplane_lib.get_frame_size_bytes(image_plane_shp)
    frame_count = imageplane_lib.get_frame_count(image_plane_shp)
    image_sequence_size_bytes = imageplane_lib.get_image_sequence_size_bytes(
        image_plane_shp
    )

    seq_size_mb = int(image_sequence_size_bytes / BYTES_TO_MEGABYTES)
    frame_size_mb = int(frame_size_bytes / BYTES_TO_MEGABYTES)
    text = '2,346MB (23MB x 102 frames)'
    text = '{seq_size_mb}MB (frame_size_mb)MB x {frame_count} frames)'
    return text.format(
        seq_size_mb=seq_size_mb, frame_size_mb=frame_size_mb, frame_count=frame_count
    )


def _format_cache_used(used_bytes, capacity_bytes):
    assert isinstance(used_bytes, int)
    assert isinstance(capacity_bytes, int)

    usage_percent = 0
    usage_gigabytes = 0
    capacity_gigabyte = 0
    if capacity_bytes > 0:
        usage_percent = used_bytes / capacity_bytes
        usage_gigabytes = used_bytes / BYTES_TO_GIGABYTES
        capacity_gigabyte = capacity_bytes / BYTES_TO_GIGABYTES

    # TODO: Limit the percentage of the gigabyte float values to only
    # 1 or 2 digits of precision.
    text = '{usage_percent} ({usage_gigabytes}GB) of {capacity_gigabyte}GB'
    return text.format(
        usage_percent=usage_percent,
        usage_gigabytes=usage_gigabytes,
        capacity_gigabyte=capacity_gigabyte,
    )


def format_cache_gpu_used(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_gpu_used: image_plane_shp=%r',
        image_plane_shp,
    )

    text = '42% (3.5GB) of 8GB'
    used_bytes = int(maya.cmds.mmImageCache(query=True, gpuUsed=True))
    capacity_bytes = int(maya.cmds.mmImageCache(query=True, gpuCapacity=True))
    return _format_cache_used(used_bytes, capacity_bytes)


def format_cache_cpu_used(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_cpu_used: image_plane_shp=%r',
        image_plane_shp,
    )

    text = '23% (34GB) of 240GB'
    used_bytes = int(maya.cmds.mmImageCache(query=True, cpuUsed=True))
    capacity_bytes = int(maya.cmds.mmImageCache(query=True, cpuCapacity=True))
    return _format_cache_used(used_bytes, capacity_bytes)


def format_cache_available(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_available: image_plane_shp=%r',
        image_plane_shp,
    )

    cpu_memory_gigabytes = maya.cmds.mmMemorySystem(query=True, systemPhysicalMemoryTotal=True, asGigaBytes=True)
    gpu_memory_gigabytes = maya.cmds.mmMemoryGPU(query=True, total=True, asGigaBytes=True)

    text = 'CPU: 240GB | GPU: 8GB'
    # TODO: Round these values to the closest value.
    text = 'CPU: {cpu_memory_gigabytes}GB | GPU: {gpu_memory_gigabytes}GB'
    return text.format(
        cpu_memory_gigabytes=cpu_memory_gigabytes,
        gpu_memory_gigabytes=gpu_memory_gigabytes
    )


def cache_remove_all_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'cache_remove_all_image_plane_slots: image_plane_shp=%r, cache_type=%r',
        image_plane_shp,
        cache_type,
    )
    return


def cache_remove_active_image_plane_slot(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'cache_remove_active_image_plane_slot: image_plane_shp=%r, cache_type=%r',
        image_plane_shp,
        cache_type,
    )
    return


def cache_remove_unused_image_plane_slots(cache_type, image_plane_shp):
    assert cache_type in const.CACHE_TYPE_VALUES
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
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
