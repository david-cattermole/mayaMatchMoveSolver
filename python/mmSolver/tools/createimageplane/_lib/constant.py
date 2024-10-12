# Copyright (C) 2022, 2024 David Cattermole.
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

DEFAULT_IMAGE_SEQUENCE_ATTR_NAME = 'imageSequenceMain'
ALT_1_IMAGE_SEQUENCE_ATTR_NAME = 'imageSequenceAlternate1'
ALT_2_IMAGE_SEQUENCE_ATTR_NAME = 'imageSequenceAlternate2'
ALT_3_IMAGE_SEQUENCE_ATTR_NAME = 'imageSequenceAlternate3'

VALID_INPUT_IMAGE_SEQUENCE_ATTR_NAMES = [
    DEFAULT_IMAGE_SEQUENCE_ATTR_NAME,
    ALT_1_IMAGE_SEQUENCE_ATTR_NAME,
    ALT_2_IMAGE_SEQUENCE_ATTR_NAME,
    ALT_3_IMAGE_SEQUENCE_ATTR_NAME,
]

SHADER_FILE_PATH_ATTR_NAME = 'imageFilePath'
INPUT_COLOR_SPACE_ATTR_NAME = 'inputColorSpace'
OUTPUT_COLOR_SPACE_ATTR_NAME = 'outputColorSpace'

SCENE_LINEAR_FILE_EXTENSIONS = ['exr', 'sxr']
SRGB_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'tga', 'iff']

MM_IMAGE_PLANE_VERSION_ONE = 'mmImagePlaneVersion1'
MM_IMAGE_PLANE_VERSION_TWO = 'mmImagePlaneVersion2'
MM_IMAGE_PLANE_VERSION_LIST = [
    MM_IMAGE_PLANE_VERSION_ONE,
    MM_IMAGE_PLANE_VERSION_TWO,
]

MM_IMAGE_PLANE_SHAPE_V1 = 'mmImagePlaneShape'
MM_IMAGE_PLANE_SHAPE_V2 = 'mmImagePlaneShape2'
MM_IMAGE_PLANE_SHAPE_LIST = [MM_IMAGE_PLANE_SHAPE_V1, MM_IMAGE_PLANE_SHAPE_V2]
MM_IMAGE_PLANE_SHAPE_MAP = {
    MM_IMAGE_PLANE_VERSION_ONE: MM_IMAGE_PLANE_SHAPE_V1,
    MM_IMAGE_PLANE_VERSION_TWO: MM_IMAGE_PLANE_SHAPE_V2,
}

MM_IMAGE_PLANE_TRANSFORM = 'mmImagePlaneTransform'
