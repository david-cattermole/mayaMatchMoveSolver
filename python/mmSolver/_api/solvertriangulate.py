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
The triangulation solver, used to solve bundles by triangulating.
"""

import collections

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger

import mmSolver.utils.lineintersect as tri_utils
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.solverbase as solverbase
import mmSolver._api.attribute as attribute
import mmSolver._api.action as api_action


LOG = mmSolver.logger.get_logger()

BUNDLE_ATTR_NAMES = ['translateX', 'translateY', 'translateZ']


def _get_marker_first_last_frame_list(mkr_node, consider_frame_list):
    """
    Get the list of frames that this marker is enabled for.
    """
    frm_list = []
    curves = maya.cmds.listConnections(mkr_node, type='animCurve') or []
    first_time = -99999
    last_time = 99999
    for node in curves:
        times = maya.cmds.keyframe(node, query=True, timeChange=True)
        first_time = max(int(times[0]), first_time)
        last_time = min(int(times[-1]), last_time)

    for t in range(first_time, last_time + 1):
        plug = mkr_node + '.enable'
        value = maya.cmds.getAttr(plug, time=t)
        if value > 0:
            if consider_frame_list is None:
                frm_list.append(t)
            elif t in consider_frame_list:
                frm_list.append(t)
    first_last_frames = []
    if len(frm_list) > 0:
        first_frame = frm_list[0]
        last_frame = frm_list[-1]
        first_last_frames = [first_frame, last_frame]
    return first_last_frames


def _triangulate_bundle(bnd_node, mkr_cam_node_frm_list):
    """
    Triangulate a 3D bundle position.

    :param bnd_node: Bundle node to be triangulated.
    :type bnd_node: str

    :param mkr_cam_node_frm_list: Marker and Camera transform to be considered for triangulation.
    :type mkr_cam_node_frm_list: [(str, stc, (int, int)), ..]
    """
    LOG.debug('triangulate_bundle: %r %r', bnd_node, mkr_cam_node_frm_list)
    prev_frame = maya.cmds.currentTime(query=True)
    try:
        for mkr_node, cam_tfm, frm_list in mkr_cam_node_frm_list:
            if len(frm_list) == 0:
                continue

            first_frm = frm_list[0]
            last_frm = frm_list[-1]
            first_pnt, first_dir = tri_utils.get_point_and_direction(
                cam_tfm,
                mkr_node,
                first_frm)
            last_pnt, last_dir = tri_utils.get_point_and_direction(
                cam_tfm,
                mkr_node,
                last_frm
            )
            a_pnt, b_pnt = tri_utils.calculate_approx_intersection_point_between_two_3d_lines(
                first_pnt, first_dir,
                last_pnt, last_dir
            )
            pnt = OpenMaya.MPoint(
                (a_pnt.x + b_pnt.x) * 0.5,
                (a_pnt.y + b_pnt.y) * 0.5,
                (a_pnt.z + b_pnt.z) * 0.5
            )

            maya.cmds.xform(
                bnd_node,
                translation=(pnt.x, pnt.y, pnt.z),
                worldSpace=True
            )
    finally:
        maya.cmds.currentTime(prev_frame, update=False)
    return


class SolverTriangulate(solverbase.SolverBase):
    """
    An operation to re-calculate the bundle positions using triangulation.
    """

    def __init__(self, *args, **kwargs):
        super(SolverTriangulate, self).__init__(*args, **kwargs)
        self.root_frame_list = None
        return

    def compile(self, col, mkr_list, attr_list, withtest=False):
        actions = []
        # TODO: Triangulate the (open) bundles here. We triangulate all
        #  valid bundles after the root frames have solved.
        #
        # NOTE: Bundle triangulation can only happen if the camera
        # is not nodal.
        #
        # NOTE: We currently assume the camera is NOT nodal.

        valid_bnd_node_list = []
        for mkr in mkr_list:
            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            valid_bnd_node_list.append(bnd_node)

        valid_node_list = collections.defaultdict(int)
        for attr in attr_list:
            assert isinstance(attr, attribute.Attribute) is True
            attr_name = attr.get_attr()
            if attr_name not in BUNDLE_ATTR_NAMES:
                continue
            attr_node = attr.get_node()
            if attr_node not in valid_bnd_node_list:
                continue
            obj_type = api_utils.get_object_type(attr_node)
            if obj_type == const.OBJECT_TYPE_BUNDLE:
                valid_node_list[attr_node] += 1

        for node, count in valid_node_list.items():
            if count != 3:
                continue
            bnd = bundle.Bundle(node=node)
            bnd_node = bnd.get_node()
            mkr_node_list = [x.get_node() for x in mkr_list]
            bnd_mkr_list = [x for x in bnd.get_marker_list()
                            if x.get_node() in mkr_node_list]
            bnd_mkr_node_list = [x.get_node() for x in bnd_mkr_list]
            bnd_cam_node_list = [x.get_camera().get_transform_node()
                                 for x in bnd_mkr_list]
            bnd_mkr_frm_list = [_get_marker_first_last_frame_list(x, self.root_frame_list)
                                for x in bnd_mkr_node_list]
            bnd_mkr_cam_frm_list = zip(
                bnd_mkr_node_list,
                bnd_cam_node_list,
                bnd_mkr_frm_list
            )

            # TODO: We must detect if the newly calculated position is
            #  behind the camera, if so, we reject the new values.
            args = [bnd_node, bnd_mkr_cam_frm_list]
            kwargs = {}
            action = api_action.Action(
                _triangulate_bundle,
                args=args,
                kwargs=kwargs
            )
            LOG.debug('adding _triangulate_bundle: func=%r',
                      _triangulate_bundle,
                      args,
                      kwargs
            )
            actions.append(action)
        return actions
