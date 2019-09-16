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

import warnings

import maya.cmds
import maya.mel
import maya.OpenMayaAnim as OpenMayaAnim

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.compile as api_compile
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.solveresult as solveresult
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstep as solverstep
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute
import mmSolver._api.sethelper as sethelper
import mmSolver._api.execute as execute


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
        self._actions_list = []

        if node is not None:
            if isinstance(node, (str, unicode)):
                self.set_node(node)
            else:
                msg = 'node argument must be a string.'
                raise TypeError(msg)

            # Make sure attributes exists on the collection node.
            # An older scene may not contain all the attributes, which we
            # assume exists.
            self.add_attributes()
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
        if node is not None:
            _create_collection_attributes(node)
        return

    def get_node(self):
        return self._set.get_node()

    def get_node_uid(self):
        return self._set.get_node_uid()

    def set_node(self, name):
        self._actions_list = []  # reset argument flag cache.
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

    def get_last_solve_timestamp(self):
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVE_TIMESTAMP
        value = self._get_attr_data(attr)
        if len(value) > 0:
            value = value[0]
        else:
            value = None
        return value

    def _set_last_solve_timestamp(self, value):
        assert isinstance(value, float)
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVE_TIMESTAMP
        value = [value]
        self._set_attr_data(attr, value)
        return

    def get_last_solve_duration(self):
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVE_DURATION
        value = self._get_attr_data(attr)
        if len(value) > 0:
            value = value[0]
        else:
            value = None
        return value

    def _set_last_solve_duration(self, value):
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVE_DURATION
        value = [value]
        self._set_attr_data(attr, value)
        return

    def get_last_solve_results(self):
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_RESULTS
        raw_data_list = self._get_attr_data(attr)
        solres_list = []
        for raw_data in raw_data_list:
            solres = solveresult.SolveResult(raw_data)
            solres_list.append(solres)
        return solres_list

    def _set_last_solve_results(self, solres_list):
        attr = const.COLLECTION_ATTR_LONG_NAME_SOLVER_RESULTS
        raw_data_list = []
        for solres in solres_list:
            raw_data = solres.get_data_raw()
            raw_data_list.append(raw_data)
        self._set_attr_data(attr, raw_data_list)
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
            sol = solverstep.SolverStep(data=item)
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
        self._actions_list = []  # reset argument flag cache.
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
        :rtype: list of solverop.Solver
        """
        solver_list = None
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        solver_list = self._solver_list
        return solver_list

    def get_solver_list_length(self):
        return len(self.get_solver_list())

    def add_solver(self, sol):
        assert isinstance(sol, solverbase.SolverBase)
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
        assert isinstance(sol, solverbase.SolverBase)
        if self._solver_list is None:
            self._solver_list = self._load_solver_list()
        solver_name_list = self._get_solver_list_names(self._solver_list)
        if sol.get_name() in solver_name_list:

            # TODO: This is really messy, we could probably clean this up with
            # an override to SolverStep.__cmp__, right?
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
            self._actions_list = []  # reset argument flag cache.
        return

    def add_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.add_members(node_list)
        self._actions_list = []  # reset argument flag cache.
        return

    def remove_marker(self, mkr):
        assert isinstance(mkr, marker.Marker)
        node = mkr.get_node()
        if self._set.member_in_set(node):
            self._set.remove_member(node)
            self._actions_list = []  # reset argument flag cache.
        return

    def remove_marker_list(self, mkr_list):
        assert isinstance(mkr_list, list)
        node_list = []
        for mkr in mkr_list:
            if isinstance(mkr, marker.Marker):
                node_list.append(mkr.get_node())
        self._set.remove_members(node_list)
        self._actions_list = []  # reset argument flag cache.
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
            self._actions_list = []  # reset argument flag cache.
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
            self._actions_list = []  # reset argument flag cache.
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
            self._actions_list = []  # reset argument flag cache.
        return

    def add_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.add_members(name_list)
        self._actions_list = []  # reset argument flag cache.
        return

    def remove_attribute(self, attr):
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        if self._set.member_in_set(name):
            self._set.remove_member(name)
            self._actions_list = []  # reset argument flag cache.
        return

    def remove_attribute_list(self, attr_list):
        assert isinstance(attr_list, list)
        name_list = []
        for attr in attr_list:
            if isinstance(attr, attribute.Attribute):
                name_list.append(attr.get_name())
        self._set.remove_members(name_list)
        self._actions_list = []  # reset argument flag cache.
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
            self._actions_list = []  # reset argument flag cache.
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
            self._actions_list = []  # reset argument flag cache.
        return

    ############################################################################

    # TODO: Add 'logging level' flag to Collection.

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
            col_node = self.get_node()
            sol_list = self.get_solver_list()
            mkr_list = self.get_marker_list()
            attr_list = self.get_attribute_list()
            api_compile.collection_compile(
                col_node,
                sol_list, mkr_list, attr_list,
                prog_fn=None, status_fn=None)
            ret = True
        except excep.NotValid as e:
            ret = False
            LOG.warn(e)
        return ret

    def execute(self,
                options=None,
                log_level=None,
                prog_fn=None,
                status_fn=None,
                info_fn=None):
        msg = 'Collection.execute is deprecated, use "execute" function.'
        warnings.warn(msg, DeprecationWarning)
        result = execute.execute(
            self,
            options=options,
            log_level=log_level,
            prog_fn=prog_fn,
            status_fn=status_fn,
            info_fn=info_fn)
        return result


def update_deviation_on_collection(col, solres_list):
    """
    Set keyframe data on the collection for the solver.
    """
    node = col.get_node()
    frame_error_list = solveresult.merge_frame_error_list(solres_list)
    frame_list = []
    err_list = []
    for frame, err in frame_error_list.items():
        frame_list.append(frame)
        err_list.append(err)
    if len(frame_list) == len(err_list) == 0:
        frame_list.append(1)
        err_list.append(999.9)
    plug = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_DEVIATION)
    try:
        maya.cmds.setAttr(plug, lock=False)
        anim_utils.create_anim_curve_node_apione(
            frame_list, err_list,
            node_attr=plug,
            anim_type=OpenMayaAnim.MFnAnimCurve.kAnimCurveTU)
    finally:
        maya.cmds.setAttr(plug, lock=True)
    return
