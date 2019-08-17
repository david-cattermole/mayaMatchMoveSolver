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

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute

LOG = mmSolver.logger.get_logger()


def _compile_markersAndCameras(mkr_list):
    # Get Markers and Cameras
    added_cameras = []
    markers = []
    cameras = []
    for mkr in mkr_list:
        assert isinstance(mkr, marker.Marker)
        mkr_node = mkr.get_node()
        assert isinstance(mkr_node, basestring)
        bnd = mkr.get_bundle()
        if bnd is None:
            msg = 'Cannot find bundle from marker, skipping; mkr_node={0}'
            msg = msg.format(repr(mkr_node))
            LOG.warning(msg)
            continue
        bnd_node = bnd.get_node()
        if bnd_node is None:
            msg = 'Bundle node is invalid, skipping; mkr_node={0}'
            msg = msg.format(repr(mkr_node))
            LOG.warning(msg)
            continue
        cam = mkr.get_camera()
        if cam is None:
            msg = 'Cannot find camera from marker; mkr={0}'
            msg = msg.format(mkr.get_node())
            LOG.warning(msg)
        cam_tfm_node = cam.get_transform_node()
        cam_shp_node = cam.get_shape_node()
        assert isinstance(cam_tfm_node, basestring)
        assert isinstance(cam_shp_node, basestring)
        markers.append((mkr_node, cam_shp_node, bnd_node))
        if cam_shp_node not in added_cameras:
            cameras.append((cam_tfm_node, cam_shp_node))
            added_cameras.append(cam_shp_node)
    return markers, cameras


def _compile_attributes(attr_list, use_animated, use_static):
    # Get Attributes
    attrs = []
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        if attr.is_locked():
            continue
        name = attr.get_name()
        node_name = attr.get_node()
        attr_name = attr.get_attr()

        # If the user does not specify a min/max value then we get it
        # from Maya directly, if Maya doesn't have one, we leave
        # min/max_value as None and pass it to the mmSolver command
        # indicating there is no bound.
        min_value = attr.get_min_value()
        max_value = attr.get_max_value()
        if min_value is None:
            min_exists = maya.cmds.attributeQuery(
                attr_name,
                node=node_name,
                minExists=True,
            )
            if min_exists:
                min_value = maya.cmds.attributeQuery(
                    attr_name,
                    node=node_name,
                    minimum=True,
                )
                if len(min_value) == 1:
                    min_value = min_value[0]
                else:
                    msg = 'Cannot handle attributes with multiple '
                    msg += 'minimum values; node={0} attr={1}'
                    msg = msg.format(node_name, attr_name)
                    raise excep.NotValid(msg)

        if max_value is None:
            max_exists = maya.cmds.attributeQuery(
                attr_name,
                node=node_name,
                maxExists=True,
            )
            if max_exists is True:
                max_value = maya.cmds.attributeQuery(
                    attr_name,
                    node=node_name,
                    maximum=True,
                )
                if len(max_value) == 1:
                    max_value = max_value[0]
                else:
                    msg = 'Cannot handle attributes with multiple '
                    msg += 'maximum values; node={0} attr={1}'
                    msg = msg.format(node_name, attr_name)
                    raise excep.NotValid(msg)

        # Scale and Offset
        scale_value = None
        offset_value = None
        attr_type = maya.cmds.attributeQuery(
            attr_name,
            node=node_name,
            attributeType=True)
        if attr_type.endswith('Angle'):
            offset_value = 360.0

        animated = attr.is_animated()
        static = attr.is_static()
        use = False
        if use_animated and animated is True:
            use = True
        if use_static and static is True:
            use = True
        if use is True:
            attrs.append(
                (name,
                 str(min_value),
                 str(max_value),
                 str(offset_value),
                 str(scale_value))
            )
    return attrs


def _compile_frames(frm_list, frame_use_tags):
    frames = []
    for frm in frm_list:
        num = frm.get_number()
        tags = frm.get_tags()
        use = False
        if len(frame_use_tags) > 0 and len(tags) > 0:
            for tag in frame_use_tags:
                if tag in tags:
                    use = True
                    break
        else:
            use = True
        if use is True:
            frames.append(num)
    return frames


class SolverStep(solverbase.SolverBase):
    """
    SolverStep; the options for how a solver should be executed.
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

    def compile(self, mkr_list, attr_list, prog_fn=None):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param self: The solver to compile
        :type self: Solver

        :param mkr_list: Markers to measure
        :type mkr_list: list of Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of Attribute

        :param prog_fn: Progress Function, with signature f(int)
        :type prog_fn: function

        :return: List of SolverActions to be performed one after the other.
        :rtype: [SolverAction, ..]
        """
        assert isinstance(self, solverbase.SolverBase)
        assert isinstance(mkr_list, list)
        assert isinstance(attr_list, list)
        assert self.get_frame_list_length() > 0

        func = maya.cmds.mmSolver
        args = []
        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['frame'] = []

        # Get Markers and Cameras
        markers, cameras = _compile_markersAndCameras(mkr_list)
        if len(markers) == 0 and len(cameras) == 0:
            LOG.warning('No Markers or Cameras found!')
            return None
        elif len(markers) == 0:
            LOG.warning('No Markers found!')
            return None
        elif len(cameras) == 0:
            LOG.warning('No Cameras found!')
            return None

        # Get Attributes
        use_animated = self.get_attributes_use_animated()
        use_static = self.get_attributes_use_static()
        attrs = _compile_attributes(attr_list, use_animated, use_static)
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return None

        # Get Frames
        frm_list = self.get_frame_list()
        frame_use_tags = self.get_frames_use_tags()
        frames = _compile_frames(frm_list, frame_use_tags)
        if len(frames) == 0:
            LOG.warning('No Frames found!')
            return None

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

        # TODO: Add 'robustLossType' flag.
        # TODO: Add 'robustLossScale' flag.
        # TODO: Add 'autoParamScaling' flag.
        # TODO: Add 'debugFile' flag.
        # TODO: Add 'printStatistics' flag.

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
        # msg = 'kwargs:\n' + pprint.pformat(kwargs)
        # LOG.debug(msg)
        return [action]


Solver = SolverStep
