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
Solver related functions.
"""

import uuid
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.constant as const


class Solver(object):
    """
    Solver; the options for how a solver should be executed.
    """
    def __init__(self, name=None, data=None):
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

        self._attributes_use = {
            'animated': True,
            'static': True,
        }
        self._frames_use = {
            'tags': ['primary', 'secondary', 'normal'],
        }
        return

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

    ############################################################################

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

    def get_max_iterations(self):
        return self._data.get('max_iterations')

    def set_max_iterations(self, value):
        if isinstance(value, int) is False:
            raise TypeError('Expected int value type.')
        self._data['max_iterations'] = value
        return

    def get_delta_factor(self):
        return self._data.get('delta')

    def set_delta_factor(self, value):
        self._data['delta'] = value
        return

    def get_auto_diff_type(self):
        return self._data.get('auto_diff_type')

    def set_auto_diff_type(self, value):
        if value not in const.AUTO_DIFF_TYPE_LIST:
            msg = 'auto_diff_type must be one of %r; value=%r'
            msg = msg % (const.AUTO_DIFF_TYPE_LIST, value)
            raise ValueError(msg)
        self._data['auto_diff_type'] = value
        return

    def get_tau_factor(self):
        return self._data.get('tau_factor')

    def set_tau_factor(self, value):
        self._data['tau_factor'] = value
        return

    def get_gradient_error_factor(self):
        return self._data.get('gradient_error')

    def set_gradient_error_factor(self, value):
        self._data['gradient_error'] = value
        return

    def get_parameter_error_factor(self):
        return self._data.get('parameter_error')

    def set_parameter_error_factor(self, value):
        self._data['parameter_error'] = value
        return

    def get_error_factor(self):
        return self._data.get('error')

    def set_error_factor(self, value):
        self._data['error'] = value
        return

    def get_solver_type(self):
        return self._data.get('solver_type')

    def set_solver_type(self, value):
        self._data['solver_type'] = value

    def get_verbose(self):
        return self._data.get('verbose')

    def set_verbose(self, value):
        if isinstance(value, bool) is False:
            raise TypeError('Expected bool value type.')
        self._data['verbose'] = value

    ############################################################################

    def get_attributes_use_animated(self):
        return self._attributes_use.get('animated')

    def set_attributes_use_animated(self, value):
        assert isinstance(value, (bool, int))
        self._attributes_use['animated'] = bool(value)

    def get_attributes_use_static(self):
        return self._attributes_use.get('static')

    def set_attributes_use_static(self, value):
        assert isinstance(value, (bool, int))
        self._attributes_use['static'] = bool(value)

    def get_frames_use_tags(self):
        return self._frames_use.get('tags')

    def set_frames_use_tags(self, value):
        assert isinstance(value, list)
        self._frames_use['tags'] = value

    ############################################################################

    def get_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_frame_list_length(self):
        return len(self.get_frame_list())

    def add_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to Solver, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid, msg

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_frame(frm)
        return

    def remove_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_frame(frm)
        return

    def set_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_frame_list(frm_list)
        return

    def clear_frame_list(self):
        key = 'frame_list'
        self._data[key] = []
        return
