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

import mmSolver.logger
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.compile as api_compile

LOG = mmSolver.logger.get_logger()


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
        mkr_state_values = precomputed_data.get(
            solverbase.MARKER_STATIC_VALUES_KEY)
        attr_state_values = precomputed_data.get(
            solverbase.ATTR_STATIC_VALUES_KEY)
        attr_stiff_state_values = precomputed_data.get(
            solverbase.ATTR_STIFFNESS_STATIC_VALUES_KEY)
        attr_smooth_state_values = precomputed_data.get(
            solverbase.ATTR_SMOOTHNESS_STATIC_VALUES_KEY)

        # Get Markers and Cameras
        markers, cameras = api_compile.markersAndCameras_compile_flags(
            mkr_list,
            mkr_static_values=mkr_state_values)
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
            attr_static_values=attr_state_values)
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return

        kwargs['marker'] = markers
        kwargs['camera'] = cameras
        kwargs['attr'] = attrs

        action = api_action.Action(
            func=func,
            args=args,
            kwargs=kwargs
        )

        # Check the inputs and outputs are valid.
        vaction = None
        if withtest is True:
            assert api_action.action_func_is_mmSolverAffects(action) is True
            vfunc = func
            vargs = list(args)
            vkwargs = kwargs.copy()
            vaction = api_action.Action(
                func=vfunc,
                args=vargs,
                kwargs=vkwargs
            )

        yield action, vaction
