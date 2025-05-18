# Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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
The .uv format has two versions; v1 ASCII format and v2 JSON format.

The v1 ASCII format is derived from the 3DEqualizer 2D Points exporter.

The UV coordinate (0.0, 0.0) is the lower-left.
The UV coordinate (1.0, 1.0) is the upper-right.


The ASCII file format looks like this::

    int     # Number of track points in the file
    string  # Name of point
    int     # Number of frames
    int float float float  # Frame, U coord, V coord, Point Weight


Simple ASCII v1 file with 1 2D track and 1 frame of data::

    1
    My Point Name
    1
    1 0.0 1.0 1.0


The JSON format takes the shape of a dictionary.
The dictionary looks like this, format version 2::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': bool,
        'points': {
            'name': str,
            'id': int,  # or None
            'set_name': str,
            'per_frame': [
                {
                    'frame': int,
                    'pos': (float, float),  # assumed to be undistorted.
                    'weight': float
                }
            ]
        }
    }


Format version 3::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': None,  # Deprecated
        'points': {
            'name': str,
            'id': int,  # or None
            'set_name': str,
            'per_frame': [
                {
                    'frame': int,
                    'pos_dist': (float, float),
                    'pos': (float, float),
                    'weight': float
                },
            ],
            '3d': {
                'x': float, # or None
                'y': float, # or None
                'z': float, # or None
                'x_lock': bool, # or None
                'y_lock': bool, # or None
                'z_lock': bool  # or None
            }
        }
    }


Format version 4::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': None,  # Deprecated
        'points': {
            'name': str,
            'id': int,  # or None
            'set_name': str,
            'per_frame': [
                {
                    'frame': int,
                    'pos_dist': (float, float),
                    'pos': (float, float),
                    'weight': float
                },
            ],
            '3d': {
                'x': float, # or None
                'y': float, # or None
                'z': float, # or None
                'x_lock': bool, # or None
                'y_lock': bool, # or None
                'z_lock': bool  # or None
            }
        },
        'camera': {
            'resolution': (int, int),
            'film_back_cm': (float, float),
            'lens_center_offset_cm': (float, float),
            'per_frame': [
                {
                    'frame': int,
                    'focal_length_cm': float,
                },
            ],
        }
    }


Format version 5::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': None,  # Deprecated
        'scene': {
            # 4x4 matrix in row-major order.
            'transform': (
                float, float, float, float,
                float, float, float, float,
                float, float, float, float,
                float, float, float, float
            )
        },
        'point_group': {
            'name': str,
            'type': str,  # 'CAMERA' or 'OBJECT' or 'MOCAP'.
            'transform': {
                # 4x4 matrix in row-major order.
                frame: (float, float, float, float,
                        float, float, float, float,
                        float, float, float, float,
                        float, float, float, float)
            }
        },
        'points': {
            'name': str,
            'id': int,  # or None
            'set_name': str,
            'per_frame': [
                {
                    'frame': int,
                    'pos_dist': (float, float),
                    'pos': (float, float),
                    'weight': float
                },
            ],
            '3d': {
                'x': float, # or None
                'y': float, # or None
                'z': float, # or None
                'x_lock': bool, # or None
                'y_lock': bool, # or None
                'z_lock': bool  # or None
            }
        },
        'camera': {
            'resolution': (int, int),
            'film_back_cm': (float, float),
            'lens_center_offset_cm': (float, float),
            'per_frame': [
                {
                    'frame': int,
                    'focal_length_cm': float,
                },
            ],
        }
    }


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import json

import maya.api.OpenMaya as OpenMaya2

import mmSolver.logger

import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.loadfile.excep as excep
import mmSolver.utils.loadfile.loader as loader
import mmSolver.utils.loadmarker.markerdata as markerdata
import mmSolver.utils.loadmarker.fileinfo as fileinfo
import mmSolver.utils.loadmarker.formatmanager as fmtmgr
import mmSolver.tools.loadmarker.constant as const

LOG = mmSolver.logger.get_logger()


def determine_format_version(file_path):
    """
    Work out the format version by reading the 'file_path'.

    returns: The format version, must be one of
        constants.UV_TRACK_FORMAT_VERSION_LIST
    """
    with open(file_path) as f:
        try:
            data = json.load(f)
        except ValueError:
            data = {}
    if len(data) == 0:
        return const.UV_TRACK_FORMAT_VERSION_1
    version = data.get('version', const.UV_TRACK_FORMAT_VERSION_UNKNOWN)
    return version


