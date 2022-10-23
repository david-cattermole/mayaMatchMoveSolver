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
Aim the selected transform nodes at the current viewport's camera.
"""

import warnings
import maya.cmds
import mmSolver.logger
import mmSolver.utils.viewport as utils_viewport
import mmSolver.tools.cameraaim.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Aims the selected transforms at the active viewport's camera
    transform node.
    """
    sel = maya.cmds.ls(sl=True, type='transform') or []
    if len(sel) == 0:
        LOG.warning('Please select at least one object!')
        return

    # Get camera
    model_editor = utils_viewport.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return
    cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
    if cam_shp is None:
        LOG.warning('Please select an active viewport to get a camera.')
        return

    lib.aim_at_target(sel, cam_tfm, remove_after=True)
    return


def aim_at_camera():
    warnings.warn("Use 'main' function instead.", DeprecationWarning)
    main()
