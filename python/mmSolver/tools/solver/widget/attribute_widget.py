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

import time

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


def _convertNodeListToAttrList(node_list):
    """
    Convert a list of MayaNode or AttrNode objects to a flat list of
    Attribute objects.

    :param node_list:
        A list of PlugNode derived objects, either MayaNode or
        AttrNode types.
    :type node_list: [PlugNode, ..]

    :return: List of Attribute objects.
    :rtype: [Attribute, ..]
    """
    attr_list = []
    for node in node_list:
        if isinstance(node, list):
            attr_list += [n for n in node]
        else:
            attr_list += [node]
    return attr_list


def _lookupMayaNodesFromAttrUINodes(indexes, model):
    maya_nodes = []
    for idx in indexes:
        ui_node = lib_uiquery.get_ui_node_from_index(idx, model)
        if ui_node is None:
            continue
        # For both AttrNode and MayaNodes we ensure we only add a new
        # Maya node if the existing node name is not in the
        # accumulated list. We do not remove the order of the nodes
        # only ensure that no duplicates are added.
        if isinstance(ui_node, attr_nodes.AttrNode):
            nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], 'data')
            node_names = [x.get_node() for x in nodes]
            maya_nodes += [x for x in node_names
                           if x not in maya_nodes]
        elif isinstance(ui_node, attr_nodes.MayaNode):
            node_uuid = ui_node.data().get('uuid')
            node_names = lib_maya_utils.get_node_names_from_uuids([node_uuid])
            maya_nodes += [x for x in node_names
                           if x not in maya_nodes]
        else:
            LOG.error("Invalid node type: %r", ui_node)
    return maya_nodes


