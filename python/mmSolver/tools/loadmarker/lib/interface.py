# Copyright (C) 2018 David Cattermole.
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
Provides a base interface for marker import plug-ins.
"""

import sys
import abc
import collections


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
        keys = self._data.keys()
        int_keys = list()
        for key in self._data.iterkeys():
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
        for key in iter(self._data):
            if initial is None:
                initial = self._data[key]
            total = total + float(self._data[key])
            total_num = total_num + 1
        average = total / total_num
        if float_is_equal(average, initial):
            self._data = average
        return True


class MarkerData(object):
    def __init__(self):
        self._name = None  # None or str or unicode
        self._group_name = None  # None or str or unicode
        self._id = None  # None or int
        self._color = None  # the colour of the point
        self._x = KeyframeData()
        self._y = KeyframeData()
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


FileInfo = collections.namedtuple(
    'FileInfo',
    [
        'marker_distorted',
        'marker_undistorted',
        'bundle_positions',
        'camera_field_of_view',
    ]
)


def create_file_info(marker_distorted=None,
                     marker_undistorted=None,
                     bundle_positions=None,
                     camera_field_of_view=None):
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
        """
        return
