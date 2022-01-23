# Copyright (C) 2020 David Cattermole.
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
Utilties to be used with Node Browser and sub-classes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.widget.ui_nodebrowser_widget as ui_nodebrowser_widget

LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(col, widgets):
    enabled = col is not None
    for widget in widgets:
        currently_enabled = widget.isEnabled()
        if currently_enabled != enabled:
            widget.setEnabled(enabled)
    return


def _expand_node(tree_view, model, parentIndex, expand=True, recurse=False):
    tree_view.setExpanded(parentIndex, expand)
    rows = model.rowCount(parentIndex)
    for rowNum in range(rows):
        childIndex = model.index(rowNum, 0, parentIndex)
        tree_view.setExpanded(childIndex, expand)
        if recurse is True:
            _expand_node(tree_view, model, childIndex, expand, recurse=recurse)
    return


def _findIndexWithUUID(node_uuid, parent_index, model, column):
    role = QtCore.Qt.DisplayRole
    data = model.data(parent_index, role)
    if node_uuid == data:
        return parent_index
    number_of_rows = model.rowCount(parent_index)
    if number_of_rows > 0:
        for row in range(number_of_rows):
            index = model.index(row, column, parent=parent_index)
            idx = _findIndexWithUUID(node_uuid, index, model, column)
            if idx is None:
                continue
            return idx
    return None


def _lookupIndexesFromMayaNodeUUIDs(node_uuids, root_index, column, model):
    """
    Find the Qt Indexes in model, with the given Node UUIDs.
    """
    indexes = []
    for node_uuid in node_uuids:
        index = _findIndexWithUUID(node_uuid, root_index, model, column)
        if index is not None:
            indexes.append(index)
    return indexes


def setNodeSelectionWithUUID(tree_view,
                             model,
                             filter_model,
                             sel_model,
                             column_name,
                             values):
    """
    Override the tree view selection based on Maya Node UUIDs.
    """
    # Ensure we don't try to access the Qt objects if they no longer
    # exist in memory.
    objs = [tree_view, model, filter_model, sel_model]
    for obj in objs:
        valid = uiutils.isValidQtObject(obj)
        if valid is False:
            return

    root_index = tree_view.rootIndex()
    column = model.getColumnIndexFromColumnName(column_name)
    indexes = _lookupIndexesFromMayaNodeUUIDs(
        values,
        root_index,
        column,
        model,
    )
    sel_model.clearSelection()  # replace the selection.
    flags = QtCore.QItemSelectionModel.Select
    flags |= QtCore.QItemSelectionModel.Rows
    for index in indexes:
        new_index = filter_model.mapFromSource(index)
        sel_model.select(new_index, flags)
    return
