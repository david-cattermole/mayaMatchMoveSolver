"""
The Solver layout, the contents of the main solver window.
"""

import sys
import time
from functools import partial

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.uimodels as uimodels
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes
import mmSolver.tools.solver.ui.ui_solver_layout as ui_solver_layout
import mmSolver.tools.solver.ui.convert_to_ui as convert_to_ui
import mmSolver.tools.solver.tool as tool
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger(level='DEBUG')


class SolverLayout(QtWidgets.QWidget, ui_solver_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

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
        self.attribute_selModel = self.attribute_treeView.selectionModel()
        self.attribute_selModel.currentChanged.connect(self.attrNodeCurrentChanged)

        # Attr Add and Remove buttons
        self.attributeAdd_toolButton.clicked.connect(self.attrAddClicked)
        self.attributeRemove_toolButton.clicked.connect(self.attrRemoveClicked)

        # TODO: Add support for table view of Solver steps.
        #  Each step contains a list of frames to compute, a strategy
        #  order to solve the frames in ('sequential', 'all'), and an
        #  attribute filter to use ('anim' or 'static + anim').  
        #
        # If 'anim' attribute filter is used then the strategy is
        #  unneeded and will solve each frame individually.
        # 
        # A custom right-click menu should be added to the list of
        #  frames; 'add current frame', 'remove current frame', 'set
        #  playback frame range' and 'clear frames'.
        # 
        # The ability to add new solver steps should be given with a +
        # and - button at top-right. There should also be buttons to
        # move the selected row up or down.
        # 

        # Solver Nodes
        self.solver_model = solver_nodes.SolverModel(font=self.font)
        self.solver_filterModel = QtCore.QSortFilterProxyModel()
        self.solver_filterModel.setSourceModel(self.solver_model)
        self.solver_filterModel.setDynamicSortFilter(False)
        self.solver_tableView.setModel(self.solver_filterModel)
        self.solver_tableView.setSortingEnabled(True)
        self.solver_tableView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.solver_selModel = self.solver_tableView.selectionModel()
        # self.solver_selModel.currentChanged.connect(self.solverNodeCurrentChanged)

        # Solver Add and Remove buttons
        self.solverAdd_toolButton.clicked.connect(self.solverAddClicked)
        self.solverRemove_toolButton.clicked.connect(self.solverRemoveClicked)
        self.solverMoveUp_toolButton.clicked.connect(self.solverMoveUpClicked)
        self.solverMoveDown_toolButton.clicked.connect(self.solverMoveDownClicked)

        # Populate the UI with data.
        self.populateUi()

    def populateUi(self):
        self.updateCollectionModel()
        self.updateObjectModel()
        self.updateAttributeModel()
        self.updateSolverModel()
        return

    def updateCollectionModel(self):
        col = tool.get_active_collection()
        self.populateCollectionModel(self.collectionName_model)
        index = self.getDefaultCollectionIndex(self.collectionName_model, col)
        self.collectionName_comboBox.setCurrentIndex(index)
        return

    def updateObjectModel(self):
        self.populateObjectModel(self.object_model)
        self.object_treeView.expandAll()
        return

    def updateAttributeModel(self):
        self.populateAttributeModel(self.attribute_model)
        self.attribute_treeView.expandAll()
        return

    def updateSolverModel(self):
        self.populateSolverModel(self.solver_model)
        return

    def populateCollectionModel(self, model):
        cols = tool.get_collections()
        string_data_list = []
        for col in cols:
            node = col.get_node()
            string_data_list.append((node, col))
        model.setStringDataList(string_data_list)
        return

    def populateObjectModel(self, model):
        col = tool.get_active_collection()
        if col is None:
            return
        mkr_list = tool.get_markers_from_collection(col)
        root = convert_to_ui.markersToObjectNodes(mkr_list)
        model.setRootNode(root)
        return

    def populateAttributeModel(self, model):
        col = tool.get_active_collection()
        if col is None:
            return
        attr_list = tool.get_attributes_from_collection(col)
        root = convert_to_ui.attributesToAttrNodes(attr_list)
        model.setRootNode(root)
        return

    def populateSolverModel(self, model):
        col = tool.get_active_collection()
        if col is None:
            return
        sol_list = tool.get_solvers_from_collection(col)
        node_list = convert_to_ui.solversToSolverNodes(sol_list, col)
        self.solver_model.setNodeList(node_list)
        return

    def getDefaultCollectionIndex(self, model, col):
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
        col = tool.create_collection()
        tool.set_active_collection(col)
        self.populateUi()
        return

    def renameCollectionNode(self):
        LOG.debug('renameCollectionNode')
        col = tool.get_active_collection()
        # TODO: Prompt for a new name.
        new_name = 'my_new_name1'
        tool.rename_collection(col, new_name)
        self.populateUi()
        return

    def removeCollectionNode(self):
        LOG.debug('removeCollectionNode')
        col = tool.get_active_collection()
        if col is not None:
            tool.delete_collection(col)
        self.populateUi()
        return

    def collectionSelectClicked(self):
        LOG.debug('collectionSelectClicked')
        col = tool.get_active_collection()
        tool.select_collection(col)
        self.populateUi()
        return

    def objectAddClicked(self):
        LOG.debug('objectAddClicked')
        mkr_list = tool.get_markers_from_selection()
        LOG.debug('mkr_list: %r', mkr_list)
        if len(mkr_list) == 0:
            msg = 'Please select objects, found no markers.'
            LOG.warning(msg)
            return
        col = tool.get_active_collection()
        if col is None:
            msg = 'Cannot add markers, active collection is not defined.'
            LOG.warning(msg)
            return
        tool.add_markers_to_collection(mkr_list, col)
        self.updateObjectModel()
        return

    def objectRemoveClicked(self):
        LOG.debug('objectRemoveClicked')
        # TODO: Write this.
        return

    def attrAddClicked(self):
        LOG.debug('attrAddClicked')
        attr_list = tool.get_selected_maya_attributes()
        LOG.debug('attr_list: %r', attr_list)
        if len(attr_list) == 0:
            msg = 'Please select attributes in the channel box, none where found.'
            LOG.warning(msg)
            return
        col = tool.get_active_collection()
        if col is None:
            msg = 'Cannot add attributes, active collection is not defined.'
            LOG.warning(msg)
            return
        tool.add_attributes_to_collection(attr_list, col)
        self.updateAttributeModel()
        return

    def attrRemoveClicked(self):
        LOG.debug('attrRemoveClicked')
        # TODO: Write this.
        return

    def solverAddClicked(self):
        LOG.debug('solverAddClicked')
        col = tool.get_active_collection()
        sol = tool.create_solver()
        tool.add_solver_to_collection(sol, col)
        self.updateSolverModel()
        return

    def solverRemoveClicked(self):
        LOG.debug('solverRemoveClicked')
        # TODO: Write this.
        return

    def solverMoveUpClicked(self):
        LOG.debug('solverMoveUpClicked')
        # TODO: Write this.
        return

    def solverMoveDownClicked(self):
        LOG.debug('solverMoveDownClicked')
        # TODO: Write this.
        return

    def getFrameList(self):
        LOG.debug('getFrameList')
        return '' # self.frames_lineEdit.text()

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
        tool.set_active_collection(data)
        self.updateObjectModel()
        self.updateAttributeModel()
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def objectNodeCurrentChanged(self, index, prevIndex):
        # TODO: Look up the Maya node from the data at index, then add
        # it to the selection.
        # TODO: Based on the Maya selection key modifiers, we should
        # add to the current selection, or toggle, as needed.
        if not index.isValid():
            return
        index_map = self.object_filterModel.mapToSource(index)
        node = index_map.internalPointer()
        if node is None:
            return
        node_data = node.data()
        if node_data is None:
            return
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def attrNodeCurrentChanged(self, index, prevIndex):
        if not index.isValid():
            return
        index_map = self.attribute_filterModel.mapToSource(index)
        node = index_map.internalPointer()
        if node is None:
            return
        nodeData = node.data()
        if nodeData is None:
            return
        return
