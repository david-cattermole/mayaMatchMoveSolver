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
Attribute Browser.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.api as mmapi
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.lib.attr as lib_attr
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.convert_to_ui as convert_to_ui
import mmSolver.tools.solver.widget.nodebrowser_widget as nodebrowser_widget
import mmSolver.tools.solver.widget.nodebrowser_utils as nodebrowser_utils
import mmSolver.tools.solver.widget.attribute_treeview as attr_treeview
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


def _lookupMayaNodesFromAttrUINodes(indexes, model):
    maya_nodes = []
    for idx in indexes:
        ui_node = lib_uiquery.get_ui_node_from_index(idx, model)
        if ui_node is None:
            continue
        if isinstance(ui_node, attr_nodes.AttrNode):
            nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], 'data')
            maya_nodes += [x.get_node() for x in nodes]
        elif isinstance(ui_node, attr_nodes.MayaNode):
            node_uuid = ui_node.data().get('uuid')
            node_names = lib_maya_utils.get_node_names_from_uuids([node_uuid])
            maya_nodes += node_names
        else:
            LOG.error("Invalid node type: %r", ui_node)
    return maya_nodes


class AttributeBrowserWidget(nodebrowser_widget.NodeBrowserWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeBrowserWidget, self).__init__(*args, **kwargs)

        self.ui.title_label.setText('Output Attributes')

        self.createToolButtons()
        self.createTreeView()

        self.dataChanged.connect(self.updateModel)

        self.callback_manager = maya_callbacks.CallbackManager()
        return

    def __del__(self):
        """
        Release all resources held by the class.
        """
        del self.callback_manager

    def createToolButtons(self):
        """
        Create the 'toggle' buttons for the Attribute browser.
        """
        self.toggleAnimated_toolButton = QtWidgets.QToolButton(self)
        self.toggleAnimated_toolButton.setText('ANM')
        self.toggleAnimated_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleAnimated_toolButton)

        self.toggleStatic_toolButton = QtWidgets.QToolButton(self)
        self.toggleStatic_toolButton.setText('STC')
        self.toggleStatic_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleStatic_toolButton)

        self.toggleLocked_toolButton = QtWidgets.QToolButton(self)
        self.toggleLocked_toolButton.setText('LCK')
        self.toggleLocked_toolButton.setCheckable(True)
        self.ui.toggleButtons_layout.addWidget(self.toggleLocked_toolButton)

        self.toggleAnimated_toolButton.clicked.connect(self.toggleAnimatedClicked)
        self.toggleStatic_toolButton.clicked.connect(self.toggleStaticClicked)
        self.toggleLocked_toolButton.clicked.connect(self.toggleLockedClicked)
        return

    def createTreeView(self):
        """
        Set up the tree view.
        """
        self.treeView = attr_treeview.AttributeTreeView()
        self.ui.treeViewLayout.addWidget(self.treeView)

        root = attr_nodes.PlugNode('root')
        self.model = attr_nodes.AttrModel(root, font=self.font)
        self.filterModel = QtCore.QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.model)
        self.filterModel.setDynamicSortFilter(False)
        self.header = QtWidgets.QHeaderView(
            QtCore.Qt.Horizontal,
            parent=self.treeView
        )
        Qt.QtCompat.QHeaderView.setSectionResizeMode(
            self.header, QtWidgets.QHeaderView.ResizeToContents
        )
        self.treeView.setHeader(self.header)

        self.treeView.setModel(self.filterModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.selModel = self.treeView.selectionModel()
        self.selModel.selectionChanged.connect(self.selectionChanged)

        # Always hide the UUID Column - it's used for selection of
        # ModelIndexes with Maya node UUIDs only.
        hidden = True
        column = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_UUID
        )
        self.treeView.setColumnHidden(column, hidden)
        return

    def populateModel(self, model):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        col = lib_state.get_active_collection()
        attr_list = []
        show_anm = const.ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE
        show_stc = const.ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE
        show_lck = const.ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE
        if col is not None:
            attr_list = lib_attr.get_attributes_from_collection(col)
            show_anm = lib_col.get_attribute_toggle_animated_from_collection(col)
            show_stc = lib_col.get_attribute_toggle_static_from_collection(col)
            show_lck = lib_col.get_attribute_toggle_locked_from_collection(col)

        def update_func():
            if uiutils.isValidQtObject(self) is False:
                return
            self.dataChanged.emit()
            return

        # Add Callbacks
        #
        # When querying attributes, we must make sure they have a Maya
        # callback attached to the node to update the UI.
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_attr.add_callbacks_to_attributes(
                attr_list,
                update_func,
                callback_manager
            )
        root = convert_to_ui.attributesToUINodes(
            attr_list,
            show_anm,
            show_stc,
            show_lck)
        model.setRootNode(root)
        return

    def updateInfo(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        anm_list = []
        stc_list = []
        lck_list = []

        text = 'Animated {anm} | Static {stc} | Locked {lck}'

        col = lib_state.get_active_collection()
        if col is not None:
            attr_list = col.get_attribute_list()
            anm_list = [True for attr in attr_list if attr.is_animated()]
            stc_list = [True for attr in attr_list if attr.is_static()]
            lck_list = [True for attr in attr_list if attr.is_locked()]

        text = text.format(anm=len(anm_list),
                           stc=len(stc_list),
                           lck=len(lck_list))
        self.ui.info_label.setText(text)
        return

    def updateToggleButtons(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        col = lib_state.get_active_collection()
        if col is None:
            return
        show_anm = lib_col.get_attribute_toggle_animated_from_collection(col)
        show_stc = lib_col.get_attribute_toggle_static_from_collection(col)
        show_lck = lib_col.get_attribute_toggle_locked_from_collection(col)
        self.toggleAnimated_toolButton.setChecked(show_anm)
        self.toggleStatic_toolButton.setChecked(show_stc)
        self.toggleLocked_toolButton.setChecked(show_lck)
        return

    def updateColumnVisibility(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        show_state = lib_state.get_display_attribute_state_state()
        show_min_max = lib_state.get_display_attribute_min_max_state()
        self.displayStateColumnChanged(show_state)
        self.displayMinMaxColumnChanged(show_min_max)
        return

    def updateModel(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return
        self.populateModel(self.model)
        valid = uiutils.isValidQtObject(self.treeView)
        if valid is False:
            return
        self.treeView.expandAll()

        widgets = [self]
        _populateWidgetsEnabled(widgets)

        block = self.blockSignals(True)
        self.dataChanged.emit()
        self.blockSignals(block)
        return

    def addClicked(self):
        """
        Add the selected nodes or node attributes to the data model.

        .. todo:: This function is very slow to run when many (20+)
           bundles are being added to the list attributes.
        """
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add attributes, active collection is not defined.'
            LOG.warning(msg)
            return

        sel = lib_maya_utils.get_scene_selection()
        attr_list = lib_maya_utils.get_selected_maya_attributes()
        attr_list = lib_maya_utils.input_attributes_filter(attr_list)
        if len(attr_list) == 0:
            attr_list = lib_maya_utils.get_selected_node_default_attributes()
            attr_list = lib_maya_utils.input_attributes_filter(attr_list)
        if len(attr_list) == 0:
            msg = 'Please select nodes or attributes in the channel box.'
            LOG.warning(msg)
            return

        lib_attr.add_attributes_to_collection(attr_list, col)

        def update_func():
            if uiutils.isValidQtObject(self) is False:
                return
            self.dataChanged.emit()
            self.viewUpdated.emit()
            return

        # Add Callbacks
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_attr.add_callbacks_to_attributes(
                attr_list,
                update_func,
                callback_manager,
            )

        update_func()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def removeClicked(self):
        """
        Remove the selected nodes or node attributes from the output
        attributes data model.
        """
        col = lib_state.get_active_collection()
        if col is None:
            return

        sel = lib_maya_utils.get_scene_selection()
        ui_nodes = lib_uiquery.get_selected_ui_nodes(
            self.treeView,
            self.filterModel
        )
        attr_list = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'data')
        lib_attr.remove_attr_from_collection(attr_list, col)

        # Remove Callbacks
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_attr.remove_callbacks_from_attributes(
                attr_list,
                callback_manager
            )

        self.dataChanged.emit()
        self.viewUpdated.emit()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def toggleAnimatedClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_animated_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_animated_on_collection(col, value)
        self.dataChanged.emit()
        return

    def toggleStaticClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_static_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_static_on_collection(col, value)
        self.dataChanged.emit()
        return

    def toggleLockedClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_locked_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_locked_on_collection(col, value)
        self.dataChanged.emit()
        return

    @QtCore.Slot(list)
    def setNodeSelection(self, values):
        """
        Override the tree view selection based on Maya Node UUIDs.
        """
        nodebrowser_utils.setNodeSelectionWithUUID(
            self.treeView,
            self.model,
            self.filterModel,
            self.selModel,
            const.ATTR_COLUMN_NAME_UUID,
            values,
        )
        return

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def selectionChanged(self, selected, deselected):
        select_indexes = [idx for idx in selected.indexes()]
        deselect_indexes = [idx for idx in deselected.indexes()]
        select_nodes = _lookupMayaNodesFromAttrUINodes(
            select_indexes,
            self.filterModel)
        deselect_nodes = _lookupMayaNodesFromAttrUINodes(
            deselect_indexes,
            self.filterModel)
        try:
            mmapi.set_solver_running(True) # disable selection callback.
            lib_maya_utils.add_scene_selection(select_nodes)
            lib_maya_utils.remove_scene_selection(deselect_nodes)
        finally:
            mmapi.set_solver_running(False) # enable selection callback
        return

    @QtCore.Slot(bool)
    def displayStateColumnChanged(self, value):
        lib_state.set_display_attribute_state_state(value)
        idx = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_STATE
        )
        self.treeView.setColumnHidden(idx, not value)
        return

    @QtCore.Slot(bool)
    def displayMinMaxColumnChanged(self, value):
        lib_state.set_display_attribute_min_max_state(value)
        idx_min = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_VALUE_MIN
        )
        idx_max = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_VALUE_MAX
        )
        self.treeView.setColumnHidden(idx_min, not value)
        self.treeView.setColumnHidden(idx_max, not value)
        return
