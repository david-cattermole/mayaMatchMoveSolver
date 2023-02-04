# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# Copyright (C) 2018, 2021, 2022 David Cattermole.
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
# ----------------------------------------------------------------------
#
# 3DE4.script.name:    Import 2D Tracks (MM Solver)...
#
# 3DE4.script.version: v1.3
#
# 3DE4.script.gui:     Main Window::3DE4::File::Import
# 3DE4.script.gui:     Object Browser::Context Menu Point
# 3DE4.script.gui:     Object Browser::Context Menu Points
# 3DE4.script.gui:     Object Browser::Context Menu PGroup
#
# 3DE4.script.comment: Imports 2D tracking points from a file.
# 3DE4.script.comment:
# 3DE4.script.comment: The supported file formats are:
# 3DE4.script.comment: - MM Solver (.uv)
# 3DE4.script.comment: - 3DEqualizer (.txt)
# 3DE4.script.comment: - MatchMover (.rz2)
# 3DE4.script.comment: - PFTrack/PFMatchIt (.2dt / .txt)
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import collections
import json
import logging
import math
import sys
import os
import os.path
import re

import tde4

LOG = logging.getLogger()

WINDOW_TITLE = 'Import 2D Tracks (MM Solver)...'
SUPPORT_POINT_SURVEY_XYZ_ENABLED = 'setPointSurveyXYZEnabledFlags' in dir(tde4)
HELP_TEXT = """Import 2D Tracks from:
- MM Solver (.uv files)
- 3DEqualizer (.txt files) *
- MatchMover (.rz2 files)
- PFTrack/PFMatchIt (.2dt / .txt files) *

* Note: Some file formats embed the image resolution.
The resolution must match in order to align to the image correctly."""

# UV Track format
# Keep this in-sync with the 3DEqualizer exporter 'uvtrack_format.py'
UV_TRACK_FORMAT_VERSION_UNKNOWN = -1
UV_TRACK_FORMAT_VERSION_1 = 1
UV_TRACK_FORMAT_VERSION_2 = 2
UV_TRACK_FORMAT_VERSION_3 = 3
UV_TRACK_FORMAT_VERSION_4 = 4

UV_TRACK_HEADER_VERSION_2 = {
    'version': UV_TRACK_FORMAT_VERSION_2,
}

UV_TRACK_HEADER_VERSION_3 = {
    'version': UV_TRACK_FORMAT_VERSION_3,
}

UV_TRACK_HEADER_VERSION_4 = {
    'version': UV_TRACK_FORMAT_VERSION_4,
}


IS_PYTHON_2 = sys.version_info[0] == 2
IS_PYTHON_3 = sys.version_info[0] == 3
if IS_PYTHON_2 is True:
    TEXT_TYPE = basestring  # noqa: F821
    INT_TYPES = (int, long)  # noqa: F821
    LONG_TYPE = long  # noqa: F821
else:
    TEXT_TYPE = str
    INT_TYPES = (int,)
    LONG_TYPE = int


class ParserWarning(Warning):
    """
    Raised when a format parser needs to warn about non-error conditions.
    """

    pass


class ParserError(Exception):
    """
    Raised when a format parser cannot continue.
    """

    pass


def float_is_equal(x, y):
    """
    Check the two float numbers match.

    :returns: True or False, if float is equal or not.
    :rtype: bool
    """
    # float equality
    if x == y:
        return True

    # float equality, with an epsilon
    eps = sys.float_info.epsilon * 100.0
    if x < (y + eps) and x > (y - eps):
        return True

    # string equality, with nine decimal places.
    x_str = '%.9f' % float(x)
    y_str = '%.9f' % float(y)
    if x_str == y_str:
        return True

    return False


def get_closest_frame(frame, value):
    """
    Get the closest frame in the dictionary value.

    :param frame: An int for the frame to look up.
    :param value: A dict with keys as the frames to look up.

    Returns the closest frame in the dict value.
    """
    keys = value.keys()
    int_keys = list()
    for key in keys:
        int_keys.append(int(key))
    keys = sorted(int_keys)
    diff = int()
    closest_frame = None
    for key in keys:
        if closest_frame is None:
            closest_frame = key
            diff = frame - closest_frame
        if (key <= frame) and (key > closest_frame):
            closest_frame = key
        diff = closest_frame - frame
    keys.reverse()
    closest_frame_rev = None
    for key in keys:
        if closest_frame_rev is None:
            closest_frame_rev = key
            diff = frame - closest_frame_rev
        if (key >= frame) and (key < closest_frame_rev):
            closest_frame_rev = key
        diff = closest_frame_rev - frame
    diffRef = abs(closest_frame_rev - frame)
    diff = abs(closest_frame - frame)
    if diffRef < diff:
        closest_frame = closest_frame_rev
    return closest_frame


