# Copyright (C) 2022 David Cattermole.
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
Provide Python 2.7 vs 3.x compatibility without using any
third-party packages (like 'six' for example).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# NOTE: Do NOT add any module imports here other than the Python
# standard library. This module is used in many places in mmSolver,
# and we do not want a circular import dependency.
import sys


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
