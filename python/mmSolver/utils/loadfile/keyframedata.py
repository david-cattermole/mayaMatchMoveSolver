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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import mmSolver.utils.loadfile.floatutils as floatutils


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
            frame = floatutils.get_closest_frame(frame, self._data)
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
        if floatutils.float_is_equal(average, initial):
            self._data = average
        return True
