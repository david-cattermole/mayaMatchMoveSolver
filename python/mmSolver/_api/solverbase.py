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
Solver operation base class.
"""

import abc
import uuid

import mmSolver.logger
import mmSolver._api.constant as const


LOG = mmSolver.logger.get_logger()

# Keys to be used in a 'precomputed data' structure.
MARKER_STATIC_VALUES_KEY = 'marker_state_values'
ATTR_STATIC_VALUES_KEY = 'attribute_state_values'
ATTR_STIFFNESS_STATIC_VALUES_KEY = 'attribute_stiffness_state_values'
ATTR_SMOOTHNESS_STATIC_VALUES_KEY = 'attribute_smoothness_state_values'


class SolverBase(object):
    """
    The base class of a Solver operation.

    A Solver Operation may have any number of methods and data, this class
    does not enforce a common method interface (yet).

    The SolverBase class should be sub-classed and then (at least) the
    'compile' function should be overridden.
    """
    def __init__(self, name=None, data=None, *args, **kwargs):
        """
        Initialise a SolverBase.

        This __init__ should be called by sub-classes, for example::

        >>> class MySolver(SolverBase):
        >>>     def __init__(self, *args, **kwargs):
        >>>         super(MySolver, self).__init__(*args, **kwargs)

        :param name: The name of the Solver.
        :type name: basestring

        :param data:
            The internal data structure to set inside the Solver base.
            The data holds information about the current options of
            the solver.
        :type data: dict

        :param args:
            Whatever positional arguments to give to the init function.
        :type args: list

        :param kwargs:
            Whatever keyword arguments to give to the init function.
        :type kwargs: dict
        """
        super(SolverBase, self).__init__(*args, **kwargs)
        self._data = const.SOLVER_DATA_DEFAULT.copy()
        if isinstance(data, dict):
            self.set_data(data)
        if isinstance(name, (str, unicode, uuid.UUID)):
            self._data['name'] = name
        else:
            # give the solver a random name.
            if 'name' not in self._data:
                self._data['name'] = str(uuid.uuid4())
        assert 'name' in self._data
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} data={data}'.format(
            hash=hex(hash(self)),
            data=self.get_data(),
        )
        result += ')>'
        return result

    def get_name(self):
        return self._data.get('name')

    def set_name(self, name):
        assert isinstance(name, (str, unicode, uuid.UUID))
        self._data['name'] = str(name)
        return

    def get_data(self):
        assert isinstance(self._data, dict)
        return self._data.copy()

    def set_data(self, data):
        assert isinstance(data, dict)
        self._data = data.copy()
        return self

    def get_enabled(self):
        """
        Flags this solver should not be used for solving.
        :rtype: bool
        """
        return self._data.get('enabled')

    def set_enabled(self, value):
        """
        Set if this solver be used?

        :param value: The enabled value.
        :type value: bool
        """
        if isinstance(value, bool) is False:
            raise TypeError('Expected bool value type.')
        self._data['enabled'] = value
        return

    def get_precomputed_data(self):
        """
        Get precomputed data that can be re-used inside this Solver.

        :rtype: dict or None
        """
        return self._data.get('precomputed_data')

    def set_precomputed_data(self, value):
        """
        Set the precomputed data (dictionary). This precomputed data will
        be used inside the Solver rather than computing many times.

        :param value:
            The data structure of the precomputed data to be re-used.
        :type value: dict
        """
        if isinstance(value, dict) is False:
            raise TypeError('Expected dict value type.')
        self._data['precomputed_data'] = value
        return

    @abc.abstractmethod
    def compile(self, col, mkr_list, attr_list, withtest=False):
        """
        Compile solver into actions.

        :raises: 'NotValid', if the compile goes wrong.

        :param col: Collection to be compile.
        :type col: Collection

        :param mkr_list: List of Markers used in the Solve.
        :type mkr_list: [Marker, ..]

        :param attr_list: Attributes to be solved for.
        :type attr_list: [Attribute, ..]

        :param withtest: Should the tests (validation) be generated
                         along with the real solver steps?
        :type withtest: bool

        :returns: Return a generator, to yield two Action objects.
        """
        raise NotImplementedError
