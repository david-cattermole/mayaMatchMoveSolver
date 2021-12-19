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
Raycast Marker constants.
"""

WINDOW_TITLE = 'Project Markers on Mesh'

# Constants for frame range mode.
FRAME_RANGE_MODE_CURRENT_FRAME_VALUE = 'current_frame'
FRAME_RANGE_MODE_TIMELINE_INNER_VALUE = 'timeline_inner'
FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE = 'timeline_outer'
FRAME_RANGE_MODE_CUSTOM_VALUE = 'custom'
FRAME_RANGE_MODE_VALUES = [
    FRAME_RANGE_MODE_CURRENT_FRAME_VALUE,
    FRAME_RANGE_MODE_TIMELINE_INNER_VALUE,
    FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE,
    FRAME_RANGE_MODE_CUSTOM_VALUE,
]
FRAME_RANGE_MODE_CURRENT_FRAME_LABEL = 'Current Frame'
FRAME_RANGE_MODE_TIMELINE_INNER_LABEL = 'Timeline (Inner)'
FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL = 'Timeline (Outer)'
FRAME_RANGE_MODE_CUSTOM_LABEL = 'Custom'
FRAME_RANGE_MODE_LABELS = [
    FRAME_RANGE_MODE_CURRENT_FRAME_LABEL,
    FRAME_RANGE_MODE_TIMELINE_INNER_LABEL,
    FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL,
    FRAME_RANGE_MODE_CUSTOM_LABEL,
]


# Constants for frame range mode.
BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE = 'no_change'
BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_VALUE = 'aim_at_camera'
BUNDLE_ROTATE_MODE_MESH_NORMAL_VALUE = 'mesh_normal'
BUNDLE_ROTATE_MODE_VALUES = [
    BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE,
    BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_VALUE,
    BUNDLE_ROTATE_MODE_MESH_NORMAL_VALUE,
]
BUNDLE_ROTATE_MODE_NO_CHANGE_LABEL = 'No Change'
BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_LABEL = 'Aim at Camera'
BUNDLE_ROTATE_MODE_MESH_NORMAL_LABEL = 'Mesh Normal'
BUNDLE_ROTATE_MODE_LABELS = [
    BUNDLE_ROTATE_MODE_NO_CHANGE_LABEL,
    BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_LABEL,
    BUNDLE_ROTATE_MODE_MESH_NORMAL_LABEL,
]


# Default Values
DEFAULT_FRAME_RANGE_MODE = FRAME_RANGE_MODE_CURRENT_FRAME_VALUE
DEFAULT_FRAME_START = 1001
DEFAULT_FRAME_END = 1101
DEFAULT_BUNDLE_ROTATE_MODE = BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE
DEFAULT_BUNDLE_UNLOCK_RELOCK = True

# Config files
CONFIG_FRAME_RANGE_MODE_KEY = 'mmSolver_raycastmarker_frameRangeMode'
CONFIG_FRAME_START_KEY = 'mmSolver_raycastmarker_frameStart'
CONFIG_FRAME_END_KEY = 'mmSolver_raycastmarker_frameEnd'
CONFIG_BUNDLE_ROTATE_MODE_KEY = 'mmSolver_raycastmarker_bundleRotateMode'
CONFIG_BUNDLE_UNLOCK_RELOCK_KEY = 'mmSolver_raycastmarker_bundleUnlockRelock'
