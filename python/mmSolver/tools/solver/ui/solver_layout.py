# Copyright (C) 2018, 2019 David Cattermole.
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
The Solver layout, the contents of the main solver window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.state as lib_state

import mmSolver.tools.solver.ui.ui_solver_layout as ui_solver_layout
import mmSolver.tools.solver.widget.attribute_widget as attrbrowser_widget
import mmSolver.tools.solver.widget.object_widget as objectbrowser_widget
import mmSolver.tools.solver.widget.collection_widget as collection_widget
import mmSolver.tools.solver.widget.solverstate_widget as solverstate_widget
import mmSolver.tools.solver.widget.solver_widget as solver_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class SolverLayout(QtWidgets.QWidget, ui_solver_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Store the parent window class, so we can set the applyBtn enabled
        # state.
        self._parentObject = parent

        # Collection Widget
        self.collection_widget = collection_widget.CollectionWidget(self)
        self.collection_layout.addWidget(self.collection_widget)

        # Object Widget
        self.object_browser = objectbrowser_widget.ObjectBrowserWidget(self)
        self.object_layout.addWidget(self.object_browser)

        # Attribute Widget
        self.attribute_browser = attrbrowser_widget.AttributeBrowserWidget(self)
        self.attribute_layout.addWidget(self.attribute_browser)

        # Solver Widget
        self.solver_settings = solver_widget.SolverWidget(self)
        self.solver_layout.addWidget(self.solver_settings)

        # Solver State Widget
        self.solver_state = solverstate_widget.SolverStateWidget(self)
        self.solverState_layout.addWidget(self.solver_state)

        # Populate the UI with data.
        self.collection_widget.nameChanged.connect(self.updateDynamicWindowTitle)
        self.collection_widget.itemChanged.connect(self.updateDynamicWindowTitle)
        # self.collection_widget.itemChanged.connect(self.solver_state.updateStatusWithSolveResult)
        self.collection_widget.itemChanged.connect(self.object_browser.updateModel)
        self.collection_widget.itemChanged.connect(self.object_browser.updateInfo)
        self.collection_widget.itemChanged.connect(self.object_browser.updateToggleButtons)
        self.collection_widget.itemChanged.connect(self.object_browser.updateColumnVisibility)
        self.collection_widget.itemChanged.connect(self.attribute_browser.updateModel)
        self.collection_widget.itemChanged.connect(self.attribute_browser.updateInfo)
        self.collection_widget.itemChanged.connect(self.attribute_browser.updateToggleButtons)
        self.collection_widget.itemChanged.connect(self.attribute_browser.updateColumnVisibility)
        self.collection_widget.itemChanged.connect(self.solver_settings.updateModel)
        self.collection_widget.itemChanged.connect(self.solver_settings.updateInfo)
        self.collection_widget.itemChanged.connect(self.solver_state.updateModel)

        self.object_browser.dataChanged.connect(self.object_browser.updateModel)
        self.object_browser.dataChanged.connect(self.object_browser.updateInfo)
        self.object_browser.dataChanged.connect(self.solver_settings.updateInfo)
        self.object_browser.viewUpdated.connect(self.object_browser.updateToggleButtons)
        self.object_browser.viewUpdated.connect(self.object_browser.updateColumnVisibility)

        self.attribute_browser.dataChanged.connect(self.attribute_browser.updateModel)
        self.attribute_browser.dataChanged.connect(self.attribute_browser.updateInfo)
        self.attribute_browser.dataChanged.connect(self.solver_settings.updateInfo)
        self.attribute_browser.viewUpdated.connect(self.attribute_browser.updateToggleButtons)
        self.attribute_browser.viewUpdated.connect(self.attribute_browser.updateColumnVisibility)

        self.solver_settings.dataChanged.connect(self.solver_settings.updateInfo)
        self.solver_settings.tabChanged.connect(self.solver_settings.updateInfo)
        self.solver_settings.tabChanged.connect(self.solver_settings.updateModel)
        self.solver_settings.sendWarning.connect(self.setStatusLine)

        # Trigger data being updated.
        self.collection_widget.itemChanged.emit()
        return

    def updateDynamicWindowTitle(self):
        """
        Dynamically set the current collection name to the title bar.
        """
        col = lib_state.get_active_collection()
        node = '<Collection>'
        if col is not None:
            node = col.get_node()
        title = str(const.WINDOW_TITLE_BAR)
        title = title.format(node)
        self._parentObject.window().setWindowTitle(title)
        return

    def updateSolveValidState(self):
        # TODO: Remove this empty function, it is kept around just because it might be called.
        return

    @QtCore.Slot(str)
    def setStatusLine(self, text):
        valid = uiutils.isValidQtObject(self)
        if valid is False:
            return
        valid = uiutils.isValidQtObject(self.solver_state)
        if valid is False:
            return
        self.solver_state.setStatusLine(text)
        return

    @QtCore.Slot(str)
    def setSolveInfoLine(self, text):
        valid = uiutils.isValidQtObject(self)
        if valid is False:
            return
        valid = uiutils.isValidQtObject(self.solver_state)
        if valid is False:
            return
        self.solver_state.setSolveInfoLine(text)
        return
