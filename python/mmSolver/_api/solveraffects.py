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
    solver_kwargs['frame'] = [1]  # 'mmSolver' must have a frame value
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

    # Method exists to be compatible with
    # 'mmSolver._api.compile.compile_solver_with_cache'.
    #
    # SolverAffects does not need any frame numbers as input, but a
    # value is needed by SolverBase class.
    def get_frame_list(self):
        return [frame.Frame(1)]

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

        func = 'maya.cmds.mmSolverAffects'
        args = []
        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['mode'] = 'addAttrsToMarkers'

        # Get precomputed data to reduce re-querying Maya for data.
        precomputed_data = self.get_precomputed_data()
        mkr_state_values = precomputed_data.get(solverbase.MARKER_STATIC_VALUES_KEY)
        attr_state_values = precomputed_data.get(solverbase.ATTR_STATIC_VALUES_KEY)

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
