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
Create a screen-space motion trail, for the selected transform nodes.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.time as utils_time
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.viewport as utils_viewport
import mmSolver.tools.screenspacemotiontrail.lib as lib


LOG = mmSolver.logger.get_logger()


def _get_active_viewport_camera():
    """Get the active viewport camera."""
    cam = None
    model_editor = utils_viewport.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return cam
    cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
    node = cam_shp
    if node is None:
        msg = 'Please select an active viewport to get a camera.'
        LOG.error(msg)
        return cam
    if camera_utils.is_startup_cam(node) is True:
        msg = "Cannot create Markers in 'persp' camera."
        LOG.error(msg)
        return cam
    if maya.cmds.nodeType(node) == 'transform':
        cam = mmapi.Camera(transform=node)
    elif maya.cmds.nodeType(node) == 'camera':
        cam = mmapi.Camera(shape=node)
    else:
        LOG.error('Camera node is invalid; %r', node)
        return cam
    return cam


def main():
    """Create a screen-space motion trail, for the selected objects,
    though the active viewport's camera.
    """
    sel = maya.cmds.ls(selection=True, long=True, type='transform')
    if len(sel) == 0:
        LOG.warn('Please select some objects to create motion trails.')
        return
    cam = _get_active_viewport_camera()
    if cam is None:
        return
    cam_shp = cam.get_shape_node()
    current_frame = maya.cmds.currentTime(query=True)

    # Create the motion trail nodes
    handle_tfms = []
    for node in sel:
        handle_tfm, handle_shp, trail_shp = lib.create_screen_space_motion_trail(
            cam_shp,
            node,
            use_frame_range=False,
        )
        handle_tfms.append(handle_tfm)
    if len(handle_tfms) > 0:
        maya.cmds.showHidden(handle_tfms, above=True)
        maya.cmds.select(handle_tfms, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.currentTime(current_frame, edit=True, update=True)
    maya.cmds.refresh()
    return
