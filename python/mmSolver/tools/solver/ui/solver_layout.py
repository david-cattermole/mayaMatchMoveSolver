"""
The Solver layout, the contents of the main solver window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.uiutils as uiutils
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
        self._parentObject = parent

        # Hide the Solve Info line until it's set up. GitHub Issue #56
        self.solveInfoLine_lineEdit.setVisible(False)

        # Collection Combo Box.
        self.collectionName_model = uimodels.StringDataListModel()
        self.collectionName_comboBox.setModel(self.collectionName_model)
        self.collectionName_comboBox.currentIndexChanged.connect(
            self.collectionIndexChanged
        )

        # Collection Select
        self.collectionSelect_pushButton.clicked.connect(
            self.collectionSelectClicked
        )

        # Object Nodes
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
        self.object_selModel.selectionChanged.connect(
            self.objectNodeSelectionChanged
        )
        self.objectToggleCamera_toolButton.clicked.connect(
            self.objectToggleCameraClicked,
        )
        self.objectToggleMarker_toolButton.clicked.connect(
            self.objectToggleMarkerClicked,
        )
        self.objectToggleBundle_toolButton.clicked.connect(
            self.objectToggleBundleClicked,
        )

        # Object Add and Remove buttons
        self.objectAdd_toolButton.clicked.connect(
            self.objectAddClicked
        )
        self.objectRemove_toolButton.clicked.connect(
            self.objectRemoveClicked
        )

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
        self.attribute_selModel.selectionChanged.connect(
            self.attrNodeSelectionChanged
        )
        self.attributeToggleAnimated_toolButton.clicked.connect(
            self.attributeToggleAnimatedClicked,
        )
        self.attributeToggleStatic_toolButton.clicked.connect(
            self.attributeToggleStaticClicked,
        )
        self.attributeToggleLocked_toolButton.clicked.connect(
            self.attributeToggleLockedClicked,
        )

        # Attr Add and Remove buttons
        self.attributeAdd_toolButton.clicked.connect(
            self.attrAddClicked
        )
        self.attributeRemove_toolButton.clicked.connect(
            self.attrRemoveClicked
        )

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

        # TODO: Write functions for Move Up/Down buttons. Until then,
        #       we'll hide the buttons to avoid confusion.
        self.solverMoveUp_toolButton.setVisible(False)
        self.solverMoveDown_toolButton.setVisible(False)
        # self.solverMoveUp_toolButton.clicked.connect(
        #     self.solverMoveUpClicked
        # )
        # self.solverMoveDown_toolButton.clicked.connect(
        #     self.solverMoveDownClicked
        # )

        # Override Current Frame
        self.overrideCurrentFrame_checkBox.stateChanged.connect(
            self.overrideCurrentFrameChanged
        )

        # Populate the UI with data.
        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateAttributeToggleButtons()
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
        self._parentObject.window().setWindowTitle(title)

    def updateCollectionModel(self):
        self.populateCollectionModel(self.collectionName_model)

        col = lib_state.get_active_collection()
        if col is None:
            cols = lib_col.get_collections()
            if len(cols) > 0:
                # If there is no active collection, but there are
                # collections already created, we make sure the first
                # collection is marked active.
                col = cols[0]
                lib_state.set_active_collection(col)

        if col is not None:
            index = self.getDefaultCollectionIndex(self.collectionName_model, col)
            if index is not None:
                self.collectionName_comboBox.setCurrentIndex(index)

        self.updateDynamicWindowTitle()
        return

    def updateObjectToggleButtons(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        show_cam = lib_col.get_object_toggle_camera_from_collection(col)
        show_mkr = lib_col.get_object_toggle_marker_from_collection(col)
        show_bnd = lib_col.get_object_toggle_bundle_from_collection(col)
        self.objectToggleCamera_toolButton.setChecked(show_cam)
        self.objectToggleMarker_toolButton.setChecked(show_mkr)
        self.objectToggleBundle_toolButton.setChecked(show_bnd)
        return

    def updateObjectModel(self):
        self.populateObjectModel(self.object_model)
        valid = uiutils.isValidQtObject(self.object_treeView)
        if valid is False:
            return
        self.object_treeView.expandAll()

        widgets = [self.object_frame]
        self.populateWidgetsEnabled(widgets)
        return

    def updateAttributeToggleButtons(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        show_anm = lib_col.get_attribute_toggle_animated_from_collection(col)
        show_stc = lib_col.get_attribute_toggle_static_from_collection(col)
        show_lck = lib_col.get_attribute_toggle_locked_from_collection(col)
        self.attributeToggleAnimated_toolButton.setChecked(show_anm)
        self.attributeToggleStatic_toolButton.setChecked(show_stc)
        self.attributeToggleLocked_toolButton.setChecked(show_lck)
        return

    def updateAttributeModel(self):
        self.populateAttributeModel(self.attribute_model)
        valid = uiutils.isValidQtObject(self.attribute_treeView)
        if valid is False:
            return
        self.attribute_treeView.expandAll()

        widgets = [self.attribute_frame]
        self.populateWidgetsEnabled(widgets)
        return

    def updateSolverModel(self):
        self.populateOverrideCurrentFrame()
        self.populateSolverModel(self.solver_model)

        widgets = [self.solverOptions_frame]
        self.populateWidgetsEnabled(widgets)
        return

    def updateSolveValidState(self):
        # self.setStatusLine(const.STATUS_COMPILING)
        # v = True
        # col = lib_state.get_active_collection()
        # if col is None:
        #     v = False
        # else:
        #     v = lib_col.compile_collection(col)
        # assert isinstance(v, bool) is True

        # # TODO: Sometimes the apply button is falsely disabled,
        # #   therefore we shouldn't disable it until it's fixed.
        # # # if self._parentObject is not None:
        # # #     self._parentObject.applyBtn.setEnabled(v)

        # if v is True:
        #     self.setStatusLine(const.STATUS_READY)
        # else:
        #     self.setStatusLine(const.STATUS_SOLVER_NOT_VALID)
        return

    def populateCollectionModel(self, model):
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

    def populateObjectModel(self, model):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        col = lib_state.get_active_collection()
        mkr_list = []
        show_cam = const.OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE
        show_mkr = const.OBJECT_TOGGLE_MARKER_DEFAULT_VALUE
        show_bnd = const.OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE
        if col is not None:
            mkr_list = lib_marker.get_markers_from_collection(col)
            show_cam = lib_col.get_object_toggle_camera_from_collection(col)
            show_mkr = lib_col.get_object_toggle_marker_from_collection(col)
            show_bnd = lib_col.get_object_toggle_bundle_from_collection(col)
        root = convert_to_ui.markersToUINodes(mkr_list, show_cam, show_mkr, show_bnd)
        model.setRootNode(root)
        return

    def populateAttributeModel(self, model):
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
            self.updateAttributeModel()
            return

        # Add Callbacks
        #
        # When querying attributes, we must make sure they have a Maya
        # callback attached to the node to update the UI.
        callback_manager = self.getCallbackManager()
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

    def populateSolverModel(self, model):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        col = lib_state.get_active_collection()
        if col is None:
            step_list = []
        else:
            step_list = lib_col.get_solver_steps_from_collection(col)
        node_list = convert_to_ui.solverStepsToUINodes(step_list, col)
        self.solver_model.setNodeList(node_list)
        return

    def populateOverrideCurrentFrame(self):
        cur_frame = False
        col = lib_state.get_active_collection()
        if col is not None:
            cur_frame = lib_col.get_override_current_frame_from_collection(col)
        self.overrideCurrentFrame_checkBox.setChecked(cur_frame)
        return

    def populateWidgetsEnabled(self, widgets):
        col = lib_state.get_active_collection()
        enabled = col is not None
        for widget in widgets:
            widget.setEnabled(enabled)
        return

    def setStatusLine(self, text):
        valid = uiutils.isValidQtObject(self)
        if valid is False:
            return
        valid = uiutils.isValidQtObject(self.statusLine_label)
        if valid is False:
            return
        self.statusLine_label.setText(text)
        return

    def getDefaultCollectionIndex(self, model, col):
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

    def getCallbackManager(self):
        """
        Get the Callback Manager from the Solver Window, or None.

        :return: Get the attached CallbackManager class, otherwise
                 None if CallbackManager cannot be found.
        :rtype: None or CallbackManager
        """
        callback_manager = None
        parentObject = getattr(self, '_parentObject', None)
        if parentObject is not None:
            callback_manager = getattr(parentObject, 'callback_manager', None)
        return callback_manager

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
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    def createNewCollectionNode(self):
        col = lib_col.create_collection()
        lib_state.set_active_collection(col)

        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateAttributeToggleButtons()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    def renameCollectionNode(self):
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
        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateAttributeToggleButtons()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    def removeCollectionNode(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to delete.')
            return

        cols = lib_col.get_collections()
        prev_col = lib_col.get_previous_collection(cols, col)

        steps = lib_col.get_solver_steps_from_collection(col)
        for step in steps:
            lib_col.remove_solver_step_from_collection(col, step)

        lib_col.delete_collection(col)
        lib_state.set_active_collection(prev_col)

        self.updateDynamicWindowTitle()
        self.updateCollectionModel()
        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateAttributeToggleButtons()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    def attributeToggleAnimatedClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_animated_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_animated_on_collection(col, value)

        self.updateAttributeModel()
        self.updateSolveValidState()
        return

    def attributeToggleStaticClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_static_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_static_on_collection(col, value)

        self.updateAttributeModel()
        self.updateSolveValidState()
        return

    def attributeToggleLockedClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_attribute_toggle_locked_from_collection(col)
        value = not value
        lib_col.set_attribute_toggle_locked_on_collection(col, value)

        self.updateAttributeModel()
        self.updateSolveValidState()
        return

    def objectToggleCameraClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_camera_from_collection(col)
        value = not value
        lib_col.set_object_toggle_camera_on_collection(col, value)

        self.updateObjectModel()
        return

    def objectToggleMarkerClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_marker_from_collection(col)
        value = not value
        lib_col.set_object_toggle_marker_on_collection(col, value)

        self.updateObjectModel()
        return

    def objectToggleBundleClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to set.')
            return
        value = lib_col.get_object_toggle_bundle_from_collection(col)
        value = not value
        lib_col.set_object_toggle_bundle_on_collection(col, value)

        self.updateObjectModel()
        return

    def collectionSelectClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            LOG.warning('No active collection to select.')
            return
        lib_col.select_collection(col)
        self.updateDynamicWindowTitle()
        return

    def objectAddClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add markers, active collection is not defined.'
            LOG.warning(msg)
            return

        sel = lib_maya_utils.get_scene_selection()
        mkr_list = lib_maya_utils.get_markers_from_selection()
        if len(mkr_list) == 0:
            msg = 'Please select objects, found no markers.'
            LOG.warning(msg)
            return
        lib_marker.add_markers_to_collection(mkr_list, col)

        def update_func():
            if uiutils.isValidQtObject(self) is False:
                return
            self.updateObjectToggleButtons()
            self.updateObjectModel()
            self.updateSolveValidState()
            return

        # Add Callbacks
        callback_manager = self.getCallbackManager()
        if callback_manager is not None:
            lib_marker.add_callbacks_to_markers(
                mkr_list,
                update_func,
                callback_manager
            )

        update_func()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def objectRemoveClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return

        sel = lib_maya_utils.get_scene_selection()
        ui_nodes = lib_uiquery.get_selected_ui_nodes(
            self.object_treeView,
            self.object_filterModel
        )
        nodes = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'marker')
        lib_marker.remove_markers_from_collection(nodes, col)

        # Remove Callbacks
        callback_manager = self.getCallbackManager()
        if callback_manager is not None:
            lib_marker.remove_callbacks_from_markers(
                nodes,
                callback_manager
            )

        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateSolveValidState()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def attrAddClicked(self):
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
            self.updateAttributeToggleButtons()
            self.updateAttributeModel()
            self.updateSolveValidState()
            return

        # Add Callbacks
        callback_manager = self.getCallbackManager()
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

    def attrRemoveClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return

        sel = lib_maya_utils.get_scene_selection()
        ui_nodes = lib_uiquery.get_selected_ui_nodes(
            self.attribute_treeView,
            self.attribute_filterModel
        )
        attr_list = lib_uiquery.convert_ui_nodes_to_nodes(ui_nodes, 'data')
        lib_attr.remove_attr_from_collection(attr_list, col)

        # Remove Callbacks
        callback_manager = self.getCallbackManager()
        if callback_manager is not None:
            lib_attr.remove_callbacks_from_attributes(
                attr_list,
                callback_manager
            )

        self.updateAttributeToggleButtons()
        self.updateAttributeModel()
        self.updateSolveValidState()

        # Restore selection.
        lib_maya_utils.set_scene_selection(sel)
        return

    def solverAddClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            msg = 'Cannot add Solver Step, active collection is invalid,'
            LOG.warning(msg)
            return
        step = lib_col.create_solver_step()
        lib_col.add_solver_step_to_collection(col, step)
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    def solverRemoveClicked(self):
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
        return

    def solverMoveUpClicked(self):
        # TODO: Write this.
        #  1 - get all UI nodes
        #  2 - get selected UI node.
        #  3 - get index of selected UI node
        #  4 - move it up by one
        raise NotImplementedError
        return

    def solverMoveDownClicked(self):
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
        self.updateObjectToggleButtons()
        self.updateObjectModel()
        self.updateAttributeToggleButtons()
        self.updateAttributeModel()
        self.updateSolverModel()
        self.updateSolveValidState()
        return

    @staticmethod
    def __lookupObjectNodes(indexes, model):
        maya_nodes = []
        for idx in indexes:
            ui_node = lib_uiquery.get_ui_node_from_index(idx, model)
            if ui_node is None:
                continue

            # Type info will be 'marker', 'bundle' or 'camera' based on
            # the selected node type.
            typeInfo = ui_node.typeInfo
            nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], typeInfo)
            if typeInfo == 'camera':
                maya_nodes += [x.get_shape_node() for x in nodes]
            else:
                # For bundles and markers
                maya_nodes += [x.get_node() for x in nodes]
        return maya_nodes

    @staticmethod
    def __lookupAttrNodes(indexes, model):
        maya_nodes = []
        for idx in indexes:
            ui_node = lib_uiquery.get_ui_node_from_index(idx, model)
            if ui_node is None:
                continue

            nodes = lib_uiquery.convert_ui_nodes_to_nodes([ui_node], 'data')
            maya_nodes += [x.get_node() for x in nodes]
        return maya_nodes

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def objectNodeSelectionChanged(self, selected, deselected):
        """
        Look up the Maya node from the 'selected' nodes, and add them
        to the Maya selection.
        """
        select_indexes = [idx for idx in selected.indexes()]
        deselect_indexes = [idx for idx in deselected.indexes()]

        select_nodes = self.__lookupObjectNodes(
            select_indexes,
            self.object_filterModel)
        deselect_nodes = self.__lookupObjectNodes(
            deselect_indexes,
            self.object_filterModel)

        lib_maya_utils.add_scene_selection(select_nodes)
        lib_maya_utils.remove_scene_selection(deselect_nodes)
        return

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def attrNodeSelectionChanged(self, selected, deselected):
        select_indexes = [idx for idx in selected.indexes()]
        deselect_indexes = [idx for idx in deselected.indexes()]

        select_nodes = self.__lookupAttrNodes(
            select_indexes,
            self.attribute_filterModel)
        deselect_nodes = self.__lookupAttrNodes(
            deselect_indexes,
            self.attribute_filterModel)
        lib_maya_utils.add_scene_selection(select_nodes)
        lib_maya_utils.remove_scene_selection(deselect_nodes)
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
