# Copyright (C) 2019 David Cattermole, Anil Reddy.
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
Marker utilities functions; Raw computations to be used without the Marker class.
"""

import time
import math

import maya.cmds

import mmSolver.logger
import mmSolver._api.attribute as attribute
import mmSolver.utils.nodeaffects as affects_utils


LOG = mmSolver.logger.get_logger()


def calculate_marker_deviation(mkr_node,
                               bnd_node,
                               cam_tfm, cam_shp,
                               times,
                               image_width,
                               image_height):
    """
    Calculate the 2D-to-3D pixel distance for the given marker.

    :param mkr_node: The marker transform node to compute with.
    :type mkr_node: str

    :param bnd_node: The bundle transform node to compute with.
    :type bnd_node: str

    :param cam_tfm: The camera transform node to compute with.
    :type cam_tfm: str

    :param cam_shp: The camera shape node to compute with.
    :type cam_shp: str

    :param times: The times to query the deviation.
    :type times: [float, ..]

    :param image_width: The width of the matchmove image plate.
    :type image_width: float

    :param image_height: The height of the matchmove image plate.
    :type image_height: float

    :returns: List of pixel deviation values for given times.
    :rtype: [float, ..]
    """
    dev = [None] * len(times)

    # Compute the pixel values.
    mkr_pos = maya.cmds.mmReprojection(
        mkr_node,
        camera=(cam_tfm, cam_shp),
        time=times,
        imageResolution=(image_width, image_height),
        asPixelCoordinate=True,
    )
    bnd_pos = maya.cmds.mmReprojection(
        bnd_node,
        camera=(cam_tfm, cam_shp),
        time=times,
        imageResolution=(image_width, image_height),
        asPixelCoordinate=True,
    )
    assert len(mkr_pos) == len(bnd_pos)

    # 2D Distance
    mkr_x = mkr_pos[0:len(mkr_pos):3]
    mkr_y = mkr_pos[1:len(mkr_pos):3]
    bnd_x = bnd_pos[0:len(mkr_pos):3]
    bnd_y = bnd_pos[1:len(mkr_pos):3]
    for i, (mx, my, bx, by) in enumerate(zip(mkr_x, mkr_y, bnd_x, bnd_y)):
        dx = mx - bx
        dy = my - by
        dev[int(i)] = math.sqrt((dx * dx) + (dy * dy))
    return dev


def get_markers_start_end_frames(selected_markers):
    """
    Gets first and last key from the selected markers list, if no keys
    found it will return current frame.

    :param selected_markers: Markers list.
    :type selected_markers: list

    :return: Start and end frame of given markers list.
    :rtype: (int, int)
    """
    first_frames = []
    last_frames = []
    for marker in selected_markers:
        plugs = [
            '%s.translateX' % marker,
            '%s.translateY' % marker,
        ]
        for plug_name in plugs:
            anim_curves = maya.cmds.listConnections(plug_name,
                                                    type='animCurve'
                                                    ) or []
            if len(anim_curves) == 0:
                continue

            first_keyframe_num = maya.cmds.keyframe(anim_curves,
                                                    query=True,
                                                    timeChange=True)
            first_frames.append(first_keyframe_num[0])
            last_keyframe_num = maya.cmds.keyframe(anim_curves,
                                                   query=True,
                                                   timeChange=True)
            last_frames.append(last_keyframe_num[-1])

    current_frame = maya.cmds.currentTime(query=True)
    start_frame = current_frame
    end_frame = current_frame
    if len(first_frames) > 0:
        start_frame = min(first_frames)
    if len(last_frames) > 0:
        end_frame = max(last_frames)
    return start_frame, end_frame


def find_marker_attr_mapping(mkr_list, attr_list):
    """
    Get a mapping of markers to attributes, as a matrix.

    :param mkr_list: Markers to consider in mapping.
    :type mkr_list: [Marker, ..]

    :param attr_list: Attributes to consider in mapping.
    :type attr_list: [Attribute, ..]

    :returns: Boolean matrix of size 'markers x attrs'. Matrix index
              is 'mapping[marker_index][attr_index]', based on the
              index of the mkr_list and attr_list given.
    :rtype: [[bool, .. ]]
    """
    assert len(mkr_list) > 0
    s = time.time()
    mapping = []
    for i, mkr in enumerate(mkr_list):
        # Initialise mapping list size.
        tmp = [False] * len(attr_list)
        mapping.append(tmp)

        bnd = mkr.get_bundle()
        cam = mkr.get_camera()
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        cam_node = cam.get_transform_node()
        mkr_plugs = affects_utils.find_plugs_affecting_transform(
            mkr_node,
            cam_node)
        bnd_plugs = affects_utils.find_plugs_affecting_transform(
            bnd_node,
            None
        )
        assert isinstance(mkr_plugs, set)
        assert isinstance(bnd_plugs, set)
        plugs = set(mkr_plugs.union(bnd_plugs))
        for j, attr in enumerate(attr_list):
            assert isinstance(attr, attribute.Attribute)
            attr_name = attr.get_name(full_path=True)
            mapping[i][j] = attr_name in plugs
    e = time.time()
    num_iters = len(mkr_list)
    assert num_iters != 0
    LOG.debug(
        'find_marker_attr_mapping: time=%r time_per_mkr=%r',
        e-s,
        (e-s) / num_iters
    )
    return mapping


def calculate_average_deviation(dev_list):
    """
    Calculate a single float number (in pixels) representing the
    average deviation of this Marker.
    """
    dev_list = [d for d in dev_list if d > 0.0]
    if len(dev_list) == 0:
        return -1.0
    dev = sum(dev_list) / len(dev_list)
    return dev


def calculate_maximum_deviation(frames, dev_list):
    """
    Return a tuple of (value, frame) for the deviation
    value and frame number that is the highest.
    """
    max_dev = -1.0
    max_frm = -1
    if len(frames) == 0 or len(dev_list) == 0:
        return max_dev, max_frm
    assert len(frames) == len(dev_list)
    for dev, frm in zip(dev_list, frames):
        if dev > max_dev:
            max_dev = dev
            max_frm = frm
    return max_dev, max_frm
