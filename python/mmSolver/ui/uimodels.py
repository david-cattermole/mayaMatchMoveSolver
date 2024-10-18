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
Qt models used in Model-View-Controller designs.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt as Qt
import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.ui.converttypes as converttypes
import mmSolver.ui.nodes as uinodes
import mmSolver.ui.uiutils as uiutils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def getNameFromDict(index, names_dict, lookup_dict):
    """
    Get the 'name' from an index, using a specific data structure.

    For example::

       index = 0
       names_dict = {
           0: 'Column',
       }
       lookup_dict = {
           'Column': 'name',
       }
       x = getNameFromDict(index, names_dict, lookup_dict)
       # x equals 'name'

    :param index: Index to look up.
    :param names_dict: The mapping data, from index to 'second key'.
    :param lookup_dict: Mapping data structure from 'second key' to
                        final look up name.

    :returns: The name in 'lookup_dict' referred to by index in
              'names_dict', or None if the name is not in the
              dictionary.
    :rtype: str or None
    """
    if index not in names_dict:
        return None
    column_name = names_dict[index]
    if column_name not in lookup_dict:
        return None
    attr_name = lookup_dict[column_name]
    return attr_name


class ItemModel(QtCore.QAbstractItemModel, uiutils.QtInfoMixin):
    def __init__(self, rootNode, font=None):
        super(ItemModel, self).__init__()
        self._rootNode = None
        self._font = font
        self.setRootNode(rootNode)

    def defaultNodeType(self):
        return uinodes.Node

    def columnNames(self):
        column_names = {
            0: 'Column',
        }
        return dict(column_names)

    def columnAlignments(self):
        values = {
            'Column': QtCore.Qt.AlignLeft,
        }
        return values

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            'Column': 'name',
        }
        return self._getLookUpFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            'Column': 'setName',
        }
        return self._getLookUpFuncFromIndex(index, set_attr_dict)

    def getColorFuncFromIndex(self, index):
        color_dict = {
            'Column': 'color',
        }
        return self._getLookUpFuncFromIndex(index, color_dict)

    ################################################

    def indexEnabled(self, index):
        node = index.internalPointer()
        return node.enabled()

    def indexCheckable(self, index):
        node = index.internalPointer()
        return node.checkable()

    def indexSelectable(self, index):
        node = index.internalPointer()
        return node.selectable()

    def indexEditable(self, index):
        node = index.internalPointer()
        return node.editable()

    def indexIcon(self, index):
        node = index.internalPointer()
        if index.column() == 0:
            return node.icon()
        return None

    def indexColumnAlignment(self, index):
        alignments = self.columnAlignments()
        column_name = self.getColumnNameFromIndex(index)
        align = alignments.get(column_name, QtCore.Qt.AlignLeft)
        return align

    ####################################################

    def _getLookUpFuncFromIndex(self, index, lookup_dict):
        column_index = index.column()
        column_names = self.columnNames()
        name = getNameFromDict(
            column_index,
            column_names,
            lookup_dict,
        )
        if name is None:
            return None
        node = index.internalPointer()
        func = getattr(node, name, None)
        return func

    def _getGetAttrFuncFromIndex(self, index, lookup_dict):
        return self._getLookUpFuncFromIndex(index, lookup_dict)

    def _getSetAttrFuncFromIndex(self, index, lookup_dict):
        return self._getLookUpFuncFromIndex(index, lookup_dict)

    def _getColorFuncFromIndex(self, index, lookup_dict):
        return self._getLookUpFuncFromIndex(index, lookup_dict)

    def getColumnNameFromIndex(self, index):
        column_index = index.column()
        column_names = self.columnNames()
        column_name = column_names.get(column_index)
        if column_name is None:
            msg = 'Column index is not set correctly; '
            msg += 'index=%r column_names=%r column_name=%r'
            LOG.warning(msg, index, column_names, column_name)
        return column_name

    def getColumnIndexFromColumnName(self, name):
        index = None
        column_names = self.columnNames()
        for idx, value in column_names.items():
            if name == value:
                index = idx
                break
        return index

    ####################################################

    def rootNode(self):
        return self._rootNode

    def setRootNode(self, rootNode):
        self.beginResetModel()
        del self._rootNode
        self._rootNode = rootNode
        self.endResetModel()
        return

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

    ####################################################

    def columnCount(self, parent=QtCore.QModelIndex()):
        column_names = self.columnNames()
        return len(column_names.keys())

    def rowCount(self, parent=QtCore.QModelIndex()):
        parentNode = None
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        if parentNode is None:
            return 0
        return parentNode.childCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            func = self.getGetAttrFuncFromIndex(index)
            value = None
            if func is not None:
                value = func()
            return value

        if role == QtCore.Qt.DecorationRole:
            return self.indexIcon(index)

        if role == QtCore.Qt.ForegroundRole:
            func = self.getColorFuncFromIndex(index)
            value = None
            if func is not None:
                value = func()
            return value

        node = index.internalPointer()
        if role == QtCore.Qt.ToolTipRole:
            return node.toolTip()

        if role == QtCore.Qt.StatusTipRole:
            return node.statusTip()

        if role == QtCore.Qt.FontRole:
            if self._font is not None:
                return self._font

        if role == QtCore.Qt.TextAlignmentRole:
            return self.indexColumnAlignment(index)
        return

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            LOG.warning('setData not valid: %r %r', index, value)
            return False
        node = index.internalPointer()

        if not self.indexEditable(index):
            LOG.warning('setData not editable: %r %r %r', index, value, node)
            return False

        if role == QtCore.Qt.EditRole:
            func = self.getSetAttrFuncFromIndex(index)
            if func is not None:
                func(value)

        # Emit Data Changed.
        if Qt.__binding__ in ['PySide', 'PyQt4']:
            self.dataChanged.emit(index, index)
        elif Qt.__binding__ in ['PySide2', 'PyQt5']:
            self.dataChanged.emit(index, index, [role])
        else:
            msg = 'Qt binding not supported: %s' % Qt.__binding__
            raise ValueError(msg)
        return True

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                column_names = self.columnNames()
                return column_names.get(section, 'Column')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return 'Row'
        return

    def flags(self, index):
        v = QtCore.Qt.NoItemFlags
        node = index.internalPointer()
        if node is None:
            LOG.warning('flags: node is None')
            return v
        if self.indexEnabled(index):
            v = v | QtCore.Qt.ItemIsEnabled
        if self.indexCheckable(index):
            v = v | QtCore.Qt.ItemIsUserCheckable
        if self.indexSelectable(index):
            v = v | QtCore.Qt.ItemIsSelectable
        if self.indexEditable(index):
            v = v | QtCore.Qt.ItemIsEditable
        if Qt.__binding__ in ['PySide2', 'PyQt5']:
            if node.neverHasChildren():
                v = v | QtCore.Qt.ItemNeverHasChildren
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
            return QtCore.QModelIndex()
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QtCore.QModelIndex()

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = None
        nodeType = self.defaultNodeType()
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = nodeType('untitled' + str(childCount))
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


