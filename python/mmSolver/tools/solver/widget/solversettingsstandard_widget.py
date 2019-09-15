# Copyright (C) 2019 David Cattermole.
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
Solver Settings 'Standard' widget.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solversettingsstandard_widget as ui_solversettingsstandard_widget
import mmSolver.tools.solver.widget.framerange_widget as framerange_widget
import mmSolver.tools.solver.widget.rootframe_widget as rootframe_widget


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class StandardRootFrameWidget(rootframe_widget.RootFrameWidget):

    def getRootFramesValue(self, col):
        value = lib_col_state.get_solver_root_frames_from_collection(col)
        return value

    def setRootFramesValue(self, col, value):
        lib_col_state.set_solver_root_frames_on_collection(col, value)
        return


class StandardFrameRangeWidget(framerange_widget.FrameRangeWidget):

    def getRangeTypeValue(self, col):
        value = lib_col_state.get_solver_range_type_from_collection(col)
        return value

    def setRangeTypeValue(self, col, value):
        lib_col_state.set_solver_range_type_on_collection(col, value)
        return

    def getFramesValue(self, col):
        value = lib_col_state.get_solver_frames_from_collection(col)
        return value

    def setFramesValue(self, col, value):
        lib_col_state.set_solver_frames_on_collection(col, value)
        return

    def getIncrementByFrameValue(self, col):
        value = lib_col_state.get_solver_increment_by_frame_from_collection(col)
        return value

    def setIncrementByFrameValue(self, col, value):
        lib_col_state.set_solver_increment_by_frame_on_collection(col, value)
        return


class SolverSettingsStandardWidget(QtWidgets.QWidget,
                                   ui_solversettingsstandard_widget.Ui_Form):

    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()
    globalSolveChanged = QtCore.Signal()
    onlyRootFramesChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super(SolverSettingsStandardWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frameRange_widget = StandardFrameRangeWidget(self)
        self.frameRange_layout.addWidget(self.frameRange_widget)

        self.rootFrames_widget = StandardRootFrameWidget(self)
        self.rootFrames_layout.addWidget(self.rootFrames_widget)

        self.globalSolve_checkBox.toggled.connect(self.globalSolveValueToggled)
        self.onlyRootFrames_checkBox.toggled.connect(self.onlyRootFramesValueToggled)

        self.advanced_pushButton.setHidden(True)

        self.dataChanged.connect(self.updateModel)
        return

    def getOnlyRootFramesValue(self, col):
        value = lib_col_state.get_solver_only_root_frames_from_collection(col)
        return value

    def setOnlyRootFramesValue(self, col, value):
        lib_col_state.set_solver_only_root_frames_on_collection(col, value)
        return

    def getGlobalSolveValue(self, col):
        value = lib_col_state.get_solver_global_solve_from_collection(col)
        return value

    def setGlobalSolveValue(self, col, value):
        lib_col_state.set_solver_global_solve_on_collection(col, value)
        return

    def updateModel(self):
        self.frameRange_widget.updateModel()
        self.rootFrames_widget.updateModel()

        col = lib_state.get_active_collection()
        if col is None:
            return

        global_solve = self.getGlobalSolveValue(col)
        only_root_frames = self.getOnlyRootFramesValue(col)
        global_solve_enabled = True
        only_root_frames_enabled = True
        frameRange_enabled = True
        if global_solve is True:
            only_root_frames_enabled = False
            only_root_frames = False
        if only_root_frames is True:
            global_solve_enabled = False
            global_solve = False
            frameRange_enabled = False

        block = self.blockSignals(True)
        self.globalSolve_checkBox.setChecked(global_solve)
        self.globalSolve_checkBox.setEnabled(global_solve_enabled)
        self.onlyRootFrames_checkBox.setChecked(only_root_frames)
        self.onlyRootFrames_checkBox.setEnabled(only_root_frames_enabled)
        self.frameRange_widget.setEnabled(frameRange_enabled)
        self.blockSignals(block)

        self.setGlobalSolveValue(col, global_solve)
        self.setOnlyRootFramesValue(col, only_root_frames)
        return

    def queryInfo(self):
        param_num = 0
        dev_num = 0
        frm_num = 0

        text = 'Parameters {param} | Deviations {dev} | Frames {frm}'
        # NOTE: We can return HTML 'rich text' in this string to allow
        # the text to be bold or coloured to indicate warnings or
        # errors.
        
        text.format(
            param=param_num,
            dev=dev_num,
            frm=frm_num
        )
        return text

    @QtCore.Slot(bool)
    def onlyRootFramesValueToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        if value:
            # 'Global Solve' cannot be used at the same time as 'Only
            # Root Frames'
            self.setGlobalSolveValue(col, False)
            self.globalSolveChanged.emit()
        self.setOnlyRootFramesValue(col, value)
        self.onlyRootFramesChanged.emit()
        self.dataChanged.emit()
        return

    @QtCore.Slot(bool)
    def globalSolveValueToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        if value:
            # 'Only Root Frames' is only valid if 'Global Solve' is off.
            self.setOnlyRootFramesValue(col, False)
            self.onlyRootFramesChanged.emit()
        self.setGlobalSolveValue(col, value)
        self.globalSolveChanged.emit()
        self.dataChanged.emit()
        return
