# Copyright (C) 2021 Patcha Saheb Binginapalli.

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
Fast Bake constants.
"""

import mmSolver.utils.time as time_utils
frame_start, frame_end = time_utils.get_maya_timeline_range_inner()


WINDOW_TITLE = 'Fast Bake'
WINDOW_WIDTH = 250
WINDOW_HEIGHT = 140

# Constants for frame range mode.

FRAME_RANGE_MODE_TIMELINE_INNER_VALUE = 'fb_timeline_inner'
FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE = 'fb_timeline_outer'
FRAME_RANGE_MODE_CUSTOM_VALUE = 'fb_custom'
FRAME_RANGE_MODE_VALUES = [FRAME_RANGE_MODE_TIMELINE_INNER_VALUE,
    					   FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE,
    					   FRAME_RANGE_MODE_CUSTOM_VALUE]

FRAME_RANGE_MODE_TIMELINE_INNER_LABEL = 'Timeline (Inner)'
FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL = 'Timeline (Outer)'
FRAME_RANGE_MODE_CUSTOM_LABEL = 'Custom'
FRAME_RANGE_MODE_LABELS = [FRAME_RANGE_MODE_TIMELINE_INNER_LABEL,
    					   FRAME_RANGE_MODE_TIMELINE_OUTER_LABEL,
						   FRAME_RANGE_MODE_CUSTOM_LABEL]

# Default Values
DEFAULT_FRAME_START = frame_start
DEFAULT_FRAME_END = frame_end
DEFAULT_FRAME_RANGE_MODE = 'fb_timeline_inner'
DEFAULT_SMART_BAKE_STATE = False
DEFAULT_FROM_CHANNELBOX_STATE = False

# Config files
CONFIG_FRAME_RANGE_MODE_KEY = 'mmSolver_fastbake_frameRangeMode'
CONFIG_FRAME_START_KEY = 'mmSolver_fastbake_frameStart'
CONFIG_FRAME_END_KEY = 'mmSolver_fastbake_frameEnd'
CONFIG_SMARTBAKE_KEY = 'mmSolver_fastbake_smartbake'
CONFIG_FROM_CHANNELBOX_KEY = 'mmSolver_fastbake_fromchannelbox'
