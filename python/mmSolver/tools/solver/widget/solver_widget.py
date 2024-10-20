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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solver_widget as ui_solver_widget
import mmSolver.tools.solver.widget.solver_basic_widget as solver_basic_widget
import mmSolver.tools.solver.widget.solver_standard_widget as solver_standard_widget
import mmSolver.tools.solver.widget.solver_camera_widget as solver_camera_widget


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class SolverWidget(QtWidgets.QWidget, ui_solver_widget.Ui_Form):
    tabChanged = QtCore.Signal()
    dataChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverWidget, self).__init__(parent, *args, **kwargs)
        self.setupUi(self)

        # Solver Settings Basic Widget
        self.basic_widget = solver_basic_widget.SolverBasicWidget(self)
        self.basic_layout.addWidget(self.basic_widget)

        # Solver Settings Standard Widget
        self.standard_widget = solver_standard_widget.SolverStandardWidget(self)
        self.standard_layout.addWidget(self.standard_widget)

        # Solver Settings Camera Widget
        self.camera_widget = solver_camera_widget.SolverCameraWidget(self)
        self.camera_layout.addWidget(self.camera_widget)


        self._tab_name_to_index_map = {
            'basic': 0,
            'standard': 1,
            'camera': 2,
        }
        self._tab_index_to_widget_map = {
            0: self.basic_widget,
            1: self.standard_widget,
            2: self.camera_widget,
        }
        self.all_tab_widgets = [
            self.basic_widget,
            self.standard_widget,
            self.camera_widget,
        ]

        for idx, widget in self._tab_index_to_widget_map.items():
            desc_text = widget.getDescriptionText()
            self.tabWidget.setTabToolTip(idx, desc_text)

        self.createConnections()

        e = time.time()
        LOG.debug('SolverWidget init: %r seconds', e - s)
        return

    def createConnections(self):
        self.tabWidget.currentChanged.connect(self._tabChanged)
        self.basic_widget.dataChanged.connect(self._dataChanged)
        self.standard_widget.dataChanged.connect(self._dataChanged)
        self.camera_widget.dataChanged.connect(self._dataChanged)

        self.standard_widget.sendWarning.connect(self._sendWarningToUser)

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
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
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
        ]
        _populateWidgetsEnabled(widgets)
        return

    @QtCore.Slot(str)
    def _sendWarningToUser(self, value):
        self.sendWarning.emit(value)
        return
