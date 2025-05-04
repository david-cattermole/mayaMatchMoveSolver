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
Solver to pre-compute relationships between objects.

The results of the pre-computation stops subsequent solvers from
needing to re-calculate the relationships (which can be expensive to
compute).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.compile as api_compile
import mmSolver._api.excep as excep

LOG = mmSolver.logger.get_logger()


def _parse_usage_list(key, in_data):
    split_char = '#'
    out_data = [x for x in in_data if x.startswith(key)]
    out_data = [x.partition(key)[-1] for x in out_data]
    out_data = split_char.join(out_data)
    out_data = out_data.split(split_char)
    out_data = [x for x in out_data if len(x) > 0]
    return out_data


def _runAndSetUsedSolveObjects(col_name, *args, **kwargs):
    """
    Call mmSolver, find (un)used objects, then set values for UIs to look up.

    :param col_name:
    :param args:
    :param kwargs:
    :return:
    """
    import maya.cmds

    # Generate mmSolver command.
    solver_args = args
    solver_kwargs = kwargs.copy()
    del solver_kwargs['mode']
    del solver_kwargs['graphMode']
    solver_kwargs['printStatistics'] = ['usedSolveObjects']
    data = maya.cmds.mmSolver(*solver_args, **solver_kwargs)

    markers_used = _parse_usage_list('markers_used=', data)
    markers_unused = _parse_usage_list('markers_unused=', data)
    attributes_used = _parse_usage_list('attributes_used=', data)
    attributes_unused = _parse_usage_list('attributes_unused=', data)

    # Set usage value attributes on Markers and Attributes.
    import mmSolver.api as mmapi

    for mkr_node in markers_used:
        mkr = mmapi.Marker(node=mkr_node)
        mkr.set_used_hint(const.MARKER_USED_HINT_USED_VALUE)
    for mkr_node in markers_unused:
        mkr = mmapi.Marker(node=mkr_node)
        mkr.set_used_hint(const.MARKER_USED_HINT_NOT_USED_VALUE)

    col = mmapi.Collection(col_name)
    for node_attr in attributes_used:
        attr = mmapi.Attribute(name=node_attr)
        col.set_attribute_used_hint(attr, const.ATTRIBUTE_USED_HINT_USED_VALUE)
    for node_attr in attributes_unused:
        attr = mmapi.Attribute(name=node_attr)
        col.set_attribute_used_hint(attr, const.ATTRIBUTE_USED_HINT_NOT_USED_VALUE)
    return


def reset_marker_used_hints(mkr_nodes):
    import mmSolver.api as mmapi

    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(node=mkr_node)
        mkr.set_used_hint(const.MARKER_USED_HINT_UNKNOWN_VALUE)
    return


def reset_attr_used_hints(col_name, node_attr_list):
    import mmSolver.api as mmapi

    col = mmapi.Collection(col_name)
    for node_attr in node_attr_list:
        attr = mmapi.Attribute(name=node_attr)
        col.set_attribute_used_hint(attr, const.ATTRIBUTE_USED_HINT_UNKNOWN_VALUE)
    return


class SolverAffects(solverbase.SolverBase):
    """
    SolverAffects is a metadata calculation solver. SolverAffects
    does not directly adjust attributes.

    The SolverAffects contains no properties, other than the base
    Markers, and Attributes lists.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a SolverAffects class with default values.

        :param args: Not used.
        :param kwargs: Not used.
        """
        super(SolverAffects, self).__init__(*args, **kwargs)
        return

    ############################################################################

    def get_graph_mode(self):
        """
        :rtype: bool
        """
        return self._data.get('graph_mode', const.AFFECTS_GRAPH_MODE_DEFAULT)

    def set_graph_mode(self, value):
        """
        :type value: bool or int
        """
        assert isinstance(value, str)
        value in const.AFFECTS_GRAPH_MODE_LIST
        self._data['graph_mode'] = value

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
                msg = 'Frame already added to SolverStep, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

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

    ##########################################

    def compile(self, col, mkr_list, attr_list, withtest=False):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param self: The solver to compile
        :type self: Solver

        :param col: The collection to compile.
        :type col: Collection

        :param mkr_list: Markers to measure
        :type mkr_list: list of Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of Attribute

        :return:
            Yields a tuple of two Actions at each iteration. First
            action is the solver action, second action is for
            validation of the solve.
        :rtype: (Action, Action)
        """
        assert isinstance(self, solverbase.SolverBase)
        assert isinstance(mkr_list, list)
        assert isinstance(attr_list, list)

        graph_mode = self.get_graph_mode()
        assert graph_mode in const.AFFECTS_GRAPH_MODE_LIST

        func = 'maya.cmds.mmSolverAffects'
        args = []
        kwargs = dict()
        kwargs['frame'] = []
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['mode'] = 'addAttrsToMarkers'
        kwargs['graphMode'] = graph_mode

        # Get precomputed data to reduce re-querying Maya for data.
        precomputed_data = self.get_precomputed_data()
        mkr_state_values = precomputed_data.get(solverbase.MARKER_STATIC_VALUES_KEY)
        attr_state_values = precomputed_data.get(solverbase.ATTR_STATIC_VALUES_KEY)

        # Get frames.
        frame_use_tags = ['primary', 'secondary', 'normal']
        frm_list = self.get_frame_list()
        frames = api_compile.frames_compile_flags(frm_list, frame_use_tags)
        if len(frames) == 0:
            LOG.warning('No Frames found!')
            return

        # Get Markers and Cameras
        markers, cameras = api_compile.markersAndCameras_compile_flags(
            mkr_list, mkr_static_values=mkr_state_values
        )
        if len(markers) == 0 and len(cameras) == 0:
            LOG.warning('No Markers or Cameras found!')
            return
        elif len(markers) == 0:
            LOG.warning('No Markers found!')
            return
        elif len(cameras) == 0:
            LOG.warning('No Cameras found!')
            return

        # Get Attributes
        #
        # NOTE: time is not a factor for the calculation of 'affects'
        # relationships, therefore use_animated and use_static are
        # True, to ensure all attributes (that are not locked) are
        # calculated.
        use_animated = True
        use_static = True
        attrs = api_compile.attributes_compile_flags(
            col,
            attr_list,
            use_animated,
            use_static,
            attr_static_values=attr_state_values,
        )
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return

        kwargs['frame'] = frames
        kwargs['marker'] = markers
        kwargs['camera'] = cameras
        kwargs['attr'] = attrs

        action = api_action.Action(func=func, args=args, kwargs=kwargs)
        yield action, action

        # Query and set 'used solver object' values on nodes.
        func = _runAndSetUsedSolveObjects
        args = [col.get_node()]
        action = api_action.Action(func=func, args=args, kwargs=kwargs)
        yield action, action
