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

"""

import time

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.widget.ui_collection_widget as ui_collection_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class CollectionWidget(QtWidgets.QWidget, ui_collection_widget.Ui_Form):

    # Signals; events that may 'happen' to this widget.
    itemAdded = QtCore.Signal()
    itemRemoved = QtCore.Signal()
    itemChanged = QtCore.Signal()
    nameChanged = QtCore.Signal()
    selectClicked = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(CollectionWidget, self).__init__(parent, *args, **kwargs)
        self.setupUi(self)

        # Collection Combo Box.
        self.model = uimodels.StringDataListModel()
        self.name_comboBox.setModel(self.model)
        self.name_comboBox.currentIndexChanged.connect(self.indexChanged)

        # Collection Select
        self.select_pushButton.clicked.connect(self.selectClickedButton)

        self.itemChanged.connect(self.updateModel)
        e = time.time()
        LOG.debug('CollectionWidget init: %r seconds', e - s)
        return

    def populateModel(self, model):
        """
        Set the model based on the current Maya scene state.
        """
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        cols = lib_col.get_collections()
        string_data_list = []
        for col in cols:
            node = col.get_node()
            string_data_list.append((node, col))
        model.setStringDataList(string_data_list)
        return

    def updateModel(self):
        """
        Refresh the name_comboBox with the current Maya scene state.
        """
        self.populateModel(self.model)

        index = None
        col = lib_state.get_active_collection()
        if col is None:
            cols = lib_col.get_collections()
            if len(cols) > 0:
                # If there is no active collection, but there are
                # collections already created, we make sure the first
                # collection is marked active.
                col = cols[0]
                lib_state.set_active_collection(col)
        else:
            index = self.getActiveIndex(self.model, col)

        block = self.blockSignals(True)
        if index is not None:
            self.name_comboBox.setCurrentIndex(index)
        self.nameChanged.emit()
        self.blockSignals(block)
        return

    def getActiveIndex(self, model, col):
        """
        Get the index for the 'currently selected' collection.
        """
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        if col is None:
            return None
        active_node = col.get_node()
        if active_node is None:
            return None
        string_data_list = model.stringDataList()
        string_list = [string for string, data in string_data_list]
        index = None
        if active_node in string_list:
            index = string_list.index(active_node)
        return index

    def createNewNode(self):
        """
        Create a new Collection node, and set it active.
        """
        col = lib_col.create_collection()
        lib_state.set_active_collection(col)

        self.itemAdded.emit()
        self.itemChanged.emit()
        self.nameChanged.emit()
        return

    def renameActiveNode(self):
        """
        Dialog prompt the user to rename the currently active node.
        """
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to rename. Skipping rename.')
            return
        node_name = col.get_node()
        title = 'Rename Collection node'
        msg = 'Enter new node name'
        new_name = lib_maya_utils.prompt_for_new_node_name(title, msg, node_name)
        if new_name is not None:
            lib_col.rename_collection(col, new_name)

        self.itemChanged.emit()
        self.nameChanged.emit()
        return

    def removeActiveNode(self):
        """
        Delete the currently active collection.
        """
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to delete.')
            return
        title = 'Remove Collection?'
        text = 'Would you like to remove the current Collection?'
        text += '\n\nRemove "' + str(col.get_node()) + '"?'
        clicked_button = QtWidgets.QMessageBox.question(self, title, text)
        if clicked_button != QtWidgets.QMessageBox.Yes:
            LOG.warn('User cancelled operation.')
            return

        cols = lib_col.get_collections()
        prev_col = lib_col.get_previous_collection(cols, col)

        steps = lib_col.get_solver_steps_from_collection(col)
        for step in steps:
            lib_col.remove_solver_step_from_collection(col, step)

        lib_col.delete_collection(col)
        lib_state.set_active_collection(prev_col)

        self.itemRemoved.emit()
        self.itemChanged.emit()
        self.nameChanged.emit()
        return

    def selectClickedButton(self):
        """
        Run when the user presses the 'select' button.
        """
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to select.')
            return
        lib_col.select_collection(col)
        self.nameChanged.emit()
        return

    @QtCore.Slot(int)
    def indexChanged(self, index):
        """
        Run when the name_comboBox index is changed.
        """
        if index < 0:
            return
        model_index = self.model.index(index, 0)
        data = self.model.data(
            model_index,
            role=QtCore.Qt.UserRole
        )
        if data is None:
            return
        lib_state.set_active_collection(data)
        self.itemChanged.emit()
        self.nameChanged.emit()
        return
