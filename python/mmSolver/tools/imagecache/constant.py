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


# The default values below are based on the following minimum/average data load:
#
# Single image size:
# >>> width = 1920
# >>> height = 1080
# >>> num_channels = 3
# >>> image_byte_size = width * height * num_channels  # 6220800 Bytes
# A image is at least 6.2208 MB each frame.
#
# Image Sequence size:
# >>> frame_count = 200
# >>> image_byte_size * frame_count  # 1244160000 Bytes
# The average image sequence will take up about 1.24416 GB of memory.
#
# We also guess that the user has at least 4GB of GPU memory, and 32GB
# of CPU memory, and we assume the user wants to have 3 different Maya
# sessions running at once, each with an image sequence loaded.
#
# 100 MB (2.5% of 4GB) of GPU memory allows ~16 1080p HD images stored
# in memory at once. For large (4K) images this means perhaps only one
# image will be stored in the Image Cache.
CONFIG_GPU_CAPACITY_PERCENT_KEY = 'data/gpu_capacity_percent'
CONFIG_GPU_CAPACITY_PERCENT_DEFAULT_VALUE = 2.5

# 3.2 GB (10%) of CPU memory allows ~514 1080p HD images stored in
# memory at once. This is a reasonable amount of CPU memory, but can
# easily be consumed for larger images or longer frame ranges.
CONFIG_CPU_CAPACITY_PERCENT_KEY = 'data/cpu_capacity_percent'
CONFIG_CPU_CAPACITY_PERCENT_DEFAULT_VALUE = 10.0

SCENE_OPTION_CAPACITY_OVERRIDE_KEY = 'mmSolver_imagecache_capacity_override'
SCENE_OPTION_CAPACITY_OVERRIDE_DEFAULT_VALUE = False

SCENE_OPTION_GPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_gpu_capacity_percent'
SCENE_OPTION_GPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0

SCENE_OPTION_CPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_cpu_capacity_percent'
SCENE_OPTION_CPU_CAPACITY_PERCENT_DEFAULT_VALUE = 0.0
