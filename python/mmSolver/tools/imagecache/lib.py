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

LOG = mmSolver.logger.get_logger()


def format_image_sequence_size(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_image_sequence_size: image_plane_shp=%r',
        image_plane_shp,
    )
    # TODO: Calculate this string.
    return '2,346MB (23MB x 102 frames)'


def format_cache_gpu_used(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_gpu_used: image_plane_shp=%r',
        image_plane_shp,
    )
    # TODO: Calculate this string.
    return '42% (3.5GB) of 8GB'


def format_cache_cpu_used(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_cpu_used: image_plane_shp=%r',
        image_plane_shp,
    )
    # TODO: Calculate this string.
    return '23% (34GB) of 240GB'


def format_cache_available(image_plane_shp):
    assert maya.cmds.nodeType(image_plane_shp) == 'mmImagePlaneShape2'
    LOG.info(
        'format_cache_available: image_plane_shp=%r',
        image_plane_shp,
    )
    # TODO: Calculate this string.
    return 'CPU: 240GB | GPU: 8GB'


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
