# Copyright (C) 2018, 2019, 2021 David Cattermole, Kazuma Tonegawa.
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
The Center 2D tool with offset features.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.reproject as reproject_utils

LOG = mmSolver.logger.get_logger()


def _update_ui_nodes():
    import mmSolver.tools.centertwodee.ui.centertwodee_window as window

    window_instance = window.CenterTwoDeeWindow.get_instance()
    if window_instance is not None:
        window_instance.update_nodes()


def main():
    """
    Center the selected transform onto the camera view.

    .. todo::

        - Allow 2D Center on selected vertices.

        - Support Stereo-camera setups (center both cameras, and ensure
          both have the same zoom).

        - Allow centering on multiple objects at once. We will center
          on the middle of all transforms.

    """
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        _update_ui_nodes()
        return

    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        msg = 'Please select an active 3D viewport to get a camera.'
        LOG.warning(msg)
        _update_ui_nodes()
        return

    try:
        # Set the solver 'running' flag so that the Solver UI does not
        # update.
        mmapi.set_solver_running(True)

        save_sel = maya.cmds.ls(selection=True, long=True) or []

        # Get selection
        objects = (
            maya.cmds.ls(
                selection=True,
                long=True,
            )
            or []
        )

        # Filter out selected imagePlanes.
        objects_tmp = list(objects)
        objects = []
        for obj in objects_tmp:
            shps = (
                maya.cmds.listRelatives(
                    obj, shapes=True, fullPath=True, type='imagePlane'
                )
                or []
            )
            if len(shps) == 0:
                objects.append(obj)

        # Create centering node network.
        if len(objects) == 0:
            msg = 'No objects selected, removing 2D centering.'
            LOG.warning(msg)
            mmapi.load_plugin()
            reproject_utils.remove_reprojection_from_camera(cam_tfm, cam_shp)
            reproject_utils.reset_pan_zoom(cam_tfm, cam_shp)
        else:
            LOG.warning('Applying 2D centering to %r', objects)
            mmapi.load_plugin()
            reproject_utils.remove_reprojection_from_camera(cam_tfm, cam_shp)

            reproj_node = reproject_utils.create_reprojection_on_camera(
                cam_tfm, cam_shp
            )
            reproject_utils.connect_objects_to_reprojection(objects, reproj_node)

            # create 2d offset setup
            offset_plus_minus_node = maya.cmds.createNode(
                'plusMinusAverage', name='offset_plusMinusAverage1'
            )

            src = reproj_node + '.outPan'
            dst = offset_plus_minus_node + '.input2D[0]'
            maya.cmds.connectAttr(src, dst)

            plug = offset_plus_minus_node + '.input2D[1]'
            maya.cmds.setAttr(plug, 0.0, 0.0, type='float2')

            src = offset_plus_minus_node + '.output2D.output2Dx'
            dst = cam_shp + '.pan.horizontalPan'
            maya.cmds.connectAttr(src, dst, force=True)

            src = offset_plus_minus_node + '.output2D.output2Dy'
            dst = cam_shp + '.pan.verticalPan'
            maya.cmds.connectAttr(src, dst, force=True)

        if len(save_sel) > 0:
            maya.cmds.select(save_sel, replace=True)
    finally:
        mmapi.set_solver_running(False)
        _update_ui_nodes()
    return


def remove():
    """
    Remove the centering nodes in the current active viewport.
    """
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        _update_ui_nodes()
        return

    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        msg = 'Please select an active 3D viewport to get a camera.'
        LOG.warning(msg)
        _update_ui_nodes()
        return

    LOG.warning('Removing 2D centering from %r', cam_tfm)
    try:
        mmapi.set_solver_running(True)
        mmapi.load_plugin()
        reproject_utils.remove_reprojection_from_camera(cam_tfm, cam_shp)
        reproject_utils.reset_pan_zoom(cam_tfm, cam_shp)
    finally:
        mmapi.set_solver_running(False)
        _update_ui_nodes()
    return


def center_two_dee():
    warnings.warn("Use 'main' function instead.", DeprecationWarning)
    main()


def center_two_dee_ui():
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return
    import mmSolver.tools.centertwodee.ui.centertwodee_window as window

    window.main()