class TableModel(QtCore.QAbstractTableModel, uiutils.QtInfoMixin):
    def __init__(self, node_list=None, font=None):
        super(TableModel, self).__init__()
        self._font = font
        self._node_list = []
        if node_list is not None:
            self._node_list = list(node_list)

    def defaultNodeType(self):
        return uinodes.Node

    def columnNames(self):
        column_names = {
            0: 'Column',
        }
        return dict(column_names)

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            'Column': 'name',
        }
        return self._getLookUpFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            'Column': 'setName',
        }
        return self._getLookUpFuncFromIndex(index, set_attr_dict)

    def getColorFuncFromIndex(self, index):
        color_dict = {
            'Column': 'color',
        }
        return self._getLookUpFuncFromIndex(index, color_dict)

    ################################################

    def indexEnabled(self, index):
        row_index = index.row()
        node = self._node_list[row_index]
        return node.enabled()

    def indexCheckable(self, index):
        row_index = index.row()
        node = self._node_list[row_index]
        return node.checkable()

    def indexSelectable(self, index):
        row_index = index.row()
        node = self._node_list[row_index]
        return node.selectable()

    def indexEditable(self, index):
        row_index = index.row()
        node = self._node_list[row_index]
        return node.editable()

    def indexIcon(self, index):
        row_index = index.row()
        node = self._node_list[row_index]
        return node.icon()

    ################################################

    def _getLookUpFuncFromIndex(self, index, lookup_dict):
        row_index = index.row()
        column_index = index.column()
        node = self._node_list[row_index]
        column_names = self.columnNames()
        name = getNameFromDict(
            column_index,
            column_names,
            lookup_dict,
        )
        if name is None:
            return None
        func = getattr(node, name, None)
        return func

    def _getGetAttrFuncFromIndex(self, index, lookup_dict):
        return self._getLookUpFuncFromIndex(index, lookup_dict)

    def _getSetAttrFuncFromIndex(self, index, lookup_dict):
        return self._getLookUpFuncFromIndex(index, lookup_dict)

    def getColumnNameFromIndex(self, index):
        column_index = index.column()
        column_names = self.columnNames()
        column_name = column_names.get(column_index)
        if column_name is None:
            msg = 'Column index is not set correctly; '
            msg += 'index=%r column_names=%r column_name=%r'
            LOG.warning(msg, index, column_names, column_name)
        return column_name

    def getColumnIndexFromColumnName(self, name):
        index = None
        column_names = self.columnNames()
        for idx, value in column_names.items():
            if name == value:
                index = idx
                break
        return index

    ################################################

    def columnCount(self, parent=QtCore.QModelIndex()):
        column_names = self.columnNames()
        return len(column_names.keys())

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._node_list)

    def data(self, index, role):
        if not index.isValid():
            return None
        row_index = index.row()
        node = self._node_list[row_index]
        roles = [
            QtCore.Qt.DisplayRole,
            QtCore.Qt.EditRole,
            QtCore.Qt.CheckStateRole,
        ]
        if role in roles:
            get_attr_func = self.getGetAttrFuncFromIndex(index)
            value = None
            if get_attr_func is not None:
                value = get_attr_func()

            # For check states, we must return a 'CheckState' of
            # Checked or Unchecked.
            if role == QtCore.Qt.CheckStateRole:
                index_checkable = self.indexCheckable(index)
                if index_checkable is True:
                    value = converttypes.stringToBoolean(value)
                    if isinstance(value, bool):
                        value = converttypes.booleanToCheckState(value)
                else:
                    # If the column is not checkable we make sure it's
                    # not displayed as checkable by returning a
                    # 'None'
                    value = None

            # value may be bool, string or None type.
            return value

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0 and node is not None:
                return self.indexIcon(index)

        if role == QtCore.Qt.ToolTipRole:
            if node is not None:
                return node.toolTip()

        if role == QtCore.Qt.StatusTipRole:
            if node is not None:
                return node.statusTip()

        if role == QtCore.Qt.FontRole:
            if self._font is not None:
                return self._font
        return

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            LOG.warning('setData not valid: %r %r', index, value)
            return False
        row_index = index.row()
        node = self._node_list[row_index]
        if node is None:
            LOG.warning('node is invalid: %r %r %r', index, value, node)
            return False
        set_attr_func = self.getSetAttrFuncFromIndex(index)
        if not node.editable():
            LOG.warning('setData not editable: %r %r %r', index, value, node)
            return False

        if set_attr_func is not None:
            if role == QtCore.Qt.EditRole:
                set_attr_func(value)

            if role == QtCore.Qt.CheckStateRole:
                index_checkable = self.indexCheckable(index)
                if index_checkable is True:
                    v = converttypes.checkStateToBoolean(value)
                    v = converttypes.booleanToString(v)
                    set_attr_func(v)

        # Changing some data will force entire row to update.
        columnCount = self.columnCount()
        index_begin = self.createIndex(row_index, 0, index.internalId)
        index_end = self.createIndex(row_index, columnCount - 1, index.internalId)

        # Emit Data Changed.
        if Qt.__binding__ in ['PySide', 'PyQt4']:
            self.dataChanged.emit(index_begin, index_end)
        elif Qt.__binding__ in ['PySide2', 'PyQt5']:
            self.dataChanged.emit(index_begin, index_end, [role])
        else:
            msg = 'Qt binding not supported: %s' % Qt.__binding__
            raise ValueError(msg)
        return True

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
                column_names = self.columnNames()
                return column_names.get(section, 'Column')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return '#' + str(section + 1)
        return

    def flags(self, index):
        v = QtCore.Qt.NoItemFlags
        if not index.isValid():
            return v
        row_index = index.row()
        node = self._node_list[row_index]
        if node is None:
            LOG.warning('flags: node is None')
            return v
        if self.indexEnabled(index):
            v = v | QtCore.Qt.ItemIsEnabled
        if self.indexCheckable(index):
            v = v | QtCore.Qt.ItemIsUserCheckable
        if self.indexSelectable(index):
            v = v | QtCore.Qt.ItemIsSelectable
        if self.indexEditable(index):
            v = v | QtCore.Qt.ItemIsEditable
        if node.neverHasChildren():
            v = v | QtCore.Qt.ItemNeverHasChildren
        return v

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        success = None
        nodeType = self.defaultNodeType()
        for row in range(rows):
            childCount = len(self._node_list)
            childNode = nodeType('untitled' + str(childCount))
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


