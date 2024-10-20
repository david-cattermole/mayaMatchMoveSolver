# Copyright (C) 2018, 2019, 2020 David Cattermole.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.constant as mmSolver_const
import mmSolver.tools.solver.lib.state as lib_state

import mmSolver.tools.solver.ui.ui_solver_layout as ui_solver_layout
import mmSolver.tools.solver.widget.attribute_widget as attrbrowser_widget
import mmSolver.tools.solver.widget.object_widget as objectbrowser_widget
import mmSolver.tools.solver.widget.collection_widget as collection_widget
import mmSolver.tools.solver.widget.solverstate_widget as solverstate_widget
import mmSolver.tools.solver.widget.solver_widget as solver_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class SolverLayout(QtWidgets.QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.ui = ui_solver_layout.Ui_Form()
        self.ui.setupUi(self)

        # Set the sizing for the Attribute and Object frames, so that
        # the Splitter will start out with a 50/50 ratio of Objects
        # to Attributes.
        self.ui.objectAttribute_splitter.setSizes([50, 50])

        # Store the parent window class, so we can set the applyBtn enabled
        # state.
        self._parentObject = parent

        # Collection Widget
        self.collection_widget = collection_widget.CollectionWidget(self)
        self.ui.collection_layout.addWidget(self.collection_widget)

        # Object Widget
        self.object_browser = objectbrowser_widget.ObjectBrowserWidget(self)
        self.ui.object_layout.addWidget(self.object_browser)

        # Attribute Widget
        self.attribute_browser = attrbrowser_widget.AttributeBrowserWidget(self)
        self.ui.attribute_layout.addWidget(self.attribute_browser)

        # Solver Widget
        self.solver_settings = solver_widget.SolverWidget(self)
        self.ui.solver_layout.addWidget(self.solver_settings)

        # Solver State Widget
        self.solver_state = solverstate_widget.SolverStateWidget(self)
        self.ui.solverState_layout.addWidget(self.solver_state)

        self.createConnections()

        # Trigger data being updated.
        self.collection_widget.itemChanged.emit()
        e = time.time()
        LOG.debug('SolverLayout init: %r seconds', e - s)
        return

    def createConnections(self):
        # Signal/Slot Connections are always lazily evaluated, and can
        # only be triggered once (unique connection).
        ct = QtCore.Qt.UniqueConnection

        # Populate the UI with data.
        self.collection_widget.nameChanged.connect(self.updateDynamicWindowTitle, ct)
        self.collection_widget.itemChanged.connect(self.updateDynamicWindowTitle, ct)
        self.collection_widget.itemChanged.connect(self.object_browser.updateModel, ct)
        self.collection_widget.itemChanged.connect(self.object_browser.updateInfo, ct)
        self.collection_widget.itemChanged.connect(
            self.object_browser.updateToggleButtons, ct
        )
        self.collection_widget.itemChanged.connect(
            self.object_browser.updateColumnVisibility, ct
        )
        self.collection_widget.itemChanged.connect(
            self.attribute_browser.updateModel, ct
        )
        self.collection_widget.itemChanged.connect(
            self.attribute_browser.updateInfo, ct
        )
        self.collection_widget.itemChanged.connect(
            self.attribute_browser.updateToggleButtons, ct
        )
        self.collection_widget.itemChanged.connect(
            self.attribute_browser.updateColumnVisibility, ct
        )
        self.collection_widget.itemChanged.connect(self.solver_settings.updateModel, ct)
        self.collection_widget.itemChanged.connect(self.solver_state.updateModel, ct)

        self.object_browser.dataChanged.connect(self.object_browser.updateModel, ct)
        self.object_browser.dataChanged.connect(self.object_browser.updateInfo, ct)
        self.object_browser.viewUpdated.connect(
            self.object_browser.updateToggleButtons, ct
        )
        self.object_browser.viewUpdated.connect(
            self.object_browser.updateColumnVisibility, ct
        )

        self.attribute_browser.dataChanged.connect(
            self.attribute_browser.updateModel, ct
        )
        self.attribute_browser.dataChanged.connect(
            self.attribute_browser.updateInfo, ct
        )
        self.attribute_browser.viewUpdated.connect(
            self.attribute_browser.updateToggleButtons, ct
        )
        self.attribute_browser.viewUpdated.connect(
            self.attribute_browser.updateColumnVisibility, ct
        )

        self.solver_settings.tabChanged.connect(self.solver_settings.updateModel, ct)
        self.solver_settings.sendWarning.connect(self.setStatusLine, ct)
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
        project_version = mmSolver_const.PROJECT_VERSION
        title = title.format(version=project_version, collection=node)
        self._parentObject.window().setWindowTitle(title)
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
