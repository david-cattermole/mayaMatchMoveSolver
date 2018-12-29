"""
The Solver layout, the contents of the main solver window.
"""

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.tools.solver.lib.attr as lib_attr
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.uiquery as lib_uiquery
import mmSolver.tools.solver.lib.marker as lib_marker
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes
import mmSolver.tools.solver.ui.ui_solver_layout as ui_solver_layout
import mmSolver.tools.solver.ui.convert_to_ui as convert_to_ui
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class SolverLayout(QtWidgets.QWidget, ui_solver_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Store the parent window class, so we can set the applyBtn enabled
        # state.
        self._parentClass = parent

        # Collection Combo Box.
        self.collectionName_model = uimodels.StringDataListModel()
        self.collectionName_comboBox.setModel(self.collectionName_model)
        self.collectionName_comboBox.currentIndexChanged.connect(self.collectionIndexChanged)

        # Collection Select
        self.collectionSelect_pushButton.clicked.connect(self.collectionSelectClicked)

        # Object Nodes
        # TODO: Perhaps we should remove a tree view and research how
        # we can embed a Maya Outliner inside our layout with a filter
        # to only show markers (and their parents), this would provide
        # a lot of default functionality from Maya.
        root = object_nodes.ObjectNode('root')
        self.object_model = object_nodes.ObjectModel(root, font=self.font)
        self.object_filterModel = QtCore.QSortFilterProxyModel()
        self.object_filterModel.setSourceModel(self.object_model)
        self.object_filterModel.setDynamicSortFilter(False)
        self.object_treeView.setModel(self.object_filterModel)
        self.object_treeView.setSortingEnabled(True)
        self.object_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.object_treeView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.object_selModel = self.object_treeView.selectionModel()
        self.object_selModel.currentChanged.connect(self.objectNodeCurrentChanged)

        # Object Add and Remove buttons
        self.objectAdd_toolButton.clicked.connect(self.objectAddClicked)
        self.objectRemove_toolButton.clicked.connect(self.objectRemoveClicked)

        # Attr Nodes
        root = attr_nodes.PlugNode('root')
        self.attribute_model = attr_nodes.AttrModel(root, font=self.font)
        self.attribute_filterModel = QtCore.QSortFilterProxyModel()
        self.attribute_filterModel.setSourceModel(self.attribute_model)
        self.attribute_filterModel.setDynamicSortFilter(False)
        self.attribute_treeView.setModel(self.attribute_filterModel)
        self.attribute_treeView.setSortingEnabled(True)
        self.attribute_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.attribute_treeView.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.attribute_selModel = self.attribute_treeView.selectionModel()
        self.attribute_selModel.currentChanged.connect(self.attrNodeCurrentChanged)

        # Attr Add and Remove buttons
        self.attributeAdd_toolButton.clicked.connect(self.attrAddClicked)
        self.attributeRemove_toolButton.clicked.connect(self.attrRemoveClicked)

        # Solver Nodes
        self.solver_model = solver_nodes.SolverModel(font=self.font)
        self.solver_filterModel = QtCore.QSortFilterProxyModel()
        self.solver_filterModel.setSourceModel(self.solver_model)
        self.solver_filterModel.setDynamicSortFilter(False)
        self.solver_tableView.setModel(self.solver_filterModel)
        self.solver_tableView.setSortingEnabled(False)
        self.solver_selModel = self.solver_tableView.selectionModel()

        # Set up custom widgets for viewing and editing the columns.
        self.solver_attrFilterDelegate = solver_nodes.AttributeComboBoxDelegate()
        self.solver_tableView.setItemDelegateForColumn(
            2,
            self.solver_attrFilterDelegate,
        )
        self.solver_strategyDelegate = solver_nodes.StrategyComboBoxDelegate()
        self.solver_tableView.setItemDelegateForColumn(
            3,
            self.solver_strategyDelegate,
        )

        # Solver Add and Remove buttons
        self.solverAdd_toolButton.clicked.connect(
            self.solverAddClicked
        )
        self.solverRemove_toolButton.clicked.connect(
            self.solverRemoveClicked
        )
        self.solverMoveUp_toolButton.clicked.connect(
            self.solverMoveUpClicked
        )
        self.solverMoveDown_toolButton.clicked.connect(
            self.solverMoveDownClicked
        )

        # Override Current Frame
        self.overrideCurrentFrame_checkBox.stateChanged.connect(
            self.overrideCurrentFrameChanged
        )

        # Populate the UI with data.
        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()
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
        self._parentClass.window().setWindowTitle(title)

    def updateCollectionModel(self):
        self.setStatusLine(const.STATUS_REFRESHING)
        col = lib_state.get_active_collection()
        self.populateCollectionModel(self.collectionName_model)
        index = self.getDefaultCollectionIndex(self.collectionName_model, col)
        self.collectionName_comboBox.setCurrentIndex(index)
        self.updateDynamicWindowTitle()
        return

    def updateObjectModel(self):
        self.setStatusLine(const.STATUS_REFRESHING)
        self.populateObjectModel(self.object_model)
        self.object_treeView.expandAll()
        return

    def updateAttributeModel(self):
        self.setStatusLine(const.STATUS_REFRESHING)
        self.populateAttributeModel(self.attribute_model)
        self.attribute_treeView.expandAll()
        return

    def updateSolverModel(self):
        self.setStatusLine(const.STATUS_REFRESHING)
        self.populateSolverModel(self.solver_model)
        return

    def updateSolveValidState(self):
        self.setStatusLine(const.STATUS_COMPILING)
        v = True
        col = lib_state.get_active_collection()
        if col is None:
            v = False
        else:
            v = lib_col.compile_collection(col)
        assert isinstance(v, bool) is True
        if self._parentClass is not None:
            self._parentClass.applyBtn.setEnabled(v)
        return

    def populateCollectionModel(self, model):
        cols = lib_col.get_collections()
        string_data_list = []
        for col in cols:
            node = col.get_node()
            string_data_list.append((node, col))
        model.setStringDataList(string_data_list)
        return

    def populateObjectModel(self, model):
        col = lib_state.get_active_collection()
        if col is None:
            return
        mkr_list = lib_marker.get_markers_from_collection(col)
        root = convert_to_ui.markersToUINodes(mkr_list)
        model.setRootNode(root)
        return

    def populateAttributeModel(self, model):
        col = lib_state.get_active_collection()
        if col is None:
            return
        attr_list = lib_attr.get_attributes_from_collection(col)
        root = convert_to_ui.attributesToUINodes(attr_list)
        model.setRootNode(root)
        return

    def populateSolverModel(self, model):
        col = lib_state.get_active_collection()
        if col is None:
            return
        step_list = lib_col.get_solver_steps_from_collection(col)
        node_list = convert_to_ui.solverStepsToUINodes(step_list, col)
        self.solver_model.setNodeList(node_list)
        return

    def setStatusLine(self, text):
        self.statusLine_label.setText(text)
        return

    def getDefaultCollectionIndex(self, model, col):
        """
        Get the index for the 'currently selected' collection.
        """
        if col is None:
            return 0
        active_node = col.get_node()
        if active_node is None:
            return 0
        string_data_list = model.stringDataList()
        for i, (string, data) in enumerate(string_data_list):
            find = string.find(active_node)
            if find != -1:
                return i
        return 0

    def createNewCollectionNode(self):
        LOG.debug('createNewCollectionNode')
        col = lib_col.create_collection()
        lib_state.set_active_collection(col)

        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()

        self.setStatusLine(const.STATUS_READY)
        return

    def renameCollectionNode(self):
        LOG.debug('renameCollectionNode')
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

        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()

        self.setStatusLine(const.STATUS_READY)
        return

    def removeCollectionNode(self):
        LOG.debug('removeCollectionNode')
        col = lib_state.get_active_collection()
        if col is not None:
            # FIXME: Solver Steps continue to hold a reference to the
            # Collection after the collection node is deleted.
            steps = lib_col.get_solver_steps_from_collection(col)
            for step in steps:
                lib_col.remove_solver_step_from_collection(col, step)
            lib_col.delete_collection(col)
            lib_state.set_active_collection(None)
        else:
            LOG.warning('No active collection to delete.')
            return

        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()

        self.setStatusLine(const.STATUS_READY)
        return

    def collectionSelectClicked(self):
        LOG.debug('collectionSelectClicked')
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to select.')
            return
        lib_col.select_collection(col)
        self.updateDynamicWindowTitle()
        self.setStatusLine(const.STATUS_READY)
        return

    def objectAddClicked(self):
        LOG.debug('objectAddClicked')
        mkr_list = lib_maya_utils.get_markers_from_selection()
        if len(mkr_list) == 0:
            msg = 'Please select objects, found no markers.'
            LOG.warning(msg)
            return
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add markers, active collection is not defined.'
            LOG.warning(msg)
            return
        lib_marker.add_markers_to_collection(mkr_list, col)
        self.updateObjectModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def objectRemoveClicked(self):
        LOG.debug('objectRemoveClicked')
        col = lib_state.get_active_collection()
        if col is None:
            return
        ui_nodes = lib_uiquery.get_selected_ui_nodes(
            self.object_treeView,
            self.object_filterModel
        )
        nodes = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'marker')
        lib_marker.remove_markers_from_collection(nodes, col)
        self.updateObjectModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def attrAddClicked(self):
        LOG.debug('attrAddClicked')
        attr_list = lib_maya_utils.get_selected_maya_attributes()
        if len(attr_list) == 0:
            msg = 'Please select attributes in the channel box, none where found.'
            LOG.warning(msg)
            return
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add attributes, active collection is not defined.'
            LOG.warning(msg)
            return
        lib_attr.add_attributes_to_collection(attr_list, col)
        self.updateAttributeModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def attrRemoveClicked(self):
        LOG.debug('attrRemoveClicked')
        col = lib_state.get_active_collection()
        if col is None:
            return
        ui_nodes = lib_uiquery.get_selected_ui_nodes(
            self.attribute_treeView,
            self.attribute_filterModel
        )
        nodes = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'data')
        lib_attr.remove_attr_from_collection(nodes, col)
        self.updateAttributeModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def solverAddClicked(self):
        LOG.debug('solverAddClicked')
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add Solver Step, active collection is invalid,'
            LOG.warning(msg)
            return
        step = lib_col.create_solver_step()
        lib_col.add_solver_step_to_collection(col, step)
        self.updateSolverModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def solverRemoveClicked(self):
        LOG.debug('solverRemoveClicked')
        ui_nodes = lib_uiquery.get_selected_ui_table_row(
            self.solver_tableView,
            self.solver_model,
            self.solver_filterModel
        )
        names = map(lambda x: x.name(), ui_nodes)
        col_nodes = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'collection_node')
        assert len(names) == len(col_nodes)
        for name, col in zip(names, col_nodes):
            step = lib_col.get_named_solver_step_from_collection(col, name)
            lib_col.remove_solver_step_from_collection(col, step)
        self.updateSolverModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return

    def solverMoveUpClicked(self):
        LOG.debug('solverMoveUpClicked')
        # TODO: Write this.
        #  1 - get all UI nodes
        #  2 - get selected UI node.
        #  3 - get index of selected UI node
        #  4 - move it up by one
        raise NotImplementedError
        return

    def solverMoveDownClicked(self):
        LOG.debug('solverMoveDownClicked')
        # TODO: Write this.
        raise NotImplementedError
        return

    @QtCore.Slot(int)
    def collectionIndexChanged(self, index):
        if index < 0:
            return
        model_index = self.collectionName_model.index(index, 0)
        data = self.collectionName_model.data(
            model_index,
            role=QtCore.Qt.UserRole
        )
        if data is None:
            return
        lib_state.set_active_collection(data)

        self.updateDynamicWindowTitle()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()

        self.setStatusLine(const.STATUS_READY)
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def objectNodeCurrentChanged(self, index, prevIndex):
        """
        Look up the Maya node from the data at index, then add it to the
        selection.
        """
        # TODO: Based on the Maya selection key modifiers, we should
        # add to the current selection, or toggle, as needed.
        # TODO: When an object node tree item is selected, the attr nodes tree
        # view must all be deselected.
        ui_node = lib_uiquery.get_ui_node_from_index(
            index,
            self.object_filterModel
        )
        if ui_node is None:
            return
        # Type info will be 'marker', 'bundle' or 'camera' based on the selected node type.
        typeInfo = ui_node.typeInfo
        nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], typeInfo)
        maya_nodes = []
        if typeInfo == 'camera':
            maya_nodes = map(lambda x: x.get_shape_node(), nodes)
        else:
            # For bundles and markers
            maya_nodes = map(lambda x: x.get_node(), nodes)
        lib_maya_utils.set_scene_selection(maya_nodes)
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def attrNodeCurrentChanged(self, index, prevIndex):
        ui_node = lib_uiquery.get_ui_node_from_index(
            index,
            self.attribute_filterModel
        )
        if ui_node is None:
            return
        nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], 'data')
        maya_nodes = map(lambda x: x.get_node(), nodes)
        lib_maya_utils.set_scene_selection(maya_nodes)
        return

    @QtCore.Slot(int)
    def overrideCurrentFrameChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection, cannot override Solver Step.')
            return
        # 'value' from Qt is expected to be an int, we expect a bool.
        value = bool(value)
        lib_col.set_override_current_frame_on_collection(col, value)
        self.updateSolverModel()
        self.updateSolveValidState()
        self.setStatusLine(const.STATUS_READY)
        return
