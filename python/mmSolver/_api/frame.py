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
The frame number that the solver will solve on.

Each Frame has a list of unlimited 'tags', this is very flexible when
creating function callbacks for inclusion/exclusion of frames in a
solve. For example, you can tag different frames for different solvers,
so that frame 1, 11 and 21 are solved by a slower solver, and
frames 1 to 21 are solved with a faster solver.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep


class Frame(object):
    """
    Hold a time value with tags meta-data.

    Example usage::

        >>> frmA = mmapi.Frame(1)
        >>> frmA.get_number()
        1
        >>> frmA.get_tags()
        ['normal']
        >>> frmB = mmapi.Frame(10, primary=True)
        >>> frmB.get_number()
        10
        >>> frmB.get_tags()
        ['primary']
        >>> frmC = mmapi.Frame(20, tags=['custom'], primary=True)
        >>> frmC.get_number()
        20
        >>> frmC.get_tags()
        ['custom', 'primary']

    """
    def __init__(self,
                 value,
                 tags=None,
                 primary=False,
                 secondary=False):
        """
        Initialise a Frame object to hold a frame value and tags.

        :param value: The frame number.
        :type value: int or float

        :param tags: List of string values accocated with this frame number.
        :type tags: [str, ... ] or None

        :param primary: Is this frame 'primary'?
        :type primary: bool

        :param secondary: Is this frame 'secondary'?
        :type secondary: bool
        """
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

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} data={data}'.format(
            hash=hex(hash(self)),
            data=self.get_data(),
        )
        result += ')>'
        return result

    def get_data(self):
        """
        Get the data of this Frame, both number and tags.

        Data structure returned is::
           
            {
                'number': int or float, 
                'tags': list of strs,
            }

        :return: Data structure.
        :rtype: dict
        """
        return {
            'number': self.get_number(),
            'tags': self.get_tags(),
        }

    def set_data(self, value):
        """
        Set the internal frame data using once function call.

        Expected data structure is::
           
            {
                'number': int or float, 
                'tags': list of strs,
            }

        :param value: Data structure with both 'number' and 'tags' keys.
        :type value: dict

        :return: None
        """
        assert isinstance(value, dict)

        num = value.get('number')
        tags = value.get('tags')
        if num is None:
            msg = 'Data is not valid, number value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid(msg)
        if tags is None:
            msg = 'Data is not valid, tags value not valid; {0}'
            msg = msg.format(value)
            raise excep.NotValid(msg)

        self.set_number(num)
        self.set_tags(tags)
        return

    def get_number(self):
        """
        Get the frame number.

        :return: The frame number.
        :rtype: int or float
        """
        # TODO: Should we convert _number to an int or float before
        #  returning?
        return self._number

    def set_number(self, value):
        """
        Set the frame number.

        :param value: the frame number.
        :type value: int or float

        :return: None
        """
        assert isinstance(value, (int, float))
        self._number = value
        return

    def get_tags(self):
        """
        Get list of tags associated with this Frame.

        :return: List of tags.
        :rtype: [str, ... ]
        """
        return self._tags

    def set_tags(self, value):
        """
        Set the tags explicitly.

        :param value: List of tags to set.
        :type value: list

        :return: None
        """
        assert isinstance(value, list)
        self._tags = value
        return

    def add_tag(self, value):
        """
        Add a tag to the list of (internally stored) tags.

        :param value: Tag name to add.
        :type value: str

        :return: None
        """
        assert isinstance(value, str)
        self._tags.append(value)
        return