class FormatManager(object):
    def __init__(self):
        self.__formats = {}

    def register_format(self, class_obj):
        if str(class_obj) not in self.__formats:
            self.__formats[str(class_obj)] = class_obj
        return True

    def get_formats(self):
        format_list = []
        for key in self.__formats:
            fmt = self.__formats[key]
            format_list.append(fmt)
        return format_list


class KeyframeData(object):
    """
    Keyframe data, used to store animated or static data.

    Note: Static data is just a single keyframe of data, or multiple keyframes
    with the same value.
    """

    def __init__(self, data=None):
        self._data = dict()
        self._up_to_date = False
        self._keyframe_values = None
        if isinstance(data, dict):
            self._data = data.copy()

    def get_start_frame(self):
        times = self.get_times()
        if len(times) == 0:
            return None
        return int(times[0])

    def get_end_frame(self):
        times = self.get_times()
        if len(times) == 0:
            return None
        return int(times[-1])

    def get_length(self):
        times = self.get_times()
        return len(times)

    def get_raw_data(self):
        """
        Gives access of the underlying data structure to the user.

        This is so that the user can query the data then give it to the
        __init__ of a new class.
        """
        return self._data.copy()

    def get_value(self, frame):
        """
        Get the key value at frame. frame is an integer.
        """
        assert isinstance(self._data, dict)
        key = str(frame)
        value = self._data.get(key)
        if value is None:
            # there is no key on the frame, find the closest frame.
            frame = get_closest_frame(frame, self._data)
            key = str(frame)
            if key in self._data:
                value = self._data[key]
        return value

    def get_keyframe_values(self):
        assert isinstance(self._data, dict)

        # This enables multiple calls not to re-compute this data.
        if self._up_to_date is True:
            return self._keyframe_values

        key_values = list()

        # Sort keys, based on int values, not string.
        int_keys = list()
        for key in self._data.keys():
            int_keys.append(int(key))
        keys = sorted(int_keys)

        # Create key/value pairs.
        for key in keys:
            key_value = (int(key), self.get_value(int(key)))
            key_values.append(key_value)

        self._keyframe_values = key_values
        self._up_to_date = True
        return key_values

    def get_times(self):
        """
        Get all times, should be first half of get_keyframe_values.
        """
        time_values = list()
        key_values = self.get_keyframe_values()
        for kv in key_values:
            time_values.append(kv[0])
        return time_values

    def get_values(self):
        """
        Get all values, should be second half of get_keyframe_values.
        """
        values = list()
        key_values = self.get_keyframe_values()
        for kv in key_values:
            values.append(kv[1])
        return values

    def get_times_and_values(self):
        """
        Get all times, should be first half of get_keyframe_values.
        """
        times = list()
        values = list()
        key_values = self.get_keyframe_values()
        for kv in key_values:
            times.append(kv[0])
            values.append(kv[1])
        return times, values

    def set_value(self, frame, value):
        """
        Set the 'value', at 'frame'.
        """
        self._up_to_date = False
        frame_str = str(frame)
        self._data[frame_str] = value
        return True

    def simplify_data(self):
        """
        Tries to convert the keyframe data into
        static if all values are the same.
        """
        assert isinstance(self._data, dict)
        self._up_to_date = False
        initial = None
        total = float()  # assume it's a float?
        total_num = int()
        for key in self._data.keys():
            if initial is None:
                initial = self._data[key]
            total = total + float(self._data[key])
            total_num = total_num + 1
        average = total / total_num
        if float_is_equal(average, initial):
            self._data = average
        return True


class LoaderBase(object):
    """
    Base class for all format loaders.
    """

    __metaclass__ = abc.ABCMeta

    name = None
    file_exts = None

    # optional arguments and default values.
    args = None

    @abc.abstractmethod
    def parse(self, file_path, **kwargs):
        """
        Parse the given file path.

        Inherit from LoaderBase and override this method.

        :raise ParserError:
            When the parser encounters an error related to parsing.

        :raise OSError:
            When there is a problem with reading or accessing the
            given file.

        :return: Tuple of FileInfo and List of MarkerData.
        :rtype: (FileInfo, [MarkerData, ...])
        """
        return


