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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger

import mmSolver.utils.lineintersect as tri_utils
import mmSolver.utils.camera as cam_utils
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.frame as frame
import mmSolver._api.solverbase as solverbase
import mmSolver._api.attribute as attribute
import mmSolver._api.action as api_action


LOG = mmSolver.logger.get_logger()
BUNDLE_ATTR_NAMES = ['translateX', 'translateY', 'translateZ']


def _get_marker_frame_list(mkr_node):
    """
    Get the full list of frames that this marker is enabled for.
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
            frm_list.append(t)
    return frm_list


def _get_marker_first_last_frame_list(mkr_node, consider_frame_list):
    """
    Get the "edges" lists of frames that this marker is enabled for.
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


def _triangulate_bundle_v1(bnd_node, mkr_cam_node_frm_list):
    """
    Triangulate a 3D bundle position

    :param bnd_node: Bundle node to be triangulated.
    :type bnd_node: str

    :param mkr_cam_node_frm_list: Marker and Camera transform to be
        considered for triangulation.
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
                cam_tfm, mkr_node, first_frm
            )
            last_pnt, last_dir = tri_utils.get_point_and_direction(
                cam_tfm, mkr_node, last_frm
            )
            (
                a_pnt,
                b_pnt,
            ) = tri_utils.calculate_approx_intersection_point_between_two_3d_lines(
                first_pnt, first_dir, last_pnt, last_dir
            )
            pnt = OpenMaya.MPoint(
                (a_pnt.x + b_pnt.x) * 0.5,
                (a_pnt.y + b_pnt.y) * 0.5,
                (a_pnt.z + b_pnt.z) * 0.5,
            )

            maya.cmds.xform(
                bnd_node, translation=(pnt.x, pnt.y, pnt.z), worldSpace=True
            )
    finally:
        maya.cmds.currentTime(prev_frame, update=False)
    return


def _triangulate_bundle_v2(
    bnd_node,
    mkr_cam_node_frm_list,
    relock=None,
    max_distance=None,
    direction_tolerance=None,
):
    """
    Triangulate a 3D bundle position.

    :param bnd_node: Bundle node to be triangulated.
    :type bnd_node: str

    :param mkr_cam_node_frm_list: Marker and Camera transform to be
        considered for triangulation.
    :type mkr_cam_node_frm_list: [(str, stc, (int, int)), ..]

    :param relock: If True any bundle translate attributes will be
                   unlocked, changed then relocked.
    :type relock: bool or None

    :param max_distance: Defines the maximum distance the bundle can
        be positioned away from camera until the value is clamped.
    :type max_distance: float or None

    :param direction_tolerance: Determines the tolerance used to
        consider if a triangulated point is valid or not.  It's not
        clear what the units are for this tolerance value. This value
        is used by OpenMaya.MVector.isEquivalent() and the Maya
        documentation doesn't really explain the units. The default
        value (if not given) is 1.0.
    :type direction_tolerance: float or None

    :returns: True if the bundle successfully triangulated, False if
        the bundle could not accurately be triangulated. For example
        if the bundle was computed to behind the camera this would be
        considered a failure.
    :rtype: bool
    """
    if relock is None:
        relock = False
    if max_distance is None:
        max_distance = 1e6
    if direction_tolerance is None:
        direction_tolerance = 1.0
    assert isinstance(relock, bool) is True
    assert isinstance(max_distance, float) is True
    assert isinstance(direction_tolerance, float) is True

    success = False
    origin_pnt = OpenMaya.MPoint(0.0, 0.0, 0.0)

    prev_frame = maya.cmds.currentTime(query=True)
    try:
        for mkr_node, cam_tfm, frm_list in mkr_cam_node_frm_list:
            if len(frm_list) == 0:
                continue

            first_frm = frm_list[0]
            last_frm = frm_list[-1]
            first_pnt, first_dir = tri_utils.get_point_and_direction(
                cam_tfm, mkr_node, first_frm
            )
            last_pnt, last_dir = tri_utils.get_point_and_direction(
                cam_tfm, mkr_node, last_frm
            )

            # If the directions are parallel, we cannot triangulate
            # anything.
            is_parallel = first_dir.isParallel(last_dir)
            if is_parallel is True:
                msg = (
                    'Bundle Marker is parallel and cannot be triangulated: '
                    'bnd=%r mkr=%r'
                )
                LOG.warn(msg, bnd_node, mkr_node)
                continue

            (
                a_pnt,
                b_pnt,
            ) = tri_utils.calculate_approx_intersection_point_between_two_3d_lines(
                first_pnt, first_dir, last_pnt, last_dir
            )
            pnt = OpenMaya.MPoint(
                (a_pnt.x + b_pnt.x) * 0.5,
                (a_pnt.y + b_pnt.y) * 0.5,
                (a_pnt.z + b_pnt.z) * 0.5,
            )

            # Check the computed point is not behind the camera.
            calc_first_dir = tri_utils.camera_to_point_direction(
                cam_tfm, pnt, first_frm
            )
            calc_last_dir = tri_utils.camera_to_point_direction(cam_tfm, pnt, last_frm)

            first_dir_is_equal = first_dir.isEquivalent(
                calc_first_dir, direction_tolerance
            )
            if first_dir_is_equal is False:
                msg = 'First Bundle direction does not match: ' 'bnd=%r a=%s b=%s'
                a = (first_dir.x, first_dir.y, first_dir.z)
                b = (calc_first_dir.x, calc_first_dir.y, calc_first_dir.z)
                LOG.debug(msg, bnd_node, a, b)
                continue

            last_dir_is_equal = last_dir.isEquivalent(
                calc_last_dir, direction_tolerance
            )
            if last_dir_is_equal is False:
                msg = 'Last Bundle direction does not match: ' 'bnd=%r a=%s b=%s'
                a = (first_dir.x, first_dir.y, first_dir.z)
                b = (calc_first_dir.x, calc_first_dir.y, calc_first_dir.z)
                LOG.debug(msg, bnd_node, a, b)
                continue

            success = True

            # Clamp the point to the max_distance units away from
            # origin.
            #
            # Tries to avoids issues where the bundles triangulated
            # are too far away from camera and it causes issues with
            # the adjustment solver.
            distance = pnt.distanceTo(origin_pnt)
            if distance > max_distance:
                magnitude = math.sqrt(pnt.x * pnt.x + pnt.y * pnt.y + pnt.z * pnt.z)
                pnt.x = (pnt.x / magnitude) * max_distance
                pnt.y = (pnt.y / magnitude) * max_distance
                pnt.z = (pnt.z / magnitude) * max_distance
                msg = (
                    'Bundle position is farther than max distance and will be clamped: '
                    'bnd=%r mkr=%r distance=%r max_distance=%r'
                )
                LOG.warn(msg, bnd_node, mkr_node, distance, max_distance)

            plugs = [
                '%s.translateX' % bnd_node,
                '%s.translateY' % bnd_node,
                '%s.translateZ' % bnd_node,
            ]
            lock_state = {}
            for plug in plugs:
                value = maya.cmds.getAttr(plug, lock=True)
                lock_state[plug] = value
                maya.cmds.setAttr(plug, lock=False)

            maya.cmds.xform(
                bnd_node, translation=(pnt.x, pnt.y, pnt.z), worldSpace=True
            )

            if relock is True:
                for plug in plugs:
                    value = lock_state.get(plug)
                    maya.cmds.setAttr(plug, lock=value)
    finally:
        maya.cmds.currentTime(prev_frame, update=False)
    return success


def _triangulate_and_solve_bundle_v2(
    bnd_node,
    mkr_cam_node_frm_list,
    relock=None,
    max_distance=None,
    direction_tolerance=None,
    solve=None,
    scene_graph_mode=None,
):
    if solve is None:
        solve = True
    if scene_graph_mode is None:
        scene_graph_mode = const.SCENE_GRAPH_MODE_MAYA_DAG
    assert isinstance(solve, bool)
    assert scene_graph_mode in const.SCENE_GRAPH_MODE_LIST

    success = _triangulate_bundle_v2(
        bnd_node,
        mkr_cam_node_frm_list,
        relock=relock,
        max_distance=max_distance,
        direction_tolerance=direction_tolerance,
    )

    if success is True:
        solver_type = const.SOLVER_TYPE_DEFAULT
        frame_solve_mode = const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE
        iteration_num = 5

        markers = []
        cameras = []
        all_frames = set()
        all_mkr_nodes = set()
        for mkr_node, cam_tfm, frm_list in mkr_cam_node_frm_list:
            all_mkr_nodes.add(mkr_node)
            all_frames |= set(frm_list)

            cam_tfm, cam_shp = cam_utils.get_camera(cam_tfm)
            cameras.append((cam_tfm, cam_shp))

            mkr_bnd = (mkr_node, cam_shp, bnd_node)
            markers.append(mkr_bnd)

        node_attrs = [
            (bnd_node + '.tx', 'None', 'None', 'None', 'None'),
            (bnd_node + '.ty', 'None', 'None', 'None', 'None'),
            (bnd_node + '.tz', 'None', 'None', 'None', 'None'),
        ]

        result = maya.cmds.mmSolver(
            frame=list(sorted(all_frames)),
            solverType=solver_type,
            sceneGraphMode=scene_graph_mode,
            iterations=iteration_num,
            frameSolveMode=frame_solve_mode,
            camera=cameras,
            marker=markers,
            attr=node_attrs,
        )
        success = result[0] == 'success=1'

    return success


def triangulate_bundle(bnd, relock=None, max_distance=None, direction_tolerance=None):
    """
    Triangulate a 3D bundle position.

    :param bnd: Bundle to be triangulated.
    :type bnd: Bundle

    :param relock: If True any bundle translate attributes will be
                   unlocked, changed then relocked.
    :type relock: bool or None

    :param max_distance: Defines the maximum distance the bundle can
        be positioned away from camera until the value is clamped.
    :type max_distance: float or None

    :param direction_tolerance: Determines the tolerance used to
        consider if a triangulated point is valid or not.  It's not
        clear what the units are for this tolerance value. This value
        is used by OpenMaya.MVector.isEquivalent() and the Maya
        documentation doesn't really explain the units. The default
        value (if not given) is 1.0.
    :type direction_tolerance: float or None

    :returns: True if the bundle successfully triangulated, False if
        the bundle could not accurately be triangulated. For example
        if the bundle was computed to behind the camera this would be
        considered a failure.
    :rtype: bool
    """
    bnd_node = bnd.get_node()
    mkr_list = bnd.get_marker_list()
    mkr_node_list = [x.get_node() for x in mkr_list]

    cam_node_list = [x.get_camera().get_transform_node() for x in mkr_list]
    mkr_frm_list = [_get_marker_frame_list(x) for x in mkr_node_list]

    mkr_cam_frm_list = list(zip(mkr_node_list, cam_node_list, mkr_frm_list))

    # TODO: If a Bundle has two markers in two different cameras,
    # but each Marker only has one frame each, this function
    # should still function, currently such a situation would not
    # work.

    success = _triangulate_bundle_v2(
        bnd_node,
        mkr_cam_frm_list,
        relock=relock,
        max_distance=max_distance,
        direction_tolerance=direction_tolerance,
    )
    return success
