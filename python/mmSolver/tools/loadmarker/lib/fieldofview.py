# Copyright (C) 2018, 2019, 2020 David Cattermole.
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
Camera field of view maths related functions.
"""

import math

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.lib.interface as interface

LOG = mmSolver.logger.get_logger()


def get_camera_field_of_view(cam_shp, frames):
    """Compute the Camera's field of view with a camera shape node at frames.

    :param cam_shp: Maya camera shape node.
    :type cam_shp: str

    :param frames: List of frames to sample the camera/marker group
    :type frames: [int, ..]

    :returns:
    :rtype: [(int, float, float), ..]
    """
    cam_fov_list = []
    for frame in frames:
        attr_fl = cam_shp + '.focalLength'
        attr_fbk_x = cam_shp + '.horizontalFilmAperture'
        attr_fbk_y = cam_shp + '.verticalFilmAperture'
        focal_length = maya.cmds.getAttr(attr_fl, time=frame)
        film_back_x = maya.cmds.getAttr(attr_fbk_x, time=frame)
        film_back_y = maya.cmds.getAttr(attr_fbk_y, time=frame)
        focal_length *= 0.1
        film_back_x *= 2.54
        film_back_y *= 2.54

        # Calculate angle of view from focal length and film back.
        angle_x = math.atan(film_back_x / (2.0 * focal_length))
        angle_y = math.atan(film_back_y / (2.0 * focal_length))
        angle_x = math.degrees(2.0 * angle_x)
        angle_y = math.degrees(2.0 * angle_y)

        cam_fov_list.append((frame, angle_x, angle_y))
    return cam_fov_list


def calculate_overscan_ratio(cam, mkr_grp, camera_fov):
    """Calculate overscan with camera and FOV.

    Query the overscan of cam by comparing to the camera_fov
    field of view.

    :param cam:
        The mmSolver.api.Camera object to query field of view from.
    :type cam: Camera

    :param camera_fov:
        Tuple of camera field of view per-frame values X and Y.
    :type camera_fov: [(int, float, float), ..]

    :param mkr_grp:
        The mmapi MarkerGroup object, to be used additionally to the
        provided camera to calculate the overscan.
    :type mkr_grp: MarkerGroup or None

    :returns: Overscan X and Y values.
    :rtype: (float, float)

    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(camera_fov, list)
    assert mkr_grp is None or isinstance(mkr_grp, mmapi.MarkerGroup)

    cam_shp = cam.get_shape_node()
    frames = [f for f, _, _ in camera_fov]
    maya_camera_fov = get_camera_field_of_view(cam_shp, frames)

    x = 1.0
    y = 1.0
    all_same_ratio_x = True
    all_same_ratio_y = True
    last_ratio_x = None
    last_ratio_y = None
    for file_fov, maya_fov in zip(camera_fov, maya_camera_fov):
        file_frame, file_angle_x, file_angle_y = file_fov
        maya_frame, maya_angle_x, maya_angle_y = maya_fov

        file_fov_x = math.tan(math.radians(file_angle_x * 0.5))
        file_fov_y = math.tan(math.radians(file_angle_y * 0.5))
        maya_fov_x = math.tan(math.radians(maya_angle_x * 0.5))
        maya_fov_y = math.tan(math.radians(maya_angle_y * 0.5))

        ratio_x = maya_fov_x / file_fov_x
        ratio_y = maya_fov_y / file_fov_y
        if last_ratio_x is None and last_ratio_y is None:
            last_ratio_x = ratio_x
            last_ratio_y = ratio_y

        ratio_same_x = interface.float_is_equal(ratio_x, last_ratio_x)
        ratio_same_y = interface.float_is_equal(ratio_y, last_ratio_y)
        if not ratio_same_x:
            all_same_ratio_x = False
        if not ratio_same_y:
            all_same_ratio_y = False
        if all_same_ratio_x is True or all_same_ratio_y is True:
            x = ratio_x
            y = ratio_y
        else:
            x = 1.0
            y = 1.0
            break

    # Account for MarkerGroup overscan.
    #
    # NOTE: We assume that the overscanX/Y values are NOT changing
    # over time.
    mkr_grp_overscan_x = 1.0
    mkr_grp_overscan_y = 1.0
    if mkr_grp is not None:
        mkr_grp_node = mkr_grp.get_node()
        if mkr_grp_node is not None:
            attr_x = mkr_grp_node + '.overscanX'
            attr_y = mkr_grp_node + '.overscanY'
            mkr_grp_overscan_x = maya.cmds.getAttr(attr_x)
            mkr_grp_overscan_y = maya.cmds.getAttr(attr_y)
    x = mkr_grp_overscan_x / x
    y = mkr_grp_overscan_y / y
    return x, y
