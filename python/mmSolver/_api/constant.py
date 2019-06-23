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
Constant values used in the API.
"""


# Plug-in names
PLUGIN_NAMES = [
    'mmSolver'
]


# Maya node prefixes and suffixes
MARKER_NAME_PREFIX = 'marker'
MARKER_NAME_SUFFIX = '_MKR'
BUNDLE_NAME_PREFIX = 'bundle'
BUNDLE_NAME_SUFFIX = '_BND'


# list of characters that are not supported in maya for node names.
# Note, only ':' and '_' are not in the list.
BAD_MAYA_CHARS = [
    ' ', '#', '-', '@', '!', '$', '%', '^', '&', '*',
    '+', '=', '/', '\\', '~', '`', '.', ',', '?', ';', '|'
    '(', ')', '[', ']', '{', '}', '<', '>'
    '\'', '\"'
]


# Object Types as constants
OBJECT_TYPE_UNKNOWN = 'unknown'
OBJECT_TYPE_ATTRIBUTE = 'attribute'
OBJECT_TYPE_MARKER = 'marker'
OBJECT_TYPE_CAMERA = 'camera'
OBJECT_TYPE_MARKER_GROUP = 'markergroup'
OBJECT_TYPE_BUNDLE = 'bundle'
OBJECT_TYPE_COLLECTION = 'collection'
OBJECT_TYPE_IMAGE_PLANE = 'imageplane'
OBJECT_TYPE_LIST = [
    OBJECT_TYPE_UNKNOWN,
    OBJECT_TYPE_ATTRIBUTE,
    OBJECT_TYPE_MARKER,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_MARKER_GROUP,
    OBJECT_TYPE_BUNDLE,
    OBJECT_TYPE_COLLECTION,
    OBJECT_TYPE_IMAGE_PLANE,
]


# Solver objects.
SOLVER_DATA_DEFAULT = {
    'enabled': True,
}


# Solver Types
SOLVER_TYPE_LEVMAR = 0
SOLVER_TYPE_CMINPACK_LM = 1


# Attribute States
ATTR_STATE_INVALID = 0
ATTR_STATE_STATIC = 1
ATTR_STATE_ANIMATED = 2
ATTR_STATE_LOCKED = 3


# Auto Differencing Types
AUTO_DIFF_TYPE_FORWARD = 0
AUTO_DIFF_TYPE_CENTRAL = 1
AUTO_DIFF_TYPE_LIST = [
    AUTO_DIFF_TYPE_FORWARD,
    AUTO_DIFF_TYPE_CENTRAL,
]


# Default node Colours for Markers and bundles.
MARKER_COLOUR_RGB = (1.0, 0.0, 0.0)
BUNDLE_COLOUR_RGB = (0.0, 1.0, 0.0)


# Node Types.
MARKER_TRANSFORM_NODE_TYPE = 'transform'
MARKER_SHAPE_NODE_TYPE = 'locator'
BUNDLE_TRANSFORM_NODE_TYPE = 'transform'
BUNDLE_SHAPE_NODE_TYPE = 'locator'


# Collection Attribute Names
COLLECTION_ATTR_LONG_NAME_SOLVER_LIST = 'solver_list'
COLLECTION_ATTR_LONG_NAME_SOLVER_RESULTS = 'solver_results'
COLLECTION_ATTR_LONG_NAME_DEVIATION = 'deviation'


# Marker Attribute Names
MARKER_ATTR_LONG_NAME_ENABLE = 'enable'
MARKER_ATTR_LONG_NAME_WEIGHT = 'weight'
MARKER_ATTR_LONG_NAME_DEVIATION = 'deviation'
MARKER_ATTR_LONG_NAME_BUNDLE = 'bundle'
MARKER_ATTR_LONG_NAME_MARKER_NAME = 'markerName'
MARKER_ATTR_LONG_NAME_MARKER_ID = 'markerId'


# Default plate fallback values.
DEFAULT_PLATE_WIDTH = 2048
DEFAULT_PLATE_HEIGHT = 1556
