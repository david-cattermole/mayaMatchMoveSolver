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

# Output directory location within the Maya workspace.
WORKSPACE_OUTPUT_SUBDIR = 'data'
OUTPUT_DIRECTORY_NAME = 'mmSolver_camerasolver'

# Scene option keys for storing camera solver settings in the Maya
# scene.  Using the scene means each saved .ma/.mb file carries its
# own solver preferences, and multiple open Maya sessions can hold
# independent values.
SCENE_OPTION_LOG_LEVEL = 'mmSolver_camerasolver_log_level'
SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE = 'mmSolver_camerasolver_adjustment_solver_type'
SCENE_OPTION_THREAD_COUNT = 'mmSolver_camerasolver_thread_count'
SCENE_OPTION_EVOLUTION_GENERATION_COUNT = (
    'mmSolver_camerasolver_evolution_generation_count'
)
SCENE_OPTION_EVOLUTION_POPULATION_COUNT = (
    'mmSolver_camerasolver_evolution_population_count'
)
SCENE_OPTION_FRAME_RANGE_MODE = 'mmSolver_camerasolver_frame_range_mode'
SCENE_OPTION_FRAME_START = 'mmSolver_camerasolver_frame_start'
SCENE_OPTION_FRAME_END = 'mmSolver_camerasolver_frame_end'
SCENE_OPTION_FOCAL_LENGTH_RANGE_MODE = 'mmSolver_camerasolver_focal_length_range_mode'
SCENE_OPTION_FOCAL_LENGTH_PERCENTAGE = 'mmSolver_camerasolver_focal_length_percentage'
SCENE_OPTION_FOCAL_LENGTH_MIN = 'mmSolver_camerasolver_focal_length_min'
SCENE_OPTION_FOCAL_LENGTH_MAX = 'mmSolver_camerasolver_focal_length_max'
SCENE_OPTION_FOCAL_LENGTH_SAMPLES = 'mmSolver_camerasolver_focal_length_samples'

# Frame range mode combo box indices.
FRAME_RANGE_MODE_TIMELINE_INNER_INDEX = 0
FRAME_RANGE_MODE_TIMELINE_OUTER_INDEX = 1
FRAME_RANGE_MODE_CUSTOM_INDEX = 2

# Focal length range mode combo box indices.
FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX = 0
FOCAL_LENGTH_RANGE_MODE_MIN_MAX_INDEX = 1

# Ordered lists mapping combo box index to constant string value.
# The position in the list corresponds to the combo box item index.
ADJUSTMENT_SOLVER_TYPE_INDEX_LIST = [
    ADJUSTMENT_SOLVER_TYPE_NONE,
    ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE,
    ADJUSTMENT_SOLVER_TYPE_EVOLUTION_UNKNOWN,
    ADJUSTMENT_SOLVER_TYPE_UNIFORM_GRID,
]
LOG_LEVEL_INDEX_LIST = [
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_PROGRESS,
    LOG_LEVEL_INFO,
    LOG_LEVEL_DEBUG,
]
ADJUSTMENT_SOLVER_TO_INDEX = {
    v: i for i, v in enumerate(ADJUSTMENT_SOLVER_TYPE_INDEX_LIST)
}
LOG_LEVEL_TO_INDEX = {v: i for i, v in enumerate(LOG_LEVEL_INDEX_LIST)}

# Default values used when a scene option has not yet been set.
DEFAULT_LOG_LEVEL = LOG_LEVEL_PROGRESS
DEFAULT_ADJUSTMENT_SOLVER_TYPE = ADJUSTMENT_SOLVER_TYPE_NONE
DEFAULT_THREAD_COUNT = 4
DEFAULT_EVOLUTION_GENERATION_COUNT = 100
DEFAULT_EVOLUTION_POPULATION_COUNT = 100
DEFAULT_FRAME_RANGE_MODE = FRAME_RANGE_MODE_TIMELINE_INNER_INDEX
DEFAULT_FRAME_START = 1
DEFAULT_FRAME_END = 120
DEFAULT_FOCAL_LENGTH_RANGE_MODE = FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX
DEFAULT_FOCAL_LENGTH_PERCENTAGE = 20.0
DEFAULT_FOCAL_LENGTH_MIN = 0.1
DEFAULT_FOCAL_LENGTH_MAX = 1000.0
DEFAULT_FOCAL_LENGTH_SAMPLES = 100
