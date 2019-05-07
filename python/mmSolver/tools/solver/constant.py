"""
Holds all constant data needed for the solver tool and UI.
"""

# Window Title Bar format.
WINDOW_TITLE_BAR = 'mmSolver | {0}'


# Available log levels for the Solver UI.
LOG_LEVEL_ERROR = 'error'
LOG_LEVEL_WARNING = 'warning'
LOG_LEVEL_INFO = 'info'
LOG_LEVEL_VERBOSE = 'verbose'
LOG_LEVEL_DEBUG = 'debug'
LOG_LEVEL_LIST = [
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_INFO,
    LOG_LEVEL_VERBOSE,
    LOG_LEVEL_DEBUG,
]


# The name of the 'Scene Data' representations.
MM_SOLVER_DATA_NODE_NAME = 'mmSolver_data_node'
MM_SOLVER_DATA_NODE_TYPE = 'script'
MM_SOLVER_DATA_ATTR_NAME = 'mmSolver_data'


# Scene Data keys and default values.
SCENE_DATA_ACTIVE_COLLECTION_UID = 'active_collection_uid'
SCENE_DATA_REFRESH_VIEWPORT = 'refresh_viewport_state'
SCENE_DATA_REFRESH_VIEWPORT_DEFAULT = True
SCENE_DATA_FORCE_DG_UPDATE = 'force_dg_update_state'
SCENE_DATA_FORCE_DG_UPDATE_DEFAULT = False
SCENE_DATA_LOG_LEVEL = 'log_level'
SCENE_DATA_LOG_LEVEL_DEFAULT = LOG_LEVEL_INFO


# Solver Step Strategies
STRATEGY_PER_FRAME = 'per_frame'
STRATEGY_TWO_FRAMES_FWD = 'two_frames_fwd'
# # Accumulate the frame numbers...
# # 1,2,3,4, becomes...
# # 1 and 2
# # 1, 2 and 3,
# # 1, 2, 3, and 4
# STRATEGY_TWO_FRAMES_FWD_ACCUM = 'two_frames_fwd_accum'
STRATEGY_ALL_FRAMES_AT_ONCE = 'all_frames_at_once'
STRATEGY_LIST = [
    STRATEGY_PER_FRAME,
    STRATEGY_TWO_FRAMES_FWD,
    STRATEGY_ALL_FRAMES_AT_ONCE,
]

STRATEGY_PER_FRAME_LABEL = 'Per-Frame'
STRATEGY_TWO_FRAMES_FWD_LABEL = 'Two Frames Fwd'
STRATEGY_ALL_FRAMES_AT_ONCE_LABEL = 'All Frames'
STRATEGY_LABEL_LIST = [
    STRATEGY_PER_FRAME_LABEL,
    STRATEGY_TWO_FRAMES_FWD_LABEL,
    STRATEGY_ALL_FRAMES_AT_ONCE_LABEL,
]

# Solver Step Attribute Filters
ATTR_FILTER_ANIM_ONLY_LABEL = 'Animated Only'
ATTR_FILTER_STATIC_AND_ANIM_LABEL = 'Static + Animated'
ATTR_FILTER_STATIC_ONLY_LABEL = 'Static Only'
ATTR_FILTER_NO_ATTRS_LABEL = 'No Attributes'
ATTR_FILTER_LABEL_LIST = [
    ATTR_FILTER_ANIM_ONLY_LABEL,
    ATTR_FILTER_STATIC_AND_ANIM_LABEL,
    # ATTR_FILTER_STATIC_ONLY_LABEL,
    # ATTR_FILTER_NO_ATTRS_LABEL,
]

# Solver Step Data (stored on Collection node)
SOLVER_STEP_ATTR = 'solver_step_list'
SOLVER_STEP_DATA_DEFAULT = {
    'name': None,
    'enabled': True,
    'frame_list': [],
    'strategy': STRATEGY_TWO_FRAMES_FWD,
    'use_anim_attrs': True,
    'use_static_attrs': False,
}

# Override Current Frame (stored on Collection node)
OVERRIDE_CURRENT_FRAME_ATTR = 'override_current_frame'

# Most simple solves converge on a result within 10
# iterations, but 20 gives a wider range to refine more
# complex set ups.
MAX_ITERATION_NUM_DEFAULT_VALUE = 20

# Force the 'central' Auto-Differencing type, because it's
# more accurate and we can converge on a result faster.
AUTO_DIFF_TYPE_DEFAULT_VALUE = 1

# List of common status messages.
STATUS_READY = 'Ready.'
STATUS_REFRESHING = 'Refreshing UI...'
STATUS_COMPILING = 'Compiling Solver...'
STATUS_SOLVER_NOT_VALID = 'Solver Not Valid!'
STATUS_EXECUTING = 'Executing...'
STATUS_FINISHED = 'Finished.'

ATTR_DEFAULT_MIN_VALUE = '<Not Set>'
ATTR_DEFAULT_MAX_VALUE = '<Not Set>'

ATTR_STATE_INVALID = 'Invalid'
ATTR_STATE_STATIC = 'Static'
ATTR_STATE_ANIMATED = 'Animated'
ATTR_STATE_LOCKED = 'Locked'

# Toggle Objects (stored on Collection node)
OBJECT_TOGGLE_CAMERA_ATTR = 'object_toggle_camera'
OBJECT_TOGGLE_MARKER_ATTR = 'object_toggle_marker'
OBJECT_TOGGLE_BUNDLE_ATTR = 'object_toggle_bundle'

OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE = True
OBJECT_TOGGLE_MARKER_DEFAULT_VALUE = True
OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE = False

# Toggle Attributes (stored on Collection node)
ATTRIBUTE_TOGGLE_ANIMATED_ATTR = 'attribute_toggle_animated'
ATTRIBUTE_TOGGLE_STATIC_ATTR = 'attribute_toggle_static'
ATTRIBUTE_TOGGLE_LOCKED_ATTR = 'attribute_toggle_locked'

ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE = True
ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE = True
ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE = False

# Information to filter invalid input attributes from the Solver UI.
ATTR_INVALID_OBJECT_TYPES = [
    'imageplane',
    'marker',
]
