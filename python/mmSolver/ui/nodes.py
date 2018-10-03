"""
Defines a basic node class able to be used for tree data models.
"""


class Node(object):
    def __init__(self, name,
                 data=None,
                 toolTip=None,
                 statusTip=None,
                 parent=None,
                 icon=None,
                 enabled=True,
                 editable=False,
                 selectable=True,
                 checkable=False,
                 neverHasChildren=False):
        if icon is None:
            icon = ':/Node.png'
        self._children = []
        self._parent = parent

        self._name = name
        self._toolTip = toolTip
        self._statusTip = statusTip
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
        assert isinstance(self._iconPath, str)
        if self._icon is None:
            import qtLearn.uiUtils as uiUtils
            self._icon = uiUtils.getIcon(self._iconPath)
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
        result = self._children[row]
        return result

    def childCount(self):
        return len(self._children)

    def children(self):
        nodes = []
        for i in range(self.childCount()):
            nodes.append(self.child(i))
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

