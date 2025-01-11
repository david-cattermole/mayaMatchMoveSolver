# Copyright (C) 2018 David Cattermole.
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
Contains constant values for the Load Marker tool.
"""

import mmSolver.tools.userpreferences.constant as userprefs_const


CONFIG_FILE_NAME = "tools_loadmarker.json"

WINDOW_TITLE = 'Load Markers - mmSolver'

# UV Track format
# Keep this in-sync with the 3DEqualizer exporter 'uvtrack_format.py'
UV_TRACK_FORMAT_VERSION_UNKNOWN = -1
UV_TRACK_FORMAT_VERSION_1 = 1
UV_TRACK_FORMAT_VERSION_2 = 2
UV_TRACK_FORMAT_VERSION_3 = 3
UV_TRACK_FORMAT_VERSION_4 = 4

UV_TRACK_HEADER_VERSION_2 = {
    'version': UV_TRACK_FORMAT_VERSION_2,
}

UV_TRACK_HEADER_VERSION_3 = {
    'version': UV_TRACK_FORMAT_VERSION_3,
}

UV_TRACK_HEADER_VERSION_4 = {
    'version': UV_TRACK_FORMAT_VERSION_4,
}


# UI values
LOAD_MODE_NEW_VALUE = 'Create New Markers'
LOAD_MODE_REPLACE_VALUE = 'Replace Selected Markers'

NEW_CAMERA_VALUE = '<Create New>'
NEW_MARKER_GROUP_VALUE = '<Create New>'
NEW_COLLECTION_VALUE = '<Create New>'

DISTORTION_MODE_VALUE = (
    userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_LABEL
)
UNDISTORTION_MODE_VALUE = (
    userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_LABEL
)


# Default values
LOAD_MODE_DEFAULT_VALUE = LOAD_MODE_NEW_VALUE


# Configuration option keys.
#
# Used to look into the Load marker configuration file and get stored
# values.
CONFIG_PATH_LOAD_MODE = 'data/load_mode'
CONFIG_PATH_USE_OVERSCAN = 'data/use_overscan'
CONFIG_PATH_DISTORTION_MODE = 'data/distortion_mode'
CONFIG_PATH_LOAD_BUNDLE_POSITION = 'data/load_bundle_position'
CONFIG_PATH_RENAME_MARKERS = 'data/rename_markers'
CONFIG_PATH_RENAME_MARKERS_NAME = 'data/rename_markers_name'
