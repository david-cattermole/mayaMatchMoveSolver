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
Helper utils for Qt.py module.

This module will *not* import Qt.py, and contains functions designed to be
run before Qt.py is imported.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

PREFERRED_BINDING = 'QT_PREFERRED_BINDING'
BINDING_ORDER = ['PySide6', 'PySide2', 'PyQt5', 'PySide', 'PyQt4']


def override_binding_order(binding_order=None):
    """
    Change the expected order of Qt bindings used by Qt.py.

    By default the binding order is defined in the module level BINDING_ORDER
    variable.

    If the user has already defined the environment variable
    'QT_PREFERRED_BINDING' then we will skip overriding the bind order.

    .. note:: This function should be run before importing Qt.py.

    :param binding_order: A list of binding names
    :type binding_order: [str, ..]]
    """
    if binding_order is None:
        binding_order = BINDING_ORDER
    if PREFERRED_BINDING not in os.environ:
        os.environ[PREFERRED_BINDING] = os.pathsep.join(binding_order)
    return
