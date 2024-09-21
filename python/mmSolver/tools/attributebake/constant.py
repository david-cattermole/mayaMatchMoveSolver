# Copyright (C) 2021 Patcha Saheb Binginapalli.
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
Attribute (fast) Bake constants.
"""

WINDOW_TITLE = 'Attribute Bake'

# Constants for frame range mode.
FRAME_RANGE_MODE_TIMELINE_INNER_VALUE = 'attrbake_timeline_inner'
FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE = 'attrbake_timeline_outer'
FRAME_RANGE_MODE_CUSTOM_VALUE = 'attrbake_custom'
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
DEFAULT_SMART_BAKE_STATE = False
DEFAULT_FROM_CHANNELBOX_STATE = True
DEFAULT_PRESERVE_OUTSIDE_KEYS_STATE = True

# Config files
CONFIG_FRAME_RANGE_MODE_KEY = 'mmSolver_attrbake_frame_range_mode'
CONFIG_FRAME_START_KEY = 'mmSolver_attrbake_frame_start'
CONFIG_FRAME_END_KEY = 'mmSolver_attrbake_frame_end'
CONFIG_SMART_BAKE_KEY = 'mmSolver_attrbake_smart_bake'
CONFIG_FROM_CHANNELBOX_KEY = 'mmSolver_attrbake_from_channel_box'
CONFIG_PRESERVE_OUTSIDE_KEYS_KEY = 'mmSolver_attrbake_preserve_outside_keys'
