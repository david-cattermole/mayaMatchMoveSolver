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

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def create_camera(name=None):
    """
    Create a new camera.
    """
    if name is None:
        name = 'camera1'
    assert isinstance(name, basestring)
    tfm = maya.cmds.createNode('transform', name=name)
    shp_name = tfm.rpartition('|')[-1] + 'Shape'
    shp = maya.cmds.createNode('camera', parent=tfm, name=shp_name)
    maya.cmds.setAttr(tfm + '.rotateOrder', 2)  # 2 = ZXY
    cam = mmapi.Camera(shape=shp)
    return cam