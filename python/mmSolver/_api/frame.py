"""
The frame number that the solver will solve on.

TODO: We could add named 'tags' to a frame, this would be very flexible when
creating function callbacks for inclusion/exclusion of frames.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep


class Frame(object):
    def __init__(self, value, primary=False, secondary=False):
        assert isinstance(value, (float, int))
        self._number = value
        self._primary = primary
        self._secondary = secondary
        return

    def get_data(self):
        return {
            'number': self.get_number(),
            'secondary': self.get_primary(),
            'primary': self.get_secondary(),
        }

    def set_data(self, value):
        assert isinstance(value, dict)

        num = value.get('number')
        pri = value.get('primary')
        sec = value.get('secondary')
        if num is None:
            msg = 'Data is not valid, number value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid, msg
        if pri is None:
            msg = 'Data is not valid, primary value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid, msg
        if sec is None:
            msg = 'Data is not valid, secondary value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid, msg

        self.set_number(num)
        self.set_primary(pri)
        self.set_secondary(sec)

    def get_number(self):
        # TODO: Should we convert _number to an int or float before returning?
        return self._number

    def set_number(self, value):
        assert isinstance(value, (int, float))
        self._number = value
        return

    def get_primary(self):
        return self._primary

    def set_primary(self, value):
        assert isinstance(value, bool)
        self._primary = value
        return

    def get_secondary(self):
        return self._secondary

    def set_secondary(self, value):
        assert isinstance(value, bool)
        self._secondary = value
        return
