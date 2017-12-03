"""
Set Helper, creates, removes and manipulates Maya set nodes.

Any queries use the Maya Python API, but modifications are handled with
maya.cmds.* so that they support undo/redo correctly.
"""

import json

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver._api.utils as api_utils
import mmSolver._api.solveresult as solveresult
import mmSolver._api.solver as solver
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute
import mmSolver._api.sethelper as sethelper


class Collection(object):
    def __init__(self, name=None):
        self._set = sethelper.SetHelper()
        self._solver_list = None
        # self._solver_list_data = None

        # Store the keyword arguments for the command, return this if the user
        # asks for the arguments. Invalidate these arguments and force a
        # re-compile if the user sets a new value, otherwise it's still valid.
        self._kwargs_list = [{}]

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
        self._kwargs_list = [{}]  # reset argument flag cache.
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
        attr_data = json.dumps(data)
        maya.cmds.setAttr(node_attr, lock=False)
        maya.cmds.setAttr(node_attr, attr_data, type='string')
        maya.cmds.setAttr(node_attr, lock=True)
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
        if not self._set.member_in_set(node):
            self._set.add_member(node)
        return

    def add_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.add_members(node_list)
        return

    def remove_marker(self, mkr):
        assert isinstance(mkr, marker.Marker)
        node = mkr.get_node()
        if self._set.member_in_set(node):
            self._set.remove_member(node)
        return

    def remove_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.remove_members(node_list)
        return

    def set_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        self.clear_marker_list()
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                self.add_marker(mkr)
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
        return

    ############################################################################

    def get_attribute_list(self):
        result = []

        # # TODO: Get hidden data from set node, set attribute attributes
        # # as needed.
        # set_node = self._set.get_node()
        # set_data = self._get_data(set_node)

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
        return

    def add_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.add_members(name_list)
        return

    def remove_attribute(self, attr):
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        if self._set.member_in_set(name):
            self._set.remove_member(name)
        return

    def remove_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.remove_members(name_list)
        return

    def set_attribute_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        self.clear_attribute_list()
        for mkr in mkr_list:
            if isinstance(mkr, attribute.Attribute):
                self.add_attribute(mkr)
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
        return

    ############################################################################

    def _compile(self):
        # TODO: Take all the data in this class and compile them into keyword
        # argument flags for the mmSolver command.

        # If the class attributes haven't been changed, re-use the previously generated arguments.
        if len(self._kwargs) > 0:
            return self._kwargs.copy()

        # re-compile the arguments.
        kwargs = {}
        self._kwargs = kwargs
        return self._kwargs.copy()

    def is_valid(self):
        # TODO: Work out how we will get the validity from self._compile().
        ret = self._compile()

    def execute(self):
        # TODO: This function will compile all the data in the collection, then
        # pass that data to the mmSolver command. The mmSolver command will
        # return a list of strings, which will then be passed to the SolveResult
        # class so the user can query the raw data using an interface.

        kwargs = self._compile()
        solve_data = maya.cmds.mmSolver(**kwargs)
        return solveresult.SolveResult(solve_data)

    ############################################################################

    def _get_data(self, node):
        pass

    def _set_data(self, node, value):
        # TODO: This function will allow setting data on arbitrary nodes, using
        # a locked string attribute.

        # import time
        #
        # # what is the maximum length annotation can support?
        # st = time.time()
        # print 'setAttr:'
        # node = x.get_node()
        # maya.cmds.addAttr(node, longName='my_string_data', dataType='string')
        # node_attr = node + '.my_string_data'
        # for i in range(8):
        #     n = pow(10, i)
        #     print 'i:', i, n
        #     s = 'c' * n
        #     maya.cmds.setAttr(node_attr, s, type='string')
        #     v = maya.cmds.getAttr(node_attr)
        #     self.assertEqual(s, v)
        #     del v
        #     del s
        # print 'time:', time.time() - st
        pass
