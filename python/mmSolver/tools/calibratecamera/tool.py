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
The camera calibration tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.calibratecamera.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Create a default set up ready for camera calibration/
    """
    sel = maya.cmds.ls(selection=True, long=True) or []

    with tools_utils.tool_context(use_undo_chunk=True):
        lib.create_new_setup()

    if len(sel) > 0:
        maya.cmds.select(sel, replace=True)
    else:
        # If the user never had anything selected at the start of the
        # function, we ensure we maintain that for the user.
        maya.cmds.select(clear=True)
    return


def _find_camera_from_selection(sel):
    cam = None
    filtered_nodes = mmapi.filter_nodes_into_categories(sel)
    cam_nodes = filtered_nodes['camera']
    mkr_grp_nodes = filtered_nodes['markergroup']
    mkr_nodes = filtered_nodes['marker']

    # Check selected camera.
    if len(cam_nodes) > 0:
        cam_node = cam_nodes[0]
        cam_tfm, cam_shp = camera_utils.get_camera(cam_node)
        if cam_tfm is not None and cam_shp is not None:
            cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
    if cam is not None and cam.is_valid():
        return cam

    # Check selected marker group.
    if len(mkr_grp_nodes) > 0:
        mkr_grp_node = mkr_grp_nodes[0]
        mkr_grp = mmapi.MarkerGroup(node=mkr_grp_node)
        cam = mkr_grp.get_camera()
    if cam is not None and cam.is_valid():
        return cam

    # Check selected marker.
    if len(mkr_nodes) > 0:
        mkr_node = mkr_nodes[0]
        mkr = mmapi.Marker(node=mkr_node)
        cam = mkr.get_camera()
    if cam is not None and cam.is_valid():
        return cam
    return None


def _get_camera_for_update(sel):
    cam = None
    if len(sel) == 0:
        # Get active viewport camera.
        model_editor = viewport_utils.get_active_model_editor()
        if model_editor is not None:
            cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
            if cam_tfm is not None and cam_shp is not None:
                cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
            if cam is not None and cam.is_valid():
                return cam
    else:
        cam = _find_camera_from_selection(sel)

    return cam


def update():
    """
    User runs this tool to update the camera calibration line up.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []

    cam = _get_camera_for_update(sel)
    if cam is None:
        msg = ('No valid nodes selected; '
               'Select a Camera, Marker Group or Markers.')
        LOG.warn(msg)
        return

    calib_node = None
    if cam is not None:
        calib_node = lib.get_calibrate_node_from_camera(cam)
    else:
        LOG.warn('Could not find camera with calibration node connected.')

    if calib_node is not None:
        with tools_utils.tool_context(use_undo_chunk=True,
                                      disable_viewport=False):
            lib.update_calibrate_values(calib_node)
    else:
        LOG.warn('Could not find calibration node.')

    if len(sel) > 0:
        maya.cmds.select(sel, replace=True)
    else:
        # If the user never had anything selected at the start of the
        # function, we ensure we maintain that for the user.
        maya.cmds.select(clear=True)
    return
