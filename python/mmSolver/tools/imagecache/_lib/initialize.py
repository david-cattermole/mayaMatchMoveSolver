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
import mmSolver.api as mmapi
import mmSolver.utils.constant as const_utils
import mmSolver.tools.imagecache._lib.imagecache_cmd as imagecache_cmd
import mmSolver.tools.imagecache.config as config


LOG = mmSolver.logger.get_logger()


def _format_gigabytes(memory_bytes):
    memory_gigabytes = 0.0
    if memory_bytes > 0:
        memory_gigabytes = memory_bytes / const_utils.BYTES_TO_GIGABYTES

    text = '{:0,.2f} GB'
    return text.format(memory_gigabytes)


def _format_percent(percent):
    text = '{:0.1f}'.format(percent)
    return text + '%'


def _ensure_plugin_loaded():
    """
    Loads all plug-ins required for the ImageCache.

    :raises: mmapi.SolverNotAvailable
    """
    mmapi.load_plugin()
    command_names = ('mmImageCache', 'mmMemoryGPU', 'mmMemorySystem')
    for command_name in command_names:
        if command_name not in dir(maya.cmds):
            raise mmapi.SolverNotAvailable
    return


def initialize():
    """
    Set Image Cache capacities from preferences.
    """
    LOG.info('MM Solver Initialize Image Cache...')

    # TODO: Install a callback to be called each time a new scene is
    # opened. We will look for enabled scene override values for the
    # cache and set it, otherwise we use the defaults.

    _ensure_plugin_loaded()

    capacity_data = config.resolve_capacity_data()
    gpu_capacity_bytes = capacity_data.gpu_resolved_capacity.size_bytes
    cpu_capacity_bytes = capacity_data.cpu_resolved_capacity.size_bytes
    gpu_capacity_percent = capacity_data.gpu_resolved_capacity.percent
    cpu_capacity_percent = capacity_data.cpu_resolved_capacity.percent

    # Set the image cache capacities.
    gpu_capacty_gigabytes = _format_gigabytes(gpu_capacity_bytes)
    cpu_capacty_gigabytes = _format_gigabytes(cpu_capacity_bytes)
    gpu_capacity_percent = _format_percent(gpu_capacity_percent)
    cpu_capacity_percent = _format_percent(cpu_capacity_percent)

    LOG.info(
        'Image Cache GPU Capacity: %s (%s)', gpu_capacty_gigabytes, gpu_capacity_percent
    )
    LOG.info(
        'Image Cache CPU Capacity: %s (%s)', cpu_capacty_gigabytes, cpu_capacity_percent
    )

    imagecache_cmd.set_gpu_cache_capacity_bytes(gpu_capacity_bytes)
    imagecache_cmd.set_cpu_cache_capacity_bytes(cpu_capacity_bytes)
    return
