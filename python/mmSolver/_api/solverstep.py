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
Solver related functions and classes for an individual solver
operation (step).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.compile as api_compile

LOG = mmSolver.logger.get_logger()


class SolverStep(solverbase.SolverBase):
    """
    Defines an individual invocation of a solver.

    The SolverStep contains the following properties:

    - :ref:`solver-design-solver-max-iterations` Max iterations

    - :ref:`solver-design-solver-delta`

    - :ref:`solver-design-solver-auto-diff-type`

    - :ref:`solver-design-solver-tau` - Tau factor

    - :ref:`solver-design-solver-epsilon-one` - Gradient error factor

    - :ref:`solver-design-solver-epsilon-two` - Parameter error factor

    - :ref:`solver-design-solver-epsilon-three` - Error factor

    - Solver type

    - Use animated attributes

    - Use static attributes

    - Use frame tags

    - Frame list

    See the individual methods for more information.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a SolverStep class with default values.

        :param args: Not used.
        :param kwargs: Not used.
        """
        super(SolverStep, self).__init__(*args, **kwargs)
        self._attributes_use = {
            'animated': True,
            'static': True,
        }
        self._frames_use = {
            'tags': ['primary', 'secondary', 'normal'],
        }
        return

    ############################################################################

    def get_max_iterations(self):
        """
        Get the maximum number of iterations the solve will perform.

        :rtype: int or None
        """
        return self._data.get('max_iterations')

    def set_max_iterations(self, value):
        """
        Set the maximum number of iterations.

        :param value: Max iterations number.
        :type value: int
        """
        if isinstance(value, int) is False:
            raise TypeError('Expected int value type.')
        self._data['max_iterations'] = value
        return

    def get_delta_factor(self):
        """
        Get the parameter delta factor.

        :rtype: float or None
        """
        return self._data.get('delta')

    def set_delta_factor(self, value):
        """
        Set the parameter delta factor.

        :param value: Delta factor number.
        :type value: float
        """
        self._data['delta'] = value
        return

    def get_auto_diff_type(self):
        """
        Get method used to calculate differencing.

        :rtype: int or None
        """
        return self._data.get('auto_diff_type')

    def set_auto_diff_type(self, value):
        """
        Set automatic differencing method.

        :param value:
            The method to be used. Must be a value in
            AUTO_DIFF_TYPE_LIST.
        :type value: int or None
        """
        if value not in const.AUTO_DIFF_TYPE_LIST:
            msg = 'auto_diff_type must be one of %r; value=%r'
            msg = msg % (const.AUTO_DIFF_TYPE_LIST, value)
            raise ValueError(msg)
        self._data['auto_diff_type'] = value
        return

    def get_tau_factor(self):
        """
        Get the Tau factor value.

        :rtype: float or None
        """
        return self._data.get('tau_factor')

    def set_tau_factor(self, value):
        """
        Set the Tau factor value.

        :param value: Initial damping Tau value.
        :type value: float
        """
        self._data['tau_factor'] = value
        return

    def get_gradient_error_factor(self):
        """
        Get the error factor for steepness changes.

        :rtype: float or None
        """
        return self._data.get('gradient_error')

    def set_gradient_error_factor(self, value):
        """
        Set the error factor for steepness changes.

        :param value:
        :type value:
        """
        self._data['gradient_error'] = value
        return

    def get_parameter_error_factor(self):
        """
        Get error level for parameter changes.

        :rtype: float or None
        """
        return self._data.get('parameter_error')

    def set_parameter_error_factor(self, value):
        """
        Set error level for parameter changes.

        :param value: Value to set.
        :type value: float
        """
        self._data['parameter_error'] = value
        return

    def get_auto_parameter_scaling(self):
        """
        :rtype: bool or None
        """
        return self._data.get('auto_parameter_scaling')

    def set_auto_parameter_scaling(self, value):
        """
        :type value: bool
        """
        if isinstance(value, bool) is False:
            raise TypeError('Expected bool value type.')
        self._data['auto_parameter_scaling'] = value

    def get_error_factor(self):
        """
        Get error level for deviation changes.

        :rtype: float or None
        """
        return self._data.get('error')

    def set_error_factor(self, value):
        """
        Set error level for deviation changes.

        :param value: Value to set.
        :type value: float
        """
        self._data['error'] = value
        return

    def get_solver_type(self):
        """
        The type of internal solver library to use, as an index.

        See the question
        :ref:`solver-faq-how-to-get-supported-solver-types`,
        for more details of the values returned.

        :rtype: int or None
        """
        return self._data.get('solver_type')

    def set_solver_type(self, value):
        """
        Set the internal solver library to use for solving.

        See the question
        :ref:`solver-faq-how-to-get-supported-solver-types`,
        for more details of the values that can be set.

        :param value: Solver type index number.
        :type value: int
        """
        self._data['solver_type'] = value

    def get_scene_graph_mode(self):
        """
        :rtype: int or None
        """
        return self._data.get('scene_graph_mode')

    def set_scene_graph_mode(self, value):
        """
        :type value: int
        """
        assert value in const.SCENE_GRAPH_MODE_LIST
        self._data['scene_graph_mode'] = value

    def get_verbose(self):
        """
        Should we print lots of information to the terminal?

        :rtype: bool or None
        """
        return self._data.get('verbose')

    def set_verbose(self, value):
        """
        Set verbosity option, yes or no.

        :param value: Turn on verbose mode? Yes or no.
        :type value: bool
        """
        if isinstance(value, bool) is False:
            raise TypeError('Expected bool value type.')
        self._data['verbose'] = value

    ############################################################################

    def get_robust_loss_scale(self):
        """
        :rtype: float or None
        """
        return self._data.get('robust_loss_scale')

    def set_robust_loss_scale(self, value):
        """
        :param value:
        :type value:
        """
        self._data['robust_loss_scale'] = value
        return

    def get_robust_loss_type(self):
        """
        :rtype: int or None
        """
        return self._data.get('robust_loss_type')

    def set_robust_loss_type(self, value):
        """
        :param value:
            The method to be used. Must be a value in
            ROBUST_LOSS_TYPE_LIST.
        :type value: int or None
        """
        if value not in const.ROBUST_LOSS_TYPE_VALUE_LIST:
            msg = 'robust_loss_type must be one of %r; value=%r'
            msg = msg % (const.ROBUST_LOSS_TYPE_VALUE_LIST, value)
            raise ValueError(msg)
        self._data['robust_loss_type'] = value
        return

    ############################################################################

    def get_time_eval_mode(self):
        return self._data.get('time_eval_mode', const.TIME_EVAL_MODE_DEFAULT)

    def set_time_eval_mode(self, value):
        assert value in const.TIME_EVAL_MODE_LIST
        self._data['time_eval_mode'] = value

    ############################################################################

    def get_frame_solve_mode(self):
        return self._data.get('frame_solve_mode', const.FRAME_SOLVE_MODE_DEFAULT)

    def set_frame_solve_mode(self, value):
        assert value in const.FRAME_SOLVE_MODE_LIST
        self._data['frame_solve_mode'] = value

    ############################################################################

    def get_use_smoothness(self):
        return self._data.get('smoothness')

    def set_use_smoothness(self, value):
        assert isinstance(value, (bool, int))
        self._data['smoothness'] = bool(value)

    def get_use_stiffness(self):
        return self._data.get('stiffness')

    def set_use_stiffness(self, value):
        assert isinstance(value, (bool, int))
        self._data['stiffness'] = bool(value)

    ############################################################################

    def get_remove_unused_markers(self):
        return self._data.get('remove_unused_markers')

    def set_remove_unused_markers(self, value):
        assert isinstance(value, (bool, int))
        self._data['remove_unused_markers'] = bool(value)

    def get_remove_unused_attributes(self):
        return self._data.get('remove_unused_attributes')

    def set_remove_unused_attributes(self, value):
        assert isinstance(value, (bool, int))
        self._data['remove_unused_attributes'] = bool(value)

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

    def get_solver_version(self):
        """
        :rtype: int or None
        """
        return self._data.get('solver_version', const.SOLVER_VERSION_DEFAULT)

    def set_solver_version(self, value):
        """
        :param value: May be SOLVER_VERSION_ONE or SOLVER_VERSION_TWO.
        """
        if isinstance(value, int) is False:
            raise TypeError('Expected int value type, got %r.' % type(value))
        if value not in const.SOLVER_VERSION_LIST:
            raise TypeError(
                'Expected value in list %r, got %r.'
                % (const.SOLVER_VERSION_LIST, value)
            )
        self._data['solver_version'] = value

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
        assert self.get_frame_list_length() > 0

        solver_version = self.get_solver_version()
        is_solver_v1 = solver_version == 1
        is_solver_v2 = solver_version == 2
        if is_solver_v1 is True:
            func = 'maya.cmds.mmSolver'
        elif is_solver_v2 is True:
            func = 'maya.cmds.mmSolver_v2'
        else:
            raise NotImplementedError(
                'solver_version has invalid value: %r' % solver_version
            )

        args = []
        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['frame'] = []

        # Get precomputed data to reduce re-querying Maya for data.
        precomputed_data = self.get_precomputed_data()
        mkr_state_values = precomputed_data.get(solverbase.MARKER_STATIC_VALUES_KEY)
        attr_state_values = precomputed_data.get(solverbase.ATTR_STATIC_VALUES_KEY)
        if is_solver_v1 is True:
            attr_stiff_state_values = precomputed_data.get(
                solverbase.ATTR_STIFFNESS_STATIC_VALUES_KEY
            )
            attr_smooth_state_values = precomputed_data.get(
                solverbase.ATTR_SMOOTHNESS_STATIC_VALUES_KEY
            )

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
        use_animated = self.get_attributes_use_animated()
        use_static = self.get_attributes_use_static()
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

        # Stiffness Attribute Flags
        stiff_flags = None
        if is_solver_v1 is True:
            use_stiffness = self.get_use_stiffness()
            if use_stiffness is True:
                stiff_flags = api_compile.attr_stiffness_compile_flags(
                    col,
                    attr_list,
                    attr_static_values=attr_state_values,
                    attr_stiff_static_values=attr_stiff_state_values,
                )

        # Smoothness Attribute Flags
        smooth_flags = None
        if is_solver_v1 is True:
            use_smoothness = self.get_use_smoothness()
            if use_smoothness is True:
                smooth_flags = api_compile.attr_smoothness_compile_flags(
                    col,
                    attr_list,
                    attr_static_values=attr_state_values,
                    attr_smooth_static_values=attr_smooth_state_values,
                )

        # Get Frames
        frm_list = self.get_frame_list()
        frame_use_tags = self.get_frames_use_tags()
        frames = api_compile.frames_compile_flags(frm_list, frame_use_tags)
        if len(frames) == 0:
            LOG.warning('No Frames found!')
            return

        kwargs['marker'] = markers
        kwargs['camera'] = cameras
        kwargs['attr'] = attrs
        kwargs['frame'] = frames

        if stiff_flags:
            kwargs['attrStiffness'] = stiff_flags
        if smooth_flags:
            kwargs['attrSmoothness'] = smooth_flags

        solver_type = self.get_solver_type()
        if solver_type is not None:
            kwargs['solverType'] = solver_type

        scene_graph_mode = self.get_scene_graph_mode()
        frame_solve_mode = self.get_frame_solve_mode()
        if scene_graph_mode is not None:
            # Otherwise the 'auto' scene graph will be passed to
            # mmSolver and mmSolver command does not support 'auto'
            # mode.
            scene_graph_mode = max(const.SCENE_GRAPH_MODE_MAYA_DAG, scene_graph_mode)

            if scene_graph_mode == const.SCENE_GRAPH_MODE_MAYA_DAG:
                assert frame_solve_mode == const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE
            kwargs['sceneGraphMode'] = scene_graph_mode

        if frame_solve_mode is not None:
            if frame_solve_mode == const.FRAME_SOLVE_MODE_PER_FRAME:
                assert scene_graph_mode == const.SCENE_GRAPH_MODE_MM_SCENE_GRAPH
            kwargs['frameSolveMode'] = frame_solve_mode

        iterations = self.get_max_iterations()
        if iterations is not None:
            kwargs['iterations'] = iterations

        verbose = self.get_verbose()
        if verbose is not None:
            kwargs['verbose'] = verbose

        delta_factor = self.get_delta_factor()
        if delta_factor is not None:
            kwargs['delta'] = delta_factor

        auto_diff_type = self.get_auto_diff_type()
        if auto_diff_type is not None:
            kwargs['autoDiffType'] = auto_diff_type

        auto_param_scaling = self.get_auto_parameter_scaling()
        if auto_param_scaling is not None:
            kwargs['autoParamScaling'] = int(auto_param_scaling)

        tau_factor = self.get_tau_factor()
        if tau_factor is not None:
            kwargs['tauFactor'] = tau_factor

        function_error_factor = self.get_error_factor()
        if function_error_factor is not None:
            kwargs['functionTolerance'] = function_error_factor

        parameter_error_factor = self.get_parameter_error_factor()
        if parameter_error_factor is not None:
            kwargs['parameterTolerance'] = parameter_error_factor

        gradient_error_factor = self.get_gradient_error_factor()
        if gradient_error_factor is not None:
            kwargs['gradientTolerance'] = gradient_error_factor

        robust_loss_type = self.get_robust_loss_type()
        if robust_loss_type is not None:
            kwargs['robustLossType'] = robust_loss_type

        robust_loss_scale = self.get_robust_loss_scale()
        if robust_loss_scale is not None:
            kwargs['robustLossScale'] = robust_loss_scale

        kwargs['timeEvalMode'] = self.get_time_eval_mode()

        if is_solver_v1 is True:
            value = self.get_remove_unused_markers()
            if value is not None:
                kwargs['removeUnusedMarkers'] = value

            value = self.get_remove_unused_attributes()
            if value is not None:
                kwargs['removeUnusedAttributes'] = value

        if is_solver_v2 is True:
            key = 'verbose'
            if key in kwargs:
                del kwargs[key]

        action = api_action.Action(func=func, args=args, kwargs=kwargs)

        # Check the inputs and outputs are valid.
        vaction = None
        if withtest is True:
            is_mmsolver_v1 = api_action.action_func_is_mmSolver_v1(action)
            is_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(action)
            assert any((is_mmsolver_v1, is_mmsolver_v2))

            vfunc = func
            vargs = list(args)
            vkwargs = kwargs.copy()
            remove_keys = ['debugFile', 'verbose']
            for key in remove_keys:
                if key in vkwargs:
                    del vkwargs[key]
            vkwargs['printStatistics'] = ['inputs']
            vaction = api_action.Action(func=vfunc, args=vargs, kwargs=vkwargs)

        yield action, vaction


# For backwards compatibility.
Solver = SolverStep
