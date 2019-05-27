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

# Maya configuration
SCENE_DATA_NODE = 'MM_SOLVER_SCENE_DATA'
SCENE_DATA_ATTR = 'data'
