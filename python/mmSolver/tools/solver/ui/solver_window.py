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
import mmSolver.tools.solver.ui.solver_layout as solver_layout
import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window


LOG = mmSolver.logger.get_logger(level='DEBUG')
UI = None


baseModule, BaseWindow = uiutils.getBaseWindow()


class SolverWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(SolverWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(solver_layout.SolverLayout)

        # TODO: Dynamically add the currenct collection name to the
        # title bar.
        self.setWindowTitle('Solver - mmSolver')

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
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

    def addMenuBarContents(self, menubar):
        # File Menu
        file_menu = QtWidgets.QMenu('File', menubar)

        # # New Collection
        # newCollectionAction = QtWidgets.QAction('New Collection', file_menu)
        # newCollectionAction.setStatusTip('Create a new Collection node.')
        # newCollectionAction.triggered.connect(partial(self.createNewCollectionNodeCB))
        #
        # # rename Collection
        # renameCollectionAction = QtWidgets.QAction('Rename Collection', file_menu)
        # renameCollectionAction.setStatusTip('Rename a Collection node.')
        # renameCollectionAction.triggered.connect(partial(self.createrenameCollectionNodeCB))

        # Close Window
        closeWindowAction = QtWidgets.QAction('Close Window', file_menu)
        closeWindowAction.setStatusTip('Close the mmSolver window.')
        closeWindowAction.triggered.connect(partial(self.closeWindowCB))

        # file_menu.addAction(newCollectionAction)
        # file_menu.addAction(renameCollectionAction)
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
        # TODO: Open a UI where we can paste a file path in and press
        # "ok". The UI could also show the point data before loading
        # the file.
        loadmarker_window.main()

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