FileInfo = collections.namedtuple(
    'FileInfo',
    [
        'marker_distorted',
        'marker_undistorted',
        'bundle_positions',
        'camera_field_of_view',
    ],
)


def create_file_info(
    marker_distorted=None,
    marker_undistorted=None,
    bundle_positions=None,
    camera_field_of_view=None,
):
    """
    Create the type of contents available in the file format.
    """
    if marker_distorted is None:
        marker_distorted = False
    if marker_undistorted is None:
        marker_undistorted = False
    if bundle_positions is None:
        bundle_positions = False
    if camera_field_of_view is None:
        camera_field_of_view = []
    file_info = FileInfo(
        marker_distorted=marker_distorted,
        marker_undistorted=marker_undistorted,
        bundle_positions=bundle_positions,
        camera_field_of_view=camera_field_of_view,
    )
    return file_info


def _get_file_path_formats(text):
    """
    Look up the possible Formats for the file path.

    :param text: File path text.

    :returns: List of formats for the file path.
    :rtype: [Format, ..]
    """
    formats = []
    if isinstance(text, TEXT_TYPE) is False:
        return formats
    if os.path.isfile(text) is False:
        return formats
    fmt_mgr = get_format_manager()
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
    assert isinstance(text, TEXT_TYPE)
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
    return info


def get_file_filter():
    """
    Construct a string to be given to QFileDialog as a file filter.

    :return: String of file filters, separated by ';;' characters.
    :rtype: str
    """
    file_fmt_names = []
    file_exts = []
    fmt_mgr = get_format_manager()
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


# module level manager, stores an instance of 'FormatManager'.
__format_manager = None


def get_format_manager():
    global __format_manager
    if __format_manager is None:
        __format_manager = FormatManager()
    return __format_manager


class MarkerData(object):
    def __init__(self):
        self._name = None  # None or str or unicode
        self._group_name = None  # None or str or unicode
        self._id = None  # None or int
        self._color = None  # the colour of the point
        self._x = KeyframeData()  # 0.0 is left, 1.0 is right.
        self._y = KeyframeData()  # 0.0 is bottom, 1.0 is top.
        self._enable = KeyframeData()
        self._weight = KeyframeData()
        self._bnd_x = None
        self._bnd_y = None
        self._bnd_z = None
        self._bnd_lock_x = None
        self._bnd_lock_y = None
        self._bnd_lock_z = None

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_id(self):
        return self._id

    def set_id(self, value):
        self._id = value

    def get_group_name(self):
        return self._group_name

    def set_group_name(self, value):
        self._group_name = value

    def get_color(self):
        return self._color

    def set_color(self, value):
        self._color = value

    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value

    def get_y(self):
        return self._y

    def set_y(self, value):
        self._y = value

    def get_enable(self):
        return self._enable

    def set_enable(self, value):
        self._enable = value

    def get_weight(self):
        return self._weight

    def set_weight(self, value):
        self._weight = value

    def get_bundle_x(self):
        return self._bnd_x

    def set_bundle_x(self, value):
        self._bnd_x = value

    def get_bundle_y(self):
        return self._bnd_y

    def set_bundle_y(self, value):
        self._bnd_y = value

    def get_bundle_z(self):
        return self._bnd_z

    def set_bundle_z(self, value):
        self._bnd_z = value

    def get_bundle_lock_x(self):
        return self._bnd_lock_x

    def set_bundle_lock_x(self, value):
        self._bnd_lock_x = value

    def get_bundle_lock_y(self):
        return self._bnd_lock_y

    def set_bundle_lock_y(self, value):
        self._bnd_lock_y = value

    def get_bundle_lock_z(self):
        return self._bnd_lock_z

    def set_bundle_lock_z(self, value):
        self._bnd_lock_z = value

    name = property(get_name, set_name)
    id = property(get_id, set_id)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    enable = property(get_enable, set_enable)
    weight = property(get_weight, set_weight)
    group_name = property(get_group_name, set_group_name)
    color = property(get_color, set_color)
    bundle_x = property(get_bundle_x, set_bundle_x)
    bundle_y = property(get_bundle_y, set_bundle_y)
    bundle_z = property(get_bundle_z, set_bundle_z)
    bundle_lock_x = property(get_bundle_lock_x, set_bundle_lock_x)
    bundle_lock_y = property(get_bundle_lock_y, set_bundle_lock_y)
    bundle_lock_z = property(get_bundle_lock_z, set_bundle_lock_z)


