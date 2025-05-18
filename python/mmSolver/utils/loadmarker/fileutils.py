# Copyright (C) 2018, 2020 David Cattermole.
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
File reading and parsing utilities.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import os.path

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.loadmarker.formatmanager as fmtmgr


LOG = mmSolver.logger.get_logger()


def _get_file_path_formats(text):
    """
    Look up the possible Formats for the file path.

    :param text: File path text.

    :returns: List of formats for the file path.
    :rtype: [Format, ..]
    """
    formats = []
    if isinstance(text, pycompat.TEXT_TYPE) is False:
        return formats
    if os.path.isfile(text) is False:
        return formats
    fmt_mgr = fmtmgr.get_format_manager()
    fmts = fmt_mgr.get_formats()
    ext_to_fmt = {}
    for fmt in fmts:
        for ext in fmt.file_exts:
            ext_to_fmt[ext] = fmt
    for ext, fmt in ext_to_fmt.items():
        if text.endswith(ext):
            formats.append(fmt)
            break
    return formats


def get_file_path_format(text, read_func):
    """
    Look up the Format from the file path.

    :param text: File path text.

    :returns: Format for the file path, or None if not found.
    :rtype: None or Format
    """
    format_ = None
    formats = _get_file_path_formats(text)
    for fmt in formats:
        file_info, _ = read_func(text)
        if file_info is not None:
            format_ = fmt
            break
    return format_


def is_valid_file_path(text, read_func):
    """
    Is the given text a file path we can load as a marker?

    :param text: A possible file path string.
    :type text: str

    :returns: File path validity.
    :rtype: bool
    """
    assert isinstance(text, pycompat.TEXT_TYPE)
    fmt = get_file_path_format(text, read_func)
    valid = fmt is not None
    return valid


def get_file_info(file_path, read_func):
    """
    Get the file path information.

    :param file_path: The marker file path to get info for.
    :type file_path: str

    :return: The file info.
    :rtype: FileInfo
    """
    file_info, _ = read_func(file_path)
    return file_info


def get_file_info_strings(file_path, read_func):
    """
    Get the file path information, as user-readable strings.

    :param file_path: The marker file path to get info for.
    :type file_path: str

    :return: Dictionary of various information about the given file path.
    :rtype: dict
    """
    info = {
        'num_points': '?',
        'point_names': '?',
        'frame_range': '?-?',
        'start_frame': '?',
        'end_frame': '?',
        'lens_dist': '?',
        'lens_undist': '?',
        'positions': '?',
        'has_camera_fov': '?',
        'has_scene_transform': '?',
        'has_point_group_transform': '?',
    }
    file_info, mkr_data_list = read_func(file_path)
    if isinstance(mkr_data_list, list) is False:
        return info

    fmt = get_file_path_format(file_path, read_func)
    info['fmt'] = fmt
    info['fmt_name'] = str(fmt.name)

    info['num_points'] = str(len(mkr_data_list))
    start_frame = int(999999)
    end_frame = int(-999999)
    point_names = []
    for mkr_data in mkr_data_list:
        name = mkr_data.get_name()
        point_names.append(name)

        # Get start / end frame.
        # We assume that there are X and Y keyframes on each frame,
        # therefore we do not test Y.
        x_keys = mkr_data.get_x()
        x_start = x_keys.get_start_frame()
        x_end = x_keys.get_end_frame()
        if x_start < start_frame:
            start_frame = x_start
        if x_end > end_frame:
            end_frame = x_end

    info['point_names'] = ' '.join(point_names)
    info['start_frame'] = start_frame
    info['end_frame'] = end_frame
    info['frame_range'] = '{0}-{1}'.format(start_frame, end_frame)
    info['lens_dist'] = file_info.marker_distorted
    info['lens_undist'] = file_info.marker_undistorted
    info['positions'] = file_info.bundle_positions
    info['has_camera_fov'] = bool(file_info.camera_field_of_view)
    info['has_scene_transform'] = bool(file_info.scene_transform)
    info['has_point_group_transform'] = bool(file_info.point_group_transform)
    return info


def get_file_filter():
    """
    Construct a string to be given to QFileDialog as a file filter.

    :return: String of file filters, separated by ';;' characters.
    :rtype: str
    """
    file_fmt_names = []
    file_exts = []
    fmt_mgr = fmtmgr.get_format_manager()
    fmts = fmt_mgr.get_formats()
    for fmt in fmts:
        file_fmt_names.append(fmt.name)
        file_exts += fmt.file_exts
    file_fmt_names = sorted(file_fmt_names)
    file_exts = sorted(file_exts)

    extensions_str = ''
    for file_ext in file_exts:
        extensions_str += '*' + file_ext + ' '

    file_filter = 'Marker Files (%s);;' % extensions_str
    for name in file_fmt_names:
        name = name + ';;'
        file_filter += name
    file_filter += 'All Files (*.*);;'
    return file_filter
