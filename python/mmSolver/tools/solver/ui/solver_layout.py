"""

Usage::

   import mmSolver.tools.solver.ui.solver_window as solver_window;
   reload(solver_window)
   solver_window.main()

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
import mmSolver.tools.solver.ui.ui_solver_layout as ui_solver_layout
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.tool as solver_tool

LOG = mmSolver.logger.get_logger(level='DEBUG')


class SolverLayout(QtWidgets.QWidget, ui_solver_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Collection Add and Remove buttons
        self.collectionAdd_toolButton.clicked.connect(self.collectionAddClicked)
        self.collectionRemove_toolButton.clicked.connect(self.collectionRemoveClicked)

        # Object Nodes
        object_rootNode = object_nodes.ObjectNode('root')
        self.objectModel = object_nodes.ObjectModel(object_rootNode, font=self.font)
        self.objectFilterModel = uimodels.SortFilterProxyModel()
        self.objectFilterModel.setSourceModel(self.objectModel)
        self.objectFilterModel.setDynamicSortFilter(True)
        self.objectFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.object_treeView.setModel(self.objectFilterModel)
        self.object_treeView.setSortingEnabled(True)
        self.object_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.object_treeView.expandAll()
        self.object_selModel = self.object_treeView.selectionModel()
        self.object_selModel.currentChanged.connect(self.slotObjectNodeCurrentChanged)

        # Object Add and Remove buttons
        self.objectAdd_toolButton.clicked.connect(self.objectAddClicked)
        self.objectRemove_toolButton.clicked.connect(self.objectRemoveClicked)

        # Attr Nodes
        attr_rootNode = attr_nodes.PlugNode('root')
        self.attrModel = attr_nodes.AttrModel(attr_rootNode, font=self.font)
        self.attrFilterModel = uimodels.SortFilterProxyModel()
        self.attrFilterModel.setSourceModel(self.attrModel)
        self.attrFilterModel.setDynamicSortFilter(True)
        self.attrFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.attribute_treeView.setModel(self.attrFilterModel)
        self.attribute_treeView.setSortingEnabled(True)
        self.attribute_treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.attribute_treeView.expandAll()
        self.attr_selModel = self.attribute_treeView.selectionModel()
        self.attr_selModel.currentChanged.connect(self.slotAttrNodeCurrentChanged)

        # Attr Add and Remove buttons
        self.attributeAdd_toolButton.clicked.connect(self.attrAddClicked)
        self.attributeRemove_toolButton.clicked.connect(self.attrRemoveClicked)

        # data = ['Existing Times', 'All Times', 'Three', 'Four', 'Five']
        # model = QStringListModel(data)
        # self.timeRangeComboBox.setModel(model)

    def collectionAddClicked(self):
        LOG.debug('collectionAddClicked')
        return

    def collectionRemoveClicked(self):
        LOG.debug('collectionRemoveClicked')
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def slotObjectNodeCurrentChanged(self, index, prevIndex):
        LOG.debug('slotObjectNodeCurrentChanged')
        if not index.isValid():
            return
        index_map = self.objectFilterModel.mapToSource(index)
        node = index_map.internalPointer()
        if node is None:
            return
        nodeData = node.data()
        if nodeData is None:
            return
        return

    def objectAddClicked(self):
        LOG.debug('objectAddClicked')
        mkr_list = solver_tool.get_associted_markers_from_selection()
        print 'mkr_list:', mkr_list
        for mkr in mkr_list:
            print 'mkr:', mkr, repr(mkr)
        return

    def objectRemoveClicked(self):
        LOG.debug('objectRemoveClicked')
        return

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def slotAttrNodeCurrentChanged(self, index, prevIndex):
        LOG.debug('slotAttrNodeCurrentChanged')
        if not index.isValid():
            return
        index_map = self.attrFilterModel.mapToSource(index)
        node = index_map.internalPointer()
        if node is None:
            return
        nodeData = node.data()
        if nodeData is None:
            return
        return

    def attrAddClicked(self):
        LOG.debug('attrAddClicked')
        return

    def attrRemoveClicked(self):
        LOG.debug('attrRemoveClicked')
        return

    def getFrameList(self):
        LOG.debug('getFrameList')
        # return self.startFrameSpinBox.value()
        return
