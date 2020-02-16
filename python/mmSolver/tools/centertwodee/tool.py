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
The Center 2D tool.
"""

import warnings

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.reproject as reproject_utils

LOG = mmSolver.logger.get_logger()


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
        return

    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        msg = 'Please select an active 3D viewport to get a camera.'
        LOG.warning(msg)
        return

    save_sel = maya.cmds.ls(selection=True, long=True) or []

    # Create centering node network.
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform',
    ) or []

    # Filter out selected imagePlanes.
    nodes_tmp = list(nodes)
    nodes = []
    for node in nodes_tmp:
        shps = maya.cmds.listRelatives(
            node,
            shapes=True,
            fullPath=True,
            type='imagePlane') or []
        if len(shps) == 0:
            nodes.append(node)

    if len(nodes) == 0:
        msg = 'No objects selected, removing 2D centering.'
        LOG.warning(msg)
        mmapi.load_plugin()
        reproject_utils.remove_reprojection_from_camera(cam_tfm, cam_shp)
        reproject_utils.reset_pan_zoom(cam_tfm, cam_shp)
    elif len(nodes) == 1:
        msg = 'Applying 2D centering to %r'
        LOG.warning(msg, nodes)
        mmapi.load_plugin()
        reproj_nodes = reproject_utils.find_reprojection_nodes(cam_tfm, cam_shp)
        if len(reproj_nodes) > 0:
            maya.cmds.delete(reproj_nodes)

        reproj_node = reproject_utils.create_reprojection_on_camera(
            cam_tfm, cam_shp)
        reproject_utils.connect_transform_to_reprojection(
            nodes[0], reproj_node)
    elif len(nodes) > 1:
        msg = 'Please select only 1 node to center on.'
        LOG.error(msg)

    if len(save_sel) > 0:
        maya.cmds.select(save_sel, replace=True)
    return


def remove():
    """
    Remove the centering nodes in the current active viewport.
    """
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return

    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        msg = 'Please select an active 3D viewport to get a camera.'
        LOG.warning(msg)
        return

    mmapi.load_plugin()
    reproject_utils.remove_reprojection_from_camera(cam_tfm, cam_shp)
    reproject_utils.reset_pan_zoom(cam_tfm, cam_shp)
    return


def center_two_dee():
    warnings.warn("Use 'main' function instead.")
    main()