class StringDataListModel(QtCore.QAbstractListModel, uiutils.QtInfoMixin):
    def __init__(self, stringDataList=None, font=None, parent=None):
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
        del self._stringDataList[row : row + count]
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
        else:
            return False

        # Emit Data Changed.
        if Qt.__binding__ in ['PySide', 'PyQt4']:
            self.dataChanged.emit(index, index)
        elif Qt.__binding__ in ['PySide6', 'PySide2', 'PyQt5']:
            if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole, QtCore.Qt.UserRole]:
                self.dataChanged.emit(index, index, [role])
        else:
            msg = 'Qt binding not supported: %s' % Qt.__binding__
            raise ValueError(msg)
        return True


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)

    def getValueList(self):
        """
        Sub-class, override this method and return a list of strings for
        the combo-box values.
        """
        raise NotImplementedError

    def createEditor(self, parent, option, index):
        if not index.isValid():
            LOG.warning('Invalid index: %r', index)
            return
        data = index.data(QtCore.Qt.EditRole)
        values = self.getValueList()
        model = QtCore.QStringListModel(values)
        widget = QtWidgets.QComboBox(parent)
        widget.setModel(model)
        return widget

    def setEditorData(self, editor, index):
        idx = 0  # Default to first index, as fallback.
        values = self.getValueList()
        data = index.data(QtCore.Qt.EditRole)
        if data in values:
            idx = values.index(data)
        else:
            msg = 'data not in values: data=%r values=%r'
            LOG.warning(msg, data, values)

        editor.blockSignals(True)
        editor.setCurrentIndex(idx)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        data = index.data(QtCore.Qt.EditRole)
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)
        return
