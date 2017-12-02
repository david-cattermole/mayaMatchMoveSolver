"""
The frame number that the solver will solve on.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver.api.utils as api_utils


class Frame(object):
    def __init__(self, value, primary=False, secondary=False):
        assert isinstance(value, (float, int))
        self._number = value
        self._primary = primary
        self._secondary = secondary
        return

    def get_number(self):
        # TODO: Should we convert _number to an int or float before returning?
        return self._number

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