def _parse_point_info_v2_v3(mkr_data, point_data):
    """
    Get general information from the point data.

    :param mkr_data: The MarkerData object to set.
    :type mkr_data: MarkerData

    :param point_data: The data dictionary, from the file format.
    :type point_data: dict

    :returns: A modified MarkerData, with general information set.
    :rtype: MarkerData
    """
    name = point_data.get('name')
    set_name = point_data.get('set_name')
    id_ = point_data.get('id')
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert set_name is None or isinstance(set_name, pycompat.TEXT_TYPE)
    assert id_ is None or isinstance(id_, int)
    mkr_data.set_name(name)
    mkr_data.set_group_name(set_name)
    mkr_data.set_id(id_)
    return mkr_data


def _parse_point_3d_data_v3_v4_and_v5(
    mkr_data, point_data, scene_data, point_group_data
):
    """
    Parses the 3D data from individual point data.

    :param mkr_data: The MarkerData object to set.
    :type mkr_data: MarkerData

    :param point_data: The data dictionary, from the file format.
    :type point_data: dict

    :param scene_data: The data for the scene.
    :type scene_data: dict

    :param point_group_data: The data for the point group.
    :type point_group_data: dict

    :returns: A modified MarkerData, with bundle information set.
    :rtype: MarkerData
    """
    assert scene_data is None or isinstance(scene_data, dict)
    assert point_group_data is None or isinstance(point_group_data, dict)

    point_3d = point_data.get('3d')
    assert isinstance(point_3d, dict)
    x = point_3d.get('x')
    y = point_3d.get('y')
    z = point_3d.get('z')
    assert x is None or isinstance(x, float)
    assert y is None or isinstance(y, float)
    assert z is None or isinstance(z, float)
    mkr_data.set_bundle_x(x)
    mkr_data.set_bundle_y(y)
    mkr_data.set_bundle_z(z)

    x_lock = point_3d.get('x_lock')
    y_lock = point_3d.get('y_lock')
    z_lock = point_3d.get('z_lock')
    assert x_lock is None or isinstance(x_lock, bool)
    assert y_lock is None or isinstance(y_lock, bool)
    assert z_lock is None or isinstance(z_lock, bool)
    mkr_data.set_bundle_lock_x(x_lock)
    mkr_data.set_bundle_lock_y(y_lock)
    mkr_data.set_bundle_lock_z(z_lock)

    has_xyz = isinstance(x, float) and isinstance(y, float) and isinstance(z, float)
    if scene_data is None or point_group_data is None or not has_xyz:
        return mkr_data
    assert isinstance(scene_data, dict)
    assert isinstance(point_group_data, dict)

    scene_transform_flat = scene_data.get('transform')
    has_scene_transform = (
        scene_transform_flat is not None and len(scene_transform_flat) == 16
    )

    point_group_type = point_group_data.get('type')
    ignore_point_group_transform = point_group_type == 'CAMERA'

    point_group_transform_data = point_group_data.get('transform')
    has_point_group_transform = len(point_group_transform_data.keys()) > 0

    if not has_scene_transform or not has_point_group_transform:
        return mkr_data

    # Calculate bundle world-space position.
    local_point_xyz = OpenMaya2.MPoint(x, y, z)
    if ignore_point_group_transform:
        # World-space matrix position of the bundle.
        scene_transform_matrix = OpenMaya2.MMatrix(scene_transform_flat)
        world_point_xyz = scene_transform_matrix * local_point_xyz

        mkr_data.bundle_world_x = world_point_xyz.x
        mkr_data.bundle_world_y = world_point_xyz.y
        mkr_data.bundle_world_z = world_point_xyz.z
        return mkr_data

    # Calculate (per-frame) bundle world-space position.
    for frame in point_group_transform_data.keys():
        point_group_transform_matrix_flat = point_group_transform_data[frame]
        assert len(point_group_transform_matrix_flat) == 16
        frame = int(frame)

        scene_transform_matrix = OpenMaya2.MMatrix(scene_transform_flat)
        point_group_transform_matrix = OpenMaya2.MMatrix(
            point_group_transform_matrix_flat
        )

        # World-space matrix position of the bundle.
        world_transform_matrix = scene_transform_matrix * point_group_transform_matrix
        world_point_xyz = world_transform_matrix * local_point_xyz

        mkr_data.bundle_world_x.set_value(frame, world_point_xyz.x)
        mkr_data.bundle_world_y.set_value(frame, world_point_xyz.y)
        mkr_data.bundle_world_z.set_value(frame, world_point_xyz.z)

    return mkr_data


