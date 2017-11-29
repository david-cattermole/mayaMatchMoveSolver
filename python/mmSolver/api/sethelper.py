"""
Set Helper, creates, removes and manipulates Maya set nodes.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.api.utils as utils


class SetHelper(object):
    def __init__(self, name=None):
        if isinstance(name, str):
            obj = utils.getNodeAsMObject(name)
            self._mfn = OpenMaya.MFnSet(obj)
        else:
            self._mfn = OpenMaya.MFnSet()

    def getNode(self):
        return self._mfn.name()

    def setNode(self, name):
        obj = utils.getNodeAsMObject(name)
        self._mfn = OpenMaya.MFnSet(obj)
        return

    def createNode(self, name):
        node = maya.cmds.sets(name=name)
        self.setNode(node)
        return self.getNode()

    def deleteNode(self):
        node = self._mfn.name()
        maya.cmds.delete(node)
        return

    def getAnnotation(self):
        return self._mfn.annotation()

    def setAnnotation(self, value):
        return self._mfn.setAnnotation(value)

    def getAllNodes(self, flatten=False):
        selList = OpenMaya.MSelectionList()
        self._mfn.getMembers(selList, flatten)

    def clearAllNodes(self):
        self._mfn.clear()

    def addNodes(self, nameList):
        selList = OpenMaya.MSelectionList()
        for name in nameList:
            selList.add(name)
        if selList.length():
            self._mfn.addMembers(selList)
        return

    def removeNodes(self, nameList):
        selList = OpenMaya.MSelectionList()
        for name in nameList:
            selList.add(name)
        if selList.length():
            self._mfn.removeMembers(selList)
        return

    def addNode(self, name):
        obj = utils.getNodeAsMObject(name)
        return self._mfn.addMember(obj)

    def removeNode(self, name):
        obj = utils.getNodeAsMObject(name)
        return self._mfn.removeMember(obj)

    def nodeInSet(self, name):
        obj = utils.getNodeAsMObject(name)
        return self._mfn.isMember(obj)

