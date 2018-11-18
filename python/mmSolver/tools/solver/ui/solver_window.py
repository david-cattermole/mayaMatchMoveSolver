"""

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
import mmSolver.tools.solver.tool as tool
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

        # TODO: Dynamically add the current collection name to the
        # title bar.
        self.setWindowTitle('mmSolver - Solver')

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

        # New Collection
        newCollectionAction = QtWidgets.QAction('New Collection', file_menu)
        newCollectionAction.setStatusTip('Create a new Collection node.')
        newCollectionAction.triggered.connect(partial(self.createNewCollectionNodeCB))
        file_menu.addAction(newCollectionAction)

        # Rename Collection
        renameCollectionAction = QtWidgets.QAction('Rename Collection', file_menu)
        renameCollectionAction.setStatusTip('Rename a Collection node.')
        renameCollectionAction.triggered.connect(partial(self.renameCollectionNodeCB))
        file_menu.addAction(renameCollectionAction)

        file_menu.addSeparator()

        # Remove Collection
        removeCollectionAction = QtWidgets.QAction('Remove Collection', file_menu)
        removeCollectionAction.setStatusTip('Remove a Collection node.')
        removeCollectionAction.triggered.connect(partial(self.removeCollectionNodeCB))
        file_menu.addAction(removeCollectionAction)

        file_menu.addSeparator()

        # Close Window
        closeWindowAction = QtWidgets.QAction('Close Window', file_menu)
        closeWindowAction.setStatusTip('Close the mmSolver window.')
        closeWindowAction.triggered.connect(partial(self.close))
        file_menu.addAction(closeWindowAction)

        menubar.addMenu(file_menu)

        # Tools Menu
        tools_menu = QtWidgets.QMenu('Tools', menubar)

        # Create Marker
        createMarkerAction = QtWidgets.QAction('Create Marker', tools_menu)
        createMarkerAction.setStatusTip('Create Markers on the selected camera.')
        createMarkerAction.triggered.connect(partial(self.createMarkerCB))
        tools_menu.addAction(createMarkerAction)

        # Convert to Marker
        convertToMarkerAction = QtWidgets.QAction('Convert to Marker...', tools_menu)
        convertToMarkerAction.setStatusTip('Convert the selection to Markers.')
        convertToMarkerAction.triggered.connect(partial(self.convertToMarkerCB))
        tools_menu.addAction(convertToMarkerAction)

        # Load Markers
        loadMarkerAction = QtWidgets.QAction('Load Marker...', tools_menu)
        loadMarkerAction.setStatusTip('Load Markers from a file.')
        loadMarkerAction.triggered.connect(partial(self.loadMarkerCB))
        tools_menu.addAction(loadMarkerAction)

        # Toogle Marker / Bundle selection
        toggleMarkerBundleSelection = QtWidgets.QAction('Toggle Marker / Bundle Selection', tools_menu)
        toggleMarkerBundleSelection.setStatusTip('Select connected Markers, or Bundles.')
        toggleMarkerBundleSelection.triggered.connect(partial(self.toggleMarkerBundleSelectionCB))
        tools_menu.addAction(toggleMarkerBundleSelection)

        menubar.addMenu(tools_menu)

        # Log Menu
        # This menu depicts a radiobutton allowing the user to choose
        # how much information is returned to the console (the logging
        # level).
        log_menu = QtWidgets.QMenu('Log', menubar)

        # Errors
        logErrorAction = QtWidgets.QAction('Errors', log_menu)
        logErrorAction.setStatusTip('Send Errors to the log.')
        logErrorAction.setCheckable(True)
        logErrorAction.triggered.connect(partial(self.logErrorCB))
        log_menu.addAction(logErrorAction)

        # Warnings
        logWarningAction = QtWidgets.QAction('Warnings', log_menu)
        logWarningAction.setStatusTip('Send Warnings to the log.')
        logWarningAction.setCheckable(True)
        logWarningAction.triggered.connect(partial(self.logWarningCB))
        log_menu.addAction(logWarningAction)

        # Information
        logInfoAction = QtWidgets.QAction('Info', log_menu)
        logInfoAction.setStatusTip('Send Information to the log.')
        logInfoAction.setCheckable(True)
        logInfoAction.triggered.connect(partial(self.logInfoCB))
        log_menu.addAction(logInfoAction)

        # Verbose
        logVerboseAction = QtWidgets.QAction('Verbose', log_menu)
        logVerboseAction.setStatusTip('Send Verboses to the log.')
        logVerboseAction.setCheckable(True)
        logVerboseAction.triggered.connect(partial(self.logVerboseCB))
        log_menu.addAction(logVerboseAction)

        # Debug
        logDebugAction = QtWidgets.QAction('Debug', log_menu)
        logDebugAction.setStatusTip('Send Debug messages to the log.')
        logDebugAction.setCheckable(True)
        logDebugAction.triggered.connect(partial(self.logDebugCB))
        log_menu.addAction(logDebugAction)

        # 'Radio' button for logging levels
        log_actionGroup = QtWidgets.QActionGroup(log_menu)
        log_actionGroup.addAction(logErrorAction)
        log_actionGroup.addAction(logWarningAction)
        log_actionGroup.addAction(logInfoAction)
        log_actionGroup.addAction(logVerboseAction)
        log_actionGroup.addAction(logDebugAction)

        log_level = tool.get_log_level()
        if log_level == 'error':
            logErrorAction.setChecked(True)
        elif log_level == 'warning':
            logWarningAction.setChecked(True)
        elif log_level == 'info':
            logInfoAction.setChecked(True)
        elif log_level == 'verbose':
            logVerboseAction.setChecked(True)
        elif log_level == 'debug':
            logDebugAction.setChecked(True)
        else:
            LOG.warning('Invalid log level given: ' % log_level)

        menubar.addMenu(log_menu)

        # Help Menu
        help_menu = QtWidgets.QMenu('Help', menubar)

        # Launch Help
        launchHelpAction = QtWidgets.QAction('Help...', help_menu)
        launchHelpAction.setStatusTip('Show help.')
        launchHelpAction.triggered.connect(partial(self.launchHelpCB))
        help_menu.addAction(launchHelpAction)

        # Launch About
        launchAboutAction = QtWidgets.QAction('About...', help_menu)
        launchAboutAction.setStatusTip('About this software.')
        launchAboutAction.triggered.connect(partial(self.launchAboutCB))
        help_menu.addAction(launchAboutAction)

        menubar.addMenu(help_menu)
        return

    def logErrorCB(self):
        LOG.debug('logErrorCB')

    def logWarningCB(self):
        LOG.debug('logWarningCB')

    def logInfoCB(self):
        LOG.debug('logInfoCB')

    def logVerboseCB(self):
        LOG.debug('logVerboseCB')

    def logDebugCB(self):
        LOG.debug('logDebugCB')

    def createNewCollectionNodeCB(self):
        LOG.debug('createNewCollectionNodeCB')
        self.subForm.createNewCollectionNode()
        return

    def renameCollectionNodeCB(self):
        LOG.debug('renameCollectionNodeCB')
        self.subForm.renameCollectionNode()
        return

    def removeCollectionNodeCB(self):
        LOG.debug('removeCollectionNodeCB')
        self.subForm.removeCollectionNode()
        return

    def createMarkerCB(self):
        LOG.debug('createMarkerCB')
        tool.create_marker()

    def convertToMarkerCB(self):
        LOG.warning('convertToMarkerCB')
        tool.convert_to_marker()

    def loadMarkerCB(self):
        LOG.debug('loadMarkerCB')
        # TODO: Open a UI where we can paste a file path in and press
        # "ok". The UI could also show the point data before loading
        # the file.
        loadmarker_window.main()

    def toggleMarkerBundleSelectionCB(self):
        LOG.warning('toggleMarkerBundleSelectionCB')

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

        col = tool.get_active_collection()
        ok = tool.compile_collection(col)
        if ok is True:
            tool.execute_solver(col)
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
