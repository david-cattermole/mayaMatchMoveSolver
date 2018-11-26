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
        self.beginResetModel()
        del self._rootNode
        self._rootNode = rootNode
        self.endResetModel()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._column_names.keys())

    def rowCount(self, parent=QtCore.QModelIndex()):
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
                msg = '{0} was not in {1}'
                msg = msg.format(column_index, self._column_names)
                raise ValueError(msg)
            column_name = self._column_names[column_index]
            if column_name not in self._node_attr_key:
                msg = '{0} was not in {1}'
                msg = msg.format(column_name, self._node_attr_key)
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
                LOG.warning('setData not editable: %r %r %r', index, value, node)
                return False
            if role == QtCore.Qt.EditRole:
                node.setName(value)
            self.dataChanged.emit(index, index, [role])
            return True
        LOG.warning('setData not valid: %r %r', index, value)
        return False

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._column_names.get(section, 'Column')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return 'Row'
        return

    def flags(self, index):
        v = QtCore.Qt.NoItemFlags
        node = index.internalPointer()
        if node is None:
            return v
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
        node = self.getNode(index)
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
            pass
            # LOG.warning('ItemModel index: %r', row)
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
            # LOG.warning('getNode index is not valid; %r', index)
            pass
        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = None
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = nodes.Node('untitled' + str(childCount))
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


def _getNameFromDict(index, names_dict, lookup_dict):
    if index not in names_dict:
        msg = '{0} was not in {1}'
        msg = msg.format(index, names_dict)
        raise ValueError(msg)
    column_name = names_dict[index]
    if column_name not in lookup_dict:
        msg = '{0} was not in {1}'
        msg = msg.format(column_name, names_dict)
        raise ValueError(msg)
    attr_name = lookup_dict[column_name]
    return attr_name


class TableModel(QtCore.QAbstractTableModel, uiutils.QtInfoMixin):
    def __init__(self, node_list=None, font=None):
        super(TableModel, self).__init__()
        self._column_names = {
            0: 'Column',
        }
        self._node_attr_key = {
            'Column': 'name',
        }
        self._node_set_attr_key = {
            'Column': 'setName',
        }
        self._font = font
        self._node_list = []
        if node_list is not None:
            self._node_list = list(node_list)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._column_names.keys())

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._node_list)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        node = self._node_list[row]
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            column_index = index.column()
            attr_name = _getNameFromDict(column_index,
                    self._column_names,
                    self._node_attr_key)
            value = getattr(node, attr_name, None)
            if value is not None:
                value = value()
            else:
                value = None
            return value

        if role == QtCore.Qt.DecorationRole:
            # TODO: Can we refactor this similar to the DisplayRole above?
            if index.column() == 0 and node is not None:
                return node.icon()

        if role == QtCore.Qt.ToolTipRole:
            if node is not None:
                return node.toolTip()

        if role == QtCore.Qt.StatusTipRole:
            if node is not None:
                return node.statusTip()

        if role == QtCore.Qt.FontRole:
            if self._font is not None:
                return self._font

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            row = index.row()
            column = index.column()
            node = self._node_list[row]
            if node is None:
                LOG.warning('node is invalid: %r %r %r', index, value, node)
            else:
                attr_name = _getNameFromDict(column,
                    self._column_names,
                    self._node_set_attr_key)
                if not node.editable():
                    LOG.warning('setData not editable: %r %r %r', index, value, node)
                    return False
                if role == QtCore.Qt.EditRole:
                    func = getattr(node, attr_name, None)
                    if func is not None:
                        func(value)
            self.dataChanged.emit(index, index, [role])
            return True
        LOG.warning('setData not valid: %r %r', index, value)
        return False

    def nodeList(self):
        """
        Get a copy of the internal node list for this model.
        """
        return list(self._node_list)

    def setNodeList(self, node_list):
        """
        Replace the internal node list entirely.
        """
        self.beginResetModel()
        del self._node_list
        self._node_list = list(node_list)
        self.endResetModel()
        return

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._column_names.get(section, 'Column')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return '#' + str(section)
        return

    def flags(self, index):
        v = QtCore.Qt.NoItemFlags
        row_index = index.row()
        node = self._node_list[row_index]
        if node is not None:
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
        else:
            LOG.warning('flags: node is None')
        return v

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        success = None
        for row in range(rows):
            childCount = len(self._node_list)
            childNode = StepNode('untitled' + str(childCount))
            success = self._node_list.insert(position, childNode)
        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = None
        for row in range(rows):
            success = self._node_list.pop(position)
        self.endRemoveRows()
        return success


class SortFilterProxyModel(QtCore.QSortFilterProxyModel, uiutils.QtInfoMixin):
    def __init__(self):
        super(SortFilterProxyModel, self).__init__()
        self._filterTagName = ''
        self._filterTagValue = ''
        self._filterTagNodeType = ''
        # TODO: Support multiple named tags for filtering, currently
        # only supports 1.

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
        LOG.debug('filterAcceptsRow: %r', node)
        return True

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


class StringDataListModel(QtCore.QAbstractListModel, uiutils.QtInfoMixin):
    def __init__(self,
                 stringDataList=None,
                 font=None,
                 parent=None):
        super(StringDataListModel, self).__init__(parent)
        self._stringDataList = []
        self._font = font
        if stringDataList is not None:
            self.setStringDataList(stringDataList)

    def stringDataList(self):
        string_data_list = []
        for string, data in self._stringDataList:
            string_data_list.append((string, data))
        return string_data_list

    def setStringDataList(self, stringDataList):
        rowCount = self.rowCount()
        self.removeRows(0, rowCount)
        self.insertRows(0, len(stringDataList))
        for i, (string, data) in enumerate(stringDataList):
            index = self.index(i)
            self.setData(index, string, role=QtCore.Qt.DisplayRole)
            self.setData(index, data, role=QtCore.Qt.UserRole)
        self._stringDataList = list(stringDataList)
        return

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return 'Name'
        elif role == QtCore.Qt.EditRole:
            return 'Name'
        elif role == QtCore.Qt.UserRole:
            return 'Data'
        return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.row() > len(self._stringDataList):
            return None
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            v = self._stringDataList[index.row()]
            if isinstance(v, (tuple, list)) and len(v) == 2:
                return v[0]
        elif role in [QtCore.Qt.UserRole]:
            v = self._stringDataList[index.row()]
            if isinstance(v, (tuple, list)) and len(v) == 2:
                return v[1]
        return None

    def flags(self, index):
        flags = super(StringDataListModel, self).flags(index)
        if index.isValid():
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        self._stringDataList[row:row] = [('', None)] * count
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        del self._stringDataList[row:row + count]
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._stringDataList)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            v = self._stringDataList[index.row()]
            v = (value, v[1])
            self._stringDataList[index.row()] = value
        elif role in [QtCore.Qt.UserRole]:
            v = self._stringDataList[index.row()]
            v = (v[0], value)
            self._stringDataList[index.row()] = value
        if role in [QtCore.Qt.DisplayRole,
                    QtCore.Qt.EditRole,
                    QtCore.Qt.UserRole]:
            self.dataChanged.emit(index, index, [role])
        else:
            return False
        return True


