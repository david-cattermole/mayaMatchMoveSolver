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

    - :ref:`solver-faq-how-to-get-supported-solver-types` - Solver type

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

    def compile(self, mkr_list, attr_list, withtest=False):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param self: The solver to compile
        :type self: Solver

        :param mkr_list: Markers to measure
        :type mkr_list: list of Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of Attribute

        :return: List of SolverActions to be performed one after the other.
        :rtype: [SolverAction, ..]
        """
        assert isinstance(self, solverbase.SolverBase)
        assert isinstance(mkr_list, list)
        assert isinstance(attr_list, list)
        assert self.get_frame_list_length() > 0

        func = 'maya.cmds.mmSolver'
        args = []
        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['frame'] = []

        # Get Markers and Cameras
        markers, cameras = api_compile.markersAndCameras_compile_flags(mkr_list)
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
        attrs = api_compile.attributes_compile_flags(attr_list,
                                                     use_animated,
                                                     use_static)
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return

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

        solver_type = self.get_solver_type()
        if solver_type is not None:
            kwargs['solverType'] = solver_type

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

        tau_factor = self.get_tau_factor()
        if tau_factor is not None:
            kwargs['tauFactor'] = tau_factor

        gradient_error_factor = self.get_gradient_error_factor()
        if gradient_error_factor is not None:
            kwargs['epsilon1'] = gradient_error_factor

        parameter_error_factor = self.get_parameter_error_factor()
        if parameter_error_factor is not None:
            kwargs['epsilon2'] = parameter_error_factor

        error_factor = self.get_error_factor()
        if error_factor is not None:
            kwargs['epsilon3'] = error_factor

        kwargs['robustLossType'] = const.ROBUST_LOSS_TYPE_TRIVIAL_VALUE
        kwargs['robustLossScale'] = 1.0

        # TODO: Add 'robustLossType' flag.
        # TODO: Add 'robustLossScale' flag.
        # TODO: Add 'autoParamScaling' flag.
        # TODO: Add 'debugFile' flag.

        # # Add a debug file flag to the mmSolver command, only
        # # triggered during debug mode.
        # # TODO: Wrap this in another function.
        # if logging.DEBUG >= LOG.getEffectiveLevel():
        #     debug_file = maya.cmds.file(query=True, sceneName=True)
        #     debug_file = os.path.basename(debug_file)
        #     debug_file, ext = os.path.splitext(debug_file)
        #     debug_file_path = os.path.join(
        #         os.path.expandvars('${TEMP}'),
        #         debug_file + '_' + str(i).zfill(6) + '.log'
        #     )
        #     if len(debug_file) > 0 and debug_file_path is not None:
        #         kwargs['debugFile'] = debug_file_path

        action = api_action.Action(
            func=func,
            args=args,
            kwargs=kwargs
        )

        # Check the inputs and outputs are valid.
        vaction = None
        if withtest is True:
            assert api_action.action_func_is_mmSolver(action) is True
            vfunc = func
            vargs = list(args)
            vkwargs = kwargs.copy()
            remove_keys = ['debugFile', 'verbose']
            for key in remove_keys:
                if key in vkwargs:
                    del vkwargs[key]
            vkwargs['printStatistics'] = ['inputs']
            vaction = api_action.Action(
                func=vfunc,
                args=vargs,
                kwargs=vkwargs
            )

        yield action, vaction


Solver = SolverStep
