# Copyright (C) 2018, 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
The main window for the 'Solver' tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import datetime
import uuid
from functools import partial

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt as Qt
import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.constant as const
import mmSolver.tools.solver.maya_callbacks as maya_callbacks
import mmSolver.tools.solver.ui.solver_layout as solver_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    helputils.open_help_in_browser(page='tools_solver_ui.html', help_source=src)
    return


class SolverWindow(BaseWindow):

    name = 'SolverWindow'

    def __init__(self, parent=None, name=None):
        s = time.time()
        s1 = time.time()
        super(SolverWindow, self).__init__(parent, name=name)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)
        self.setupUi(self)
        self.addSubForm(solver_layout.SolverLayout)
        self.setStatusLine(const.STATUS_READY)
        self._saved_ui_size = QtCore.QSize()

        # Menu Bar
        self.addMenuBarContents(self.menubar)
        self.menubar.show()

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText(const.WINDOW_BUTTON_SOLVE_START_LABEL)
        self.closeBtn.setText(const.WINDOW_BUTTON_CLOSE_LABEL)

        self.applyBtn.clicked.connect(self.apply)

        # Hide irrelevant stuff
        self.baseHideProgressBar()
        e1 = time.time()
        s2 = time.time()

        # Callbacks
        self.callback_manager = maya_callbacks.CallbackManager()

        # Add Maya callback to track Selection
        callback_ids = maya_callbacks.add_selection_changed_callback(self)
        self.callback_manager.add_node_ids(
            maya_callbacks.TYPE_SELECTION_CHANGED,
            None,
            callback_ids,
        )

        # Add Maya callbacks for the UI
        callback_ids = maya_callbacks.add_callbacks_new_scene(self)
        self.callback_manager.add_node_ids(
            maya_callbacks.TYPE_NEW_SCENE,
            None,
            callback_ids,
        )
        e2 = time.time()
        e = time.time()
        LOG.debug('SolverWindow init: %r seconds', e - s)
        LOG.debug('SolverWindow initA: %r seconds', e1 - s1)
        LOG.debug('SolverWindow initB: %r seconds', e2 - s2)
        return

    def __del__(self):
        """
        Release all resources held by the class.
        """
        callback_ids = list(self.callback_manager.get_all_ids())
        maya_callbacks.remove_callbacks(callback_ids)
        del self.callback_manager

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
        label = 'Rename Collection...'
        tooltip = 'Rename a Collection node.'
        action = QtWidgets.QAction(label, file_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(partial(self.renameCollectionNodeCB))
        file_menu.addAction(action)

        file_menu.addSeparator()

        # Remove Collection
        label = 'Remove Collection...'
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

        # Edit Menu
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        edit_menu.setTearOffEnabled(True)

        # Solver Preferences
        label = 'Solver Preferences...'
        tooltip = 'Adjust how the solver displays and executes.'
        action = QtWidgets.QAction(label, edit_menu)
        action.setStatusTip(tooltip)
        action.triggered.connect(self.solverPrefWindowTriggeredCB)
        edit_menu.addAction(action)

        # View Menu
        view_menu = QtWidgets.QMenu('View', menubar)
        view_menu.setTearOffEnabled(True)

        if Qt.IsPySide2 or Qt.IsPyQt5:
            view_menu.addSection('Input Object Display')

        # Display Object Weight
        label = 'Weight Column'
        tooltip = 'Display Object weight column'
        value = lib_state.get_display_object_weight_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(self.subForm.object_browser.displayWeightColumnChanged)
        view_menu.addAction(action)

        # Display Object Frame Deviation
        label = 'Frame Deviation'
        tooltip = 'Display per-frame deviation for each Marker/Camera.'
        value = lib_state.get_display_object_frame_deviation_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(
            self.subForm.object_browser.displayFrameDeviationColumnChanged
        )
        view_menu.addAction(action)

        # Display Object Average Deviation
        label = 'Average Deviation'
        tooltip = 'Display average deviation column'
        value = lib_state.get_display_object_average_deviation_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(
            self.subForm.object_browser.displayAverageDeviationColumnChanged
        )
        view_menu.addAction(action)

        # Display Object Maximum Deviation
        label = 'Maximum Deviation'
        tooltip = 'Display maximum deviation column'
        value = lib_state.get_display_object_maximum_deviation_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(
            self.subForm.object_browser.displayMaximumDeviationColumnChanged
        )
        view_menu.addAction(action)

        if Qt.IsPySide2 or Qt.IsPyQt5:
            view_menu.addSection('Output Attribute Display')

        # Display Attribute State
        label = 'Display Attribute State'
        tooltip = 'Display Attribute State column'
        value = lib_state.get_display_attribute_state_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(self.subForm.attribute_browser.displayStateColumnChanged)
        view_menu.addAction(action)

        # Display Attribute Min/Max
        label = 'Display Attribute Min/Max'
        tooltip = 'Display Attribute Minimum and Maximum columns'
        value = lib_state.get_display_attribute_min_max_state()
        action = QtWidgets.QAction(label, view_menu)
        action.setStatusTip(tooltip)
        action.setCheckable(True)
        action.setChecked(value)
        action.toggled.connect(
            self.subForm.attribute_browser.displayMinMaxColumnChanged
        )
        view_menu.addAction(action)

        menubar.addMenu(view_menu)

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
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
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
        self.subForm.collection_widget.createNewNode()
        return

    def renameCollectionNodeCB(self):
        self.subForm.collection_widget.renameActiveNode()
        return

    def removeCollectionNodeCB(self):
        self.subForm.collection_widget.removeActiveNode()
        return

    def setActiveCollection(self, col):
        assert isinstance(col, mmapi.Collection)
        lib_state.set_active_collection(col)
        self.triggerCollectionUpdate()
        return

    def triggerCollectionUpdate(self):
        self.subForm.collection_widget.itemChanged.emit()
        return

    def triggerInputObjectsUpdate(self):
        self.subForm.object_browser.dataChanged.emit()
        return

    def triggerOutputAttributesUpdate(self):
        self.subForm.attribute_browser.dataChanged.emit()
        return

    def solverPrefWindowTriggeredCB(self):
        LOG.debug('solverPrefWindowTriggeredCB')
        return

    @staticmethod
    def refreshActionToggledCB(value):
        lib_state.set_refresh_viewport_state(value)
        return

    @staticmethod
    def forceDgUpdateActionToggledCB(value):
        lib_state.set_force_dg_update_state(value)
        return

    @staticmethod
    def preSolveForceEvalActionToggledCB(value):
        lib_state.set_pre_solve_force_eval_state(value)
        return

    @staticmethod
    def isolateObjectWhileSolvingActionToggledCB(value):
        lib_state.set_isolate_object_while_solving_state(value)
        return

    @staticmethod
    def displayImagePlaneWhileSolvingActionToggledCB(value):
        lib_state.set_display_image_plane_while_solving_state(value)
        return

    @staticmethod
    def displayMeshesWhileSolvingActionToggledCB(value):
        lib_state.set_display_meshes_while_solving_state(value)
        return

    @QtCore.Slot(list)
    def setNodeSelection(self, values):
        if uiutils.isValidQtObject(self) is True:
            self.subForm.object_browser.setNodeSelection(values)
            self.subForm.attribute_browser.setNodeSelection(values)
        return

    def setStatusLine(self, text):
        if uiutils.isValidQtObject(self) is True:
            self.subForm.setStatusLine(text)
        QtWidgets.QApplication.processEvents()
        return

    def setSolveInfoLine(self, text):
        if uiutils.isValidQtObject(self) is True:
            self.subForm.setSolveInfoLine(text)
        QtWidgets.QApplication.processEvents()
        return

    def setProgressValue(self, value):
        if uiutils.isValidQtObject(self) is True:
            self.progressBar.setValue(value)
        QtWidgets.QApplication.processEvents()
        return

    def setMinimalUI(self, value):
        """
        Change the currently open Solver window to be "minimal", or not.

        If the Solver window is not open, nothing happens.

        "minimal" UI means hiding most widgets in the Solver UI, and not
        "minimal" means showing all widgets as a user normally would
        expect.
        """
        assert isinstance(value, bool)

        def _set_widget_visibility(window, visible):
            self.menubar.setVisible(visible)
            self.subForm.collection_widget.setVisible(visible)
            self.subForm.object_browser.setVisible(visible)
            self.subForm.attribute_browser.setVisible(visible)
            self.subForm.solver_settings.setVisible(visible)
            self.subForm.ui.objectAttribute_splitter.setVisible(visible)
            self.subForm.ui.line_1.setVisible(visible)
            self.subForm.ui.line_2.setVisible(visible)

        if uiutils.isValidQtObject(self) is True:
            QtWidgets.QApplication.processEvents()
            if value is False:
                _set_widget_visibility(self, True)

                # Restore non-minimal window size.
                QtWidgets.QApplication.processEvents()
                self.resize(self._saved_ui_size)
            else:
                self._saved_ui_size = self.size()

                # TODO: Can we find out how many pending events ther
                # eare so we can call 'processEvents' that many times?

                QtWidgets.QApplication.processEvents()
                _set_widget_visibility(self, False)

                # Resize the bottom window edge upwards.
                width = self.size().width()
                self.resize(width, 1)
                QtWidgets.QApplication.processEvents()

                # Run again to trigger the UI to resize properly.
                _set_widget_visibility(self, False)
                self.resize(width, 1)
                QtWidgets.QApplication.processEvents()

        QtWidgets.QApplication.processEvents()
        return

    def apply(self):
        """
        This button launches a solve, but can also be used to cancel a solve.
        """
        running_state = lib_state.get_solver_is_running_state()
        if running_state is True:
            # Cancel out of a running solve if the user presses
            # the button again.
            lib_state.set_solver_user_interrupt_state(True)
            return
        if uiutils.isValidQtObject(self) is False:
            return
        undo_id = 'mmSolver: '
        undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
        undo_id += ' '
        undo_id += str(uuid.uuid4())
        with tools_utils.tool_context(
            use_undo_chunk=True,
            undo_chunk_name=undo_id,
            restore_current_frame=False,
            pre_update_frame=False,
            post_update_frame=False,
            use_dg_evaluation_mode=True,
            disable_viewport=False,
        ):
            block = self.blockSignals(True)
            try:
                mmapi.set_solver_running(True)
                self.applyBtn.setText(const.WINDOW_BUTTON_SOLVE_STOP_LABEL)
                self.closeBtn.setText(const.WINDOW_BUTTON_CLOSE_AND_STOP_LABEL)
                options = lib_collection.gather_execute_options()
                log_level = lib_state.get_log_level()
                col = lib_state.get_active_collection()
                lib_collection.run_solve_ui(col, options, log_level, self)
            finally:
                mmapi.set_solver_running(False)
                if uiutils.isValidQtObject(self) is True:
                    self.applyBtn.setText(const.WINDOW_BUTTON_SOLVE_START_LABEL)
                    self.closeBtn.setText(const.WINDOW_BUTTON_CLOSE_LABEL)
                    self.blockSignals(block)
        return

    def closeEvent(self, event):
        # Cancel out of a running solve, before closing the UI.
        running_state = lib_state.get_solver_is_running_state()
        if running_state is True:
            lib_state.set_solver_user_interrupt_state(True)
        super(SolverWindow, self).closeEvent(event)
        return


def loadAllResources():
    base_install_location = os.environ.get('MMSOLVER_LOCATION', None)
    assert base_install_location is not None
    fallback = os.path.join(base_install_location, 'resources')
    resource_paths = os.environ.get('MMSOLVER_RESOURCE_PATH', fallback)
    assert isinstance(resource_paths, pycompat.TEXT_TYPE)
    resource_paths = resource_paths.split(os.pathsep)
    for directory_path in resource_paths:
        if not os.path.isdir(directory_path):
            continue
        file_names = os.listdir(directory_path)
        for file_name in file_names:
            if not file_name.endswith('.rcc'):
                continue
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                is_registered = QtCore.QResource.registerResource(file_path)
                if is_registered:
                    LOG.debug("Resource registered: %r", file_path)
                else:
                    LOG.error("Resource failed to register: %r", file_path)
    return


def main(show=True, auto_raise=True, delete=False, dock=True):
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
    loadAllResources()

    win = SolverWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete, dock=dock
    )
    return win
