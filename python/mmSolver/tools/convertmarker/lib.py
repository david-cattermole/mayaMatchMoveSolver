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
The 'Convert to Marker' library functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.lib.interface as loadmkr_interface
import mmSolver.tools.convertmarker.constant as const
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile

LOG = mmSolver.logger.get_logger()


def convert_nodes_to_marker_data_list(cam_tfm, cam_shp,
                                      nodes,
                                      start_frame, end_frame):
    cur_time = maya.cmds.currentTime(query=True)
    mkr_data_list = []
    frames = range(start_frame, end_frame + 1)
    for node in nodes:
        image_width = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture')
        image_height = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture')
        image_width *= 1000.0
        image_height *= 1000.0
        # BUG: If a camera has 'camera scale' attribute set other than
        # 1.0, the reprojected values will not be correct.
        values = maya.cmds.mmReprojection(
            node,
            time=frames,
            imageResolution=(image_width, image_height),
            camera=(cam_tfm, cam_shp),
            asNormalizedCoordinate=True)
        assert (len(frames) * 3) == len(values)

        mkr_data = loadmkr_interface.MarkerData()
        mkr_data.set_name(node)
        mkr_data.weight.set_value(start_frame, 1.0)

        iterator_u = itertools.islice(values, 0, len(values), 3)
        iterator_v = itertools.islice(values, 1, len(values), 3)
        for frame, mkr_u, mkr_v in zip(frames, iterator_u, iterator_v):
            mkr_data.enable.set_value(frame, True)
            # TODO: The values calculated are slightly wrong in Y (V
            # axis), this looks like an aspect ratio problem overall.
            mkr_data.x.set_value(frame, mkr_u)
            mkr_data.y.set_value(frame, mkr_v)
        mkr_data_list.append(mkr_data)

    maya.cmds.currentTime(cur_time, edit=True, update=True)
    return mkr_data_list


def _match_node_position(nodes, target_nodes, start_frame, end_frame, delete_static_anim_curves):
    """
    Move the 'nodes' to the position of the 'target_nodes'.

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


def create_markers_from_transforms(cam_tfm, cam_shp, tfm_nodes,
                                   start_frame, end_frame,
                                   bundle_position_mode,
                                   delete_static_anim_curves):
    """
    Create Markers from Maya transform nodes.

    :param cam_tfm: Camera transform node.
    :type cam_tfm: str

    :param cam_shp: Camera shape node.
    :type cam_shp: str

    :param tfm_nodes: Input transform nodes to be converted.
    :type tfm_nodes: [str, ...]

    :param start_frame: The frame range to sample the input
        transform nodes, and convert to animation.
    :type start_frame: int

    :param end_frame: The frame range to sample the input
        transform nodes, and convert to animation.
    :type end_frame: int

    :param bundle_position_mode: The position for the newly created
        Bundle (connected to the Marker).
    :type bundle_position_mode: None or BUNDLE_POSITION_MODE_*

    :param delete_static_anim_curves: When enabled, this will remove
        all keyframes from the bundle, if the bundle is not animated.
    :type delete_static_anim_curves: bool

    :returns: A tuple of 2 lists; First list is the Marker nodes
        created by the function, and the second list is the bundle
        nodes created by this function.
    :rtype: ([str, ...], [str, ...])
    """
    # Compute the Marker Data.
    mkr_data_list = convert_nodes_to_marker_data_list(
        cam_tfm,
        cam_shp,
        tfm_nodes,
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

    bnd_list = [mkr.get_bundle() for mkr in mkr_list]
    bnd_list = [bnd for bnd in bnd_list if bnd is not None]
    bnd_nodes = [bnd.get_node() for bnd in bnd_list]

    if bundle_position_mode == const.BUNDLE_POSITION_MODE_ORIGIN_VALUE:
        # Bundle stays at the origin.
        pass
    elif bundle_position_mode == const.BUNDLE_POSITION_MODE_SOURCE_VALUE:
        # Move the newly created bundle to the original transform's
        # location.
        _match_node_position(
            bnd_nodes, tfm_nodes,
            start_frame, end_frame,
            delete_static_anim_curves)
    return mkr_nodes, bnd_nodes
