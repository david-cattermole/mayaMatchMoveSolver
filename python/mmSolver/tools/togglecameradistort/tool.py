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
The Toggle the Camera Distortion mode.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.camera as utils_camera

LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggle the effect of lens distortion in the given camera.
    """
    mmapi.load_plugin()

    # Get selected camera(s).
    sel = maya.cmds.ls(sl=True, long=True)
    node_filtered = mmapi.filter_nodes_into_categories(sel)
    cams = node_filtered['camera']
    cams = [x for x in cams if utils_camera.is_not_startup_cam(x)]

    cams_to_toggle = []
    if len(cams) == 0:
        # Create a lens in the active viewport camera.
        model_editor = utils_viewport.get_active_model_editor()
        if model_editor is None:
            msg = 'Please select an active 3D viewport.'
            LOG.warning(msg)
            return
        cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
        node = cam_shp
        if node is None:
            msg = 'Please select an active viewport to get a camera.'
            LOG.error(msg)
            return
        if utils_camera.is_startup_cam(node) is True:
            msg = "Cannot create Lens on 'persp' camera."
            LOG.error(msg)
            return
        cam_tfm, cam_shp = utils_camera.get_camera(node)
        cam = mmapi.Camera(shape=cam_shp)
        cams_to_toggle.append(cam)

    elif len(cams) > 0:
        # Create a Lens under the selected cameras.
        for node in cams:
            cam_tfm, cam_shp = utils_camera.get_camera(node)
            cam = mmapi.Camera(shape=cam_shp)
            cams_to_toggle.append(cam)

    else:
        LOG.error('Should not get here.')
        return

    for cam in cams_to_toggle:
        # Set lens mode (enabled/disabled)
        enable = cam.get_lens_enable()
        if enable is None:
            LOG.error('Cannot toggle lens distortion on camera; cam=%r', cam)
            continue
        cam.set_lens_enable(not enable)
    maya.cmds.select(sel, replace=True)
    return
