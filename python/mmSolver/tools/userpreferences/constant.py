# Copyright (C) 2020 David Cattermole.
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
Contains constant data to be used for user preferences.
"""

CONFIG_FILE_NAME = 'user_preferences.json'


# The different value types a preference is allowed to have.
#
# Limited to a list of hard-coded integer values.
TYPE_ENUMERATION_INT = 'enumeration_int'
# Any string value.
TYPE_STRING = 'string'


# "Register Events - Add New Markers To" preference.
REG_EVNT_ADD_NEW_MKR_TO_KEY = 'register_events/add_new_markers_to'
REG_EVNT_ADD_NEW_MKR_TO_TYPE = TYPE_ENUMERATION_INT
REG_EVNT_ADD_NEW_MKR_TO_NONE_VALUE = 0
REG_EVNT_ADD_NEW_MKR_TO_NONE_LABEL = 'None'
REG_EVNT_ADD_NEW_MKR_TO_ACTIVE_COL_VALUE = 1
REG_EVNT_ADD_NEW_MKR_TO_ACTIVE_COL_LABEL = 'Active Collection'
REG_EVNT_ADD_NEW_MKR_TO_VALUES = [
    REG_EVNT_ADD_NEW_MKR_TO_NONE_VALUE,
    REG_EVNT_ADD_NEW_MKR_TO_ACTIVE_COL_VALUE,
]
REG_EVNT_ADD_NEW_MKR_TO_LABELS = [
    REG_EVNT_ADD_NEW_MKR_TO_NONE_LABEL,
    REG_EVNT_ADD_NEW_MKR_TO_ACTIVE_COL_LABEL,
]


# "Register Events - Add New Line To" preference.
REG_EVNT_ADD_NEW_LINE_TO_KEY = 'register_events/add_new_lines_to'
REG_EVNT_ADD_NEW_LINE_TO_TYPE = TYPE_ENUMERATION_INT
REG_EVNT_ADD_NEW_LINE_TO_NONE_VALUE = 0
REG_EVNT_ADD_NEW_LINE_TO_NONE_LABEL = 'None'
REG_EVNT_ADD_NEW_LINE_TO_ACTIVE_COL_VALUE = 1
REG_EVNT_ADD_NEW_LINE_TO_ACTIVE_COL_LABEL = 'Active Collection'
REG_EVNT_ADD_NEW_LINE_TO_VALUES = [
    REG_EVNT_ADD_NEW_LINE_TO_NONE_VALUE,
    REG_EVNT_ADD_NEW_LINE_TO_ACTIVE_COL_VALUE,
]
REG_EVNT_ADD_NEW_LINE_TO_LABELS = [
    REG_EVNT_ADD_NEW_LINE_TO_NONE_LABEL,
    REG_EVNT_ADD_NEW_LINE_TO_ACTIVE_COL_LABEL,
]


# "Load Marker UI - Distortion Mode Default" preference.
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY = 'load_marker_ui/distortion_mode_default'
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_TYPE = TYPE_ENUMERATION_INT
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_VALUE = 1
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_LABEL = 'Undistorted'
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_VALUE = 0
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_LABEL = 'Distorted'
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_VALUES = [
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_VALUE,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_VALUE,
]
LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_LABELS = [
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_LABEL,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_LABEL,
]


# "Load Marker UI - Use Overscan Default" preference.
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY = 'load_marker_ui/use_overscan_default'
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TYPE = TYPE_ENUMERATION_INT
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_VALUE = 1
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_LABEL = 'Yes'
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_FALSE_VALUE = 0
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_FALSE_LABEL = 'No'
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_VALUES = [
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_VALUE,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_FALSE_VALUE,
]
LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_LABELS = [
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_LABEL,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_FALSE_LABEL,
]


# "Load Marker UI - Load Bundle Positions Default" preference.
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY = 'load_marker_ui/load_bundle_positions_default'
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TYPE = TYPE_ENUMERATION_INT
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_VALUE = 1
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_LABEL = 'Yes'
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_FALSE_VALUE = 0
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_FALSE_LABEL = 'No'
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_VALUES = [
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_VALUE,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_FALSE_VALUE,
]
LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_LABELS = [
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_LABEL,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_FALSE_LABEL,
]


# "Solver UI - Validate on open" preference.
#
# This option is deprecated and is not used.
SOLVER_UI_VALIDATE_ON_OPEN_KEY = 'solver_ui/validate_on_open'
SOLVER_UI_VALIDATE_ON_OPEN_TYPE = TYPE_ENUMERATION_INT
SOLVER_UI_VALIDATE_ON_OPEN_TRUE_VALUE = 1
SOLVER_UI_VALIDATE_ON_OPEN_TRUE_LABEL = 'Yes'
SOLVER_UI_VALIDATE_ON_OPEN_FALSE_VALUE = 0
SOLVER_UI_VALIDATE_ON_OPEN_FALSE_LABEL = 'No'
SOLVER_UI_VALIDATE_ON_OPEN_VALUES = [
    SOLVER_UI_VALIDATE_ON_OPEN_TRUE_VALUE,
    SOLVER_UI_VALIDATE_ON_OPEN_FALSE_VALUE,
]
SOLVER_UI_VALIDATE_ON_OPEN_LABELS = [
    SOLVER_UI_VALIDATE_ON_OPEN_TRUE_LABEL,
    SOLVER_UI_VALIDATE_ON_OPEN_FALSE_LABEL,
]


# "Solver UI - Show Validate Button" preference.
#
# This option is deprecated and is not used.
SOLVER_UI_SHOW_VALIDATE_BTN_KEY = 'solver_ui/show_validate_button'
SOLVER_UI_SHOW_VALIDATE_BTN_TYPE = TYPE_ENUMERATION_INT
SOLVER_UI_SHOW_VALIDATE_BTN_TRUE_VALUE = 1
SOLVER_UI_SHOW_VALIDATE_BTN_TRUE_LABEL = 'Yes'
SOLVER_UI_SHOW_VALIDATE_BTN_FALSE_VALUE = 0
SOLVER_UI_SHOW_VALIDATE_BTN_FALSE_LABEL = 'No'
SOLVER_UI_SHOW_VALIDATE_BTN_VALUES = [
    SOLVER_UI_SHOW_VALIDATE_BTN_TRUE_VALUE,
    SOLVER_UI_SHOW_VALIDATE_BTN_FALSE_VALUE,
]
SOLVER_UI_SHOW_VALIDATE_BTN_LABELS = [
    SOLVER_UI_SHOW_VALIDATE_BTN_TRUE_LABEL,
    SOLVER_UI_SHOW_VALIDATE_BTN_FALSE_LABEL,
]


# "Solver UI - Show Object Relationships" preference.
#
# This option is deprecated and is not used.
SOLVER_UI_ALLOW_OBJECT_RELATIONS_KEY = 'solver_ui/allow_object_relationships'
SOLVER_UI_ALLOW_OBJECT_RELATIONS_TYPE = TYPE_ENUMERATION_INT
SOLVER_UI_ALLOW_OBJECT_RELATIONS_TRUE_VALUE = 1
SOLVER_UI_ALLOW_OBJECT_RELATIONS_TRUE_LABEL = 'Yes'
SOLVER_UI_ALLOW_OBJECT_RELATIONS_FALSE_VALUE = 0
SOLVER_UI_ALLOW_OBJECT_RELATIONS_FALSE_LABEL = 'No'
SOLVER_UI_ALLOW_OBJECT_RELATIONS_VALUES = [
    SOLVER_UI_ALLOW_OBJECT_RELATIONS_TRUE_VALUE,
    SOLVER_UI_ALLOW_OBJECT_RELATIONS_FALSE_VALUE,
]
SOLVER_UI_ALLOW_OBJECT_RELATIONS_LABELS = [
    SOLVER_UI_ALLOW_OBJECT_RELATIONS_TRUE_LABEL,
    SOLVER_UI_ALLOW_OBJECT_RELATIONS_FALSE_LABEL,
]


# "Solver UI - Minimal UI While Solving" preference.
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY = 'solver_ui/minimal_ui_while_solving'
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TYPE = TYPE_ENUMERATION_INT
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_VALUE = 1
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_LABEL = 'Yes'
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_FALSE_VALUE = 0
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_FALSE_LABEL = 'No'
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_VALUES = [
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_VALUE,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_FALSE_VALUE,
]
SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_LABELS = [
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_LABEL,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_FALSE_LABEL,
]


# "Create Controller - Shape Node Type" preference.
CREATE_CONTROLLER_SHAPE_KEY = 'create_controller/shape_node_type'
CREATE_CONTROLLER_SHAPE_TYPE = TYPE_ENUMERATION_INT
CREATE_CONTROLLER_SHAPE_GROUP_VALUE = 0
CREATE_CONTROLLER_SHAPE_GROUP_LABEL = 'Group'
CREATE_CONTROLLER_SHAPE_LOCATOR_VALUE = 1
CREATE_CONTROLLER_SHAPE_LOCATOR_LABEL = 'Locator'
CREATE_CONTROLLER_SHAPE_VALUES = [
    CREATE_CONTROLLER_SHAPE_GROUP_VALUE,
    CREATE_CONTROLLER_SHAPE_LOCATOR_VALUE,
]
CREATE_CONTROLLER_SHAPE_LABELS = [
    CREATE_CONTROLLER_SHAPE_GROUP_LABEL,
    CREATE_CONTROLLER_SHAPE_LOCATOR_LABEL,
]


# Key to Values mapping.
VALUES_MAP = {
    REG_EVNT_ADD_NEW_MKR_TO_KEY: REG_EVNT_ADD_NEW_MKR_TO_VALUES,
    REG_EVNT_ADD_NEW_LINE_TO_KEY: REG_EVNT_ADD_NEW_LINE_TO_VALUES,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY: LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_VALUES,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY: LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_VALUES,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY: LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_VALUES,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY: SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_VALUES,
    CREATE_CONTROLLER_SHAPE_KEY: CREATE_CONTROLLER_SHAPE_VALUES,
}


# Key to Labels mapping.
LABELS_MAP = {
    REG_EVNT_ADD_NEW_MKR_TO_KEY: REG_EVNT_ADD_NEW_MKR_TO_LABELS,
    REG_EVNT_ADD_NEW_LINE_TO_KEY: REG_EVNT_ADD_NEW_LINE_TO_LABELS,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY: LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_LABELS,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY: LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_LABELS,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY: LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_LABELS,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY: SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_LABELS,
    CREATE_CONTROLLER_SHAPE_KEY: CREATE_CONTROLLER_SHAPE_LABELS,
}


# Key to default values.
DEFAULT_VALUE_MAP = {
    REG_EVNT_ADD_NEW_MKR_TO_KEY: REG_EVNT_ADD_NEW_MKR_TO_ACTIVE_COL_VALUE,
    REG_EVNT_ADD_NEW_LINE_TO_KEY: REG_EVNT_ADD_NEW_LINE_TO_ACTIVE_COL_VALUE,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY: LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_VALUE,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY: LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_VALUE,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY: LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_VALUE,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY: SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TRUE_VALUE,
    CREATE_CONTROLLER_SHAPE_KEY: CREATE_CONTROLLER_SHAPE_LOCATOR_VALUE,
}


# Key to the type of the preference.
VALUE_TYPE_MAP = {
    REG_EVNT_ADD_NEW_MKR_TO_KEY: REG_EVNT_ADD_NEW_MKR_TO_TYPE,
    REG_EVNT_ADD_NEW_LINE_TO_KEY: REG_EVNT_ADD_NEW_LINE_TO_TYPE,
    LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY: LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_TYPE,
    LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY: LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TYPE,
    LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY: LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TYPE,
    SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY: SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_TYPE,
    CREATE_CONTROLLER_SHAPE_KEY: CREATE_CONTROLLER_SHAPE_TYPE,
}


# A list of all the valid keys in the user preferences file.
VALID_KEYS = DEFAULT_VALUE_MAP.keys()
