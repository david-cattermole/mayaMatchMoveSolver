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

import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.uimodels as uimodels
import mmSolver.tools.solver.ui.ui_solver_window as ui_solver_window
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
UI = None


class SolverLayout(QtWidgets.QWidget, ui_solver_window.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Object Nodes
        object_rootNode = object_nodes.MyObjectNode('root')
        self.objectModel = object_nodes.MyObjectModel(object_rootNode, font=self.font)
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
        # self.attr_selModel.currentChanged.connect(self.slotAttrNodeCurrentChanged)

        # Attr Add and Remove buttons
        self.attributeAdd_toolButton.clicked.connect(self.attrAddClicked)
        self.attributeRemove_toolButton.clicked.connect(self.attrRemoveClicked)

        # data = ['Existing Times', 'All Times', 'Three', 'Four', 'Five']
        # model = QStringListModel(data)
        # self.timeRangeComboBox.setModel(model)

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


baseModule, BaseWindow = uiutils.getBaseWindow()


class SolverWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(SolverWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(SolverLayout)

        self.setWindowTitle('mmSolver')

        # Menu Bar
        self.addMenuBarContents(self.menubar)
        self.menubar.show()

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Solve')

        self.applyBtn.clicked.connect(self.apply)
        self.resetBtn.clicked.connect(self.reset)
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

    def addMenuBarContents(self, menubar):
        # File Menu
        file_menu = QtWidgets.QMenu('File', menubar)

        # New Collection
        newCollectionAction = QtWidgets.QAction('New Collection', file_menu)
        newCollectionAction.setStatusTip('Create a new Collection node.')
        newCollectionAction.triggered.connect(partial(self.createNewCollectionNodeCB))

        # Close Window
        closeWindowAction = QtWidgets.QAction('Close Window', file_menu)
        closeWindowAction.setStatusTip('Close the mmSolver window.')
        closeWindowAction.triggered.connect(partial(self.closeWindowCB))

        file_menu.addAction(newCollectionAction)
        file_menu.addSeparator()
        file_menu.addAction(closeWindowAction)
        menubar.addMenu(file_menu)

        # Tools Menu
        tools_menu = QtWidgets.QMenu('Tools', menubar) 

        # Load Markers
        loadMarkerAction = QtWidgets.QAction('Load Marker', tools_menu)
        loadMarkerAction.setStatusTip('Load Markers from a file.')
        loadMarkerAction.triggered.connect(partial(self.loadMarkerCB))

        tools_menu.addAction(loadMarkerAction)
        menubar.addMenu(tools_menu)

        # Help Menu
        help_menu = QtWidgets.QMenu('Help', menubar)

        # Launch Help
        launchHelpAction = QtWidgets.QAction('Help...', help_menu)
        launchHelpAction.setStatusTip('Show help.')
        launchHelpAction.triggered.connect(partial(self.launchHelpCB))

        # Launch About
        launchAboutAction = QtWidgets.QAction('About...', help_menu)
        launchAboutAction.setStatusTip('About this software.')
        launchAboutAction.triggered.connect(partial(self.launchAboutCB))

        help_menu.addAction(launchHelpAction)
        help_menu.addAction(launchAboutAction)
        menubar.addMenu(help_menu)
        return

    def createNewCollectionNodeCB(self):
        LOG.debug('createNewCollectionNodeCB')

    def closeWindowCB(self):
        LOG.debug('closeWindowCB')

    def loadMarkerCB(self):
        LOG.debug('loadMarkerCB')

    def launchHelpCB(self):
        LOG.debug('launchHelpCB')
        self.help()

    def launchAboutCB(self):
        LOG.debug('launchAboutCB')

    def apply(self):
        self.progressBar.show()
        frame_list = self.subForm.getFrameList()
        LOG.debug('apply: %r', frame_list)
        for i in range(100):
            self.progressBar.setValue(i)
            time.sleep(0.01)
        self.progressBar.hide()
        # TODO: Get all UI elements, and launch solve. 
        # Should we create 'tool' function?
        # How should we pass the data to the tool function?
        return

    def reset(self):
        LOG.debug('reset')
        return

    def help(self):
        LOG.debug('help')
        return


def main(show=True, widthHeight=(800, 600)):
    global UI

    name = 'SolverWindow'
    app, parent = uiutils.getParent()

    if UI is not None:
        UI.close()
    UI = SolverWindow(parent=parent, name=name)
    if not UI:
        return UI
    if show:
        UI.show()

    if widthHeight:
        pos = UI.pos()
        UI.setGeometry(pos.x(), pos.y(), widthHeight[0], widthHeight[1])

    # Enter Qt application main loop
    if app is not None:
        sys.exit(app.exec_())
    return UI
