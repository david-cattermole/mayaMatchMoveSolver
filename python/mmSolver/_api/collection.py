"""
Set Helper, creates, removes and manipulates Maya set nodes.

Any queries use the Maya Python API, but modifications are handled with
maya.cmds.* so that they support undo/redo correctly.
"""

import json

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.solveresult as solveresult
import mmSolver._api.solver as solver
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute
import mmSolver._api.sethelper as sethelper


class Collection(object):
    def __init__(self, name=None):
        self._set = sethelper.SetHelper()
        self._solver_list = None

        # Store the keyword arguments for the command, return this if the user
        # asks for the arguments. Invalidate these arguments and force a
        # re-compile if the user sets a new value, otherwise it's still valid.
        self._kwargs_list = []

        if isinstance(name, (str, unicode)):
            self.set_node(name)

    def create(self, name):
        self._set.create_node(name)
        set_node = self._set.get_node()

        # Add 'solver_list' attribute.
        attr_name = 'solver_list'
        maya.cmds.addAttr(set_node, longName=attr_name, dt='string')
        maya.cmds.setAttr(set_node + '.' + attr_name, lock=True)

        return set_node

    def get_node(self):
        return self._set.get_node()

    def set_node(self, name):
        self._kwargs_list = []  # reset argument flag cache.
        return self._set.set_node(name)

    ############################################################################

    def _get_attr_data(self, attr_name):
        ret = None
        set_node = self._set.get_node()
        attrs = maya.cmds.listAttr(set_node)
        if attr_name in attrs:
            node_attr = set_node + '.' + attr_name
            attr_data = maya.cmds.getAttr(node_attr)
            data = json.loads(attr_data)
            if isinstance(data, list):
                ret = data
        return ret

    def _set_attr_data(self, attr_name, data):
        assert isinstance(attr_name, (str, unicode))
        assert isinstance(data, (list, dict))
        set_node = self._set.get_node()
        node_attr = set_node + '.' + attr_name

        new_attr_data = json.dumps(data)
        old_attr_data = maya.cmds.getAttr(node_attr)
        if old_attr_data == new_attr_data:
            return  # no change is needed.

        maya.cmds.setAttr(node_attr, lock=False)
        maya.cmds.setAttr(node_attr, new_attr_data, type='string')
        maya.cmds.setAttr(node_attr, lock=True)
        self._kwargs_list = []  # reset argument flag cache.
        return

    ############################################################################

    def _load_solver_list(self):
        solver_list = None
        attr_data = self._get_attr_data('solver_list')
        if isinstance(attr_data, list):
            solver_list = []
            for item in attr_data:
                if isinstance(attr_data, dict):
                    sol = solver.Solver(data=item)
                    solver_list.append(sol)
        return solver_list

    def _dump_solver_list(self, solver_list):
        assert isinstance(solver_list, list)
        data_list = []
        for sol in solver_list:
            data = sol.get_data()
            if isinstance(data, dict):
                data_list.append(data)
        self._set_attr_data('solver_list', data_list)
        return

    def _get_solver_list_names(self, solver_list):
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
        else:
            solver_list = self._solver_list
        return solver_list

    def get_solver_list_length(self):
        return len(self.get_solver_list())

    def add_solver(self, sol):
        assert isinstance(sol, solver.Solver)
        if self._solver_list is None:
            self._solver_list = []
        solver_name_list = self._get_solver_list_names(self._solver_list)
        if sol.get_name() not in solver_name_list:
            self._solver_list.append(sol)
            self._dump_solver_list(self._solver_list)
        return

    def add_solver_list(self, sol_list):
        assert isinstance(sol_list, list)
        if self._solver_list is None:
            self._solver_list = []
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
            self._solver_list = []
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
            if object_type == 'marker':
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
            if object_type == 'marker':
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
            if object_type == 'attribute':
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
            if object_type == 'attribute':
                rm_list.append(member)
        if len(rm_list) > 0:
            self._set.remove_members(rm_list)
            self._kwargs_list = []  # reset argument flag cache.
        return

    ############################################################################

    def __compile_solver(self, sol, mkr_list, attr_list):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param sol: The solver to compile
        :type sol: solver.Solver

        :param mkr_list: Markers to measure
        :type mkr_list: list of marker.Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of attribute.Attribute

        :return:
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
            bnd = mkr.get_bundle()
            cam = mkr.get_camera()
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()
            cam_tfm_node = cam.get_transform_node()
            cam_shp_node = cam.get_shape_node()
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
            node_name = attr.get_node_name()
            attr_name = attr.get_attr_name()

            # If the user does not specify a min/max value then we get it
            # from Maya directly, if Maya doesn't have one, we leave
            # min/max_value as None and pass it to the mmSolver command
            # indicating there is no bound.
            min_value = attr.get_min_value()
            max_value = attr.get_max_value()
            if min_value is None:
                if maya.cmds.attributeQuery(attr_name,
                                            node=node_name,
                                            minExists=True):
                    min_value = maya.cmds.attributeQuery(attr_name,
                                                         node=node_name,
                                                         minimum=True)
            if max_value is None:
                if maya.cmds.attributeQuery(attr_name,
                                            node=node_name,
                                            maxExists=True):
                    max_value = maya.cmds.attributeQuery(attr_name,
                                                         node=node_name,
                                                         maximum=True)

            animated = attr.is_animated()
            static = attr.is_static()
            use = False
            if use_animated and animated is True:
                use = True
            if use_static and static is True:
                use = True
            if use is True:
                # TODO: Add the min/max values to the
                # attrs.append((name, min_value, max_value))
                attrs.append((name))
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

        kwargs['solverType'] = sol.get_solver_type()
        kwargs['iterations'] = sol.get_max_iterations()
        kwargs['verbose'] = sol.get_verbose()
        delta = sol.get_delta()
        if delta is not None:
            kwargs['delta'] = delta

        tau_factor = sol.get_tau_factor()
        if tau_factor is not None:
            kwargs['tauFactor'] = tau_factor
        # TODO: epsilon1 argument
        # TODO: epsilon2 argument
        # TODO: epsilon3 argument

        print 'kwargs:', repr(kwargs)
        return kwargs

    def _compile(self):
        """
        Take the data in this class and compile it into keyword argument flags.

        :return: list of keyword arguments.
        :rtype: list of dict
        """

        # If the class attributes haven't been changed, re-use the previously
        # generated arguments.
        if len(self._kwargs_list) > 0:
            return self._kwargs_list

        # Re-compile the arguments.
        kwargs_list = []
        col_node = self.get_node()

        # Check Solvers
        sol_list = self.get_solver_list()
        if len(sol_list) == 0:
            msg = 'Collection is not valid, no Solvers given; collection={0}'
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
        for sol in sol_list:
            if sol.get_frame_list_length() == 0:
                assert False
            kwargs = self.__compile_solver(sol, mkr_list, attr_list)
            if isinstance(kwargs, dict):
                kwargs_list.append(kwargs)
            else:
                assert False

        # Set arguments
        self._kwargs_list = kwargs_list  # save a copy
        return self._kwargs_list

    def is_valid(self):
        try:
            self._compile()
            ret = True
        except excep.NotValid:
            ret = False
        return ret

    def execute(self):
        """
        Compile the collection, then pass that data to the 'mmSolver' command.

        The mmSolver command will return a list of strings, which will then be
        passed to the SolveResult class so the user can query the raw data using an interface.

        :return: List of SolveResults
        :rtype: list of solveresult.SolverResult
        """

        # Check for validity
        solres_list = []
        if self.is_valid() is False:
            maya.cmds.warning('collection not valid', self.get_node())
            return solres_list

        kwargs_list = self._compile()
        for kwargs in kwargs_list:
            solve_data = maya.cmds.mmSolver(**kwargs)
            solres = solveresult.SolveResult(solve_data)
            solres_list.append(solres)
        return solres_list
