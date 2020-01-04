# Copyright (C) 2019 David Cattermole.
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
Conversion functions between various types, for Qt types.

This module should NOT be imported into any module that may not run with a
GUI avalable (for example on the farm)
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.utils.converttypes as utils_convert

LOG = mmSolver.logger.get_logger()

# Aliases for backwards compatibility.
TRUE_WORDS = utils_convert.TRUE_WORDS
FALSE_WORDS = utils_convert.FALSE_WORDS
stringToBoolean = utils_convert.stringToBoolean
booleanToString = utils_convert.booleanToString
stringToIntList = utils_convert.stringToIntList
intListToString = utils_convert.intListToString
stringToInteger = utils_convert.stringToInteger


def stringToStrategy(value):
    return value


def stringToAttrFilter(value):
    return value


def booleanToCheckState(value):
    # NOTE: This requires the Qt GUI imports, so this cannot be moved into
    # mmSolver.utils.converttypes
    if isinstance(value, bool) is False:
        msg = 'value is not bool type: %r'
        raise TypeError(msg % type(value))
    v = QtCore.Qt.CheckState.Unchecked
    if value is True:
        v = QtCore.Qt.CheckState.Checked
    return v


def checkStateToBoolean(value):
    # NOTE: This requires the Qt GUI imports, so this cannot be moved into
    # mmSolver.utils.converttypes
    v = False
    if value == QtCore.Qt.CheckState.Checked:
        v = True
    return v