def _parse_int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None


def _parse_float_or_none(value):
    try:
        return float(value)
    except ValueError:
        return None


def _remove_comments_from_lines(lines):
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        line = line.partition('#')[0]
        clean_lines.append(line)
    return clean_lines


class LoaderPFTrack2DT(LoaderBase):

    name = 'PFTrack 2D Tracks (*.2dt / *.txt)'
    file_exts = ['.2dt', '.txt']
    args = [
        ('image_width', None),
        ('image_height', None),
    ]

    def parse(self, file_path, **kwargs):
        """
        Parse the file path as a PFTrack .2dt/.txt file.

        :param file_path: File path to parse.
        :type file_path: str

        :param kwargs: expected to contain 'image_width' and 'image_height'.

        :return: List of MarkerData.
        """
        # If the image width/height is not given we raise an error immediately.
        image_width = kwargs.get('image_width')
        image_height = kwargs.get('image_height')
        if image_width is None:
            image_width = 1.0
        if image_height is None:
            image_height = 1.0
        inv_image_width = 1.0 / image_width
        inv_image_height = 1.0 / image_height

        lines = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if len(lines) == 0:
            raise OSError('No contents in the file: %s' % file_path)
        mkr_data_list = []

        i = 0
        lines = _remove_comments_from_lines(lines)
        while i < len(lines):
            line = lines[i]
            mkr_name = None
            # Tracker Name
            if line.startswith('"') and line.endswith('"'):
                mkr_name = line[1:-1]
                i += 1
            else:
                i += 1
                continue

            # Clip number or Camera name.
            #
            # PFTrack 5 used a camera name, but future versions of
            # PFTrack use clip numbers.
            #
            # Either way, this value is parsed by never used by the
            # importer because I don't know how the clip number or
            # camera name should be used in mmSolver.
            cam_name = None
            line = lines[i]
            clip_number = _parse_int_or_none(line)
            if clip_number is not None:
                i += 1
            elif line.startswith('"') and line.endswith('"'):
                cam_name = line[1:-1]
                i += 1
            else:
                msg = 'File invalid, ' 'expecting a camera name (string) in line: %r'
                raise ParserError(msg % line)

            # Create marker
            mkr_data = MarkerData()
            mkr_data.set_name(mkr_name)

            # Number of frames.
            line = lines[i]
            number_of_frames = _parse_int_or_none(line)
            if number_of_frames is None:
                msg = (
                    'File invalid, '
                    'expecting a number of frames (integer) in line: %r'
                )
                raise ParserError(msg % line)
            i += 1

            # Parse per-frame data.
            frames = []
            for frame_index in range(number_of_frames):
                line = lines[i]
                line_split = line.split(' ')
                frame = None
                mkr_u = 0.0
                mkr_v = 0.0
                residual = None
                zdepth = None
                if len(line_split) not in [4, 5]:
                    msg = 'File invalid, ' 'there must be 4 or 5 numbers in line: %r'
                    raise ParserError(msg % line)

                frame = _parse_int_or_none(line_split[0])
                pos_x = _parse_float_or_none(line_split[1])
                pos_y = _parse_float_or_none(line_split[2])
                if frame is None or pos_x is None or pos_y is None:
                    raise ParserError('Invalid file format.')

                # PFTrack treats the center of the pixel as "0.0",
                # which is different from other matchmove
                # software.
                mkr_u = (pos_x + 0.5) * inv_image_width
                mkr_v = (pos_y + 0.5) * inv_image_height

                # # There is no need for residual or the Z-depth for now.
                # residual = _parse_float_or_none(line_split[3])
                # if len(line_split) == 5:
                #     zdepth = _parse_float_or_none(line_split[4])

                mkr_weight = 1.0
                mkr_data.weight.set_value(frame, mkr_weight)
                mkr_data.x.set_value(frame, mkr_u)
                mkr_data.y.set_value(frame, mkr_v)
                frames.append(frame)
                i += 1

            # Fill in occluded frames
            all_frames = list(range(min(frames), max(frames) + 1))
            for frame in all_frames:
                mkr_enable = int(frame in frames)
                mkr_data.enable.set_value(frame, mkr_enable)
                if mkr_enable is False:
                    mkr_data.weight.set_value(frame, 0.0)

            mkr_data_list.append(mkr_data)

        file_info = create_file_info()
        return file_info, mkr_data_list


