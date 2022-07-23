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
Position Bundle under the Marker.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.lineintersect as tri_utils


LOG = mmSolver.logger.get_logger()


def get_marker_frame_list(mkr_node):
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
            frm_list.append(t)
    return frm_list


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
        mkr_list = bnd.get_marker_list()
        # TODO: If a Bundle has two markers in two different cameras,
        # but each Marker only has one frame each, this function
        # should still function, currently such a situation would not
        # work.
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            frm_list = get_marker_frame_list(mkr_node)
            if len(frm_list) == 0:
                continue

            bnd_node = bnd.get_node()
            cam = mkr.get_camera()
            cam_tfm = cam.get_transform_node()

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
