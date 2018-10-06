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
import mmSolver.tools.loadmarker.ui.loadmarker_layout as loadmarker_layout
import mmSolver.tools.loadmarker.mayareadfile as mayareadfile


LOG = mmSolver.logger.get_logger(level='DEBUG')
UI = None


baseModule, BaseWindow = uiutils.getBaseWindow()


class LoadMarkerWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(LoadMarkerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(loadmarker_layout.LoadMarkerLayout)

        self.setWindowTitle('Load Markers - mmSolver')

        # # Menu Bar
        # self.addMenuBarContents(self.menubar)
        # self.menubar.show()
        self.baseHideMenuBar()

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Load')

        self.applyBtn.clicked.connect(self.apply)
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

    # def addMenuBarContents(self, menubar):
    #     # Help Menu
    #     help_menu = QtWidgets.QMenu('Help', menubar)
    #
    #     # Launch Help
    #     launchHelpAction = QtWidgets.QAction('Help...', help_menu)
    #     launchHelpAction.setStatusTip('Show help.')
    #     launchHelpAction.triggered.connect(partial(self.launchHelpCB))
    #
    #     # Launch About
    #     launchAboutAction = QtWidgets.QAction('About...', help_menu)
    #     launchAboutAction.setStatusTip('About this software.')
    #     launchAboutAction.triggered.connect(partial(self.launchAboutCB))
    #
    #     help_menu.addAction(launchHelpAction)
    #     help_menu.addAction(launchAboutAction)
    #     menubar.addMenu(help_menu)
    #     return

    def createNewCollectionNodeCB(self):
        LOG.debug('createNewCollectionNodeCB')

    def closeWindowCB(self):
        LOG.debug('closeWindowCB')

    def apply(self):
        self.progressBar.show()
        file_path = self.subForm.getFilePath()
        LOG.debug('apply: %r', file_path)
        for i in range(100):
            self.progressBar.setValue(i)
            time.sleep(0.01)
        self.progressBar.hide()
        # TODO: Load the markers.
        mkr_list = mayareadfile.read(file_path)
        return

    def help(self):
        LOG.debug('help')
        return


def main(show=True, widthHeight=(800, 400)):
    global UI

    name = 'SolverWindow'
    app, parent = uiutils.getParent()

    if UI is not None:
        UI.close()
    UI = LoadMarkerWindow(parent=parent, name=name)
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
