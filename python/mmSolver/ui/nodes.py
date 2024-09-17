# Copyright (C) 2019 David Cattermole.
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
Defines a basic node class able to be used for tree data models.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.utils.python_compat as pycompat


def get_nodes_recursively(top_node):
    nodes = []
    children = top_node.children()
    if len(children) > 1:
        for child in children:
            nodes += get_nodes_recursively(child)
    else:
        nodes.append(top_node)
    return nodes


class Node(object):
    def __init__(
        self,
        name,
        data=None,
        toolTip=None,
        statusTip=None,
        parent=None,
        icon=None,
        enabled=True,
        editable=False,
        selectable=True,
        checkable=False,
        neverHasChildren=False,
    ):
        if icon is None:
            icon = ':/mmSolver_node.png'
        self._children = []
        self._parent = parent

        self._name = name
        self._toolTip = toolTip
        self._statusTip = statusTip
        self._color = None
        if isinstance(data, dict):
            data = data.copy()
        self._data = data

        self._enabled = enabled
        self._checkable = checkable
        self._editable = editable
        self._selectable = selectable
        self._neverHasChildren = neverHasChildren

        self._iconPath = icon
        self._icon = None
        self.typeInfo = 'node'
        if parent is not None:
            parent.addChild(self)

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} name={name} data={data}'.format(
            hash=hash(self), name=self.name(), data=self.data()
        )
        result += ')>'
        return result

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def toolTip(self):
        return self._toolTip

    def setToolTip(self, toolTip):
        self._toolTip = toolTip

    def statusTip(self):
        return self._statusTip

    def setStatusTip(self, statusTip):
        self._statusTip = statusTip

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def data(self):
        if self._data is None:
            return {}
        return self._data.copy()

    def setData(self, value):
        self._data = value.copy()

    def enabled(self):
        """Can the data be enabled?"""
        return self._enabled

    def setEnabled(self, value):
        self._enabled = value

    def checkable(self):
        """Can the data be checked?"""
        return self._checkable

    def setCheckable(self, value):
        self._checkable = value

    def editable(self):
        """Can the data be edited?"""
        return self._editable

    def setEditable(self, value):
        self._editable = value

    def selectable(self):
        """Can the data be selected?"""
        return self._selectable

    def setSelectable(self, value):
        self._selectable = value

    def neverHasChildren(self):
        """Optimisation, only set True if this is surely the last child node."""
        return self._neverHasChildren

    def setNeverHasChildren(self, value):
        self._neverHasChildren = value

    def icon(self):
        assert isinstance(self._iconPath, pycompat.TEXT_TYPE)
        if self._icon is None:
            import mmSolver.ui.uiutils as uiutils

            self._icon = uiutils.getIcon(self._iconPath)
        return self._icon

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def child(self, row):
        if row >= len(self._children):
            return None
        result = self._children[row]
        return result

    def childCount(self):
        return len(self._children)

    def children(self):
        nodes = []
        for i in range(self.childCount()):
            child = self.child(i)
            if child is None:
                continue
            nodes.append(child)
        return nodes

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)
        return 0

    def parentTags(self):
        """
        Get list of names for all nodes above the current node.

        :return: list of strs
        """
        tags = []
        node = self
        while node:
            # Allows us to skip the root node.
            if node is not None:
                tags.append(node.name())
                node = node.parent()
        return tags

    def childrenTags(self):
        """
        Get list of names for nodes below the current node.

        :return: list of strs
        """
        tags = []
        node = self
        if node.childCount() > 0:
            children = node.children()
            for child in children:
                tags.append(child.name())
                tags += child.childrenTags()
        return tags

    def allTags(self):
        """
        Get list of names for nodes above and below the current node.

        :return: list of strs
        """
        parent_tags = self.parentTags()
        children_tags = self.childrenTags()

        result = []
        result += parent_tags
        result += children_tags
        return result

    def allTagsStr(self):
        result = self.allTags()
        result = '|'.join(result)
        return result
