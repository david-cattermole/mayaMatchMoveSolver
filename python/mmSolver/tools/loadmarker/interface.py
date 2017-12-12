"""
Provides a base interface for marker import plug-ins.
"""

import sys
import abc


def float_is_equal(x, y):
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
    # TODO: This function is quite slow, it should be improved.
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

    def __init__(self, initial_value=None):
        self._value = dict()
        self._uptodate = False
        self._keyframe_values = None
        if initial_value is not None:
            self.set_value(initial_value, 0)

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

    def get_value(self, frame):
        """
        Get the key value at frame. frame is an integer.
        """
        assert isinstance(self._value, dict)
        key = str(frame)
        value = self._value.get(key)
        if value is None:
            # there is no key on the frame, find the closest frame.
            frame = get_closest_frame(frame, self._value)
            key = str(frame)
            if key in self._value:
                value = self._value[key]
        return value

    def get_keyframe_values(self):
        assert isinstance(self._value, dict)

        # This enables multiple calls not to re-compute this data.
        if self._uptodate is True:
            return self._keyframe_values

        key_values = list()

        # Sort keys, based on int values, not string.
        keys = self._value.keys()
        int_keys = list()
        # for key in keys:
        for key in self._value.iterkeys():
            int_keys.append(int(key))
        keys = sorted(int_keys)

        # Create key/value pairs.
        for key in keys:
            key_value = (int(key), self.get_value(int(key)))
            key_values.append(key_value)

        self._keyframe_values = key_values
        self._uptodate = True
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
        self._uptodate = False
        frame_str = str(frame)
        self._value[frame_str] = value
        return True

    def simplify_data(self):
        """
        Tries to convert the keyframe data into
        static if all values are the same.
        """
        assert isinstance(self._value, dict)
        self._uptodate = False
        initial = None
        total = float()  # assume it's a float?
        total_num = int()
        for key in iter(self._value):
            if initial is None:
                initial = self._value[key]
            total = total + self._value[key]
            total_num = total_num + 1
        average = total / total_num
        if float_is_equal(average, initial):
            self._value = average
        return True


class MarkerData(object):
    def __init__(self):
        self._name = None  # None or str or unicode
        self._colour = None  # the colour of the point
        self._x = KeyframeData()
        self._y = KeyframeData()
        self._enable = KeyframeData()
        self._weight = KeyframeData()

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_colour(self):
        return self._colour

    def set_colour(self, value):
        self._colour = value

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

    name = property(get_name, set_name)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    enable = property(get_enable, set_enable)
    weight = property(get_weight, set_weight)
    colour = property(get_colour, set_colour)


class LoaderBase(object):
    __metaclass__ = abc.ABCMeta

    name = None
    file_exts = None

    @abc.abstractmethod
    def parse(self, file_path):
        return
