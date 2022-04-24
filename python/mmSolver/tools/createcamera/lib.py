# Copyright (C) 2020 David Cattermole.
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
Library functions for creating Cameras.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def create_camera(name=None, aspect_ratio=None):
    """
    Create a new camera.
    """
    if name is None:
        name = 'camera1'
    if aspect_ratio is None:
        # HD (16:9) aspect ratio - matches the default image plane size.
        aspect_ratio = 16 / 9
    assert isinstance(name, pycompat.TEXT_TYPE)
    tfm = maya.cmds.createNode('transform', name=name)
    shp_name = tfm.rpartition('|')[-1] + 'Shape'
    shp = maya.cmds.createNode('camera', parent=tfm, name=shp_name)
    maya.cmds.setAttr(tfm + '.rotateOrder', 2)  # 2 = ZXY

    # Viewport display helpers.
    maya.cmds.setAttr(tfm + '.displayGateMaskColor', 0.0, 0.0, 0.0, type='double3')
    maya.cmds.setAttr(tfm + '.displayFilmGate', 1)
    maya.cmds.setAttr(tfm + '.displayCameraFrustum', 1)

    # Default to full-frame camera with aspect ratio.
    film_back_width_mm = 36.0
    film_back_width_inches = film_back_width_mm / 25.4
    film_back_height_inches = film_back_width_inches * (1 / aspect_ratio)
    maya.cmds.setAttr(shp + '.horizontalFilmAperture', film_back_width_inches)
    maya.cmds.setAttr(shp + '.verticalFilmAperture', film_back_height_inches)

    cam = mmapi.Camera(shape=shp)
    return cam
