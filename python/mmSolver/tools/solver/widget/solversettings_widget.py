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
Widget class to hold all Solver Settings for the solver GUI.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solversettings_widget as ui_solversettings_widget
import mmSolver.tools.solver.widget.solversettingsstandard_widget as solversettingsstandard_widget
import mmSolver.tools.solver.widget.solversettingsbasic_widget as solversettingsbasic_widget
import mmSolver.tools.solver.widget.solversettingslegacy_widget as solversettingslegacy_widget


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class SolverSettingsWidget(QtWidgets.QWidget, ui_solversettings_widget.Ui_Form):

    tabChanged = QtCore.Signal()
    dataChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super(SolverSettingsWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Solver Settings Basic Widget
        self.basic_widget = solversettingsbasic_widget.SolverSettingsBasicWidget(self)
        self.basic_layout.addWidget(self.basic_widget)

        # Solver Settings Standard Widget
        self.standard_widget = solversettingsstandard_widget.SolverSettingsStandardWidget(self)
        self.standard_layout.addWidget(self.standard_widget)

        # Solver Settings Legacy Widget
        self.legacy_widget = solversettingslegacy_widget.SolverSettingsLegacyWidget(self)
        self.legacy_layout.addWidget(self.legacy_widget)

        self._tab_name_to_index_map = {
            'basic': 0,
            'standard': 1,
            'legacy': 2,
        }
        self._tab_index_to_widget_map = {
            0: self.basic_widget,
            1: self.standard_widget,
            2: self.legacy_widget,
        }
        self.all_tab_widgets = [
            self.basic_widget,
            self.standard_widget,
            self.legacy_widget
        ]

        # Set defaults for info text fields.
        self.info_label.setHidden(False)

        self.tabWidget.currentChanged.connect(self._tabChanged)
        self.basic_widget.dataChanged.connect(self._dataChanged)
        self.standard_widget.dataChanged.connect(self._dataChanged)
        self.legacy_widget.dataChanged.connect(self._dataChanged)
        return

    def getSolverTabValue(self, col):
        value = lib_col_state.get_solver_tab_from_collection(col)
        return value

    def setSolverTabValue(self, col, value):
        lib_col_state.set_solver_tab_on_collection(col, value)
        return

    @QtCore.Slot(int)
    def _tabChanged(self, idx):
        self.updateModel()

        # Store the tab name we've changed to.
        col = lib_state.get_active_collection()
        if col is not None:
            name = self.tabWidget.tabText(idx)
            name = name.lower()
            self.setSolverTabValue(col, name)

        self.tabChanged.emit()
        return

    def _dataChanged(self):
        self.dataChanged.emit()
        return

    def _getTabWidget(self, idx):
        widget = self._tab_index_to_widget_map.get(idx, None)
        if widget is None:
            raise RuntimeError('tab index is not valid: %r' % idx)
        assert widget is not None
        return widget

    def updateModel(self):
        col = lib_state.get_active_collection()
        if col is not None:
            tab_name = self.getSolverTabValue(col)
            tab_name = tab_name.lower()
            idx = self._tab_name_to_index_map.get(tab_name, None)
            if idx is None:
                msg = 'Solver tab name is not valid: %r' % tab_name
                raise ValueError(msg)
            self.tabWidget.setCurrentIndex(idx)

        idx = self.tabWidget.currentIndex()
        tab_widget = self._getTabWidget(idx)
        tab_widget.updateModel()

        widgets = [
            tab_widget,
            self.info_label,
        ]
        _populateWidgetsEnabled(widgets)
        return

    def updateInfo(self):
        idx = self.tabWidget.currentIndex()
        tab_widget = self._getTabWidget(idx)
        text = tab_widget.queryInfo()
        self.info_label.setText(text)
        return
