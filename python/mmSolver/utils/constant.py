# Copyright (C) 2019 David Cattermole.
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
Constant values for utilities.
"""

# Constants for smooth method selection.
SMOOTH_TYPE_AVERAGE = 'average'
SMOOTH_TYPE_GAUSSIAN = 'gaussian'
SMOOTH_TYPE_FOURIER = 'fourier'
SMOOTH_TYPES = [
    SMOOTH_TYPE_AVERAGE,
    SMOOTH_TYPE_GAUSSIAN,
    SMOOTH_TYPE_FOURIER,
]

# Raytrace
RAYTRACE_MAX_DIST = 9999999999.0
RAYTRACE_EPSILON = 0.0001

# Config
CONFIG_PATH_VAR_NAME = 'MMSOLVER_CONFIG_PATH'
CONFIG_HOME_DIR_PATH = {
    'Linux': '${HOME}/.mmSolver/',
    'Windows': '${APPDATA}/mmSolver/',
}

# Maya configuration
SCENE_DATA_NODE = 'MM_SOLVER_SCENE_DATA'
SCENE_DATA_ATTR = 'data'


# Maya Transform related constants.
EVAL_MODE_API_DG_CONTEXT = 'api_dg_context'
EVAL_MODE_TIME_SWITCH_GET_ATTR = 'time_switch_get_attr'
EVAL_MODE_DEFAULT = EVAL_MODE_TIME_SWITCH_GET_ATTR
EVAL_MODE_LIST = [
    EVAL_MODE_API_DG_CONTEXT,
    EVAL_MODE_TIME_SWITCH_GET_ATTR
]
ROTATE_ORDER_STR_LIST = [
    'xyz',
    'yzx',
    'zxy',
    'xzy',
    'yxz',
    'zyx'
]
ROTATE_ORDER_INDEX_TO_STR = {
    0: 'xyz',
    1: 'yzx',
    2: 'zxy',
    3: 'xzy',
    4: 'yxz',
    5: 'zyx'
}
ROTATE_ORDER_STR_TO_INDEX = {
    'xyz': 0,
    'yzx': 1,
    'zxy': 2,
    'xzy': 3,
    'yxz': 4,
    'zyx': 5,
}
