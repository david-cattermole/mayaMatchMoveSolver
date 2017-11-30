"""
Set Helper, creates, removes and manipulates Maya set nodes.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.api.utils as apiUtils


class SetHelper(object):
    def __init__(self, name=None):
        if isinstance(name, (str, unicode)):
            obj = apiUtils.get_as_object(name)
            self._mfn = OpenMaya.MFnSet(obj)
        else:
            self._mfn = OpenMaya.MFnSet()
        return

    def get_node(self):
        try:
            node = self._mfn.name()
        except RuntimeError:
            node = None
        return node

    def set_node(self, name):
        obj = apiUtils.get_as_object(name)
        try:
            self._mfn = OpenMaya.MFnSet(obj)
        except RuntimeError:
            raise
        return

    def create_node(self, name):
        node = maya.cmds.sets(name=name)
        self.set_node(node)
        return self.get_node()

    def delete_node(self):
        node = self._mfn.name()
        maya.cmds.delete(node)
        return

    def get_annotation(self):
        try:
            ret = self._mfn.annotation()
        except RuntimeError:
            ret = None
        return ret

    def set_annotation(self, value):
        try:
            self._mfn.setAnnotation(value)
        except RuntimeError:
            raise
        return

    def get_all_nodes(self, flatten=False, fullPath=True):
        assert isinstance(flatten, bool)
        assert isinstance(fullPath, bool)

        sel_list = OpenMaya.MSelectionList()
        try:
            self._mfn.getMembers(sel_list, flatten)
        except RuntimeError:
            return []

        ret = []
        sel_list.getSelectionStrings(ret)
        if fullPath is True:
            ret = maya.cmds.ls(ret, long=True) or []

        return ret

    def clear_all_nodes(self):
        try:
            self._mfn.clear()
        except RuntimeError:
            raise
        return

    def add_nodes(self, name_list):
        sel_list = OpenMaya.MSelectionList()
        for name in name_list:
            sel_list.add(name)
        if sel_list.length():
            self._mfn.addMembers(sel_list)
        return

    def remove_nodes(self, nameList):
        sel_list = OpenMaya.MSelectionList()
        for name in nameList:
            sel_list.add(name)
        if sel_list.length():
            self._mfn.removeMembers(sel_list)
        return

    def add_node(self, name):
        if '.' in name:
            # name is a plug
            try:
                plug = apiUtils.get_as_plug(name)
                self._mfn.addMember(plug)
            except RuntimeError:
                raise
        else:
            # name is a node
            try:
                obj = apiUtils.get_as_object(name)
                self._mfn.addMember(obj)
            except RuntimeError:
                raise
        return

    def remove_node(self, name):
        obj = apiUtils.get_as_object(name)
        return self._mfn.removeMember(obj)

    def node_in_set(self, name):
        obj = apiUtils.get_as_object(name)
        return self._mfn.isMember(obj)

