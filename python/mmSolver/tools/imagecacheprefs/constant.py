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

WINDOW_TITLE = 'Image Cache Preferences'

CONFIG_FILE_NAME = "tools_imagecacheprefs.json"

CONFIG_SCENE_CAPACITY_OVERRIDE_KEY = 'mmSolver_imagecache_capacity_override'
CONFIG_SCENE_GPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_gpu_capacity_percent'
CONFIG_SCENE_CPU_CAPACITY_PERCENT_KEY = 'mmSolver_imagecache_cpu_capacity_percent'

CONFIG_UPDATE_EVERY_N_SECONDS_KEY = 'data/update_every_n_seconds'
CONFIG_UPDATE_EVERY_N_SECONDS_DEFAULT_VALUE = 2
CONFIG_GPU_CAPACITY_PERCENT_KEY = 'data/gpu_capacity_percent'
CONFIG_CPU_CAPACITY_PERCENT_KEY = 'data/cpu_capacity_percent'