def _parse_per_frame_v2_v3_v4_v5(mkr_data, per_frame_data, pos_key=None):
    """
    Get the MarkerData per-frame, including X, Y, weight and enabled
    values.

    :param mkr_data: The Marker data to set.
    :type mkr_data: MarkerData

    :param per_frame_data: List of per-frame data structures.
    :type per_frame_data: [dict, ..]

    :param pos_key: What key should we use to get the U/V Marker data?
    :type pos_key: str or None

    :returns: Tuple of Marker data and the list of frames we have data for.
    :rtype ([MarkerData, ..], [int, ..])
    """
    if pos_key is None:
        pos_key = 'pos'
    assert isinstance(pos_key, str)

    frames = []
    for frame_data in per_frame_data:
        frame_num = frame_data.get('frame')
        assert frame_num is not None
        frames.append(frame_num)

        pos = frame_data.get(pos_key)
        assert pos is not None
        mkr_u, mkr_v = pos

        mkr_weight = frame_data.get('weight')

        # Set Marker Data
        mkr_data.x.set_value(frame_num, mkr_u)
        mkr_data.y.set_value(frame_num, mkr_v)
        mkr_data.weight.set_value(frame_num, mkr_weight)
        mkr_data.enable.set_value(frame_num, True)
    return mkr_data, frames


def _parse_marker_occluded_frames_v1_v2_v3(mkr_data, frames):
    """
    Set the enable and weight values based on the frames we have data
    for.

    :param mkr_data: The Marker data to set.
    :type mkr_data: MarkerData

    :param frames: The frames this a marker has been enabled for.
    :type frames: [int, ..]

    :rtype: MarkerData
    """
    all_frames = list(range(min(frames), max(frames) + 1))
    for frame in all_frames:
        mkr_enable = int(frame in frames)
        mkr_data.enable.set_value(frame, mkr_enable)
        if mkr_enable is False:
            mkr_data.weight.set_value(frame, 0.0)
    return mkr_data


def _parse_v2_v3_v4_and_v5(
    data, scene_data=None, point_group_data=None, undistorted=None, with_3d_pos=None
):
    """
    Parse the UV file format.

    :param data: The data to parse, from the file path.
    :type data: dict

    :param scene_data: The point group data. Only used with v5 format.
    :type scene_data: dict

    :param point_group_data: The point group data. Only used with v5 format.
    :type point_group_data: dict

    :param undistorted: Should we choose the undistorted or distorted
                        marker data?
    :type undistorted: bool or None

    :param with_3d_pos: Try to parse 3D position bundle data from
                        the file path? None means False.
                        with_3d_pos is only accepted on
                        uvtrack version 3+.
    :type with_3d_pos: bool or None

    :return: List of MarkerData objects.
    """
    assert isinstance(data, dict)
    assert scene_data is None or isinstance(scene_data, dict)
    assert point_group_data is None or isinstance(point_group_data, dict)

    if with_3d_pos is None:
        with_3d_pos = False

    pos_key = 'pos_dist'
    if undistorted is None:
        undistorted = True
    if undistorted is True:
        pos_key = 'pos'

    msg = 'Per-frame tracking data was not found on marker, skipping. name=%r'
    points = data.get('points', [])
    mkr_data_list = []
    for point_data in points:
        mkr_data = markerdata.MarkerData()

        # Static point information.
        mkr_data = _parse_point_info_v2_v3(mkr_data, point_data)

        # 3D point data.
        if with_3d_pos is True:
            mkr_data = _parse_point_3d_data_v3_v4_and_v5(
                mkr_data, point_data, scene_data, point_group_data
            )

        per_frame = point_data.get('per_frame', [])
        if len(per_frame) == 0:
            name = mkr_data.get_name()
            LOG.warning(msg, name)
            continue

        # Create marker per-frame data.
        mkr_data, frames = _parse_per_frame_v2_v3_v4_v5(
            mkr_data,
            per_frame,
            pos_key=pos_key,
        )

        # Fill in occluded point frames.
        mkr_data = _parse_marker_occluded_frames_v1_v2_v3(
            mkr_data,
            frames,
        )
        mkr_data_list.append(mkr_data)

    return mkr_data_list


