"""
The main window for the 'Solver' tool.
"""

import sys
from functools import partial

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.constant as const
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.ui.solver_layout as solver_layout
import mmSolver.tools.loadmarker.tool as loadmarker_tool
import mmSolver.tools.selection.tools as selection_tool
import mmSolver.tools.cameraaim.tool as cameraaim_tool
import mmSolver.tools.createmarker.tool as createmarker_tool
import mmSolver.tools.createbundle.tool as createbundle_tool
import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
import mmSolver.tools.convertmarker.tool as convertmarker_tool
import mmSolver.tools.centertwodee.tool as centertwodee_tool
# import mmSolver.tools.snaponcurve.tool as snaponcurve_tool
# import mmSolver.tools.surfacerivet.tool as surfacerivet_tool


LOG = mmSolver.logger.get_logger()
UI = None


baseModule, BaseWindow = uiutils.getBaseWindow()


class SolverWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(SolverWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(solver_layout.SolverLayout)
        self.setStatusLine(const.STATUS_READY)

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

        # Callbacks
        self.callback_manager = maya_callbacks.CallbackManager()

        # Add Maya callbacks for the UI
        callback_ids = maya_callbacks.add_callbacks_new_scene(self)
        self.callback_manager.add_node_ids(
            maya_callbacks.TYPE_NEW_SCENE,
            None,
            callback_ids,
        )
        return

    def __del__(self):
        """
        Release all resources held by the class.
        """
        callback_ids = list(self.callback_manager.get_all_ids())
        maya_callbacks.remove_callbacks(callback_ids)
        del self.callback_manager
        self.callback_manager = maya_callbacks.CallbackManager()

    def addMenuBarContents(self, menubar):
        # File Menu
        file_menu = QtWidgets.QMenu('File', menubar)

        # New Collection
        label = 'New Collection'
        tooltip = 'Create a new Collection node.'
        action = QtWidgets.QAction(label, file_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.createNewCollectionNodeCB))
        file_menu.addAction(action)

        # Rename Collection
        label = 'Rename Collection'
        tooltip = 'Rename a Collection node.'
        action = QtWidgets.QAction(label, file_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.renameCollectionNodeCB))
        file_menu.addAction(action)

        file_menu.addSeparator()

        # Remove Collection
        label = 'Remove Collection'
        tooltip = 'Remove a Collection node.'
        action = QtWidgets.QAction(label, file_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.removeCollectionNodeCB))
        file_menu.addAction(action)

        file_menu.addSeparator()

        # Close Window
        label = 'Close Window'
        tooltip = 'Close the mmSolver window.'
        action = QtWidgets.QAction(label, file_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.close))
        file_menu.addAction(action)

        menubar.addMenu(file_menu)

        # Tools Menu
        tools_menu = QtWidgets.QMenu('Tools', menubar)

        # Create Marker
        label = 'Create Marker'
        tooltip = 'Create Markers on the selected camera.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.createMarkerCB))
        tools_menu.addAction(action)

        # Convert to Marker
        label = 'Convert to Marker'
        tooltip = 'Convert the selection to Markers.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.convertToMarkerCB))
        tools_menu.addAction(action)

        # Load Markers
        label = 'Load Markers...'
        tooltip = 'Load Markers from a file.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.loadMarkerCB))
        tools_menu.addAction(action)

        tools_menu.addSeparator()

        # Create Bundle
        label = 'Create Bundle'
        tooltip = 'Create a default Bundle node.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.createBundleCB))
        tools_menu.addAction(action)

        tools_menu.addSeparator()

        # Link Marker + Bundle
        label = 'Link Marker + Bundle'
        tooltip = 'Link the selected Marker and Bundle together.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.linkMarkerBundleCB))
        tools_menu.addAction(action)

        # Unlink Marker from all Bundles
        label = 'Unlink Marker from all Bundles'
        tooltip = 'Unlink all selected Markers from their Bundle.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.unlinkMarkerBundleCB))
        tools_menu.addAction(action)

        tools_menu.addSeparator()

        # Toogle Marker / Bundle selection
        label = 'Toggle Marker / Bundle'
        tooltip = 'Select connected Markers, or Bundles.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.toggleMarkerBundleSelectionCB))
        tools_menu.addAction(action)

        # Select Marker / Bundle
        label = 'Select Marker + Bundle'
        tooltip = 'Select the connected Markers and Bundles.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.selectBothMarkersAndBundlesCB))
        tools_menu.addAction(action)

        tools_menu.addSeparator()

        # Camera Aim
        label = 'Aim at Camera'
        tooltip = 'Aim the selected transform nodes at camera.'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.aimAtCameraCB))
        tools_menu.addAction(action)

        label = 'Center 2D on Selection'
        tooltip = 'Visually center the 2D viewport on the selected node'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.centerTwoDeeCB))
        tools_menu.addAction(action)

        tools_menu.addSeparator()

        # Refresh Viewport During Solve
        label = 'Refresh Viewport'
        tooltip = 'Refresh the viewport while Solving.'
        refresh_value = lib_state.get_refresh_viewport_state()
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(refresh_value)
        action.toggled.connect(type(self).refreshActionToggledCB)
        tools_menu.addAction(action)

        menubar.addMenu(tools_menu)

        # Log Menu
        # This menu depicts a radio button allowing the user to choose
        # how much information is returned to the console (the logging
        # level).
        log_menu = QtWidgets.QMenu('Log', menubar)

        # Errors
        label = 'Errors'
        tooltip = 'Send Errors to the log.'
        logErrorAction = QtWidgets.QAction(label, log_menu)
        logErrorAction.setStatusTip(tooltip)
        logErrorAction.setCheckable(True)
        logErrorAction.triggered.connect(partial(self.logErrorCB))
        log_menu.addAction(logErrorAction)

        # Warnings
        label = 'Warnings'
        tooltip = 'Send Warnings to the log.'
        logWarningAction = QtWidgets.QAction(label, log_menu)
        logWarningAction.setStatusTip(tooltip)
        logWarningAction.setCheckable(True)
        logWarningAction.triggered.connect(partial(self.logWarningCB))
        log_menu.addAction(logWarningAction)

        # Information
        label = 'Info'
        tooltip = 'Send Information to the log.'
        logInfoAction = QtWidgets.QAction(label, log_menu)
        logInfoAction.setStatusTip(tooltip)
        logInfoAction.setCheckable(True)
        logInfoAction.triggered.connect(partial(self.logInfoCB))
        log_menu.addAction(logInfoAction)

        # Verbose
        label = 'Verbose'
        tooltip = 'Send Verboses to the log.'
        logVerboseAction = QtWidgets.QAction(label, log_menu)
        logVerboseAction.setStatusTip(tooltip)
        logVerboseAction.setCheckable(True)
        logVerboseAction.triggered.connect(partial(self.logVerboseCB))
        log_menu.addAction(logVerboseAction)

        # Debug
        label = 'Debug'
        tooltip = 'Send Debug messages to the log.'
        logDebugAction = QtWidgets.QAction(label, log_menu)
        logDebugAction.setStatusTip(tooltip)
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

        log_level = lib_state.get_log_level()
        if log_level == const.LOG_LEVEL_ERROR:
            logErrorAction.setChecked(True)
        elif log_level == const.LOG_LEVEL_WARNING:
            logWarningAction.setChecked(True)
        elif log_level == const.LOG_LEVEL_INFO:
            logInfoAction.setChecked(True)
        elif log_level == const.LOG_LEVEL_VERBOSE:
            logVerboseAction.setChecked(True)
        elif log_level == const.LOG_LEVEL_DEBUG:
            logDebugAction.setChecked(True)
        else:
            LOG.warning('Invalid log level given: %r' % log_level)

        menubar.addMenu(log_menu)

        # Help Menu
        help_menu = QtWidgets.QMenu('Help', menubar)

        # Launch Help
        label = 'Help...'
        tooltip = 'Show help.'
        action = QtWidgets.QAction(label, help_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.launchHelpCB))
        help_menu.addAction(action)

        # Launch About
        label = 'About...'
        tooltip = 'About this software.'
        action = QtWidgets.QAction(label, help_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.launchAboutCB))
        help_menu.addAction(action)

        menubar.addMenu(help_menu)
        return

    def logErrorCB(self):
        LOG.debug('logErrorCB')
        lib_state.set_log_level(const.LOG_LEVEL_ERROR)

    def logWarningCB(self):
        LOG.debug('logWarningCB')
        lib_state.set_log_level(const.LOG_LEVEL_WARNING)

    def logInfoCB(self):
        LOG.debug('logInfoCB')
        lib_state.set_log_level(const.LOG_LEVEL_INFO)

    def logVerboseCB(self):
        LOG.debug('logVerboseCB')
        lib_state.set_log_level(const.LOG_LEVEL_VERBOSE)

    def logDebugCB(self):
        LOG.debug('logDebugCB')
        lib_state.set_log_level(const.LOG_LEVEL_DEBUG)

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
        createmarker_tool.create_marker()

    def convertToMarkerCB(self):
        """
        Converts all selected transform nodes into markers.
        """
        LOG.debug('convertToMarkerCB')
        convertmarker_tool.convert_to_marker()
        return

    def loadMarkerCB(self):
        """
        Open a UI where we can paste a file path in and press "ok". The UI
        could also show the point data before loading the file.
        """
        LOG.debug('loadMarkerCB')
        loadmarker_tool.open_window()

    def createBundleCB(self):
        """
        Create a Bundle node, attached to the selected markers.
        """
        LOG.debug('createBundleCB')
        createbundle_tool.create_bundle()

    def aimAtCameraCB(self):
        """
        Aim the selected nodes at the viewport camera.
        """
        LOG.debug('aimAtCameraCB')
        cameraaim_tool.aim_at_camera()

    def centerTwoDeeCB(self):
        """
        Center the viewport on the selected node.
        """
        LOG.debug('centerTwoDeeCB')
        centertwodee_tool.center_two_dee()

    def toggleMarkerBundleSelectionCB(self):
        LOG.debug('toggleMarkerBundleSelectionCB')
        selection_tool.swap_between_selected_markers_and_bundles()

    def selectBothMarkersAndBundlesCB(self):
        LOG.debug('selectBothMarkersAndBundlesCB')
        selection_tool.select_both_markers_and_bundles()

    def linkMarkerBundleCB(self):
        LOG.debug('linkMarkerBundleCB')
        link_mb_tool.link_marker_bundle()

    def unlinkMarkerBundleCB(self):
        LOG.debug('unlinkMarkerBundleCB')
        link_mb_tool.unlink_marker_bundle()

    @staticmethod
    def refreshActionToggledCB(value):
        LOG.warning('refreshActionToggledCB: %r', value)
        lib_state.set_refresh_viewport_state(value)

    def launchHelpCB(self):
        LOG.debug('launchHelpCB')
        self.help()

    def launchAboutCB(self):
        LOG.debug('launchAboutCB')

    def setStatusLine(self, text):
        self.subForm.setStatusLine(text)
        return

    def apply(self):
        LOG.debug('apply')
        self.setStatusLine(const.STATUS_EXECUTING)
        try:
            refresh_state = lib_state.get_refresh_viewport_state()
            log_level = lib_state.get_log_level()

            self.progressBar.setValue(0)
            self.progressBar.show()
            col = lib_state.get_active_collection()
            if col is None:
                msg = 'No active collection.'
                self.setStatusLine('ERROR: ' + msg)
                LOG.error(msg)
            ok = lib_collection.compile_collection(col)
            if ok is not True:
                msg = 'Cannot execute solver, collection is not valid.'
                msg += 'collection=%r'
                self.setStatusLine('Warning: ' + msg)
                LOG.warning(msg, col)
            else:
                lib_collection.execute_collection(
                    col,
                    log_level=log_level,
                    refresh=refresh_state,
                    prog_fn=self.progressBar.setValue,
                    status_fn=self.setStatusLine,
                )
        finally:
            self.progressBar.setValue(100)
            self.progressBar.hide()
            self.setStatusLine(const.STATUS_FINISHED)
        return

    def help(self):
        LOG.debug('help')
        return


def main(show=True, widthHeight=(800, 600)):
    # Force the Plug-in to load.  If the plug-in cannot load, the UI
    # will not open and an error will be given.
    lib_maya_utils.ensure_plugin_loaded()

    global UI

    valid = uiutils.isValidQtObject(UI)
    if UI is not None and valid is True:
        UI.close()

    name = 'SolverWindow'
    app, parent = uiutils.getParent()
    UI = SolverWindow(parent=parent, name=name)
    if not UI:
        return UI
    if show:
        UI.show()

    if ((isinstance(widthHeight, (tuple, list)) is True)
         and (len(widthHeight) == 2)):
        pos = UI.pos()
        UI.setGeometry(pos.x(), pos.y(), widthHeight[0], widthHeight[1])

    # Enter Qt application main loop
    if app is not None:
        sys.exit(app.exec_())
    return UI
