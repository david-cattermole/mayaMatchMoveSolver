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
import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.imagecache.config_utils as config_utils
import mmSolver.tools.imagecache.constant as const
import mmSolver.tools.imagecache._lib.query_resources as query_resources

LOG = mmSolver.logger.get_logger()


def get_cache_scene_override():
    name = const.SCENE_OPTION_CAPACITY_OVERRIDE_KEY
    value = configmaya.get_scene_option(name, default=None)
    assert value is None or isinstance(value, bool)
    return value


def set_cache_scene_override(value):
    assert value is None or isinstance(value, bool)
    name = const.SCENE_OPTION_CAPACITY_OVERRIDE_KEY
    configmaya.set_scene_option(name, value, add_attr=True)
    return


def get_gpu_capacity_percent():
    default_value = const.SCENE_OPTION_GPU_CAPACITY_PERCENT_DEFAULT_VALUE
    assert isinstance(default_value, float)
    name = const.SCENE_OPTION_GPU_CAPACITY_PERCENT_KEY
    percent = configmaya.get_scene_option(name, default=default_value)
    total_bytes = query_resources.get_gpu_memory_total_bytes()
    return config_utils.convert_to_capacity_value(percent, total_bytes)


def set_gpu_capacity_percent(percent):
    assert isinstance(percent, float)
    name = const.SCENE_OPTION_GPU_CAPACITY_PERCENT_KEY
    percent = configmaya.set_scene_option(name, percent, add_attr=True)
    return


def get_cpu_capacity_percent():
    default_value = const.SCENE_OPTION_CPU_CAPACITY_PERCENT_DEFAULT_VALUE
    assert isinstance(default_value, float)
    name = const.SCENE_OPTION_CPU_CAPACITY_PERCENT_KEY
    percent = configmaya.get_scene_option(name, default=default_value)
    total_bytes = query_resources.get_cpu_memory_total_bytes()
    return config_utils.convert_to_capacity_value(percent, total_bytes)


def set_cpu_capacity_percent(percent):
    assert isinstance(percent, float)
    name = const.SCENE_OPTION_CPU_CAPACITY_PERCENT_KEY
    percent = configmaya.set_scene_option(name, percent, add_attr=True)
    return