class LoaderRZ2(LoaderBase):

    name = 'MatchMover TrackPoints (*.rz2)'
    file_exts = ['.rz2']
    args = []

    def parse(self, file_path, **kwargs):
        if not isinstance(file_path, TEXT_TYPE):
            raise TypeError('file_path is not a string: %r' % file_path)
        if not os.path.isfile(file_path):
            raise OSError('File path does not exist: %s' % file_path)

        mkr_data_list = []
        f = open(file_path, 'r')
        text = f.read()
        f.close()

        idx = text.find('imageSequence')
        if idx == -1:
            msg = "Could not get 'imageSequence' index from: %r"
            raise ParserError(msg % text)

        start_idx = text.find('{', idx + 1)
        if start_idx == -1:
            msg = 'Could not get the starting index from: %r'
            raise ParserError(msg % text)

        end_idx = text.find('}', start_idx + 1)
        if end_idx == -1:
            msg = 'Could not get the ending index from: %r'
            raise ParserError(msg % text)

        imgseq = text[start_idx + 1 : end_idx]
        imgseq = imgseq.strip()
        splt = imgseq.split()
        x_res = int(splt[0])
        y_res = int(splt[1])

        # Get path
        imgseq_path = re.search(r'.*f\(\s\"(.*)\"\s\).*', imgseq)
        if imgseq_path is None:
            msg = 'Could not get the image sequence path from: %r'
            raise ParserError(msg % imgseq)
        imgseq_path = imgseq_path.groups()

        # Get frame range
        range_regex = re.search(r'.*b\(\s(\d*)\s(\d*)\s(\d*)\s\)', imgseq)
        if range_regex is None:
            msg = 'Could not get the frame range from: %r'
            raise ParserError(msg % imgseq)
        range_grps = range_regex.groups()
        start_frame = int(range_grps[0])
        end_frame = int(range_grps[1])
        by_frame = int(range_grps[2])
        frames = range(start_frame, end_frame + 1, by_frame)

        idx = end_idx
        while True:
            idx = text.find('pointTrack', idx + 1)
            if idx == -1:
                break
            start_idx = text.find('{', idx + 1)
            if start_idx == -1:
                break
            end_idx = text.find('}', start_idx + 1)
            if end_idx == -1:
                break

            # Get point track name
            point_track_header = text[idx:start_idx]
            track_regex = re.search(r'pointTrack\s*\"(.*)\".*', point_track_header)
            if track_regex is None:
                continue
            track_grps = track_regex.groups()
            if len(track_grps) == 0:
                continue
            mkr_name = track_grps[0]

            # create marker
            mkr_data = MarkerData()
            mkr_data.set_name(mkr_name)
            mkr_data.weight.set_value(start_frame, 1.0)
            for frame in frames:
                mkr_data.enable.set_value(frame, 0)

            point_track = text[start_idx + 1 : end_idx]
            for line in point_track.splitlines():
                splt = line.split()
                if len(splt) == 0:
                    continue
                frame = int(splt[0])
                # NOTE: In MatchMover, top-left is (0,0), but we want
                # bottom-left to be (0,0).
                x = float(splt[1]) / x_res
                y = ((float(splt[2]) / y_res) * -1) + 1.0
                enable_value = int(frame in frames)

                mkr_data.enable.set_value(frame, enable_value)
                mkr_data.x.set_value(frame, x)
                mkr_data.y.set_value(frame, y)

            mkr_data_list.append(mkr_data)

        file_info = create_file_info()
        return file_info, mkr_data_list


