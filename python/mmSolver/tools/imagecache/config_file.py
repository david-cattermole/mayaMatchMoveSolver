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

import mmSolver.utils.config
import mmSolver.tools.imagecache.config_utils as config_utils
import mmSolver.tools.imagecache.constant as const
import mmSolver.tools.imagecache.lib as lib

LOG = mmSolver.logger.get_logger()


# Initialised without a file path, because we only look up the file in
# the functions below.
#
# Users are not allowed to touch this variable.
#
# Note we never re-assign this variable. The Config object instance is
# always reused.
__CONFIG_PATH = mmSolver.utils.config.get_home_dir_path(const.CONFIG_FILE_NAME)
__CONFIG = mmSolver.utils.config.Config(__CONFIG_PATH)
__CONFIG.autoread = True
__CONFIG.autowrite = False


def _get_config():
    global __CONFIG
    return __CONFIG


def _get_config_value(config, key, fallback):
    """Query the attribute from the user's home directory. If the user's
    option is saved, use that value instead.
    """
    value = fallback
    if config is not None:
        value = config.get_value(key, fallback)
    return value


def write():
    global __CONFIG
    __CONFIG.write()


def get_gpu_capacity_percent():
    default_value = const.CONFIG_GPU_CAPACITY_PERCENT_DEFAULT_VALUE
    assert isinstance(default_value, float)
    name = const.CONFIG_GPU_CAPACITY_PERCENT_KEY
    config = _get_config()
    percent = _get_config_value(config, name, default_value)
    total_bytes = lib.get_gpu_memory_total_bytes()
    return config_utils.convert_to_capacity_value(percent, total_bytes)


def set_gpu_capacity_percent(value):
    config_file = _get_config()
    config_file.set_value(const.CONFIG_GPU_CAPACITY_PERCENT_KEY, value)
    return


def get_cpu_capacity_percent():
    default_value = const.CONFIG_CPU_CAPACITY_PERCENT_DEFAULT_VALUE
    assert isinstance(default_value, float)
    name = const.CONFIG_CPU_CAPACITY_PERCENT_KEY
    config = _get_config()
    percent = _get_config_value(config, name, default_value)
    total_bytes = lib.get_cpu_memory_total_bytes()
    return config_utils.convert_to_capacity_value(percent, total_bytes)


def set_cpu_capacity_percent(value):
    config_file = _get_config()
    config_file.set_value(const.CONFIG_CPU_CAPACITY_PERCENT_KEY, value)
    return
