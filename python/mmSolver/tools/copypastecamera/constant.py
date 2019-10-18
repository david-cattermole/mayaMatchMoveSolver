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
Contains constant values for the Copy/Paste Camera tool.
"""

# MM Camera format
# Keep this in-sync with the 3DEqualizer exporter 'mmcamera_format.py'
MM_CAMERA_FORMAT_VERSION_UNKNOWN = -1
MM_CAMERA_FORMAT_VERSION_1 = 1
MM_CAMERA_HEADER_VERSION_1 = {
    'version': MM_CAMERA_FORMAT_VERSION_1,
    'data': {}
}


EXT = '.mmcamera'

# Regular Expression matching 'file.ext'.
PATTERN_RE_FILE_EXT = r'(.{1,})(\.)(.{1,})'

# Regular Expression matching 'file.1001.ext' or 'file_1001.ext'.
PATTERN_RE_FILE_FRAME_EXT = r'(.{1,})([\.\_])(\d{1,})(\.)(.{1,})'

# The format expects rotations in ZXY rotation order only.
ROTATE_ORDER = 'zxy'

# Should the tool access the OS disk to query plate details?
TEST_DISK = True

# How many significant digits are floating point 'pixel aspect ratio'
# values expected to need?
PIXEL_ASPECT_RATIO_SIGNIFICANT_DIGITS = 3