class Loader3DETXT(LoaderBase):

    name = '3DEqualizer Track Points (*.txt)'
    file_exts = ['.txt']
    args = [
        ('image_width', None),
        ('image_height', None),
    ]

    def parse(self, file_path, **kwargs):
        """
        Parse the file path as a 3DEqualizer .txt file.

        :param file_path: File path to parse.
        :type file_path: str

        :param kwargs: expected to contain 'image_width' and 'image_height'.

        :return: List of MarkerData.
        """
        # If the image width/height is not given we raise an error immediately.
        image_width = kwargs.get('image_width')
        image_height = kwargs.get('image_height')
        if image_width is None:
            image_width = 1.0
        if image_height is None:
            image_height = 1.0
        inv_image_width = 1.0 / image_width
        inv_image_height = 1.0 / image_height

        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            raise OSError('No contents in the file: %s' % file_path)
        mkr_data_list = []

        lines = _remove_comments_from_lines(lines)

        line = lines[0]
        line = line.strip()
        num_points = _parse_int_or_none(line)
        if num_points is None:
            raise ParserError('Invalid file format.')
        if num_points < 1:
            raise ParserError('No points exist.')

        idx = 1  # Skip the first line
        for i in range(num_points):
            line = lines[idx]
            mkr_name = line.strip()

            # Create marker
            mkr_data = MarkerData()
            mkr_data.set_name(mkr_name)

            # Get point color
            idx += 1
            line = lines[idx]
            line = line.strip()
            mkr_color = _parse_int_or_none(line)
            if mkr_color is None:
                raise ParserError('Invalid file format.')
            mkr_data.set_color(mkr_color)

            idx += 1
            line = lines[idx]
            line = line.strip()
            num_frames = _parse_int_or_none(line)
            if num_frames is None:
                raise ParserError('Invalid file format.')
            if num_frames <= 0:
                idx += 1
                msg = 'point has no data: %r'
                LOG.warning(msg, mkr_name)
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
                if len(split) != 3:
                    # We should not get here
                    msg = 'File invalid, there must be 3 numbers in line: %r'
                    raise ParserError(msg % line)
                frame = _parse_int_or_none(split[0])
                pos_x = _parse_float_or_none(split[1])
                pos_y = _parse_float_or_none(split[2])
                if frame is None or pos_x is None or pos_y is None:
                    raise ParserError('Invalid file format.')
                mkr_u = pos_x * inv_image_width
                mkr_v = pos_y * inv_image_height
                mkr_weight = 1.0

                mkr_data.weight.set_value(frame, mkr_weight)
                mkr_data.x.set_value(frame, mkr_u)
                mkr_data.y.set_value(frame, mkr_v)
                frames.append(frame)

            # Fill in occluded point frames
            all_frames = list(range(min(frames), max(frames) + 1))
            for frame in all_frames:
                mkr_enable = bool(frame in frames)
                mkr_data.enable.set_value(frame, int(mkr_enable))
                if mkr_enable is False:
                    mkr_data.weight.set_value(frame, 0.0)

            mkr_data_list.append(mkr_data)
            idx += 1

        file_info = create_file_info()
        return file_info, mkr_data_list


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
        return UV_TRACK_FORMAT_VERSION_1
    version = data.get('version', UV_TRACK_FORMAT_VERSION_UNKNOWN)
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
    assert isinstance(name, TEXT_TYPE)
    assert set_name is None or isinstance(set_name, TEXT_TYPE)
    assert id_ is None or isinstance(id_, int)
    mkr_data.set_name(name)
    mkr_data.set_group_name(set_name)
    mkr_data.set_id(id_)
    return mkr_data


def _parse_point_3d_data_v3(mkr_data, point_data):
    """
    Parses the 3D data from individual point data.

    :param mkr_data: The MarkerData object to set.
    :type mkr_data: MarkerData

    :param point_data: The data dictionary, from the file format.
    :type point_data: dict

    :returns: A modified MarkerData, with bundle information set.
    :rtype: MarkerData
    """
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
    return mkr_data


def _parse_per_frame_v2_v3_v4(mkr_data, per_frame_data, pos_key=None):
    """
    Get the MarkerData per-frame, including X, Y, weight and enabled
    values.

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


def _parse_v2_and_v3(file_path, undistorted=None, with_3d_pos=None):
    """
    Parse the UV file format, using JSON.

    :param file_path: File path to read.
    :type file_path: str

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
    if with_3d_pos is None:
        with_3d_pos = False

    pos_key = 'pos_dist'
    if undistorted is None:
        undistorted = True
    if undistorted is True:
        pos_key = 'pos'

    mkr_data_list = []
    with open(file_path) as f:
        data = json.load(f)

    msg = 'Per-frame tracking data was not found on marker, skipping. ' 'name=%r'
    points = data.get('points', [])
    for point_data in points:
        mkr_data = MarkerData()

        # Static point information.
        mkr_data = _parse_point_info_v2_v3(mkr_data, point_data)

        # 3D point data
        if with_3d_pos is True:
            mkr_data = _parse_point_3d_data_v3(mkr_data, point_data)

        per_frame = point_data.get('per_frame', [])
        if len(per_frame) == 0:
            name = mkr_data.get_name()
            LOG.warning(msg, name)
            continue

        # Create marker per-frame data
        mkr_data, frames = _parse_per_frame_v2_v3_v4(
            mkr_data,
            per_frame,
            pos_key=pos_key,
        )

        # Fill in occluded point frames
        mkr_data = _parse_marker_occluded_frames_v1_v2_v3(
            mkr_data,
            frames,
        )
        mkr_data_list.append(mkr_data)

    return mkr_data_list