def _parse_camera_fov_v4(data):
    """
    Parse the camera FoV value.

    :param data: The data to parse, from the file path.
    :type data: dict

    :return: List of MarkerData objects.
    """
    assert isinstance(data, dict)

    camera_data = data.get('camera', {})
    img_width, img_height = camera_data.get('resolution', (0, 0))
    film_back_x, film_back_y = camera_data['film_back_cm']
    per_frame_data = camera_data.get('per_frame', [])
    cam_fov_list = [None] * len(per_frame_data)
    for i, frame_data in enumerate(per_frame_data):
        f = frame_data['frame']
        focal_length = frame_data['focal_length_cm']

        # Calculate angle of view from focal length and film back.

        angle_x = math.atan(film_back_x / (2.0 * focal_length))
        angle_y = math.atan(film_back_y / (2.0 * focal_length))
        angle_x = math.degrees(2.0 * angle_x)
        angle_y = math.degrees(2.0 * angle_y)

        cam_fov_list[i] = (f, angle_x, angle_y)

    return cam_fov_list


def parse_v1(file_path, **kwargs):
    """
    Parse the UV file format or 3DEqualizer .txt format.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if len(lines) == 0:
        raise OSError('No contents in the file: %s' % file_path)
    mkr_data_list = []

    num_points = int(lines[0])
    if num_points < 1:
        raise excep.ParserError('No points exist.')

    idx = 1  # Skip the first line
    for _ in range(num_points):
        mkr_name = lines[idx]
        mkr_name = mkr_name.strip()

        # Create marker
        mkr_data = markerdata.MarkerData()
        mkr_data.set_name(mkr_name)

        idx += 1
        num_frames = int(lines[idx])
        if num_frames <= 0:
            idx += 1
            msg = 'Point has no data: mkr_name=%r line_num=%r'
            LOG.warning(msg, mkr_name, idx)
            continue

        # Frame data parsing
        frames = []
        j = num_frames
        while j > 0:
            idx += 1
            line = lines[idx]
            line = line.strip()
            if len(line) == 0:
                # Have we reached the end of the file?
                break
            j = j - 1
            split = line.split()
            if len(split) != 4:
                # We should not get here
                msg = (
                    'File invalid, there must be 4 numbers in a line'
                    ' (separated by spaces): line=%r line_num=%r'
                )
                raise excep.ParserError(msg % (line, idx))
            frame = int(split[0])
            mkr_u = float(split[1])
            mkr_v = float(split[2])
            mkr_weight = float(split[3])

            mkr_data.weight.set_value(frame, mkr_weight)
            mkr_data.x.set_value(frame, mkr_u)
            mkr_data.y.set_value(frame, mkr_v)
            frames.append(frame)

        # Fill in occluded point frames
        mkr_data = _parse_marker_occluded_frames_v1_v2_v3(
            mkr_data,
            frames,
        )

        mkr_data_list.append(mkr_data)
        idx += 1

    file_info = fileinfo.create_file_info(marker_undistorted=True)
    return file_info, mkr_data_list


def parse_v2(file_path, **kwargs):
    """
    Parse the UV file format, using JSON.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    file_info = fileinfo.create_file_info(marker_undistorted=True)

    with open(file_path) as f:
        data = json.load(f)

    mkr_data_list = _parse_v2_v3_v4_and_v5(data, undistorted=True, with_3d_pos=False)
    return file_info, mkr_data_list


