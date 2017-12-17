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
    def __init__(self, value, tags=None,
                 primary=False, secondary=False):
        assert isinstance(value, (float, int))
        assert tags is None or isinstance(tags, list)
        self._number = value
        self._tags = []
        if tags is not None and isinstance(tags, list):
            self._tags = tags

        tag = 'primary'
        if primary is True and tag not in self._tags:
            self._tags.append(tag)

        tag = 'secondary'
        if secondary is True and tag not in self._tags:
            self._tags.append(tag)

        if len(self._tags) == 0:
            self._tags.append('normal')
        assert isinstance(self._tags, list)
        return

    def get_data(self):
        return {
            'number': self.get_number(),
            'tags': self.get_tags(),
        }

    def set_data(self, value):
        assert isinstance(value, dict)

        num = value.get('number')
        tags = value.get('tags')
        if num is None:
            msg = 'Data is not valid, number value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid, msg
        if tags is None:
            msg = 'Data is not valid, tags value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid, msg

        self.set_number(num)
        self.set_tags(tags)

    def get_number(self):
        # TODO: Should we convert _number to an int or float before returning?
        return self._number

    def set_number(self, value):
        assert isinstance(value, (int, float))
        self._number = value
        return

    def get_tags(self):
        return self._tags

    def set_tags(self, value):
        assert isinstance(value, list)
        self._tags = value
        return

    def add_tag(self, value):
        assert isinstance(value, str)
        self._tags.append(value)
        return
