"""
Holds all constant data needed for the solver tool and UI.
"""

MM_SOLVER_DATA_NODE_NAME = 'mmSolver_data_node'
MM_SOLVER_DATA_NODE_TYPE = 'script'
MM_SOLVER_DATA_ATTR_NAME = 'mmSolver_data'


SCENE_DATA_ACTIVE_COLLECTION_UID = 'active_collection_uid'


# Words recognised as True or False.
FALSE_WORDS = ['0', 'n', 'f', 'no', 'off', 'nah', 'nope', 'false']
TRUE_WORDS = ['1', 'y', 't', 'yes', 'on', 'ya', 'yeah', 'true']


# Solver Step Strategies
STRATEGY_TWO_FRAMES_FWD = 'two_frames_fwd'
# # Accumulate the frame numbers...
# # 1,2,3,4, becomes...
# # 1 and 2
# # 1, 2 and 3,
# # 1, 2, 3, and 4
# STRATEGY_TWO_FRAMES_FWD_ACCUM = 'two_frames_fwd_accum'
STRATEGY_ALL_FRAMES_AT_ONCE = 'all_frames_at_once'
STRATEGY_LIST = [
    STRATEGY_TWO_FRAMES_FWD,
    STRATEGY_ALL_FRAMES_AT_ONCE,
]

STRATEGY_TWO_FRAMES_FWD_LABEL = 'Two Frames Fwd'
STRATEGY_ALL_FRAMES_AT_ONCE_LABEL = 'All Frames'
STRATEGY_LABEL_LIST = [
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
    ATTR_FILTER_STATIC_ONLY_LABEL,
    ATTR_FILTER_NO_ATTRS_LABEL,
]

# Solver Step Data
SOLVER_STEP_ATTR = 'solver_step_list'
SOLVER_STEP_DATA_DEFAULT = {
    'name': None,
    'enabled': True,
    'frame_list': [],
    'strategy': STRATEGY_TWO_FRAMES_FWD,
    'use_anim_attrs': True,
    'use_static_attrs': False,
}

