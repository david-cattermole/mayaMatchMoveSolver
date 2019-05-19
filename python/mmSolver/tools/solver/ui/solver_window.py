"""
The main window for the 'Solver' tool.
"""

import sys
from functools import partial

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.constant as const
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.ui.solver_layout as solver_layout
import mmSolver.tools.loadmarker.tool as loadmarker_tool
import mmSolver.tools.selection.tools as selection_tool
import mmSolver.tools.createmarker.tool as createmarker_tool
import mmSolver.tools.createbundle.tool as createbundle_tool
import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
import mmSolver.tools.convertmarker.tool as convertmarker_tool
import mmSolver.tools.markerbundlerename.tool as mbrename_tool


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class SolverWindow(BaseWindow):

    name = 'SolverWindow'

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

        # Rename Marker + Bundle
        label = 'Rename Markers + Bundles'
        tooltip = 'Rename the selected Markers and Bundles;'
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.renameMarkerBundleCB))
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

        # Force DG evaluation.
        label = 'Force DG Update'
        tooltip = 'Force Maya DG Evaluation while solving.'
        force_dg_update_value = lib_state.get_force_dg_update_state()
        action = QtWidgets.QAction(label, tools_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(force_dg_update_value)
        action.toggled.connect(type(self).forceDgUpdateActionToggledCB)
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

        # # Launch About
        # label = 'About...'
        # tooltip = 'About this software.'
        # action = QtWidgets.QAction(label, help_menu)
        # action.setStatusTip(tooltip)
        # action.triggered.connect(partial(self.launchAboutCB))
        # help_menu.addAction(action)

        menubar.addMenu(help_menu)
        return

    def logErrorCB(self):
        lib_state.set_log_level(const.LOG_LEVEL_ERROR)

    def logWarningCB(self):
        lib_state.set_log_level(const.LOG_LEVEL_WARNING)

    def logInfoCB(self):
        lib_state.set_log_level(const.LOG_LEVEL_INFO)

    def logVerboseCB(self):
        lib_state.set_log_level(const.LOG_LEVEL_VERBOSE)

    def logDebugCB(self):
        lib_state.set_log_level(const.LOG_LEVEL_DEBUG)

    def createNewCollectionNodeCB(self):
        self.subForm.createNewCollectionNode()
        return

    def renameCollectionNodeCB(self):
        self.subForm.renameCollectionNode()
        return

    def removeCollectionNodeCB(self):
        self.subForm.removeCollectionNode()
        return

    def createMarkerCB(self):
        """
        Create a Marker under the active viewport camera.
        """
        createmarker_tool.main()

    def convertToMarkerCB(self):
        """
        Converts all selected transform nodes into markers.
        """
        convertmarker_tool.main()
        return

    def loadMarkerCB(self):
        """
        Open a UI where we can paste a file path in and press "ok". The UI
        could also show the point data before loading the file.
        """
        loadmarker_tool.open_window()

    def createBundleCB(self):
        """
        Create a Bundle node, attached to the selected markers.
        """
        createbundle_tool.main()

    def toggleMarkerBundleSelectionCB(self):
        selection_tool.swap_between_selected_markers_and_bundles()

    def selectBothMarkersAndBundlesCB(self):
        selection_tool.select_both_markers_and_bundles()

    def renameMarkerBundleCB(self):
        """
        Rename the selected markers and bundles (with a prompt window).
        """
        mbrename_tool.main()

    def linkMarkerBundleCB(self):
        link_mb_tool.link_marker_bundle()

    def unlinkMarkerBundleCB(self):
        link_mb_tool.unlink_marker_bundle()

    @staticmethod
    def refreshActionToggledCB(value):
        lib_state.set_refresh_viewport_state(value)

    @staticmethod
    def forceDgUpdateActionToggledCB(value):
        lib_state.set_force_dg_update_state(value)

    def launchHelpCB(self):
        self.help()

    # def launchAboutCB(self):
    #     # LOG.info('Launch About... not yet.')
    #     self.help()

    def setStatusLine(self, text):
        self.subForm.setStatusLine(text)
        QtWidgets.QApplication.processEvents()
        return

    def setProgressValue(self, value):
        self.progressBar.setValue(value)
        QtWidgets.QApplication.processEvents()
        return

    def apply(self):
        """
        Tbis button launches a solve, but can also be used to cancel a solve.
        """
        running_state = lib_state.get_solver_is_running_state()
        if running_state is True:
            lib_state.set_solver_user_interrupt_state(True)
            return
        refresh_state = lib_state.get_refresh_viewport_state()
        force_update_state = lib_state.get_force_dg_update_state()
        log_level = lib_state.get_log_level()
        col = lib_state.get_active_collection()
        lib_collection.run_solve_ui(
            col,
            refresh_state,
            force_update_state,
            log_level,
            self)
        return

    def help(self):
        src = helputils.get_help_source()
        helputils.open_help_in_browser(
            page='tools.html#solver-ui',
            help_source=src)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Solver UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: SolverWindow or None.
    """
    # Force the Plug-in to load.  If the plug-in cannot load, the UI
    # will not open and an error will be given.
    lib_maya_utils.ensure_plugin_loaded()

    win = SolverWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
