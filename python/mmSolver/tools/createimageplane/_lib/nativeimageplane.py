# Copyright (C) 2020, 2022 David Cattermole.
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
Library functions for creating and modifying image planes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def copy_depth_value(mm_image_plane_tfm, native_image_plane_shp):
    """
    Copy the image plane 'depth' attribute value to the poly image plane.
    """
    if native_image_plane_shp is not None:
        src = native_image_plane_shp + '.depth'
        dst = mm_image_plane_tfm + '.depth'
        value = maya.cmds.getAttr(src)
        maya.cmds.setAttr(dst, value)
    return mm_image_plane_tfm
