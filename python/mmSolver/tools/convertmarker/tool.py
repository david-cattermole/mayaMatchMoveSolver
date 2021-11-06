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
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.time as utils_time
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile
import mmSolver.tools.convertmarker.lib as lib


LOG = mmSolver.logger.get_logger()

BUNDLE_POSITION_MODE_ORIGIN = 'origin'  # Bundle stays at the origin.
BUNDLE_POSITION_MODE_SOURCE = 'source'  # Bundle moves to the source transform.


def _match_node_position(nodes, target_nodes, start_frame, end_frame, delete_static_anim_curves):
    """Move the 'nodes' to the position of the 'target_nodes'.

    'nodes' and 'target_nodes' are expected to be lists of equal
    length, each list index corresponds to the other list.
    """
    constraint_nodes = []
    for target_node, node in zip(target_nodes, nodes):
        constraint_nodes += maya.cmds.pointConstraint(
            target_node, node,
            maintainOffset=False)

    # Bake and delete the constraints.
    if len(constraint_nodes) > 0:
        frame_range = (float(start_frame), float(end_frame),)
        maya.cmds.bakeResults(
            nodes,
            time=frame_range,
            sampleBy=1,
            sparseAnimCurveBake=False,
            minimizeRotation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            controlPoints=False,
            shape=False)
        maya.cmds.delete(nodes, constraints=True)
        maya.cmds.filterCurve(nodes)

        if delete_static_anim_curves is True:
            maya.cmds.delete(nodes, staticChannels=True)
    return


def main(bundle_position_mode=None, delete_static_anim_curves=None):
    """Convert all selected transforms into 2D markers under a camera.

    :param bundle_position_mode: The position for the newly created
       Bundle (connected to the Marker).
    :type bundle_position_mode: None or BUNDLE_POSITION_MODE_*

    :param delete_static_anim_curves: When enabled, this will remove
       all keyframes from the bundle, if the bundle is not animated.
    :type delete_static_anim_curves: bool

    """
    if bundle_position_mode is None:
        bundle_position_mode = BUNDLE_POSITION_MODE_ORIGIN
    if delete_static_anim_curves is None:
        delete_static_anim_curves = True

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

    start_frame, end_frame = utils_time.get_maya_timeline_range_outer()
    with tools_utils.tool_context(pre_update_frame=True):
        # Compute the Marker Data.
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
            mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)
        else:
            mkr_grp = mmapi.MarkerGroup(node=mkr_grp_nodes[0])

        # Create Marker nodes
        mkr_list = mayareadfile.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=mkr_grp,
            with_bundles=True,
        )
        mkr_nodes = [mkr.get_node() for mkr in mkr_list]

        if bundle_position_mode == BUNDLE_POSITION_MODE_ORIGIN:
            # Bundle stays at the origin.
            pass
        elif bundle_position_mode == BUNDLE_POSITION_MODE_SOURCE:
            # Move the newly created bundle to the original transform's
            # location.
            bnd_list = [mkr.get_bundle() for mkr in mkr_list]
            bnd_list = [bnd for bnd in bnd_list if bnd is not None]
            bnd_nodes = [bnd.get_node() for bnd in bnd_list]
            _match_node_position(
                bnd_nodes, nodes,
                start_frame, end_frame,
                delete_static_anim_curves)

    if len(mkr_nodes) > 0:
        maya.cmds.select(mkr_nodes, replace=True)
    return


def convert_to_marker():
    warnings.warn("Use 'main' function instead.")
    main()
