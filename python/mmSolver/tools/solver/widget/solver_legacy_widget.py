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
Solver Settings 'Legacy' widget.

This widget holds the older 'legacy' solver, which contains solver
steps as a TableView for users to manipulate.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes
import mmSolver.tools.solver.ui.convert_to_ui as convert_to_ui
import mmSolver.tools.solver.widget.ui_solver_legacy_widget as ui_solver_legacy_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class SolverLegacyWidget(QtWidgets.QWidget, ui_solver_legacy_widget.Ui_Form):

    itemAdded = QtCore.Signal()
    itemRemoved = QtCore.Signal()
    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverLegacyWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.createTableView()

        # Solver Add and Remove buttons
        self.add_toolButton.clicked.connect(self.addClicked)
        self.remove_toolButton.clicked.connect(self.removeClicked)

        # Override Current Frame
        self.overrideCurrentFrame_checkBox.stateChanged.connect(
            self.overrideCurrentFrameChanged
        )

        # Ensure the model is updated when data is changed.
        self.dataChanged.connect(self.updateModel)
        e = time.time()
        LOG.debug('SolverLegacyWidget init: %r seconds', e - s)
        return

    def createTableView(self):
        self.model = solver_nodes.SolverModel(font=self.font)
        self.filterModel = QtCore.QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.model)
        self.filterModel.setDynamicSortFilter(False)
        self.tableView.setModel(self.filterModel)
        self.tableView.setSortingEnabled(False)
        self.selModel = self.tableView.selectionModel()

        # Set up custom widgets for viewing and editing the columns.
        self.attrFilterDelegate = solver_nodes.AttributeComboBoxDelegate()
        attr_idx = self.model.getColumnIndexFromColumnName(
            const.SOLVER_COLUMN_NAME_ATTRIBUTES
        )
        strategy_idx = self.model.getColumnIndexFromColumnName(
            const.SOLVER_COLUMN_NAME_STRATEGY
        )
        self.tableView.setItemDelegateForColumn(
            attr_idx,
            self.attrFilterDelegate,
        )
        self.strategyDelegate = solver_nodes.StrategyComboBoxDelegate()
        self.tableView.setItemDelegateForColumn(
            strategy_idx,
            self.strategyDelegate,
        )
        return

    def populateModel(self, model):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        col = lib_state.get_active_collection()
        if col is None:
            step_list = []
        else:
            step_list = lib_col.get_solver_steps_from_collection(col)
        node_list = convert_to_ui.solverStepsToUINodes(step_list, col)
        self.model.setNodeList(node_list)
        return

    def populateOverrideCurrentFrame(self):
        cur_frame = False
        col = lib_state.get_active_collection()
        if col is not None:
            cur_frame = lib_col.get_override_current_frame_from_collection(col)
        self.overrideCurrentFrame_checkBox.setChecked(cur_frame)
        return

    def updateModel(self):
        self.populateOverrideCurrentFrame()
        self.populateModel(self.model)

        widgets = [self]
        _populateWidgetsEnabled(widgets)
        return

    def queryInfo(self):
        LOG.debug('RUN legacy queryInfo')
        col = lib_state.get_active_collection()
        text = lib_col.query_solver_info_text(col)
        return text

    def addClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add Solver Step, active collection is invalid,'
            LOG.warning(msg)
            return
        step = lib_col.create_solver_step()
        lib_col.add_solver_step_to_collection(col, step)

        self.itemAdded.emit()
        self.dataChanged.emit()
        self.viewUpdated.emit()
        return

    def removeClicked(self):
        ui_nodes = lib_uiquery.get_selected_ui_table_row(
            self.tableView, self.model, self.filterModel
        )
        names = map(lambda x: x.name(), ui_nodes)
        col_nodes = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'collection_node')
        assert len(names) == len(col_nodes)
        for name, col in zip(names, col_nodes):
            step = lib_col.get_named_solver_step_from_collection(col, name)
            lib_col.remove_solver_step_from_collection(col, step)

        self.itemRemoved.emit()
        self.dataChanged.emit()
        self.viewUpdated.emit()
        return

    def setOverrideCurrentFrame(self, col, value):
        """
        Set the override status for the collection given.

        Updates the relevant UI components with the new data.

        :param col: The Collection to set.
        :type col: Collection

        :param value: Should we override the current frame? Yes or No.
        :type value: bool
        """
        assert isinstance(value, bool)
        lib_col.set_override_current_frame_on_collection(col, value)

        self.dataChanged.emit()
        self.viewUpdated.emit()
        return

    @QtCore.Slot(int)
    def overrideCurrentFrameChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection, cannot override Solver Step.')
            return
        # 'value' from Qt is expected to be an int, we expect a bool.
        value = bool(value)
        self.setOverrideCurrentFrame(col, value)
        return