def _parse_camera_fov_v4(file_path):
    """
    Parse the UV file format, using JSON.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    with open(file_path) as f:
        data = json.load(f)

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

    :param file_path:
    :return:
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if len(lines) == 0:
        raise OSError('No contents in the file: %s' % file_path)
    mkr_data_list = []

    num_points = int(lines[0])
    if num_points < 1:
        raise ParserError('No points exist.')

    idx = 1  # Skip the first line
    for _ in range(num_points):
        mkr_name = lines[idx]
        mkr_name = mkr_name.strip()

        # Create marker
        mkr_data = MarkerData()
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
                raise ParserError(msg % (line, idx))
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

    file_info = create_file_info(marker_undistorted=True)
    return file_info, mkr_data_list


def parse_v2(file_path, **kwargs):
    """
    Parse the UV file format, using JSON.

    :param file_path: File path to read.
    :type file_path: str

    :return: List of MarkerData objects.
    """
    file_info = create_file_info(marker_undistorted=True)
    mkr_data_list = _parse_v2_and_v3(file_path, undistorted=True, with_3d_pos=False)
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

    file_info = create_file_info(
        marker_distorted=True,
        marker_undistorted=True,
        bundle_positions=True,
    )
    mkr_data_list = _parse_v2_and_v3(
        file_path,
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

    cam_fov_list = _parse_camera_fov_v4(
        file_path,
    )
    file_info = create_file_info(
        marker_distorted=True,
        marker_undistorted=True,
        bundle_positions=True,
        camera_field_of_view=cam_fov_list,
    )
    mkr_data_list = _parse_v2_and_v3(
        file_path,
        undistorted=undistorted,
        with_3d_pos=with_3d_pos,
    )
    return file_info, mkr_data_list


class LoaderUVTrack(LoaderBase):

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
        if version == UV_TRACK_FORMAT_VERSION_1:
            file_info, mkr_data_list = parse_v1(file_path, **kwargs)
        elif version == UV_TRACK_FORMAT_VERSION_2:
            file_info, mkr_data_list = parse_v2(file_path, **kwargs)
        elif version == UV_TRACK_FORMAT_VERSION_3:
            file_info, mkr_data_list = parse_v3(file_path, **kwargs)
        elif version == UV_TRACK_FORMAT_VERSION_4:
            file_info, mkr_data_list = parse_v4(file_path, **kwargs)
        else:
            msg = 'Could not determine format version for UV Track file.'
            raise ParserError(msg)
        return file_info, mkr_data_list


# Register the File Formats
mgr = get_format_manager()
mgr.register_format(LoaderUVTrack)
mgr.register_format(Loader3DETXT)
mgr.register_format(LoaderRZ2)
mgr.register_format(LoaderPFTrack2DT)


def read(file_path, **kwargs):
    """
    Read a file path, find the format parser based on the file extension.
    """
    if isinstance(file_path, TEXT_TYPE) is False:
        msg = 'file path must be a string, got %r'
        raise TypeError(msg % type(file_path))
    if os.path.isfile(file_path) is False:
        msg = 'file path does not exist; %r'
        raise OSError(msg % file_path)

    file_format_classes = []
    mgr = get_format_manager()
    for fmt in mgr.get_formats():
        attr = getattr(fmt, 'file_exts', None)
        if attr is None:
            continue
        if not isinstance(fmt.file_exts, list):
            continue
        for ext in fmt.file_exts:
            if file_path.endswith(ext):
                file_format_classes.append(fmt)
    if len(file_format_classes) == 0:
        msg = 'No file formats found for file path: %r'
        raise RuntimeError(msg % file_path)

    file_info = None
    mkr_data_list = []
    for file_format_class in file_format_classes:
        file_format_obj = file_format_class()
        try:
            contents = file_format_obj.parse(file_path, **kwargs)
        except (ParserError, OSError):
            contents = (None, [])

        file_info, mkr_data_list = contents
        if file_info and (isinstance(mkr_data_list, list) and len(mkr_data_list) > 0):
            break

    return file_info, mkr_data_list


def _set_3d_point(pg, p, mkr_data):
    bundle_pos = [mkr_data.bundle_x, mkr_data.bundle_y, mkr_data.bundle_z]
    bundle_pos_are_float = [isinstance(x, float) for x in bundle_pos]
    if all(bundle_pos_are_float) is False:
        return False

    tde4.setPointCalculated3D(pg, p, 1)
    tde4.setPointSurveyPosition3D(pg, p, bundle_pos)
    tde4.setPointSurveyMode(pg, p, 'SURVEY_EXACT')

    if SUPPORT_POINT_SURVEY_XYZ_ENABLED is False:
        return True

    bundle_lock = [
        int(mkr_data.bundle_lock_x or 0),
        int(mkr_data.bundle_lock_y or 0),
        int(mkr_data.bundle_lock_z or 0),
    ]
    if any(bundle_lock) is True:
        tde4.setPointSurveyXYZEnabledFlags(
            pg,
            p,
            bundle_lock[0],
            bundle_lock[1],
            bundle_lock[2],
        )
    return True


def create_markers(c, pg, start_frame, file_info, mkr_data_list):
    frames = tde4.getCameraNoFrames(c)
    if frames == 0:
        return []

    point_list = []
    for mkr_data in mkr_data_list:
        curve = [[-1.0, -1.0]] * (frames + 1)
        for frame in range(frames):
            pos_x = -1.0
            pos_y = -1.0
            real_frame = start_frame + frame
            enable = mkr_data.enable.get_value(real_frame)
            if enable:
                pos_x = mkr_data.x.get_value(real_frame)
                pos_y = mkr_data.y.get_value(real_frame)
            curve[frame] = [pos_x, pos_y]

        weight = mkr_data.weight.get_value(1)

        p = tde4.createPoint(pg)
        tde4.setPointName(pg, p, mkr_data.name)
        tde4.setPointWeight(pg, p, weight)
        tde_start_frame = 1  # 3DE internally always starts at frame 1.
        tde4.setPointPosition2DBlock(pg, p, c, tde_start_frame, curve)
        point_list.append(p)

        _set_3d_point(pg, p, mkr_data)

    return point_list


# GUI
c = tde4.getCurrentCamera()
pg = tde4.getCurrentPGroup()
if c is not None and pg is not None:
    req = tde4.createCustomRequester()
    tde4.addTextAreaWidget(req, 'help_text', 'Help', 170, 0)
    tde4.addSeparatorWidget(req, 'separator1')
    tde4.addFileWidget(req, 'file_browser', 'File Name...', '*')
    tde4.addOptionMenuWidget(
        req, 'distortion_mode', 'Distortion Mode', 'Distorted', 'Undistorted'
    )
    tde4.addToggleWidget(req, 'with_3d_position', 'Use Survey Position', 0)

    tde4.appendTextAreaWidgetString(req, 'help_text', HELP_TEXT)

    ret = tde4.postCustomRequester(req, WINDOW_TITLE, 800, 340, 'Ok', 'Cancel')
    if ret == 1:
        file_path = tde4.getWidgetValue(req, 'file_browser')
        if file_path is not None and os.path.isfile(file_path):
            distortion_mode = tde4.getWidgetValue(req, 'distortion_mode')
            undistorted = distortion_mode == 2

            with_3d_pos = tde4.getWidgetValue(req, 'with_3d_position') == 1

            image_width = tde4.getCameraImageWidth(c)
            image_height = tde4.getCameraImageHeight(c)
            file_info, mkr_data_list = read(
                file_path,
                image_width=image_width,
                image_height=image_height,
                undistorted=undistorted,
                with_3d_pos=with_3d_pos,
            )

            start, end, step = tde4.getCameraSequenceAttr(c)
            start_frame = start

            create_markers(c, pg, start_frame, file_info, mkr_data_list)
else:
    tde4.postQuestionRequester(
        WINDOW_TITLE, 'There is no current Point Group or Camera.', 'Ok'
    )
