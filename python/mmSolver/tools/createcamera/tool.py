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
The Create Camera tool.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.createcamera.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Create a new Camera.
    """
    mmapi.load_plugin()
    cam = lib.create_camera()
    cam_tfm = cam.get_transform_node()
    maya.cmds.select(cam_tfm, replace=True)
    return
