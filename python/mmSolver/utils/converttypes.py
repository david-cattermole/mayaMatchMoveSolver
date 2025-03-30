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
Conversion functions between various types, for fundamental Python types.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


# Words recognised as True or False.
TRUE_WORDS = ['1', 'y', 't', 'yes', 'on', 'ya', 'yeah', 'true']
FALSE_WORDS = ['0', 'n', 'f', 'no', 'off', 'nah', 'nope', 'false']


def stringToBoolean(value):
    """
    Convert a string into a boolean value, using list of 'TRUE_WORDS'
    """
    v = None
    if isinstance(value, bool):
        v = value
    elif isinstance(value, pycompat.TEXT_TYPE):
        value = value.strip().lower()
        if value in TRUE_WORDS:
            v = True
        elif value in FALSE_WORDS:
            v = False
        else:
            return False
    else:
        raise TypeError
    return v


def booleanToString(value):
    """
    Convert boolean value to a string.
    """
    return str(value)


def stringToIntList(value):
    """
    Convert a string of integer ranges to a list of integers.

    value = '1001-1101'
    value = '1001,1002,1003-1005,1010-1012'

    :param value: The string value to convert.
    :type value: str

    :return: List of integer numbers parsed from the string.
    :rtype: [int, ..]
    """
    if isinstance(value, pycompat.TEXT_TYPE) is False:
        msg = 'Given argument is not a string: type=%r value=%r'
        raise TypeError(msg, type(value), value)
    value = value.strip()
    int_list = []
    for v in value.split(','):
        v = v.strip()
        if v.isdigit() is True:
            i = int(v)
            int_list.append(i)
        if '-' not in v:
            continue

        dash_split = v.split('-')
        dash_split = [x for x in dash_split if x.isdigit()]
        if len(dash_split) > 1:
            # Even if the user adds more than 1 dash character, we only take
            # the first two.
            s = int(dash_split[0])
            e = int(dash_split[1])
            if s == e:
                int_list.append(s)
                continue
            if s < e:
                int_list += list(range(s, e + 1))
    int_list = list(set(int_list))
    int_list = list(sorted(int_list))
    return int_list


def intListToString(value):
    """
    Convert a list of integers to a string.
    """
    if isinstance(value, list) is False:
        msg = 'Given argument is not a list: type=%r value=%r'
        raise TypeError(msg, type(value), value)
    int_list = list(sorted(set(value)))
    grps = []
    start = -1
    end = -1
    prev = -1
    for i, num in enumerate(int_list):
        first = i == 0
        last = (i + 1) == len(int_list)
        if first is True:
            # Start a new group.
            start = num
            end = num
        if (prev + 1) != num:
            # End old group.
            end = prev
            if end != -1:
                grps.append((start, end))
            # New group
            start = num
            end = num
        if last is True:
            # Close off final group.
            end = num
            if end != -1:
                grps.append((start, end))
        prev = num

    string_list = []
    for grp in grps:
        s, e = grp
        if s == e:
            string_list.append(str(s))
        else:
            string_list.append('{0}-{1}'.format(s, e))
    return ','.join(string_list)


def stringToInteger(value):
    return int(value)
