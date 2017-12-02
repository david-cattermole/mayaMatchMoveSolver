"""
Set Helper, creates, removes and manipulates Maya set nodes.

Any queries use the Maya Python API, but modifications are handled with
maya.cmds.* so that they support undo/redo correctly.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.api.utils as api_utils
import mmSolver.api.solveresult as solveresult
import mmSolver.api.solver as solver
import mmSolver.api.marker as marker
import mmSolver.api.bundle as bundle
import mmSolver.api.attribute as attribute
import mmSolver.api.sethelper as sethelper


class Collection(object):
    def __init__(self, name=None):
        self._set = sethelper.SetHelper()
        self._solver = None

        # Store the keyword arguments for the command, return this if the user
        # asks for the arguments. Invalidate these arguments and force a
        # re-compile if the user sets a new value, otherwise it's still valid.
        self._kwargs_list = [{}]

        if isinstance(name, (str, unicode)):
            self.set_node(name)

    def create(self, name):
        self._set.create_node(name)
        return self._set.get_node()

    def get_node(self):
        return self._set.get_node()

    def set_node(self, name):
        self._kwargs = {}  # reset argument flag cache.
        return self._set.set_node(name)

    ############################################################################

    # TODO: Make solver a list of solvers.
    def get_solver(self):
        return self._solver

    def set_solver(self, value):
        self._solver = value
        # TODO: Get data from solver, set it into the collection set attr data.
        return

    ############################################################################

    def get_marker_list(self):
        result = []

        # # TODO: Get hidden data from set node, set marker attributes
        # # as needed.
        # set_node = self._set.get_node()
        # set_data = self._get_data(set_node)

        members = self._set.get_all_members(flatten=False, full_path=True)
        for member in members:
            object_type = api_utils.detect_object_type(member)
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
            object_type = api_utils.detect_object_type(member)
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
            object_type = api_utils.detect_object_type(member)
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
            object_type = api_utils.detect_object_type(member)
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
