# Copyright (C) 2018, 2019 David Cattermole.
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
Naming utilities.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

import maya.cmds

import mmSolver.utils.python_compat as pycompat
from mmSolver._api import constant as const
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def find_valid_maya_node_name(
    name,
    prefix=None,
    auto_add_num=True,
    auto_add_num_padding=3,
    auto_inc=True,
    auto_inc_try_limit=999,
):
    """
    Get a new valid Maya name - canonical function to get valid Maya node names.

    Examples of auto-adding a number suffix::

       >>> find_valid_maya_node_name('name')
       name_001
       >>> find_valid_maya_node_name('name', auto_add_num_padding=4)
       name_0001

    Examples of auto-incrementing::

       >>> find_valid_maya_node_name('name_01')
       name_02
       >>> find_valid_maya_node_name('name_001')
       name_002
       >>> find_valid_maya_node_name('001')
       prefix_002

    :param name: The name string to validate.
    :type name: str

    :param prefix: Prefix to add to name in case of invalid first character.
    :type prefix: str or None

    :param auto_add_num: If given a node with no number in it, should
                         we add a number automatically?
    :type auto_add_num: bool

    :param auto_add_num_padding: Padding of the number to add,
                                 2 = '01', 3 = '001', 4 = '0001'.
    :type auto_add_num_padding: int

    :param auto_inc: Should we auto-increment the number in the name?
    :type auto_inc: bool

    :param auto_inc_try_limit: When trying to find a non-existing Maya
                               node name, how many times can we
                               increment until we give up?
    :type auto_inc_try_limit: int

    :return: A valid Maya node name.
    :rtype: str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert prefix is None or isinstance(prefix, pycompat.TEXT_TYPE)
    assert isinstance(auto_add_num, bool)
    assert isinstance(auto_add_num_padding, int)
    assert isinstance(auto_inc, bool)
    assert isinstance(auto_inc_try_limit, int)

    # Ensure no unsupported characters are used in the node name.
    for char in const.BAD_MAYA_CHARS:
        name.replace(char, '_')

    # Add prefix, if the first letter is a digit (which Maya doesn't
    # allow.)
    #
    # NOTE: name could start with a number; this should be prefixed.
    if name[0].isdigit():
        if prefix is None:
            prefix = 'prefix'
        name = prefix + '_' + name

    # Add a number suffix if no number is already added to the
    # node name, add a number.
    if auto_add_num is True:
        splits = []
        contents = re.split('([0-9]+)', name)
        has_digit = len(contents) > 1
        if has_digit is False:
            new_number = '1'.zfill(auto_add_num_padding)
            contents.append('_')
            contents.append(new_number)
        name = ''.join(contents)

    # Auto-increment a number in the name given.
    if auto_inc is True:
        i = 0
        limit = auto_inc_try_limit
        while i <= limit and maya.cmds.objExists(name):
            splits = []
            contents = re.split('([0-9]+)', name)

            # Increment the number.
            incremented = False
            for content in reversed(contents):
                if content.isdigit() is True and incremented is False:
                    size = len(content)
                    num = int(content) + 1
                    content = str(num).zfill(size)
                    incremented = True
                splits.append(content)
            name = ''.join(reversed(splits))
            i = i + 1
    return name


def get_new_marker_name(name, prefix=None, suffix=None):
    """
    Create a name for a marker object, using 'name' as the base
    identifier.

    :param name: Name of object.
    :type name: str

    :param prefix: Prefix of the marker, if a number is the first
                   character. If None, a default name is added.
    :type prefix: str or None

    :param suffix: Suffix of the marker, added to the name. If None, a
                   default name is added.
    :type suffix: str or None

    :return: Name for the marker.
    :rtype: str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert prefix is None or isinstance(prefix, pycompat.TEXT_TYPE)
    assert suffix is None or isinstance(suffix, pycompat.TEXT_TYPE)
    if prefix is None:
        prefix = const.MARKER_NAME_PREFIX
    if suffix is None:
        suffix = const.MARKER_NAME_SUFFIX
    if suffix.lower() not in name.lower():
        name += suffix
    name = find_valid_maya_node_name(name, prefix=prefix, auto_add_num=False)
    return name


def get_new_bundle_name(name, prefix=None, suffix=None):
    """
    Create a name for a bundle object, using 'name' as the base
    identifier.

    :param name: Name of object.
    :type name: str

    :param prefix: Prefix of the bundle, if a number is the first
                   character. If None, a default name is added.
    :type prefix: str or None

    :param suffix: Suffix of the bundle, added to the name. If None, a
                   default name is added.
    :type suffix: str or None

    :return: Name for the bundle.
    :rtype: str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert prefix is None or isinstance(prefix, pycompat.TEXT_TYPE)
    assert suffix is None or isinstance(suffix, pycompat.TEXT_TYPE)
    if prefix is None:
        prefix = const.BUNDLE_NAME_PREFIX
    if suffix is None:
        suffix = const.BUNDLE_NAME_SUFFIX
    if suffix.lower() not in name.lower():
        name += suffix
    name = find_valid_maya_node_name(name, prefix=prefix, auto_add_num=False)
    return name


def get_new_line_name(name, prefix=None, suffix=None):
    """
    Create a name for a line object, using 'name' as the base
    identifier.

    :param name: Name of object.
    :type name: str

    :param prefix: Prefix of the line, if a number is the first
                   character. If None, a default name is added.
    :type prefix: str or None

    :param suffix: Suffix of the line, added to the name. If None, a
                   default name is added.
    :type suffix: str or None

    :return: Name for the line.
    :rtype: str
    """
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert prefix is None or isinstance(prefix, pycompat.TEXT_TYPE)
    assert suffix is None or isinstance(suffix, pycompat.TEXT_TYPE)
    if prefix is None:
        prefix = const.LINE_NAME_PREFIX
    if suffix is None:
        suffix = const.LINE_NAME_SUFFIX
    if suffix.lower() not in name.lower():
        name += suffix
    name = find_valid_maya_node_name(name, prefix=prefix, auto_add_num=False)
    return name
