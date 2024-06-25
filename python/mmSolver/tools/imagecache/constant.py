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
Image Cache constants.
"""


CACHE_TYPE_GPU = 'gpu'
CACHE_TYPE_CPU = 'cpu'
CACHE_TYPE_VALUES = [
    CACHE_TYPE_GPU,
    CACHE_TYPE_CPU,
]

CONFIG_FILE_NAME = 'tools_imagecache.json'

CONFIG_GPU_CAPACITY_PERCENT_KEY = 'data/gpu_capacity_percent'
CONFIG_GPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0

CONFIG_CPU_CAPACITY_PERCENT_KEY = 'data/cpu_capacity_percent'
CONFIG_CPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0

SCENE_OPTION_CAPACITY_OVERRIDE_KEY = 'mmSolver_imagecache_capacity_override'
SCENE_OPTION_CAPACITY_OVERRIDE_DEFAULT_VALUE = False

SCENE_OPTION_GPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_gpu_capacity_percent'
SCENE_OPTION_GPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0

SCENE_OPTION_CPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_cpu_capacity_percent'
SCENE_OPTION_CPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0
