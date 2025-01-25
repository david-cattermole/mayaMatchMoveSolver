# Copyright (C) 2018, 2019 David Cattermole.
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
Holds all constant data needed for the solver tool and UI.
"""

import mmSolver._api.constant as mmapi_const

# Window Title Bar format.
WINDOW_TITLE_BAR = '{collection} | mmSolver v{version}'

# Window button text.
WINDOW_BUTTON_SOLVE_START_LABEL = 'Solve'
WINDOW_BUTTON_SOLVE_STOP_LABEL = 'Stop Solve'
WINDOW_BUTTON_CLOSE_LABEL = 'Close'
WINDOW_BUTTON_CLOSE_AND_STOP_LABEL = 'Stop Solve and Close'

# HTML Color Names, for Qt Rich Text.
#
# https://htmlcolorcodes.com/color-names/
#
COLOR_HTML_HEX_WHITE = '#FFFFFF'  # 'white'
COLOR_HTML_HEX_ORANGE = '#FFA500'  # 'orange'
COLOR_HTML_HEX_YELLOW = '#FFFF00'  # 'yellow'
COLOR_HTML_HEX_RED = '#FF0000'  # 'red'
COLOR_TEXT_DEFAULT = COLOR_HTML_HEX_WHITE
COLOR_WARNING = COLOR_HTML_HEX_ORANGE
COLOR_ERROR = COLOR_HTML_HEX_RED


# Available log levels for the Solver UI.
#
# NOTE: These values are also part of the mmSolver API. If you change
# these values, make sure to also update the mmSolver API, see
# ./python/mmSolver/_api/constant.py
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


# Default Collection
COLLECTION_DEFAULT_NODE_NAME = 'collection1'


# The name of the 'Scene Data' representations.
MM_SOLVER_DATA_NODE_NAME = 'mmSolver_data_node'
MM_SOLVER_DATA_NODE_TYPE = 'script'
MM_SOLVER_DATA_ATTR_NAME = 'mmSolver_data'


# Scene Data keys and default values.
SCENE_DATA_ACTIVE_COLLECTION_UID = 'active_collection_uid'
SCENE_DATA_PRE_SOLVE_FORCE_EVAL = 'pre_solve_force_eval'
SCENE_DATA_REFRESH_VIEWPORT = 'refresh_viewport_state'
SCENE_DATA_FORCE_DG_UPDATE = 'force_dg_update_state'
SCENE_DATA_DISPLAY_IMAGE_PLANE_WHILE_SOLVING = 'display_image_plane_while_solving'
SCENE_DATA_DISPLAY_MESHES_WHILE_SOLVING = 'display_meshes_while_solving'
SCENE_DATA_ISOLATE_OBJECT_WHILE_SOLVING = 'isolate_object_while_solving'
SCENE_DATA_DISPLAY_OBJECT_FRAME_DEVIATION = 'display_object_frame_deviation'
SCENE_DATA_DISPLAY_OBJECT_AVERAGE_DEVIATION = 'display_object_average_deviation'
SCENE_DATA_DISPLAY_OBJECT_MAXIMUM_DEVIATION = 'display_object_maximum_deviation'
SCENE_DATA_DISPLAY_OBJECT_WEIGHT = 'display_object_weight'
SCENE_DATA_DISPLAY_ATTRIBUTE_STATE = 'display_attribute_state'
SCENE_DATA_DISPLAY_ATTRIBUTE_MIN_MAX = 'display_attribute_min_max'
SCENE_DATA_DISPLAY_ATTRIBUTE_STIFFNESS = 'display_attribute_stiffness'
SCENE_DATA_DISPLAY_ATTRIBUTE_SMOOTHNESS = 'display_attribute_smoothness'
SCENE_DATA_LOG_LEVEL = 'log_level'
SCENE_DATA_PRE_SOLVE_FORCE_EVAL_DEFAULT = True
SCENE_DATA_REFRESH_VIEWPORT_DEFAULT = True
SCENE_DATA_FORCE_DG_UPDATE_DEFAULT = True
SCENE_DATA_ISOLATE_OBJECT_WHILE_SOLVING_DEFAULT = False
SCENE_DATA_DISPLAY_IMAGE_PLANE_WHILE_SOLVING_DEFAULT = False
SCENE_DATA_DISPLAY_MESHES_WHILE_SOLVING_DEFAULT = False
SCENE_DATA_DISPLAY_OBJECT_WEIGHT_DEFAULT = True
SCENE_DATA_DISPLAY_OBJECT_FRAME_DEVIATION_DEFAULT = False
SCENE_DATA_DISPLAY_OBJECT_AVERAGE_DEVIATION_DEFAULT = True
SCENE_DATA_DISPLAY_OBJECT_MAXIMUM_DEVIATION_DEFAULT = False
SCENE_DATA_DISPLAY_ATTRIBUTE_STATE_DEFAULT = True
SCENE_DATA_DISPLAY_ATTRIBUTE_MIN_MAX_DEFAULT = True
SCENE_DATA_DISPLAY_ATTRIBUTE_STIFFNESS_DEFAULT = False
SCENE_DATA_DISPLAY_ATTRIBUTE_SMOOTHNESS_DEFAULT = False
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
SOLVER_STEP_ATTR_TYPE = 'string'
SOLVER_STEP_DEFAULT_VALUE = None  # Do not set any default value.
SOLVER_STEP_DATA_DEFAULT = {
    'name': None,
    'enabled': True,
    'frame_list': [],
    'strategy': STRATEGY_TWO_FRAMES_FWD,
    'use_anim_attrs': True,
    'use_static_attrs': False,
}

# List of common status messages.
STATUS_READY = 'Ready.'
STATUS_REFRESHING = 'Refreshing UI...'
STATUS_COMPILING = 'Compiling Solver...'
STATUS_SOLVER_NOT_VALID = 'Solver Not Valid!'
STATUS_EXECUTING = 'Executing...'
STATUS_FINISHED = 'Finished.'

# Default UI values (displayed in the UI as fall back strings)
# u'\u2014' == "Em Dash" symbol
OBJECT_DEFAULT_WEIGHT_UI_VALUE = u'\u2014'
OBJECT_DEFAULT_DEVIATION_UI_VALUE = u'\u2014'
OBJECT_DEFAULT_STATUS_UI_VALUE = u'\u2014'
ATTR_DEFAULT_MIN_UI_VALUE = '-'
ATTR_DEFAULT_MAX_UI_VALUE = '-'
ATTR_DEFAULT_MIN_MAX_UI_VALUE = ' {min}  to  {max} '
ATTR_DEFAULT_STIFFNESS_UI_VALUE = u'\u2014'
ATTR_DEFAULT_SMOOTHNESS_UI_VALUE = u'\u2014'
ATTR_DEFAULT_STATUS_UI_VALUE = u'\u2014'

ATTR_STATE_INVALID = 'Invalid'
ATTR_STATE_STATIC = 'Static'
ATTR_STATE_ANIMATED = 'Animated'
ATTR_STATE_LOCKED = 'Locked'

# Object Nodes UI - Type info.
OBJECT_NODE_TYPE_INFO_OBJECT_VALUE = 'object'
OBJECT_NODE_TYPE_INFO_MARKER_VALUE = 'marker'
OBJECT_NODE_TYPE_INFO_CAMERA_VALUE = 'camera'
OBJECT_NODE_TYPE_INFO_BUNDLE_VALUE = 'bundle'
OBJECT_NODE_TYPE_INFO_LINE_VALUE = 'line'
OBJECT_NODE_TYPE_INFO_LIST = [
    OBJECT_NODE_TYPE_INFO_OBJECT_VALUE,
    OBJECT_NODE_TYPE_INFO_MARKER_VALUE,
    OBJECT_NODE_TYPE_INFO_CAMERA_VALUE,
    OBJECT_NODE_TYPE_INFO_BUNDLE_VALUE,
    OBJECT_NODE_TYPE_INFO_LINE_VALUE,
]

# Toggle Objects (stored on Collection node)
OBJECT_TOGGLE_CAMERA_ATTR = 'object_toggle_camera'
OBJECT_TOGGLE_LINE_ATTR = 'object_toggle_line'
OBJECT_TOGGLE_MARKER_ATTR = 'object_toggle_marker'
OBJECT_TOGGLE_BUNDLE_ATTR = 'object_toggle_bundle'

OBJECT_TOGGLE_CAMERA_ATTR_TYPE = 'bool'
OBJECT_TOGGLE_LINE_ATTR_TYPE = 'bool'
OBJECT_TOGGLE_MARKER_ATTR_TYPE = 'bool'
OBJECT_TOGGLE_BUNDLE_ATTR_TYPE = 'bool'

OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE = True
OBJECT_TOGGLE_LINE_DEFAULT_VALUE = True
OBJECT_TOGGLE_MARKER_DEFAULT_VALUE = True
OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE = False

# Toggle Attributes (stored on Collection node)
ATTRIBUTE_TOGGLE_ANIMATED_ATTR = 'attribute_toggle_animated'
ATTRIBUTE_TOGGLE_STATIC_ATTR = 'attribute_toggle_static'
ATTRIBUTE_TOGGLE_LOCKED_ATTR = 'attribute_toggle_locked'

ATTRIBUTE_TOGGLE_ANIMATED_ATTR_TYPE = 'bool'
ATTRIBUTE_TOGGLE_STATIC_ATTR_TYPE = 'bool'
ATTRIBUTE_TOGGLE_LOCKED_ATTR_TYPE = 'bool'

ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE = True
ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE = True
ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE = False

# Information to filter invalid input attributes from the Solver UI.
ATTR_INVALID_OBJECT_TYPES = [
    'imageplane',
    'marker',
]

# The Column Names for the Object Model (used to display input Objects
# to the user).
OBJECT_COLUMN_NAME_NODE = 'Node'
OBJECT_COLUMN_NAME_STATUS = 'Status'
OBJECT_COLUMN_NAME_WEIGHT = 'Weight'
OBJECT_COLUMN_NAME_DEVIATION_FRAME = 'Frame Dev (px)'
OBJECT_COLUMN_NAME_DEVIATION_AVERAGE = 'Avg Dev (px)'
OBJECT_COLUMN_NAME_DEVIATION_MAXIMUM = 'Max Dev (px @ frame)'
OBJECT_COLUMN_NAME_UUID = 'Maya Node UUID'

# The Column Names for the Attribute Model (used to display output
# Attributes to the user).
ATTR_COLUMN_NAME_ATTRIBUTE = 'Attr'
ATTR_COLUMN_NAME_STATUS = 'Status'
ATTR_COLUMN_NAME_STATE = 'State'
ATTR_COLUMN_NAME_VALUE_MIN_MAX = 'Range'
ATTR_COLUMN_NAME_VALUE_STIFFNESS = 'Stiffness'
ATTR_COLUMN_NAME_VALUE_SMOOTHNESS = 'Smoothness'
ATTR_COLUMN_NAME_UUID = 'Maya Node UUID'

# The Column Names for the Solver Model (used to display Solver Steps
# to the user).
SOLVER_COLUMN_NAME_ENABLED = 'Enabled'
SOLVER_COLUMN_NAME_FRAMES = 'Frames'
SOLVER_COLUMN_NAME_ATTRIBUTES = 'Attributes'
SOLVER_COLUMN_NAME_STRATEGY = 'Strategy'

# Frame 'Range Type' enumeration values
RANGE_TYPE_CURRENT_FRAME_VALUE = 0
RANGE_TYPE_TIMELINE_INNER_VALUE = 1
RANGE_TYPE_TIMELINE_OUTER_VALUE = 2
RANGE_TYPE_CUSTOM_FRAMES_VALUE = 3

RANGE_TYPE_CURRENT_FRAME_NAME = 'Current Frame'
RANGE_TYPE_TIMELINE_INNER_NAME = 'Timeline (Inner)'
RANGE_TYPE_TIMELINE_OUTER_NAME = 'Timeline (Outer)'
RANGE_TYPE_CUSTOM_FRAMES_NAME = 'Custom Frames'

RANGE_TYPE_VALUE_LIST = [
    RANGE_TYPE_CURRENT_FRAME_VALUE,
    RANGE_TYPE_TIMELINE_INNER_VALUE,
    RANGE_TYPE_TIMELINE_OUTER_VALUE,
    RANGE_TYPE_CUSTOM_FRAMES_VALUE,
]

RANGE_TYPE_NAME_LIST = [
    RANGE_TYPE_CURRENT_FRAME_NAME,
    RANGE_TYPE_TIMELINE_INNER_NAME,
    RANGE_TYPE_TIMELINE_OUTER_NAME,
    RANGE_TYPE_CUSTOM_FRAMES_NAME,
]
# NOTE: RANGE_TYPE_VALUE_LIST and RANGE_TYPE_NAME_LIST are expected to
# be in order.
assert len(RANGE_TYPE_NAME_LIST) == len(RANGE_TYPE_VALUE_LIST)

# Solver Tab values
SOLVER_TAB_BASIC_VALUE = 'basic'
SOLVER_TAB_STANDARD_VALUE = 'standard'
SOLVER_TAB_CAMERA_VALUE = 'camera'
SOLVER_TAB_VALUE_LIST = [
    SOLVER_TAB_BASIC_VALUE,
    SOLVER_TAB_STANDARD_VALUE,
    SOLVER_TAB_CAMERA_VALUE,
]

# Solver Tab (stored on Collection node)
SOLVER_TAB_ATTR = 'solver_tab'
SOLVER_TAB_ATTR_TYPE = 'string'
SOLVER_TAB_DEFAULT_VALUE = 'basic'

# Solver Frame Range Type (stored on Collection node)
SOLVER_RANGE_TYPE_ATTR = 'solver_range_type'
SOLVER_RANGE_TYPE_ATTR_TYPE = 'byte'  # 8-bit integer
SOLVER_RANGE_TYPE_DEFAULT_VALUE = RANGE_TYPE_TIMELINE_INNER_VALUE

# Solver Frames (stored on Collection node)
SOLVER_FRAMES_ATTR = 'solver_frames'
SOLVER_FRAMES_ATTR_TYPE = 'string'
SOLVER_FRAMES_DEFAULT_VALUE = None  # No default value.

# Solver Frames (stored on Collection node)
SOLVER_INCREMENT_BY_FRAME_ATTR = 'solver_increment_by_frame'
SOLVER_INCREMENT_BY_FRAME_ATTR_TYPE = 'long'
SOLVER_INCREMENT_BY_FRAME_DEFAULT_VALUE = 1

# Solver User Frames (stored on Collection node)
SOLVER_USER_FRAMES_ATTR = 'solver_user_frames'
SOLVER_USER_FRAMES_ATTR_TYPE = 'string'
SOLVER_USER_FRAMES_DEFAULT_VALUE = None  # No default value.

# Solver Use Per-Marker Frames (stored on Collection node)
SOLVER_USE_PER_MARKER_FRAMES_ATTR = 'solver_use_per_marker_frames'
SOLVER_USE_PER_MARKER_FRAMES_ATTR_TYPE = 'bool'
SOLVER_USE_PER_MARKER_FRAMES_DEFAULT_VALUE = True

# Solver Per-Marker Frames (stored on Collection node)
SOLVER_PER_MARKER_FRAMES_ATTR = 'solver_per_marker_frames'
SOLVER_PER_MARKER_FRAMES_ATTR_TYPE = 'long'
SOLVER_PER_MARKER_FRAMES_DEFAULT_VALUE = 3

# Solver Use Span Frames (stored on Collection node)
SOLVER_USE_SPAN_FRAMES_ATTR = 'solver_use_span_frames'
SOLVER_USE_SPAN_FRAMES_ATTR_TYPE = 'bool'
SOLVER_USE_SPAN_FRAMES_DEFAULT_VALUE = True

# Solver Span Frames (stored on Collection node)
SOLVER_SPAN_FRAMES_ATTR = 'solver_span_frames'
SOLVER_SPAN_FRAMES_ATTR_TYPE = 'long'
SOLVER_SPAN_FRAMES_DEFAULT_VALUE = 10

# Solver Root Frames (stored on Collection node)
SOLVER_ROOT_FRAMES_ATTR = 'solver_root_frames'
SOLVER_ROOT_FRAMES_ATTR_TYPE = 'string'
SOLVER_ROOT_FRAMES_DEFAULT_VALUE = None  # No default value.

# Solver Only Root Frames (stored on Collection node)
SOLVER_ONLY_ROOT_FRAMES_ATTR = 'solver_only_root_frames'
SOLVER_ONLY_ROOT_FRAMES_ATTR_TYPE = 'bool'
SOLVER_ONLY_ROOT_FRAMES_DEFAULT_VALUE = False

# Solver Global Solve (stored on Collection node)
SOLVER_GLOBAL_SOLVE_ATTR = 'solver_global_solve'
SOLVER_GLOBAL_SOLVE_ATTR_TYPE = 'bool'
SOLVER_GLOBAL_SOLVE_DEFAULT_VALUE = False

# Solver Evaluate Complex Node Graphs (stored on Collection node)
SOLVER_EVAL_COMPLEX_GRAPHS_ATTR = 'solver_eval_complex_node_graphs'
SOLVER_EVAL_COMPLEX_GRAPHS_ATTR_TYPE = 'bool'
SOLVER_EVAL_COMPLEX_GRAPHS_DEFAULT_VALUE = False


# Solver Type Mode
#
# The plug-in doesn't actually define a 'default' with an index, so
# this is a special value for the solver UI only.
SOLVER_TYPE_DEFAULT = 255
SOLVER_TYPE_CMINPACK_LMDIF = mmapi_const.SOLVER_TYPE_CMINPACK_LMDIF
SOLVER_TYPE_CMINPACK_LMDER = mmapi_const.SOLVER_TYPE_CMINPACK_LMDER
SOLVER_TYPE_CERES_LMDIF = mmapi_const.SOLVER_TYPE_CERES_LMDIF
SOLVER_TYPE_LIST = [
    SOLVER_TYPE_DEFAULT,
    SOLVER_TYPE_CMINPACK_LMDIF,
    SOLVER_TYPE_CMINPACK_LMDER,
    SOLVER_TYPE_CERES_LMDIF,
]

SOLVER_TYPE_DEFAULT_LABEL = 'Default'
SOLVER_TYPE_CMINPACK_LMDIF_LABEL = 'CMinpack LMDIF'
SOLVER_TYPE_CMINPACK_LMDER_LABEL = 'CMinpack LMDER'
SOLVER_TYPE_CERES_LMDIF_LABEL = 'Ceres LMDIF'
SOLVER_TYPE_LABEL_LIST = [
    SOLVER_TYPE_DEFAULT_LABEL,
    SOLVER_TYPE_CMINPACK_LMDIF_LABEL,
    SOLVER_TYPE_CMINPACK_LMDER_LABEL,
    SOLVER_TYPE_CERES_LMDIF_LABEL,
]

SOLVER_TYPE_LABEL_VALUE_LIST = [
    (SOLVER_TYPE_DEFAULT_LABEL, SOLVER_TYPE_DEFAULT),
    (SOLVER_TYPE_CMINPACK_LMDIF_LABEL, SOLVER_TYPE_CMINPACK_LMDIF),
    (SOLVER_TYPE_CMINPACK_LMDER_LABEL, SOLVER_TYPE_CMINPACK_LMDER),
    (SOLVER_TYPE_CERES_LMDIF_LABEL, SOLVER_TYPE_CERES_LMDIF),
]

# Hide the Solver Type mode in the UI.
SOLVER_TYPE_WIDGET_VISIBLE = False

# Solver Scene Graph (stored on Collection node)
SOLVER_TYPE_ATTR = 'solver_type'
SOLVER_TYPE_ATTR_TYPE = 'long'
SOLVER_TYPE_DEFAULT_VALUE = SOLVER_TYPE_DEFAULT


# Solver Scene Graph Mode
SCENE_GRAPH_MODE_AUTO = 0
SCENE_GRAPH_MODE_MAYA_DAG = 1
SCENE_GRAPH_MODE_MM_SCENE_GRAPH = 2
SCENE_GRAPH_MODE_LIST = [
    SCENE_GRAPH_MODE_AUTO,
    SCENE_GRAPH_MODE_MAYA_DAG,
    SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
]

SCENE_GRAPH_MODE_AUTO_LABEL = 'Auto'
SCENE_GRAPH_MODE_MAYA_DAG_LABEL = 'Maya DAG'
SCENE_GRAPH_MODE_MM_SCENE_GRAPH_LABEL = 'MM Scene Graph'
SCENE_GRAPH_MODE_LABEL_LIST = [
    SCENE_GRAPH_MODE_AUTO_LABEL,
    SCENE_GRAPH_MODE_MAYA_DAG_LABEL,
    SCENE_GRAPH_MODE_MM_SCENE_GRAPH_LABEL,
]

SCENE_GRAPH_MODE_LABEL_VALUE_LIST = [
    (SCENE_GRAPH_MODE_AUTO_LABEL, SCENE_GRAPH_MODE_AUTO),
    (SCENE_GRAPH_MODE_MAYA_DAG_LABEL, SCENE_GRAPH_MODE_MAYA_DAG),
    (SCENE_GRAPH_MODE_MM_SCENE_GRAPH_LABEL, SCENE_GRAPH_MODE_MM_SCENE_GRAPH),
]

# Hide the Scene Graph mode in the UI, the value defaults to 'auto',
# which should do work out the fastest scene graph by default.
SCENE_GRAPH_MODE_WIDGET_VISIBLE = False

# Solver Scene Graph (stored on Collection node)
SOLVER_SCENE_GRAPH_MODE_ATTR = 'solver_scene_graph'
SOLVER_SCENE_GRAPH_MODE_ATTR_TYPE = 'long'
SOLVER_SCENE_GRAPH_MODE_DEFAULT_VALUE = SCENE_GRAPH_MODE_AUTO

# Solver Origin Frame (stored on Collection node)
SOLVER_ORIGIN_FRAME_ATTR = 'solver_origin_frame'
SOLVER_ORIGIN_FRAME_ATTR_TYPE = 'long'
SOLVER_ORIGIN_FRAME_DEFAULT_VALUE = 0

# Solver Scene Scale (stored on Collection node)
SOLVER_SCENE_SCALE_ATTR = 'solver_scene_scale'
SOLVER_SCENE_SCALE_ATTR_TYPE = 'double'
SOLVER_SCENE_SCALE_DEFAULT_VALUE = 10.0

# Solver Solve Lens Distortion (stored on Collection node)
SOLVER_SOLVE_FOCAL_LENGTH_ATTR = 'solver_solve_focal_length'
SOLVER_SOLVE_FOCAL_LENGTH_ATTR_TYPE = 'bool'
SOLVER_SOLVE_FOCAL_LENGTH_DEFAULT_VALUE = True

# Solver Solve Lens Distortion (stored on Collection node)
SOLVER_SOLVE_LENS_DISTORTION_ATTR = 'solver_solve_lens_distortion'
SOLVER_SOLVE_LENS_DISTORTION_ATTR_TYPE = 'bool'
SOLVER_SOLVE_LENS_DISTORTION_DEFAULT_VALUE = True

# Descriptions for solvers
SOLVER_BASIC_DESC_DEFAULT = 'Solve only animated attributes on frames.'
SOLVER_STD_DESC_DEFAULT = (
    'Solve animated and static attributes on root frames, '
    'then solve animated attributes on frames.'
)
SOLVER_CAM_DESC_DEFAULT = (
    'Solve (free-move) Camera from scratch with only Markers as input.'
)


# Attribute Type
ATTR_TYPE_TRANSLATE = 'attr_type_translate'
ATTR_TYPE_ROTATE = 'attr_type_rotate'
ATTR_TYPE_SCALE = 'attr_type_scale'
ATTR_TYPE_CAMERA = 'attr_type_camera'
ATTR_TYPE_LENS = 'attr_type_lens'
ATTR_TYPE_OTHER = 'attr_type_other'

# Icon names
OBJECT_ICON_NAME = ':/mmSolver_object.png'
MARKER_ICON_NAME = ':/mmSolver_marker.png'
BUNDLE_ICON_NAME = ':/mmSolver_bundle.png'
CAMERA_ICON_NAME = ':/mmSolver_camera.png'
LINE_ICON_NAME = ':/mmSolver_line.png'
PLUG_ICON_NAME = ':/mmSolver_plug.png'
NODE_ICON_NAME = ':/mmSolver_node.png'
ATTR_ICON_NAME = ':/mmSolver_attr.png'
ATTR_TYPE_TRANSLATE_ICON_NAME = ':/mmSolver_attr_type_translate.png'
ATTR_TYPE_ROTATE_ICON_NAME = ':/mmSolver_attr_type_rotate.png'
ATTR_TYPE_SCALE_ICON_NAME = ':/mmSolver_attr_type_scale.png'
ATTR_TYPE_CAMERA_ICON_NAME = ':/mmSolver_attr_type_camera.png'
ATTR_TYPE_LENS_ICON_NAME = ':/mmSolver_attr_type_lens.png'
ATTR_TYPE_OTHER_ICON_NAME = ':/mmSolver_attr_type_other.png'
SOLVER_STEP_ICON_NAME = ':/mmSolver_solverStep.png'
