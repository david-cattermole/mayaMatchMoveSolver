# Copyright (C) 2021 David Cattermole.
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
The Save Marker File library functions.

Write out a mmSolver Marker node as a .uv file.
"""

import json
import os
import tempfile

import maya.cmds

import mmSolver.logger
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.savemarkerfile.constant as const


LOG = mmSolver.logger.get_logger()


def _marker_object_to_point_data(mkr, frames):
    mkr_node = mkr.get_node()
    bnd = mkr.get_bundle()
    mkr_grp = mkr.get_marker_group()
    mkr_grp_node = mkr_grp.get_node()

    # Per-frame data.
    frames_data = []
    for f in frames:
        enable = mkr.get_enable(time=f)
        if not enable:
            continue
        attr_tx = mkr_node + '.translateX'
        attr_ty = mkr_node + '.translateY'
        # Lower-left is (0.0, 0.0), upper-right is (1.0, 1.0).
        tx = 0.5 + maya.cmds.getAttr(attr_tx, time=f)
        ty = 0.5 + maya.cmds.getAttr(attr_ty, time=f)
        pos = (tx, ty)
        weight = mkr.get_weight(time=f)

        frame_data = {}
        frame_data['frame'] = f
        frame_data['pos_dist'] = pos
        frame_data['pos'] = pos
        frame_data['weight'] = weight
        frames_data.append(frame_data)
    if len(frames_data) == 0:
        LOG.warn('No enabled frames for Marker %r', mkr_node)
        return None

    # 3D data.
    bnd_pos_x = 0.0
    bnd_pos_y = 0.0
    bnd_pos_z = 0.0
    bnd_pos_x_lock = False
    bnd_pos_y_lock = False
    bnd_pos_z_lock = False
    if bnd is not None:
        bnd_node = bnd.get_node()
        if bnd_node is not None:
            attr_bnd_tx = bnd_node + '.translateX'
            attr_bnd_ty = bnd_node + '.translateY'
            attr_bnd_tz = bnd_node + '.translateZ'
            bnd_pos_x = maya.cmds.getAttr(attr_bnd_tx)
            bnd_pos_y = maya.cmds.getAttr(attr_bnd_ty)
            bnd_pos_z = maya.cmds.getAttr(attr_bnd_tz)
            bnd_pos_x_lock = maya.cmds.getAttr(attr_bnd_tx, lock=True)
            bnd_pos_y_lock = maya.cmds.getAttr(attr_bnd_ty, lock=True)
            bnd_pos_z_lock = maya.cmds.getAttr(attr_bnd_tz, lock=True)

    point_data = const.DEFAULT_POINT_DATA_VERSION_4.copy()
    point_data['name'] = mkr_node.rpartition('|')[-1]
    point_data['set_name'] = mkr_grp_node.rpartition('|')[-1]
    point_data['per_frame'] = frames_data
    point_data['3d']['x'] = bnd_pos_x
    point_data['3d']['y'] = bnd_pos_y
    point_data['3d']['z'] = bnd_pos_z
    point_data['3d']['x_lock'] = bnd_pos_x_lock
    point_data['3d']['y_lock'] = bnd_pos_y_lock
    point_data['3d']['z_lock'] = bnd_pos_z_lock
    return point_data


def _camera_to_camera_data(cam, frames):
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    attr_focal_length = cam_shp + '.focalLength'
    attr_fbk_width = cam_shp + '.horizontalFilmAperture'
    attr_fbk_height = cam_shp + '.verticalFilmAperture'
    attr_lco_x = cam_shp + '.horizontalFilmOffset'
    attr_lco_y = cam_shp + '.verticalFilmOffset'
    fbk_width_inch = maya.cmds.getAttr(attr_fbk_width)
    fbk_height_inch = maya.cmds.getAttr(attr_fbk_height)
    lco_x_inch = maya.cmds.getAttr(attr_lco_x)
    lco_y_inch = maya.cmds.getAttr(attr_lco_y)

    fbk_width_cm = fbk_width_inch * 2.54
    fbk_height_cm = fbk_height_inch * 2.54
    lco_x_cm = lco_x_inch * 2.54
    lco_y_cm = lco_y_inch * 2.54

    res_x = 0
    res_y = 0
    imgpl_shps = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    for shp in imgpl_shps:
        attr_coverage_x = shp + '.coverageX'
        attr_coverage_y = shp + '.coverageY'
        coverage_x = maya.cmds.getAttr(attr_coverage_x)
        coverage_y = maya.cmds.getAttr(attr_coverage_y)
        if coverage_x > res_x and coverage_y > res_y:
            res_x = coverage_x
            res_y = coverage_y
    if res_x == 0 or res_y == 0:
        # Fallback fake resolution values, so the aspect ratio is
        # correct.
        res_x = fbk_width_cm * 1000.0
        res_y = fbk_height_cm * 1000.0

    camera_data = const.DEFAULT_CAMERA_DATA_VERSION_4.copy()
    camera_data['resolution'] = (res_x, res_y)
    camera_data['film_back_cm'] = (fbk_width_cm, fbk_height_cm)
    camera_data['lens_center_offset_cm'] = (lco_x_cm, lco_y_cm)

    per_frame_data = []
    for f in frames:
        focal_length_mm = maya.cmds.getAttr(attr_focal_length, time=f)
        focal_length_cm = focal_length_mm * 0.1
        frame_data = {'frame': f, 'focal_length_cm': focal_length_cm}
        per_frame_data.append(frame_data)

    camera_data['per_frame'] = per_frame_data
    return camera_data


def generate(mkr_list, frame_range, fmt=None):
    """
    Convert all Markers to data that can be written out.

    :param mkr_list: List of Marker objects to convert.
    :type mkr_list: [Marker]

    :param frame_range: Frame range to generate data for.
    :type frame_range: range

    :param fmt: The format to generate, either const.UV_TRACK_FORMAT_VERSION_1
                or const.UV_TRACK_FORMAT_VERSION_4. If None, uses preferred version.
    :type fmt: None or int

    :returns: String data (v1) or dictionary data (v4) that can be written out
    :rtype: str or dict
    """
    if fmt is None:
        fmt = const.UV_TRACK_FORMAT_VERSION_PREFERRED

    if fmt == const.UV_TRACK_FORMAT_VERSION_1:
        return _generate_v1(mkr_list, frame_range)
    elif fmt == const.UV_TRACK_FORMAT_VERSION_4:
        return _generate_v4(mkr_list, frame_range)
    else:
        raise ValueError("Unsupported format version: %r" % fmt)


def _generate_v1(mkr_list, frame_range):
    """
    Generate the UV file format contents, using a basic ASCII format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)

    :param mkr_list: List of Marker objects to convert.
    :type mkr_list: [Marker]

    :param frame_range: Frame range to generate data for.
    :type frame_range: range

    :returns: ASCII format string, with the UV Track data in it.
    :rtype: str
    """
    frames = list(range(frame_range.start, frame_range.end + 1))
    assert len(frames) > 0

    if len(mkr_list) == 0:
        return ''

    data_str = ''
    data_str += '{0:d}\n'.format(len(mkr_list))

    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        name = mkr_node.rpartition('|')[-1]

        # Write per-frame position data.
        num_valid_frame = 0
        pos_list = []
        weight_list = []

        for f in frames:
            enable = mkr.get_enable(time=f)
            if not enable:
                continue

            attr_tx = mkr_node + '.translateX'
            attr_ty = mkr_node + '.translateY'
            # Lower-left is (0.0, 0.0), upper-right is (1.0, 1.0).
            tx = 0.5 + maya.cmds.getAttr(attr_tx, time=f)
            ty = 0.5 + maya.cmds.getAttr(attr_ty, time=f)
            pos = (tx, ty)
            weight = mkr.get_weight(time=f)

            # Number of points with valid positions.
            num_valid_frame += 1

            pos_list.append((f, pos))
            weight_list.append((f, weight))

        # Add data.
        data_str += name + '\n'
        data_str += '{0:d}\n'.format(num_valid_frame)
        for pos_data, weight_data in zip(pos_list, weight_list):
            f = pos_data[0]
            v = pos_data[1]
            w = weight_data[1]
            assert f == weight_data[0]
            data_str += '%d %.15f %.15f %.8f\n' % (f, v[0], v[1], w)

    return data_str


def _generate_v4(mkr_list, frame_range):
    """
    Generate the UV file format contents, using JSON format (version 4).

    :param mkr_list: List of Marker objects to convert.
    :type mkr_list: [Marker]

    :param frame_range: Frame range to generate data for.
    :type frame_range: range

    :returns: Dictionary data that can be written as JSON.
    :rtype: dict
    """
    frames = list(range(frame_range.start, frame_range.end + 1))
    assert len(frames) > 0

    cameras_map = {}

    cam = None
    points_data = []
    for mkr in mkr_list:
        cam = mkr.get_camera()
        if cam is None:
            continue
        cam_shp = cam.get_shape_node()
        cameras_map[cam_shp] = mkr

        point_data = _marker_object_to_point_data(mkr, frames)
        if point_data is not None:
            points_data.append(point_data)

    if len(points_data) == 0:
        LOG.error('No marker data to export.')
        return {}

    if len(cameras_map) > 1:
        cam_mkrs = []
        for k, v in cameras_map.items():
            cam_mkrs.append(v)
        LOG.error('Cannot export markers from multiple cameras: %r', cam_mkrs)
        return {}

    assert cam is not None
    camera_data = _camera_to_camera_data(cam, frames)

    data = const.DEFAULT_DATA_VERSION_4.copy()
    data['num_points'] = len(points_data)
    data['points'] = points_data
    data['camera'] = camera_data
    return data


def write_file(file_path, data):
    """
    Write data to file. Handles both string (v1) and dictionary (v4) data.

    :param file_path: Path to write the file to.
    :type file_path: str

    :param data: Data to write. String for v1, dict for v4.
    :type data: str or dict

    :returns: True if file was written successfully.
    :rtype: bool
    """
    with open(file_path, 'w') as f:
        if isinstance(data, dict):
            json.dump(data, f)
        else:
            f.write(data)
    result = os.path.isfile(file_path)
    return result


def write_temp_file(data):
    """
    Write file to temporary location. Handles both string (v1) and dictionary (v4) data.

    :param data: Data to write. String for v1, dict for v4.
    :type data: str or dict

    :returns: Temporary file path or False if failed.
    :rtype: str or bool
    """
    if isinstance(data, dict):
        data_str = json.dumps(data)
    else:
        data_str = data

    assert isinstance(data_str, pycompat.TEXT_TYPE)
    file_ext = const.EXT
    f = tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False)
    if f.closed:
        LOG.error("Error: Couldn't open file.\n%r", f.name)
        return False
    f.write(data_str)
    f.close()
    return f.name
