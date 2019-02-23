"""
Set Helper, creates, removes and manipulates Maya set nodes.

Any queries use the Maya Python API, but modifications are handled with
maya.cmds.* so that they support undo/redo correctly.
"""

# import pprint
import uuid

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.solveresult as solveresult
import mmSolver._api.solver as solver
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute
import mmSolver._api.sethelper as sethelper


LOG = mmSolver.logger.get_logger()


class Collection(object):
    def __init__(self, name=None):
        self._set = sethelper.SetHelper()
        self._solver_list = None

        # Store the keyword arguments for the command, return this if the user
        # asks for the arguments. Invalidate these arguments and force a
        # re-compile if the user sets a new value, otherwise it's still valid.
        self._kwargs_list = []

        if name is not None:
            if isinstance(name, (str, unicode)):
                self.set_node(name)
            else:
                msg = 'name argument must be a string.'
                raise TypeError(msg)
        return

    def create_node(self, name):
        """
        Create a collection set node.
        """
        self._set.create_node(name)
        set_node = self._set.get_node()

        # Add 'solver_list' attribute.
        attr_name = 'solver_list'
        maya.cmds.addAttr(
            set_node,
            longName=attr_name,
            dataType='string')
        maya.cmds.setAttr(
            set_node + '.' + attr_name,
            lock=True)

        return self

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
        return api_utils.get_data_on_node_attr(set_node, attr_name)

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
        api_utils.set_data_on_node_attr(set_node, attr_name, data)
        self._kwargs_list = []  # reset argument flag cache.
        return

    ############################################################################

    def _load_solver_list(self):
        """
        Get all Solvers from the attribute data on the Collection.

        :return: List of Solver objects.
        :rtype: list of Solver
        """
        solver_list = []
        attr_data = self._get_attr_data('solver_list')
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
        self._set_attr_data('solver_list', data_list)
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
        :type sol: solver.Solver

        :param mkr_list: Markers to measure
        :type mkr_list: list of marker.Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of attribute.Attribute

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
                msg = 'Cannot find bundle from marker; mkr=%r'
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
            return None
        if len(cameras) == 0:
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

            animated = attr.is_animated()
            static = attr.is_static()
            use = False
            if use_animated and animated is True:
                use = True
            if use_static and static is True:
                use = True
            if use is True:
                attrs.append((name, str(min_value), str(max_value)))
        if len(attrs) == 0:
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
        sol_enabled_list = filter(lambda x: x.get_enabled() is True, sol_list)
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
        for sol in sol_enabled_list:
            if sol.get_frame_list_length() == 0:
                raise excep.NotValid(msg)
            kwargs = self.__compile_solver(sol, mkr_list, attr_list)
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
        try:
            self._compile(prog_fn=None, status_fn=None)
            ret = True
        except excep.NotValid:
            ret = False
        return ret

    @staticmethod
    def __set_progress(prog_fn, value):
        if prog_fn is not None:
            prog_fn(int(value))
        return

    @staticmethod
    def __set_status(status_fn, text):
        if status_fn is not None:
            status_fn(str(text))
        return

    @staticmethod
    def __is_single_frame(kwargs):
        """
        Logic to determine if the solver arguments will solve a single
        frame or not.
        """
        has_one_frame = len(kwargs.get('frame')) is 1
        is_interactive = maya.cmds.about(query=True, batch=True) is False
        return has_one_frame and is_interactive

    @staticmethod
    def __disconnect_animcurves(kwargs):
        # HACK: Disconnect animCurves from animated attributes,
        # then re-connect afterward. This is to solve a Maya bug,
        # which will not solve values on a single frame.
        f = kwargs.get('frame')[0]
        maya.cmds.currentTime(f, edit=True, update=False)

        save_node_attrs = []
        attrs = kwargs.get('attr') or []
        for attr_name, min_val, max_val in attrs:
            attr_obj = attribute.Attribute(attr_name)
            if attr_obj.is_animated() is False:
                continue

            in_plug_name = None
            out_plug_name = attr_name
            plug = api_utils.get_as_plug(attr_name)
            isDest = plug.isDestination()
            if isDest:
                connPlugs = OpenMaya.MPlugArray()
                asDest = True  # get the source plugs on the other end of 'plug'.
                asSrc = False
                plug.connectedTo(connPlugs, asDest, asSrc)
                for i, conn in enumerate(connPlugs):
                    connPlug = connPlugs[i]
                    connObj = connPlug.node()
                    if connObj.hasFn(OpenMaya.MFn.kAnimCurve):
                        # dependsNode = OpenMaya.MFnDependencyNode(connObj)
                        # animCurveName = dependsNode.name()
                        in_plug_name = connPlug.name()
                        break
            if in_plug_name is not None:
                save_node_attrs.append((in_plug_name, out_plug_name))
                if maya.cmds.isConnected(in_plug_name, out_plug_name) is True:
                    maya.cmds.disconnectAttr(in_plug_name, out_plug_name)
                else:
                    LOG.error('Nodes are not connected. This is WRONG.')
        return save_node_attrs

    @staticmethod
    def __reconnect_animcurves(kwargs, save_node_attrs):
        f = kwargs.get('frame')[0]
        maya.cmds.currentTime(f, edit=True, update=False)

        # Re-connect animCurves, and set the solved values.
        for in_plug_name, out_plug_name in save_node_attrs:
            if maya.cmds.isConnected(in_plug_name, out_plug_name) is False:
                v = maya.cmds.getAttr(out_plug_name)
                maya.cmds.connectAttr(in_plug_name, out_plug_name)
                attr_obj = attribute.Attribute(name=out_plug_name)
                tangent_type = 'linear'
                maya.cmds.setKeyframe(
                    attr_obj.get_node(),
                    attribute=attr_obj.get_attr(),
                    time=f, value=v,
                    inTangentType=tangent_type,
                    outTangentType=tangent_type,
                )
            else:
                LOG.error('Nodes are connected. This is WRONG.')
        return

    def execute(self, verbose=False, refresh=False, prog_fn=None, status_fn=None):
        """
        Compile the collection, then pass that data to the 'mmSolver' command.

        The mmSolver command will return a list of strings, which will then be
        passed to the SolveResult class so the user can query the raw data
        using an interface.

        :return: List of SolveResults from the executed collection.
        :rtype: [SolverResult, ..]
        """
        # Ensure the plug-in is loaded, so we fail before trying to run.
        api_utils.load_plugin()

        # Save current frame, to revert to later on.
        cur_frame = maya.cmds.currentTime(query=True)

        undo_state = maya.cmds.undoInfo(query=True, state=True)
        undo_id = 'mmSolver.api.collection.execute: ' + str(uuid.uuid4())
        try:
            if undo_state is True:
                maya.cmds.undoInfo(openChunk=True, chunkName=undo_id)
            self.__set_progress(prog_fn, 0)
            self.__set_status(status_fn, 'Solver Initializing...')
            api_utils.set_solver_running(True)

            # Check for validity
            solres_list = []
            if self.is_valid() is False:
                LOG.warning('collection not valid: %r', self.get_node())
                return solres_list
            kwargs_list = self._compile()
            self.__set_progress(prog_fn, 1)

            # Run Solver...
            start = 0
            total = len(kwargs_list)
            for i, kwargs in enumerate(kwargs_list):
                frame = kwargs.get('frame')
                self.__set_status(status_fn, 'Evaluating frames %r' % frame)
                if frame is None or len(frame) == 0:
                    raise excep.NotValid

                # HACK: Overriding the verbosity, irrespective of what
                # the solver verbosity value is set to.
                if verbose is True:
                    kwargs['verbose'] = True

                # HACK for single frame solves.
                save_node_attrs = []
                is_single_frame = self.__is_single_frame(kwargs)
                if is_single_frame is True:
                    save_node_attrs = self.__disconnect_animcurves(kwargs)

                # Run Solver Maya plug-in command
                solve_data = maya.cmds.mmSolver(**kwargs)

                # Revert special HACK for single frame solves
                if is_single_frame is True:
                    self.__reconnect_animcurves(kwargs, save_node_attrs)

                # Create SolveResult.
                solres = solveresult.SolveResult(solve_data)
                solres_list.append(solres)

                # Update progress
                ratio = float(i) / float(total)
                percent = float(start) + (ratio * (100.0 - start))
                self.__set_progress(prog_fn, int(percent))

                if solres.get_success() is False:
                    msg = 'Solver failed!!!'
                    self.__set_status(status_fn, 'ERROR:' + msg)
                    LOG.error(msg)

                # Refresh the Viewport.
                if refresh is True:
                    self.__set_status(status_fn, 'Refresh Viewport...')
                    maya.cmds.currentTime(
                        frame[0],
                        edit=True,
                        update=True
                    )
                    maya.cmds.refresh()
        except:
            solres_list = []
            # TODO: If we have failed, should we attempt to clean up the mess
            # and undo the entire undo chunk?
            raise
        finally:
            self.__set_progress(prog_fn, 100)
            api_utils.set_solver_running(False)

            if undo_state is True:
                maya.cmds.undoInfo(closeChunk=True, chunkName=undo_id)
            maya.cmds.currentTime(cur_frame, edit=True, update=True)
        return solres_list
