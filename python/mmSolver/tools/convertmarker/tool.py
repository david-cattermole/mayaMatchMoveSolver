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
The 'Convert to Marker' tool.
"""

import warnings

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as utils_camera
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.time as utils_time
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile
import mmSolver.tools.convertmarker.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Convert all selected transforms into 2D markers under a camera.
    """
    # Get camera
    model_editor = utils_viewport.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return

    cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
    if cam_shp is None:
        LOG.error('Please select an active viewport to get a camera.')
        return
    if utils_camera.is_startup_cam(cam_shp) is True:
        LOG.error("Cannot create Markers in 'persp' camera.")
        return

    # Get transforms
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform',
    ) or []
    if len(nodes) == 0:
        LOG.warning('Please select one or more transform nodes.')
        return

    mmapi.load_plugin()
    try:
        utils_viewport.viewport_turn_off()

        # Compute the Marker Data.
        start_frame, end_frame = utils_time.get_maya_timeline_range_outer()
        mkr_data_list = lib.convert_nodes_to_marker_data_list(
            cam_tfm,
            cam_shp,
            nodes,
            start_frame,
            end_frame,
        )

        # Get Camera
        cam = mmapi.Camera(shape=cam_shp)

        # Get or create Marker Group.
        mkr_grp = None
        mkr_grp_nodes = maya.cmds.ls(cam_tfm, dag=True, long=True,
                                     type='mmMarkerGroupTransform') or []
        mkr_grp_nodes = sorted(mkr_grp_nodes)
        if len(mkr_grp_nodes) == 0:
            mkr_grp = markergroup.MarkerGroup().create_node(cam=cam)
        else:
            mkr_grp = markergroup.MarkerGroup(node=mkr_grp_nodes[0])

        # Create Marker nodes
        mkr_list = mayareadfile.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=mkr_grp,
            with_bundles=True,
        )
        mkr_nodes = [mkr.get_node() for mkr in mkr_list]
    finally:
        utils_viewport.viewport_turn_on()
    if len(mkr_nodes) > 0:
        maya.cmds.select(mkr_nodes, replace=True)
    return


def convert_to_marker():
    warnings.warn("Use 'main' function instead.")
    main()