def parse_v3(file_path, **kwargs):
    """
    Parse the UV file format, using JSON.

    Accepts the keyword 'undistorted'.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    # Should we choose the undistorted or distorted marker data?
    undistorted = kwargs.get('undistorted', None)
    assert undistorted is None or isinstance(undistorted, bool)

    with_3d_pos = kwargs.get('with_3d_pos', True)
    assert isinstance(with_3d_pos, bool)

    with open(file_path) as f:
        data = json.load(f)

    file_info = fileinfo.create_file_info(
        marker_distorted=True,
        marker_undistorted=True,
        bundle_positions=True,
    )
    mkr_data_list = _parse_v2_v3_v4_and_v5(
        data,
        undistorted=undistorted,
        with_3d_pos=with_3d_pos,
    )
    return file_info, mkr_data_list


def parse_v4(file_path, **kwargs):
    """
    Parse the UV file format, using JSON.

    Accepts the keyword 'undistorted', 'overscan_x' and 'overscan_y'.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    # Should we choose the undistorted or distorted marker data?
    undistorted = kwargs.get('undistorted', None)
    assert undistorted is None or isinstance(undistorted, bool)

    with_3d_pos = kwargs.get('with_3d_pos', True)
    assert isinstance(with_3d_pos, bool)

    with open(file_path) as f:
        data = json.load(f)

    cam_fov_list = _parse_camera_fov_v4(
        data,
    )
    file_info = fileinfo.create_file_info(
        marker_distorted=True,
        marker_undistorted=True,
        bundle_positions=True,
        camera_field_of_view=cam_fov_list,
    )
    mkr_data_list = _parse_v2_v3_v4_and_v5(
        data,
        undistorted=undistorted,
        with_3d_pos=with_3d_pos,
    )
    return file_info, mkr_data_list


def parse_v5(file_path, **kwargs):
    """
    Parse the UV file format, using JSON.

    Accepts the keyword 'undistorted', 'overscan_x' and 'overscan_y'.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    # Should we choose the undistorted or distorted marker data?
    undistorted = kwargs.get('undistorted', None)
    assert undistorted is None or isinstance(undistorted, bool)

    with_3d_pos = kwargs.get('with_3d_pos', True)
    assert isinstance(with_3d_pos, bool)

    with open(file_path) as f:
        data = json.load(f)

    scene_data = data.get('scene', dict())
    scene_transform = scene_data.get('transform')
    has_scene_transform = scene_transform is not None and len(scene_transform) == 16

    point_group_data = data.get('point_group', dict())
    point_group_transform = point_group_data.get('transform')
    has_point_group_transform = (
        isinstance(point_group_transform, dict) and len(point_group_transform) > 0
    )

    cam_fov_list = _parse_camera_fov_v4(data)
    file_info = fileinfo.create_file_info(
        marker_distorted=True,
        marker_undistorted=True,
        bundle_positions=True,
        scene_transform=has_scene_transform,
        point_group_transform=has_point_group_transform,
        camera_field_of_view=cam_fov_list,
    )
    mkr_data_list = _parse_v2_v3_v4_and_v5(
        data,
        scene_data=scene_data,
        point_group_data=point_group_data,
        undistorted=undistorted,
        with_3d_pos=with_3d_pos,
    )
    return file_info, mkr_data_list


class LoaderUVTrack(loader.LoaderBase):
    name = 'UV Track Points (*.uv)'
    file_exts = ['.uv']
    args = ['undistorted', 'with_3d_pos']

    def parse(self, file_path, **kwargs):
        """
        Decodes a file path into a list of MarkerData.

        :param file_path: The file path to parse.
        :type file_path: str

        :param kwargs: The keyword 'undistorted' is used by
            UV_TRACK_FORMAT_VERSION_3 formats. 'with_3d_pos' can be
            used to use the (3D) bundle positions or not.

        :return: List of MarkerData
        """
        version = determine_format_version(file_path)
        if version == const.UV_TRACK_FORMAT_VERSION_1:
            file_info, mkr_data_list = parse_v1(file_path, **kwargs)
        elif version == const.UV_TRACK_FORMAT_VERSION_2:
            file_info, mkr_data_list = parse_v2(file_path, **kwargs)
        elif version == const.UV_TRACK_FORMAT_VERSION_3:
            file_info, mkr_data_list = parse_v3(file_path, **kwargs)
        elif version == const.UV_TRACK_FORMAT_VERSION_4:
            file_info, mkr_data_list = parse_v4(file_path, **kwargs)
        elif version == const.UV_TRACK_FORMAT_VERSION_5:
            file_info, mkr_data_list = parse_v5(file_path, **kwargs)
        else:
            msg = 'Could not determine format version for UV Track file.'
            raise excep.ParserError(msg)
        return file_info, mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(LoaderUVTrack)
