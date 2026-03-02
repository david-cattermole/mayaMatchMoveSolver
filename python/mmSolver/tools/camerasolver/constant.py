# Copyright (C) 2026 David Cattermole.
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
Holds all constant data needed for the camera solver tool and UI.
"""

# Window Title Bar format.
WINDOW_TITLE_BAR = 'Camera Solver'

# Window button text.
WINDOW_BUTTON_SOLVE_START_LABEL = 'Solve'
WINDOW_BUTTON_SOLVE_STOP_LABEL = 'Stop Solve'
WINDOW_BUTTON_CLOSE_LABEL = 'Close'
WINDOW_BUTTON_CLOSE_AND_STOP_LABEL = 'Stop Solve and Close'

# Available log levels for the Camera Solver UI.
LOG_LEVEL_ERROR = 'error'
LOG_LEVEL_WARNING = 'warn'
LOG_LEVEL_PROGRESS = 'progress'
LOG_LEVEL_INFO = 'info'
LOG_LEVEL_DEBUG = 'debug'
LOG_LEVEL_LIST = [
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_PROGRESS,
    LOG_LEVEL_INFO,
    LOG_LEVEL_DEBUG,
]


# Adjustment solver type.
ADJUSTMENT_SOLVER_TYPE_NONE = 'adjustment_solver_type_none'
ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE = 'adjustment_solver_type_evolution_refine'
ADJUSTMENT_SOLVER_TYPE_EVOLUTION_UNKNOWN = 'adjustment_solver_type_evolution_unknown'
ADJUSTMENT_SOLVER_TYPE_UNIFORM_GRID = 'adjustment_solver_type_uniform_grid'
ADJUSTMENT_SOLVER_TYPE_LIST = [
    ADJUSTMENT_SOLVER_TYPE_NONE,
    ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE,
    ADJUSTMENT_SOLVER_TYPE_EVOLUTION_UNKNOWN,
    ADJUSTMENT_SOLVER_TYPE_UNIFORM_GRID,
]

# The environment variable name that is used to find the executable.
MMSOLVER_LOCATION_ENV_VAR_NAME = 'MMSOLVER_LOCATION'

# The expected file name for the camera solver executable.
EXECUTABLE_FILE_NAME = 'mmsolver-camerasolve'


# This is a special attribute name that is expected by the
# mmcamerasolve executable.
ATTR_CAMERA_FOCAL_LENGTH = 'camera.focal_length_mm'
