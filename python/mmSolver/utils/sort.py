# Copyright (C) 2020 David Cattermole.
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
Sorting utilities.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def __convert_to_integer(text):
    return int(text) if text.isdigit() else text


def sort_strings_with_digits(items):
    """Sort the given iterable in the way that humans expect.

    For example, using the built-in Python 'sorted' function without
    extra arguments sorts::

        >>> x = ['a1', 'a2', 'a10']
        >>> sorted(x)
        ['a1', 'a10', 'a2']

    This function will correctly sort the numbers on the ends of the
    letters as a human would expect::

        >>> x = ['a1', 'a2', 'a10']
        >>> sort_strings_with_digits(x)
        ['a1', 'a2', 'a10']

    Helpful function from:
    https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
    """
    key_func = lambda key: [__convert_to_integer(c) for c in re.split('([0-9]+)', key)]
    return sorted(items, key=key_func)
