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
Set Helper, creates, removes and manipulates Maya set nodes.

Any queries use the Maya Python API, but modifications are handled with
maya.cmds.* so that they support undo/redo correctly.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()


class SetHelper(object):
    def __init__(self, node=None, name=None):
        """
        Initialize the SetHelper with the given Maya node.

        :param node: Maya node to attach to.
        :type node: str or None

        :param name: This is a backwards compatible kwarg for 'node'.
        :type name: None or str
        """
        if name is not None:
            msg = (
                "mmSolver.api.SetHelper(name=value), "
                "'name' is a deprecated flag, use 'node' "
            )
            warnings.warn(msg, DeprecationWarning)
            node = name
        if node is not None:
            if isinstance(node, pycompat.TEXT_TYPE):
                obj = node_utils.get_as_object(node)
                self._mfn = OpenMaya.MFnSet(obj)
            else:
                msg = 'node argument must be a string.'
                raise TypeError(msg)
        else:
            self._mfn = OpenMaya.MFnSet()
        return

    def get_node(self):
        node = None
        try:
            obj = self._mfn.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn.name()
            except RuntimeError:
                pass
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def get_node_uid(self):
        node = self.get_node()
        if node is None:
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    def set_node(self, name):
        obj = node_utils.get_as_object(name)
        try:
            self._mfn = OpenMaya.MFnSet(obj)
        except RuntimeError:
            raise
        return

    def create_node(self, name):
        node = maya.cmds.sets(name=name, empty=True)
        self.set_node(node)
        return self

    def delete_node(self):
        node = self._mfn.name()
        maya.cmds.delete(node)
        return self

    def get_annotation(self):
        try:
            ret = self._mfn.annotation()
        except RuntimeError:
            ret = None
        return ret

    def set_annotation(self, value):
        assert isinstance(value, pycompat.TEXT_TYPE)
        set_node = self.get_node()
        maya.cmds.sets(set_node, edit=True, text=value)
        return

    def add_members(self, name_list):
        assert isinstance(name_list, list)
        set_node = self.get_node()
        maya.cmds.sets(*name_list, edit=True, include=set_node, noWarnings=True)
        return

    def remove_members(self, name_list):
        assert isinstance(name_list, list)
        set_node = self.get_node()
        maya.cmds.sets(name_list, edit=True, remove=set_node)
        return

    def add_member(self, name):
        assert isinstance(name, pycompat.TEXT_TYPE)
        set_node = self.get_node()
        maya.cmds.sets(name, edit=True, include=set_node, noWarnings=True)
        return

    def remove_member(self, name):
        set_node = self.get_node()
        maya.cmds.sets(name, edit=True, remove=set_node)
        return

    def get_all_members(self, flatten=False, full_path=True):
        assert isinstance(flatten, bool)
        assert isinstance(full_path, bool)

        sel_list = OpenMaya.MSelectionList()
        try:
            self._mfn.getMembers(sel_list, flatten)
        except RuntimeError:
            return []

        ret = []
        sel_list.getSelectionStrings(ret)
        if full_path is True:
            ret = maya.cmds.ls(ret, long=True) or []

        return ret

    def clear_all_members(self):
        set_node = self.get_node()
        maya.cmds.sets(edit=True, clear=set_node)
        return

    def member_in_set(self, name):
        # NOTE: For attributes, you must use a MPlug, as testing with
        # an MObject only tests the dependency node
        if '.' in name:
            plug = node_utils.get_as_plug(name)
            ret = self._mfn.isMember(plug)
        else:
            obj = node_utils.get_as_object(name)
            ret = self._mfn.isMember(obj)
        return ret

    def length(self):
        return len(self.get_all_members())

    def is_empty(self):
        return len(self.get_all_members()) == 0
