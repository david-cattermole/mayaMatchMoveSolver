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
Collection functions used to group and execute a solve using mmSolver.
"""

import time
import pprint
import os
import warnings
import uuid
import logging

import maya.cmds
import maya.mel
import maya.OpenMayaAnim as OpenMayaAnim

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.node as node_utils
import mmSolver.utils.animutils as anim_utils
import mmSolver._api.state as api_state
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.solveresult as solveresult
import mmSolver._api.solver as solver
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute
import mmSolver._api.sethelper as sethelper
import mmSolver._api.collectionutils as collectionutils


LOG = mmSolver.logger.get_logger()


def _create_collection_attributes(node):
    """
    Create the attributes expected to be on a Collection (set) node.

    :param node: Collection set node to add attributes to.
    :type node: str
    """
    attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_LIST
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            dataType='string'
        )
        plug = node + '.' + attr
        maya.cmds.setAttr(plug, lock=True)

    attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_RESULTS
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            dataType='string'
        )
        plug = node + '.' + attr
        maya.cmds.setAttr(plug, lock=True)

    attr = const.COLLECTION_ATTR_LONG_NAME_DEVIATION
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=-1.0,
            defaultValue=-1.0,
            keyable=True
        )
        plug = node + '.' + attr
        maya.cmds.setAttr(plug, lock=True)
    return


class Collection(object):
    """
    Holds all data needed for a mmSolver run.
    """

    def __init__(self, node=None, name=None):
        """
        Initialize the Collection with the given Maya node.

        :param node: Maya node to attach to.
        :type node: str or None

        :param name: This is a backwards compatible kwarg for 'node'.
        :type name: None or str
        """
        if name is not None:
            msg = (
                "mmSolver.api.Collection(name=value), "
                "'name' is a deprecated flag, use 'node' "
            )
            warnings.warn(msg)
            node = name

        self._set = sethelper.SetHelper()
        self._solver_list = None

        # Store the keyword arguments for the command, return this if the user
        # asks for the arguments. Invalidate these arguments and force a
        # re-compile if the user sets a new value, otherwise it's still valid.
        self._kwargs_list = []

        if node is not None:
            if isinstance(node, (str, unicode)):
                self.set_node(node)
            else:
                msg = 'node argument must be a string.'
                raise TypeError(msg)
        return

    def create_node(self, name):
        """
        Create a collection set node.
        """
        self._set.create_node(name)
        set_node = self._set.get_node()
        _create_collection_attributes(set_node)
        return self

    def add_attributes(self):
        """
        Adds attributes to the collection node, if they do not already
        exist.
        """
        node = self.get_node()
        _create_collection_attributes(node)
        return

    def get_node(self):
        return self._set.get_node()

    def get_node_uid(self):
        return self._set.get_node_uid()

    def set_node(self, name):
        self._kwargs_list = []  # reset argument flag cache.
        return self._set.set_node(name)

    ############################################################################

    def _get_attr_data(self, attr_name):
        """
        Get data from an attribute on the collection node.

        :param attr_name: The name of the attribute to get data form.
        :type attr_name: str

        :return: List of data arbitrary structures.
        :rtype: list of dict
        """
        set_node = self._set.get_node()
        return configmaya.get_node_option_structure(set_node, attr_name)

    def _set_attr_data(self, attr_name, data):
        """
        Set arbitrary data onto a collection node.

        :param attr_name: Attribute name to store data with.
        :type attr_name: str

        :param data: The data to store.
        :type data: list or dict

        ;return: Nothing.
        :rtype: None
        """
        set_node = self._set.get_node()
        configmaya.set_node_option_structure(
            set_node, attr_name, data,
            add_attr=True)
        return

    ############################################################################

    def _load_solver_list(self):
        """
        Get all Solvers from the attribute data on the Collection.

        :return: List of Solver objects.
        :rtype: list of Solver
        """
        solver_list = []
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_LIST
        attr_data = self._get_attr_data(attr)
        if isinstance(attr_data, list) is False:
            return solver_list
        for item in attr_data:
            if isinstance(item, dict) is False:
                continue
            sol = solver.Solver(data=item)
            solver_list.append(sol)
        return solver_list

    def _dump_solver_list(self, solver_list):
        """
        Write solver_list to the attribute data on the Collection.

        :param solver_list: The Solvers to be written.
        :type solver_list: list of Solver

        :return: None
        :rtype: None
        """
        assert isinstance(solver_list, list)
        data_list = []
        for sol in solver_list:
            data = sol.get_data()
            if isinstance(data, dict):
                data_list.append(data)
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_LIST
        self._set_attr_data(attr, data_list)
        self._kwargs_list = []  # reset argument flag cache.
        return

    def _get_solver_list_names(self, solver_list):
        """
        Get the names of solvers in the given list.

        :param solver_list: The Solvers to get names from.
        :type solver_list: list of Solver

        :return: List of solver names
        :rtype: list of str
        """
        ret = []
        for sol in solver_list:
            name = sol.get_name()
            if name is not None:
                ret.append(name)
        return ret

    def get_solver_list(self):
        """
        Get Solver objects attached to the collection.

        :return: Solver objects.
        :rtype: list of solver.Solver
        """
        solver_list = None
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        solver_list = self._solver_list
        return solver_list

    def get_solver_list_length(self):
        return len(self.get_solver_list())

    def add_solver(self, sol):
        assert isinstance(sol, solver.Solver)
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        solver_name_list = self._get_solver_list_names(self._solver_list)
        if sol.get_name() not in solver_name_list:
            self._solver_list.append(sol)
            self._dump_solver_list(self._solver_list)
        return

    def add_solver_list(self, sol_list):
        assert isinstance(sol_list, list)
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        changed = False
        solver_name_list = self._get_solver_list_names(self._solver_list)
        for sol in sol_list:
            if sol.get_name() not in solver_name_list:
                self._solver_list.append(sol)
                changed = True
        if changed is True:
            # Only save, if changes have been made.
            self._dump_solver_list(self._solver_list)
        return

    def remove_solver(self, sol):
        assert isinstance(sol, solver.Solver)
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        solver_name_list = self._get_solver_list_names(self._solver_list)
        if sol.get_name() in solver_name_list:

            # TODO: This is really messy, we could probably clean this up with
            # an override to Solver.__cmp__, right?
            tmp_list = self._solver_list
            for sol2 in tmp_list:
                if sol.get_name() == sol2.get_name():
                    tmp_list.remove(sol2)
            self._solver_list = tmp_list

            self._dump_solver_list(self._solver_list)
        return

    def remove_solver_list(self, sol_list):
        assert isinstance(sol_list, list)
        for sol in sol_list:
            self.remove_solver(sol)
        return

    def set_solver_list(self, sol_list):
        assert isinstance(sol_list, list)
        self.clear_solver_list()
        self.add_solver_list(sol_list)
        return

    def clear_solver_list(self):
        self._solver_list = []
        self._dump_solver_list(self._solver_list)
        return

    ############################################################################

    def get_marker_list(self):
        result = []
        members = self._set.get_all_members(flatten=False, full_path=True)
        for member in members:
            object_type = api_utils.get_object_type(member)
            if object_type == const.OBJECT_TYPE_MARKER:
                mkr = marker.Marker(member)
                result.append(mkr)
        return result

    def get_marker_list_length(self):
        return len(self.get_marker_list())

    def add_marker(self, mkr):
        assert isinstance(mkr, marker.Marker)
        node = mkr.get_node()
        assert isinstance(node, (str, unicode))
        assert len(node) > 0
        if self._set.member_in_set(node) is False:
            self._set.add_member(node)
            self._kwargs_list = []  # reset argument flag cache.
        return

    def add_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.add_members(node_list)
        self._kwargs_list = []  # reset argument flag cache.
        return

    def remove_marker(self, mkr):
        assert isinstance(mkr, marker.Marker)
        node = mkr.get_node()
        if self._set.member_in_set(node):
            self._set.remove_member(node)
            self._kwargs_list = []  # reset argument flag cache.
        return

    def remove_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.remove_members(node_list)
        self._kwargs_list = []  # reset argument flag cache.
        return

    def set_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        before_num = self.get_marker_list_length()

        self.clear_marker_list()
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                self.add_marker(mkr)

        after_num = self.get_marker_list_length()
        if before_num != after_num:
            self._kwargs_list = []  # reset argument flag cache.
        return

    def clear_marker_list(self):
        members = self._set.get_all_members(flatten=False, full_path=True)
        rm_list = []
        for member in members:
            object_type = api_utils.get_object_type(member)
            if object_type == const.OBJECT_TYPE_MARKER:
                rm_list.append(member)
        if len(rm_list) > 0:
            self._set.remove_members(rm_list)
            self._kwargs_list = []  # reset argument flag cache.
        return

    ############################################################################

    def get_attribute_list(self):
        result = []
        members = self._set.get_all_members(flatten=False, full_path=True)
        for member in members:
            object_type = api_utils.get_object_type(member)
            if object_type == const.OBJECT_TYPE_ATTRIBUTE:
                attr = attribute.Attribute(name=member)
                result.append(attr)
        return result

    def get_attribute_list_length(self):
        return len(self.get_attribute_list())

    def add_attribute(self, attr):
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        assert isinstance(name, (str, unicode))
        if not self._set.member_in_set(name):
            self._set.add_member(name)
            self._kwargs_list = []  # reset argument flag cache.
        return

    def add_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.add_members(name_list)
        self._kwargs_list = []  # reset argument flag cache.
        return

    def remove_attribute(self, attr):
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        if self._set.member_in_set(name):
            self._set.remove_member(name)
            self._kwargs_list = []  # reset argument flag cache.
        return

    def remove_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.remove_members(name_list)
        self._kwargs_list = []  # reset argument flag cache.
        return

    def set_attribute_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        before_num = self.get_attribute_list_length()

        self.clear_attribute_list()
        for mkr in mkr_list:
            if isinstance(mkr, attribute.Attribute):
                self.add_attribute(mkr)

        after_num = self.get_attribute_list_length()
        if before_num != after_num:
            self._kwargs_list = []  # reset argument flag cache.
        return

    def clear_attribute_list(self):
        members = self._set.get_all_members(flatten=False, full_path=True)
        rm_list = []
        for member in members:
            object_type = api_utils.get_object_type(member)
            if object_type == const.OBJECT_TYPE_ATTRIBUTE:
                rm_list.append(member)
        if len(rm_list) > 0:
            self._set.remove_members(rm_list)
            self._kwargs_list = []  # reset argument flag cache.
        return

    ############################################################################

    def __compile_solver(self, sol, mkr_list, attr_list, prog_fn=None):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param sol: The solver to compile
        :type sol: Solver

        :param mkr_list: Markers to measure
        :type mkr_list: list of Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of Attribute

        :param prog_fn: Progress Function, with signature f(int)
        :type prog_fn: function

        :return: The keyword arguments for the mmSolver command.
        :rtype: None or dict
        """
        assert isinstance(sol, solver.Solver)
        assert isinstance(mkr_list, list)
        assert isinstance(attr_list, list)
        assert sol.get_frame_list_length() > 0

        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['frame'] = []

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
        if len(markers) == 0:
            LOG.warning('No Markers found!')
            return None
        if len(cameras) == 0:
            LOG.warning('No Cameras found!')
            return None

        # Get Attributes
        use_animated = sol.get_attributes_use_animated()
        use_static = sol.get_attributes_use_static()
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
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return None

        # Get Frames
        frm_list = sol.get_frame_list()
        frame_use_tags = sol.get_frames_use_tags()
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
        if len(frames) == 0:
            LOG.warning('No Frames found!')
            return None

        kwargs['marker'] = markers
        kwargs['camera'] = cameras
        kwargs['attr'] = attrs
        kwargs['frame'] = frames

        solver_type = sol.get_solver_type()
        if solver_type is not None:
            kwargs['solverType'] = solver_type

        iterations = sol.get_max_iterations()
        if iterations is not None:
            kwargs['iterations'] = iterations

        verbose = sol.get_verbose()
        if verbose is not None:
            kwargs['verbose'] = verbose

        delta_factor = sol.get_delta_factor()
        if delta_factor is not None:
            kwargs['delta'] = delta_factor

        auto_diff_type = sol.get_auto_diff_type()
        if auto_diff_type is not None:
            kwargs['autoDiffType'] = auto_diff_type

        tau_factor = sol.get_tau_factor()
        if tau_factor is not None:
            kwargs['tauFactor'] = tau_factor

        gradient_error_factor = sol.get_gradient_error_factor()
        if gradient_error_factor is not None:
            kwargs['epsilon1'] = gradient_error_factor

        parameter_error_factor = sol.get_parameter_error_factor()
        if parameter_error_factor is not None:
            kwargs['epsilon2'] = parameter_error_factor

        error_factor = sol.get_error_factor()
        if error_factor is not None:
            kwargs['epsilon3'] = error_factor

        # msg = 'kwargs:\n' + pprint.pformat(kwargs)
        # LOG.debug(msg)
        return kwargs

    def _compile(self, prog_fn=None, status_fn=None):
        """
        Take the data in this class and compile it into keyword argument flags.

        :return: list of keyword arguments.
        :rtype: list of dict
        """
        # TODO: Cache the compiled result internally to speed up
        # 'is_valid' then '_compile' calls.

        # If the class attributes haven't been changed, re-use the previously
        # generated arguments.
        if len(self._kwargs_list) > 0:
            return self._kwargs_list

        # Re-compile the arguments.
        kwargs_list = []
        col_node = self.get_node()

        # Check Solvers
        sol_list = self.get_solver_list()
        sol_enabled_list = [sol for sol in sol_list
                            if sol.get_enabled() is True]
        if len(sol_enabled_list) == 0:
            msg = 'Collection is not valid, no enabled Solvers given; '
            msg += 'collection={0}'
            msg = msg.format(repr(col_node))
            raise excep.NotValid(msg)

        # Check Markers
        mkr_list = self.get_marker_list()
        if len(mkr_list) == 0:
            msg = 'Collection is not valid, no Markers given; collection={0}'
            msg = msg.format(repr(col_node))
            raise excep.NotValid(msg)

        # Check Attributes
        attr_list = self.get_attribute_list()
        if len(attr_list) == 0:
            msg = 'Collection is not valid, no Attributes given; collection={0}'
            msg = msg.format(repr(col_node))
            raise excep.NotValid(msg)

        # Compile all the solvers
        for i, sol in enumerate(sol_enabled_list):
            if sol.get_frame_list_length() == 0:
                msg = 'Collection is not valid, no frames to solve;'
                msg += ' collection={0}'
                msg = msg.format(repr(col_node))
                raise excep.NotValid(msg)
            kwargs = self.__compile_solver(sol, mkr_list, attr_list)

            # Add a debug file flag to the mmSolver command, only
            # triggered during debug mode.
            if logging.DEBUG >= LOG.getEffectiveLevel():
                debug_file = maya.cmds.file(query=True, sceneName=True)
                debug_file = os.path.basename(debug_file)
                debug_file, ext = os.path.splitext(debug_file)
                debug_file_path = os.path.join(
                    os.path.expandvars('${TEMP}'),
                    debug_file + '_' + str(i).zfill(6) + '.log'
                )
                if len(debug_file) > 0 and debug_file_path is not None:
                    kwargs['debugFile'] = debug_file_path

            if isinstance(kwargs, dict):
                kwargs_list.append(kwargs)
            else:
                msg = 'Collection is not valid, failed to compile solver;'
                msg += ' collection={0}'
                msg = msg.format(repr(col_node))
                raise excep.NotValid(msg)

        # Set arguments
        self._kwargs_list = kwargs_list  # save a copy
        return self._kwargs_list

    def is_valid(self, prog_fn=None, status_fn=None):
        """
        Tests if the current sate of this Collection is valid to solve with.

        :param prog_fn: Progress function callback. If not None this
                        function will be executed to emit progress
                        messages.
        :type prog_fn: callable

        :param status_fn: Status message function callback. If not
                          None this function will be executed each
                          time a status message needs to be printed.
        :type status_fn: callable

        :returns: Is the Collection valid to solve? Yes or no.
        :rtype: bool
        """
        try:
            self._compile(prog_fn=None, status_fn=None)
            ret = True
        except excep.NotValid:
            ret = False
        return ret

    def execute(self,
                verbose=False,
                refresh=False,
                force_update=False,
                prog_fn=None,
                status_fn=None):
        """
        Compile the collection, then pass that data to the 'mmSolver' command.

        The mmSolver command will return a list of strings, which will then be
        passed to the SolveResult class so the user can query the raw data
        using an interface.

        :param verbose: Print extra solver information while a solve is
                        running.
        :type verbose: bool

        :param refresh: Should the solver refresh the viewport while
                        solving?
        :type refresh: bool

        :param force_update: Force updating the DG network, to help the
                             solver in case of a Maya evaluation DG bug.
        :type force_update: bool

        :param prog_fn: The function used report progress messages to
                        the user.
        :type prog_fn: callable or None

        :param status_fn: The function used to report status messages
                          to the user.
        :type status_fn: callable or None

        :return: List of SolveResults from the executed collection.
        :rtype: [SolverResult, ..]
        """
        do_isolate = False

        # Ensure the plug-in is loaded, so we fail before trying to run.
        api_utils.load_plugin()

        # Make sure attributes exists on the collection node.
        # An older scene may not contain all the attributes, which we
        # assume exists.
        self.add_attributes()

        # If 'refresh' is 'on' change all viewports to 'isolate
        # selected' on only the markers and bundles being solved. This
        # will speed up computations, especially per-frame solving as
        # it will not re-compute any invisible nodes (such as rigs or
        # image planes).
        panel_objs = {}
        panel_img_pl_vis = {}
        panels = viewport_utils.get_all_model_panels()
        if refresh is True:
            for panel in panels:
                if do_isolate is True:
                    state = maya.cmds.isolateSelect(
                        panel,
                        query=True,
                        state=True)
                    nodes = None
                    if state is True:
                        nodes = viewport_utils.get_isolated_nodes(panel)
                    panel_objs[panel] = nodes
                panel_img_pl_vis[panel] = viewport_utils.get_image_plane_visibility(panel)

        # Save current frame, to revert to later on.
        cur_frame = maya.cmds.currentTime(query=True)

        try:
            collectionutils.run_progress_func(prog_fn, 0)
            collectionutils.run_status_func(status_fn, 'Solver Initializing...')
            api_state.set_solver_running(True)

            # Check for validity
            solres_list = []
            if self.is_valid() is False:
                LOG.warning('Collection not valid: %r', self.get_node())
                return solres_list
            kwargs_list = self._compile()
            collectionutils.run_progress_func(prog_fn, 1)

            # Isolate all nodes used in all of the kwargs to be run.
            # Note; This assumes the isolated objects are visible, but
            # they may actually be hidden.
            if refresh is True:
                s = time.time()
                if do_isolate is True:
                    isolate_nodes = set()
                    for kwargs in kwargs_list:
                        isolate_nodes |= collectionutils.generate_isolate_nodes(kwargs)
                    if len(isolate_nodes) == 0:
                        raise excep.NotValid
                    isolate_node_list = list(isolate_nodes)
                    for panel in panels:
                        viewport_utils.set_isolated_nodes(panel, isolate_node_list, True)
                for panel in panels:
                    viewport_utils.set_image_plane_visibility(panel, False)
                e = time.time()
                LOG.debug('Perform Pre-Isolate; time=%r', e - s)

            # Set the first current time to the frame before current.
            # This is to help trigger evaluations on the 'current
            # frame', if the current frame is the same as the first
            # frame.
            frame_list = []
            for kwargs in kwargs_list:
                frame_list += kwargs.get('frame', [])
            frame_list = list(set(frame_list))
            frame_list = list(sorted(frame_list))
            is_whole_solve_single_frame = len(frame_list) == 1
            if is_whole_solve_single_frame is False:
                s = time.time()
                maya.cmds.currentTime(
                    cur_frame - 1,
                    edit=True,
                    update=force_update,
                )
                e = time.time()
                LOG.debug('Update previous of current time; time=%r', e - s)

            # Run Solver...
            kwargs_markers = []
            start = 0
            total = len(kwargs_list)
            for i, kwargs in enumerate(kwargs_list):
                frame = kwargs.get('frame')
                collectionutils.run_status_func(status_fn, 'Evaluating frames %r' % frame)
                if frame is None or len(frame) == 0:
                    raise excep.NotValid

                debug_file_path = kwargs.get('debugFile', None)
                if debug_file_path is not None:
                    options_file_path = debug_file_path.replace('.log', '.flags')
                    text = pprint.pformat(kwargs)
                    with open(options_file_path, 'w') as file_:
                        file_.write(text)

                # HACK: Overriding the verbosity, irrespective of what
                # the solver verbosity value is set to.
                if verbose is True:
                    kwargs['verbose'] = True

                # HACK for single frame solves.
                save_node_attrs = []
                is_single_frame = collectionutils.is_single_frame(kwargs)
                if is_single_frame is True:
                    save_node_attrs = collectionutils.disconnect_animcurves(kwargs)

                # Run Solver Maya plug-in command
                solve_data = maya.cmds.mmSolver(**kwargs)

                # Revert special HACK for single frame solves
                if is_single_frame is True:
                    collectionutils.reconnect_animcurves(kwargs, save_node_attrs)

                # Create SolveResult.
                solres = solveresult.SolveResult(solve_data)
                solres_list.append(solres)

                # Update progress
                ratio = float(i) / float(total)
                percent = float(start) + (ratio * (100.0 - start))
                collectionutils.run_progress_func(prog_fn, int(percent))

                # Check if the user wants to stop solving.
                cmd_cancel = solres.get_user_interrupted()
                gui_cancel = api_state.get_user_interrupt()
                if cmd_cancel is True or gui_cancel is True:
                    msg = 'Cancelled by User'
                    api_state.set_user_interrupt(False)
                    collectionutils.run_status_func(status_fn, 'WARNING: ' + msg)
                    LOG.warning(msg)
                    break
                if solres.get_success() is False:
                    msg = 'Solver failed!!!'
                    collectionutils.run_status_func(status_fn, 'ERROR: ' + msg)
                    LOG.error(msg)

                kwargs_markers += kwargs.get('marker', [])

                # Refresh the Viewport.
                if refresh is True:
                    s = time.time()
                    maya.cmds.currentTime(
                        frame[0],
                        edit=True,
                        update=force_update,
                    )
                    maya.cmds.refresh()
                    e = time.time()
                    LOG.debug('Refresh Viewport; time=%r', e - s)

            # Calculate marker deviation, and set it on the marker.
            frame_list_set = [int(x) for x in frame_list]
            frame_list_set = set(frame_list_set)
            for mkr_node, cam_shp_node, bnd_node in kwargs_markers:
                mkr = marker.Marker(node=mkr_node)
                mkr_frames = mkr.get_enabled_frames()
                mkr_frames = [int(x) for x in mkr_frames]
                mkr_frames = set(mkr_frames).intersection(frame_list_set)
                mkr_frames = list(mkr_frames)
                if len(mkr_frames) > 0:
                    deviation_list = mkr.compute_deviation(mkr_frames)
                    mkr.set_deviation(mkr_frames, deviation_list)

        finally:
            if refresh is True:
                s = time.time()
                for panel, objs in panel_objs.items():
                    if objs is None:
                        # No original objects, disable 'isolate
                        # selected' after resetting the objects.
                        if do_isolate is True:
                            viewport_utils.set_isolated_nodes(panel, [], False)
                        img_pl_vis = panel_img_pl_vis.get(panel, True)
                        viewport_utils.set_image_plane_visibility(panel, img_pl_vis)
                    else:
                        if do_isolate is True:
                            viewport_utils.set_isolated_nodes(panel, list(objs), True)
                e = time.time()
                LOG.debug('Finally; reset isolate selected; time=%r', e - s)

            collectionutils.run_progress_func(prog_fn, 100)
            api_state.set_solver_running(False)

            maya.cmds.currentTime(cur_frame, edit=True, update=True)

        # Store output information of the solver.
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_RESULTS
        raw_data_list = []
        for solres in solres_list:
            raw_data = solres.get_data_raw()
            raw_data_list.append(raw_data)
        self._set_attr_data(attr, raw_data_list)

        # Set keyframe data on the collection for the solver
        frame_error_list = solveresult.merge_frame_error_list(solres_list)
        frame_list = []
        err_list = []
        for frame, err in frame_error_list.items():
            frame_list.append(frame)
            err_list.append(err)
        node = self.get_node()
        plug = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_DEVIATION)
        try:
            maya.cmds.setAttr(plug, lock=False)
            anim_utils.create_anim_curve_node(
                frame_list, err_list,
                node_attr=plug,
                anim_type=OpenMayaAnim.MFnAnimCurve.kAnimCurveTU)
        finally:
            maya.cmds.setAttr(plug, lock=True)

        return solres_list
