# Copyright (C) 2025 David Cattermole.
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
Attribute Curve Filter constants.
"""

WINDOW_TITLE = 'Attribute Curve Filter Pops'

# Constants for frame range mode.
FRAME_RANGE_MODE_TIMELINE_INNER_VALUE = 'attrcurvefilterpops_timeline_inner'
FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE = 'attrcurvefilterpops_timeline_outer'
FRAME_RANGE_MODE_CUSTOM_VALUE = 'attrcurvefilterpops_custom'
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

FRAME_RANGE_MODE_VALUE_LABEL_MAP = {
    FRAME_RANGE_MODE_TIMELINE_INNER_VALUE: FRAME_RANGE_MODE_TIMELINE_INNER_LABEL,
    FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE: FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL,
    FRAME_RANGE_MODE_CUSTOM_VALUE: FRAME_RANGE_MODE_CUSTOM_LABEL,
}


# Default Values
DEFAULT_FRAME_START = 1
DEFAULT_FRAME_END = 120
DEFAULT_FRAME_RANGE_MODE = FRAME_RANGE_MODE_TIMELINE_INNER_VALUE
DEFAULT_THRESHOLD = 1.0

# Config files
CONFIG_FRAME_RANGE_MODE_KEY = 'mmSolver_attrcurvefilterpops_frame_range_mode'
CONFIG_FRAME_START_KEY = 'mmSolver_attrcurvefilterpops_frame_start'
CONFIG_FRAME_END_KEY = 'mmSolver_attrcurvefilterpops_frame_end'
CONFIG_THRESHOLD_KEY = 'mmSolver_attrcurvefilterpops_threshold'