class AttributeBrowserWidget(nodebrowser_widget.NodeBrowserWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeBrowserWidget, self).__init__(*args, **kwargs)

        self.ui.title_label.setText('Output Attributes')

        self.createToolButtons()
        self.createTreeView()

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

    def populateModel(self, model, col):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
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
            col,
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
        show_stiffness = lib_state.get_display_attribute_stiffness_state()
        show_smoothness = lib_state.get_display_attribute_smoothness_state()
        self.displayStateColumnChanged(show_state)
        self.displayMinMaxColumnChanged(show_min_max)
        self.displayStiffnessColumnChanged(show_stiffness)
        self.displaySmoothnessColumnChanged(show_smoothness)
        return

    def updateModel(self):
        is_running = mmapi.is_solver_running()
        if is_running is True:
            return

        col = lib_state.get_active_collection()
        if col is None:
            return

        widgets = [self]
        nodebrowser_utils._populateWidgetsEnabled(col, widgets)
        self.populateModel(self.model, col)
        nodebrowser_utils._expand_node(
            self.treeView,
            self.treeView.model(),
            self.treeView.rootIndex(),
            expand=True,
            recurse=False)

        block = self.blockSignals(True)
        self.dataChanged.emit()
        self.blockSignals(block)
        return

    def addClicked(self):
        """
        Add the selected nodes or node attributes to the data model.
        """
        s = time.time()
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add attributes, active collection is not defined.'
            LOG.warning(msg)
            return
        e = time.time()
        LOG.debug("attribute addClicked1: t=%s", e - s)

        s = time.time()
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
        e = time.time()
        LOG.debug("attribute addClicked2: t=%s", e - s)

        s = time.time()
        try:
            mmapi.set_solver_running(True)  # disable selection callback.
            lib_attr.add_attributes_to_collection(attr_list, col)
        finally:
            mmapi.set_solver_running(False)  # enable selection callback
        e = time.time()
        LOG.debug("attribute addClicked3: t=%s", e - s)

        def update_func():
            if uiutils.isValidQtObject(self) is False:
                return
            self.dataChanged.emit()
            self.viewUpdated.emit()
            return

        # Add Callbacks
        s = time.time()
        callback_manager = self.callback_manager
        if callback_manager is not None:
            lib_attr.add_callbacks_to_attributes(
                attr_list,
                update_func,
                callback_manager,
            )
        e = time.time()
        LOG.debug("attribute addClicked4: t=%s", e - s)

        s = time.time()
        update_func()
        e = time.time()
        LOG.debug("attribute addClicked5: t=%s", e - s)

        # Restore selection.
        s = time.time()
        lib_maya_utils.set_scene_selection(sel)
        e = time.time()
        LOG.debug("attribute addClicked6: t=%s", e - s)
        return

    def removeClicked(self):
        """
        Remove the selected nodes or node attributes from the output
        attributes data model.
        """
        try:
            mmapi.set_solver_running(True)  # disable selection callback.

            s = time.time()
            col = lib_state.get_active_collection()
            if col is None:
                return
            e = time.time()
            LOG.debug("attribute removeClicked1: t=%s", e - s)

            s = time.time()
            sel = lib_maya_utils.get_scene_selection()
            ui_nodes = lib_uiquery.get_selected_ui_nodes(
                self.treeView,
                self.filterModel
            )
            node_list = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'data')
            e = time.time()
            LOG.debug("attribute removeClicked2: t=%s", e - s)

            s = time.time()
            attr_list = _convertNodeListToAttrList(node_list)
            lib_attr.remove_attr_from_collection(attr_list, col)

            e = time.time()
            LOG.debug("attribute removeClicked3: t=%s", e - s)

            # Remove Callbacks
            s = time.time()
            callback_manager = self.callback_manager
            if callback_manager is not None:
                lib_attr.remove_callbacks_from_attributes(
                    attr_list,
                    callback_manager
                )
            e = time.time()
            LOG.debug("attribute removeClicked4: t=%s", e - s)
        finally:
            mmapi.set_solver_running(False)  # enable selection callback

        s = time.time()
        self.dataChanged.emit()
        self.viewUpdated.emit()
        e = time.time()
        LOG.debug("attribute removeClicked5: t=%s", e - s)

        # Restore selection.
        s = time.time()
        lib_maya_utils.set_scene_selection(sel)
        e = time.time()
        LOG.debug("attribute removeClicked5: t=%s", e - s)
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
        selected_indexes = self.selModel.selectedRows()
        select_nodes = _lookupMayaNodesFromAttrUINodes(
            select_indexes,
            self.filterModel)
        deselect_nodes = _lookupMayaNodesFromAttrUINodes(
            deselect_indexes,
            self.filterModel)
        selected_nodes = _lookupMayaNodesFromAttrUINodes(
            selected_indexes,
            self.filterModel)
        if self.isActiveWindow() is True:
            # Only allow Maya selection changes when the user has the
            # UI focused. This breaks the Maya and Qt selection
            # callback cycle.

            # Because an attribute and node may refer to the same
            # underlying node name, we must be sure we don't deselect a
            # node that has other attributes selected.
            deselect_nodes = list(set(deselect_nodes) - set(selected_nodes))
            try:
                mmapi.set_solver_running(True)  # disable selection callback.
                lib_maya_utils.add_scene_selection(select_nodes)
                lib_maya_utils.remove_scene_selection(deselect_nodes)
            finally:
                mmapi.set_solver_running(False)  # enable selection callback
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
        idx_min_max = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_VALUE_MIN_MAX
        )
        self.treeView.setColumnHidden(idx_min_max, not value)
        return

    @QtCore.Slot(bool)
    def displayStiffnessColumnChanged(self, value):
        lib_state.set_display_attribute_stiffness_state(value)
        idx_stiff = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_VALUE_STIFFNESS
        )
        self.treeView.setColumnHidden(idx_stiff, not value)
        return

    @QtCore.Slot(bool)
    def displaySmoothnessColumnChanged(self, value):
        lib_state.set_display_attribute_smoothness_state(value)
        idx_smooth = self.model.getColumnIndexFromColumnName(
            const.ATTR_COLUMN_NAME_VALUE_SMOOTHNESS
        )
        self.treeView.setColumnHidden(idx_smooth, not value)
        return
