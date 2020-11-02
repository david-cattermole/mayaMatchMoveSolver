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

DISTORTION_MODE_VALUE = 'Distorted'
UNDISTORTION_MODE_VALUE = 'Undistorted'


# Default values
LOAD_MODE_DEFAULT_VALUE = LOAD_MODE_NEW_VALUE
DISTORTION_MODE_DEFAULT_VALUE = UNDISTORTION_MODE_VALUE
LOAD_BUNDLE_POS_DEFAULT_VALUE = True
USE_OVERSCAN_DEFAULT_VALUE = True
