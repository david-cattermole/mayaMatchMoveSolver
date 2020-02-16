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

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.solver.widget.ui_nodebrowser_widget as ui_nodebrowser_widget

LOG = mmSolver.logger.get_logger()


def _findIndexWithUUID(node_uuid, parent_index, model, column):
    role = QtCore.Qt.DisplayRole
    data = model.data(parent_index, role)
    if node_uuid == data:
        return parent_index
    number_of_rows = model.rowCount(parent_index)
    if number_of_rows > 0:
        for row in xrange(number_of_rows):
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
