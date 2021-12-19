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
Contains constant values for the Convert To Marker tool.
"""

import mmSolver.utils.constant as const

WINDOW_TITLE = 'Convert to Marker'

# Constants for frame range mode.
FRAME_RANGE_MODE_TIMELINE_INNER_VALUE = const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE
FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE = const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE
FRAME_RANGE_MODE_CUSTOM_VALUE = const.FRAME_RANGE_MODE_CUSTOM_VALUE
FRAME_RANGE_MODE_VALUES = [
    FRAME_RANGE_MODE_TIMELINE_INNER_VALUE,
    FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE,
    FRAME_RANGE_MODE_CUSTOM_VALUE,
]
FRAME_RANGE_MODE_TIMELINE_INNER_LABEL = 'Timeline (Inner)'
FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL = 'Timeline (Outer)'
FRAME_RANGE_MODE_CUSTOM_LABEL = 'Custom'
FRAME_RANGE_MODE_LABELS = [
    FRAME_RANGE_MODE_TIMELINE_INNER_LABEL,
    FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL,
    FRAME_RANGE_MODE_CUSTOM_LABEL,
]

# Constants for bake mode.
BUNDLE_POSITION_MODE_ORIGIN_VALUE = 'origin'  # Bundle stays at the origin.
BUNDLE_POSITION_MODE_SOURCE_VALUE = 'source'  # Bundle moves to the source transform.
BUNDLE_POSITION_MODE_VALUES = [
    BUNDLE_POSITION_MODE_ORIGIN_VALUE,
    BUNDLE_POSITION_MODE_SOURCE_VALUE,
]
BUNDLE_POSITION_MODE_ORIGIN_LABEL = '3D Origin'
BUNDLE_POSITION_MODE_SOURCE_LABEL = 'Source Transform'
BUNDLE_POSITION_MODE_LABELS = [
    BUNDLE_POSITION_MODE_ORIGIN_LABEL,
    BUNDLE_POSITION_MODE_SOURCE_LABEL,
]

# Default Values
DEFAULT_FRAME_RANGE_MODE = FRAME_RANGE_MODE_TIMELINE_INNER_VALUE
DEFAULT_FRAME_START = 1001
DEFAULT_FRAME_END = 1101
DEFAULT_BUNDLE_POSITION_MODE = BUNDLE_POSITION_MODE_ORIGIN_VALUE
DEFAULT_DELETE_STATIC_ANIM_CURVES = 1

# Config files
CONFIG_FRAME_RANGE_MODE_KEY = 'mmSolver_convertmarker_frameRangeMode'
CONFIG_FRAME_START_KEY = 'mmSolver_convertmarker_frameStart'
CONFIG_FRAME_END_KEY = 'mmSolver_convertmarker_frameEnd'
CONFIG_BUNDLE_POSITION_MODE_KEY = 'mmSolver_convertmarker_bundlePositionMode'
CONFIG_DELETE_STATIC_ANIM_CURVES_KEY = 'mmSolver_convertmarker_deleteStaticAnimCurves'
