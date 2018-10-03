"""
Qt models used in Model-View-Controller designs.
"""

import Qt as Qt
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore

import mmSolver.ui.nodes as nodes
import mmSolver.ui.uiutils as uiutils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


class ItemModel(QtCore.QAbstractItemModel, uiutils.QtInfoMixin):
    def __init__(self, rootNode, font=None):
        super(ItemModel, self).__init__()
        self._rootNode = None
        self._column_names = {
            0: 'Column',
        }
        self._node_attr_key = {
            'Column': 'name',
        }

        self._font = font

        self.setRootNode(rootNode)

    def rootNode(self):
        return self._rootNode

    def setRootNode(self, rootNode):
        cls = super(ItemModel, self)
        useBeginAndEnd = False
        if 'beginResetModel' in cls.__dict__ and 'endResetModel' in cls.__dict__:
            useBeginAndEnd = True

        if useBeginAndEnd is True:
            # super(ItemModel, self).beginResetModel()
            self.beginResetModel()

        del self._rootNode
        self._rootNode = rootNode
        # if useBeginAndEnd is False:
        #     self.modelReset()

        if useBeginAndEnd is True:
            self.endResetModel()

        topLeft = self.createIndex(0, 0)
        self.dataChanged.emit(topLeft, topLeft)

    def columnCount(self, parent):
        return len(self._column_names.keys())

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            column_index = index.column()
            if column_index not in self._column_names:
                msg = '{0} was not in {1}'.format(column_index, self._column_names)
                raise ValueError(msg)
            column_name = self._column_names[column_index]
            if column_name not in self._node_attr_key:
                msg = '{0} was not in {1}'.format(column_name, self._node_attr_key)
                raise ValueError(msg)
            attr_name = self._node_attr_key[column_name]
            value = getattr(node, attr_name, None)
            if value is not None:
                value = value()
            return value

        if role == QtCore.Qt.DecorationRole:
            # TODO: Can we refactor this similar to the DisplayRole above?
            if index.column() == 0:
                return node.icon()

        if role == QtCore.Qt.ToolTipRole:
            return node.toolTip()

        if role == QtCore.Qt.StatusTipRole:
            return node.statusTip()

        if role == QtCore.Qt.FontRole:
            if self._font is not None:
                return self._font

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if not node.editable():
                return False
            if role == QtCore.Qt.EditRole:
                node.setName(value)
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return self._column_names.get(section, 'Column')

    def flags(self, index):
        v = QtCore.Qt.NoItemFlags
        node = index.internalPointer()
        if node.enabled():
            v = v | QtCore.Qt.ItemIsEnabled
        if node.checkable():
            v = v | QtCore.Qt.ItemIsUserCheckable
        if node.neverHasChildren():
            v = v | QtCore.Qt.ItemNeverHasChildren
        if node.selectable():
            v = v | QtCore.Qt.ItemIsSelectable
        if node.editable():
            v = v | QtCore.Qt.ItemIsEditable
        return v

    def parent(self, index):
        node = self.getNode(index)  # index.internalPointer()
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        if parentNode is None:
            return QtCore.QModelIndex()
        row = parentNode.row()
        return self.createIndex(row, 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        if row < 0 and row >= parentNode.childCount():
            LOG.warning('ItemModel index: %r', row)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QtCore.QModelIndex()

    def getNode(self, index):
        node = None
        if index.isValid():
            node = index.internalPointer()
            if node is not None:
                return node
        else:
            LOG.warning('getNode index is not valid; %r', index)
        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = None
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = nodes.Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = None
        for row in range(rows):
            success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success


class SortFilterProxyModel(QtCore.QSortFilterProxyModel, uiutils.QtInfoMixin):
    def __init__(self):
        super(SortFilterProxyModel, self).__init__()
        self._filterTagName = ''
        self._filterTagValue = ''
        self._filterTagNodeType = ''
        # TODO: Support multiple named tags for filtering, currently only supports 1.

    ############################################################################

    def filterTagName(self):
        return self._filterTagName

    def setFilterTagName(self, value):
        self._filterTagName = value
        self.invalidateFilter()

    def filterTagValue(self):
        return self._filterTagValue

    def setFilterTagValue(self, value):
        self._filterTagValue = value
        self.invalidateFilter()

    def filterTagNodeType(self):
        return self._filterTagNodeType

    def setFilterTagNodeType(self, value):
        self._filterTagNodeType = value
        self.invalidateFilter()

    ############################################################################

    def filterAcceptsRow(self, sourceRow, sourceParent):
        result = False
        srcModel = self.sourceModel()
        column = self.filterKeyColumn()
        if column < 0:
            column = 0
        index = srcModel.index(sourceRow, column, sourceParent)
        node = index.internalPointer()

        tagName = self.filterTagName()
        if tagName is None or len(tagName) == 0:
            return True

        filterNodeType = self.filterTagNodeType()
        typeInfo = node.typeInfo

        if filterNodeType is None or typeInfo == filterNodeType:
            tagValue = self.filterTagValue()
            nodeData = node.data()
            nodeDataValue = nodeData.get(tagName)
            if tagValue is None or len(tagValue) == 0:
                result = True
            elif nodeDataValue == tagValue:
                result = True
            else:
                result = False
        else:
            pattern = self.filterRegExp().pattern()
            if pattern is None or len(pattern) == 0:
                result = True
            else:
                path = node.allTags()
                if pattern in path:
                    result = True
        return result
