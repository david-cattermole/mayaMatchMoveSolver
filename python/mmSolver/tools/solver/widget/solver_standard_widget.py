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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solver_standard_widget as ui_solver_standard_widget
import mmSolver.tools.solver.widget.framerange_widget as framerange_widget
import mmSolver.tools.solver.widget.rootframe_widget as rootframe_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class StandardRootFrameWidget(rootframe_widget.RootFrameWidget):
    def getUserFramesValue(self, col):
        value = lib_col_state.get_solver_user_frames_from_collection(col)
        return value

    def setUserFramesValue(self, col, value):
        lib_col_state.set_solver_user_frames_on_collection(col, value)
        return

    def getUsePerMarkerFramesValue(self, col):
        value = lib_col_state.get_solver_use_per_marker_frames_from_collection(col)
        return value

    def setUsePerMarkerFramesValue(self, col, value):
        lib_col_state.set_solver_use_per_marker_frames_on_collection(col, value)

    def getPerMarkerFramesValue(self, col):
        value = lib_col_state.get_solver_per_marker_frames_from_collection(col)
        return value

    def setPerMarkerFramesValue(self, col, value):
        lib_col_state.set_solver_per_marker_frames_on_collection(col, value)

    def getUseSpanFramesValue(self, col):
        value = lib_col_state.get_solver_use_span_frames_from_collection(col)
        return value

    def setUseSpanFramesValue(self, col, value):
        lib_col_state.set_solver_use_span_frames_on_collection(col, value)

    def getSpanFramesValue(self, col):
        value = lib_col_state.get_solver_span_frames_from_collection(col)
        return value

    def setSpanFramesValue(self, col, value):
        lib_col_state.set_solver_span_frames_on_collection(col, value)

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


class SolverStandardWidget(QtWidgets.QWidget, ui_solver_standard_widget.Ui_Form):
    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()
    globalSolveChanged = QtCore.Signal()
    onlyRootFramesChanged = QtCore.Signal()
    solverTypeChanged = QtCore.Signal()
    sceneGraphModeChanged = QtCore.Signal()
    evalComplexGraphsChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverStandardWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frameRange_widget = StandardFrameRangeWidget(self)
        self.frameRange_layout.addWidget(self.frameRange_widget)

        self.rootFrames_widget = StandardRootFrameWidget(self)
        self.rootFrames_layout.addWidget(self.rootFrames_widget)

        # Solver Type Combo Box.
        self.solverType_model = uimodels.StringDataListModel()
        self.solverType_model.setStringDataList(const.SOLVER_TYPE_LABEL_VALUE_LIST)
        self.solverType_comboBox.setModel(self.solverType_model)
        self.solverType_comboBox.currentIndexChanged.connect(
            self.solverTypeIndexChanged
        )
        self.solverType_comboBox.setVisible(const.SOLVER_TYPE_WIDGET_VISIBLE)
        self.solverType_label.setVisible(const.SOLVER_TYPE_WIDGET_VISIBLE)

        # Scene Graph Mode Combo Box.
        self.sceneGraphMode_model = uimodels.StringDataListModel()
        self.sceneGraphMode_model.setStringDataList(
            const.SCENE_GRAPH_MODE_LABEL_VALUE_LIST
        )
        self.sceneGraphMode_comboBox.setModel(self.sceneGraphMode_model)
        self.sceneGraphMode_comboBox.currentIndexChanged.connect(
            self.sceneGraphModeIndexChanged
        )
        self.sceneGraphMode_comboBox.setVisible(const.SCENE_GRAPH_MODE_WIDGET_VISIBLE)
        self.sceneGraphMode_label.setVisible(const.SCENE_GRAPH_MODE_WIDGET_VISIBLE)

        self.globalSolve_checkBox.toggled.connect(self.globalSolveValueToggled)
        self.onlyRootFrames_checkBox.toggled.connect(self.onlyRootFramesValueToggled)

        self.evalComplexGraphs_checkBox.toggled.connect(
            self.evalComplexGraphsValueToggled
        )
        self.solveFocalLength_checkBox.toggled.connect(
            self.solveFocalLengthValueToggled
        )
        self.solveLensDistortion_checkBox.toggled.connect(
            self.solveLensDistortionValueToggled
        )

        self.dataChanged.connect(self.updateModel)
        self.frameRange_widget.rangeTypeChanged.connect(self.updateModel)
        self.rootFrames_widget.sendWarning.connect(self._sendWarningToUser)
        e = time.time()
        LOG.debug('SolverStandardWidget init: %r seconds', e - s)
        return

    def getDescriptionText(self):
        return const.SOLVER_STD_DESC_DEFAULT

    def getSolverTypeValue(self, col):
        value = lib_col_state.get_solver_type_from_collection(col)
        return value

    def setSolverTypeValue(self, col, value):
        lib_col_state.set_solver_type_on_collection(col, value)
        return

    def getSceneGraphModeValue(self, col):
        value = lib_col_state.get_solver_scene_graph_mode_from_collection(col)
        return value

    def setSceneGraphModeValue(self, col, value):
        lib_col_state.set_solver_scene_graph_mode_on_collection(col, value)
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

    def getEvalComplexGraphsValue(self, col):
        value = lib_col_state.get_solver_eval_complex_graphs_from_collection(col)
        return value

    def setEvalComplexGraphsValue(self, col, value):
        lib_col_state.set_solver_eval_complex_graphs_on_collection(col, value)
        return

    def getSolveFocalLengthValue(self, col):
        value = lib_col_state.get_solver_solve_focal_length_from_collection(col)
        return value

    def setSolveFocalLengthValue(self, col, value):
        lib_col_state.set_solver_solve_focal_length_on_collection(col, value)
        return

    def getSolveLensDistortionValue(self, col):
        value = lib_col_state.get_solver_solve_lens_distortion_from_collection(col)
        return value

    def setSolveLensDistortionValue(self, col, value):
        lib_col_state.set_solver_solve_lens_distortion_on_collection(col, value)
        return

    def getSolverTypeActiveIndex(self, model, col):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        if col is None:
            return None
        active_node = col.get_node()
        if active_node is None:
            return None
        value = self.getSolverTypeValue(col)
        string_data_list = model.stringDataList()
        data_list = [data for string, data in string_data_list]
        index = None
        if value in data_list:
            index = data_list.index(value)
        return index

    def getSceneGraphActiveIndex(self, model, col):
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        if col is None:
            return None
        active_node = col.get_node()
        if active_node is None:
            return None
        value = self.getSceneGraphModeValue(col)
        string_data_list = model.stringDataList()
        data_list = [data for string, data in string_data_list]
        index = None
        if value in data_list:
            index = data_list.index(value)
        return index

    def updateModel(self):
        self.frameRange_widget.updateModel()
        self.rootFrames_widget.updateModel()

        col = lib_state.get_active_collection()
        if col is None:
            return

        solver_type_value = self.getSolverTypeValue(col)
        solver_type_index = self.getSolverTypeActiveIndex(self.solverType_model, col)
        if solver_type_index is None:
            LOG.error('Could not get the active solver type index.')
            return

        scene_graph_mode = self.getSceneGraphActiveIndex(self.sceneGraphMode_model, col)
        if scene_graph_mode is None:
            LOG.error('Could not get the active scene graph mode index.')
            return

        range_type = self.frameRange_widget.getRangeTypeValue(col)
        global_solve = self.getGlobalSolveValue(col)
        only_root_frames = self.getOnlyRootFramesValue(col)
        eval_complex_graphs = self.getEvalComplexGraphsValue(col)
        solve_focal_length = self.getSolveFocalLengthValue(col)
        solve_lens_distortion = self.getSolveLensDistortionValue(col)
        global_solve_enabled = True
        only_root_frames_enabled = True
        eval_complex_graphs_enabled = True
        frameRange_enabled = True
        rootFrames_enabled = True
        if range_type == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
            global_solve_enabled = False
            only_root_frames_enabled = False
            eval_complex_graphs_enabled = False
            frameRange_enabled = True
            rootFrames_enabled = False
        else:
            if global_solve is True:
                only_root_frames_enabled = False
                only_root_frames = False
                eval_complex_graphs_enabled = False
                rootFrames_enabled = True
                frameRange_enabled = True
            if only_root_frames is True:
                global_solve_enabled = False
                global_solve = False
                frameRange_enabled = False
                rootFrames_enabled = True
                eval_complex_graphs_enabled = True

        block = self.blockSignals(True)
        self.globalSolve_checkBox.setChecked(global_solve)
        self.globalSolve_checkBox.setEnabled(global_solve_enabled)
        self.onlyRootFrames_checkBox.setChecked(only_root_frames)
        self.onlyRootFrames_checkBox.setEnabled(only_root_frames_enabled)
        self.solverType_comboBox.setCurrentIndex(solver_type_index)
        self.sceneGraphMode_comboBox.setCurrentIndex(scene_graph_mode)
        self.evalComplexGraphs_checkBox.setChecked(eval_complex_graphs)
        self.evalComplexGraphs_checkBox.setEnabled(eval_complex_graphs_enabled)
        self.solveFocalLength_checkBox.setChecked(solve_focal_length)
        self.solveLensDistortion_checkBox.setChecked(solve_lens_distortion)
        self.frameRange_widget.setEnabled(frameRange_enabled)
        self.rootFrames_widget.setEnabled(rootFrames_enabled)
        self.blockSignals(block)

        self.setGlobalSolveValue(col, global_solve)
        self.setOnlyRootFramesValue(col, only_root_frames)
        self.setSolverTypeValue(col, solver_type_value)
        self.setSceneGraphModeValue(col, scene_graph_mode)
        self.setEvalComplexGraphsValue(col, eval_complex_graphs)
        self.setSolveFocalLengthValue(col, solve_focal_length)
        self.setSolveLensDistortionValue(col, solve_lens_distortion)
        return

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

        block = self.blockSignals(True)
        self.frameRange_widget.setEnabled(not value)
        self.globalSolve_checkBox.setEnabled(not value)
        self.blockSignals(block)

        self.setOnlyRootFramesValue(col, value)
        self.onlyRootFramesChanged.emit()
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

        # "Evaluate Complex Graphs" causes the solver to evaluate
        # time per-frame, so it's not possible to use with "Global
        # Solve" - therefore it's disabled.
        block = self.blockSignals(True)
        self.evalComplexGraphs_checkBox.setEnabled(not value)
        self.onlyRootFrames_checkBox.setEnabled(not value)
        self.blockSignals(block)

        self.setGlobalSolveValue(col, value)
        self.globalSolveChanged.emit()
        return

    @QtCore.Slot(int)
    def solverTypeIndexChanged(self, index):
        if index < 0:
            return
        col = lib_state.get_active_collection()
        if col is None:
            return
        model_index = self.solverType_model.index(index, 0)
        data = self.solverType_model.data(model_index, role=QtCore.Qt.UserRole)
        if data is None:
            return
        assert isinstance(data, pycompat.INT_TYPES)
        self.setSolverTypeValue(col, data)
        self.solverTypeChanged.emit()
        return

    @QtCore.Slot(int)
    def sceneGraphModeIndexChanged(self, index):
        if index < 0:
            return
        col = lib_state.get_active_collection()
        if col is None:
            return
        model_index = self.sceneGraphMode_model.index(index, 0)
        data = self.sceneGraphMode_model.data(model_index, role=QtCore.Qt.UserRole)
        if data is None:
            return
        assert isinstance(data, pycompat.INT_TYPES)
        self.setSceneGraphModeValue(col, data)
        self.sceneGraphModeChanged.emit()
        return

    @QtCore.Slot(bool)
    def evalComplexGraphsValueToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setEvalComplexGraphsValue(col, value)
        self.evalComplexGraphsChanged.emit()
        return

    @QtCore.Slot(bool)
    def solveFocalLengthValueToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setSolveFocalLengthValue(col, value)
        return

    @QtCore.Slot(bool)
    def solveLensDistortionValueToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setSolveLensDistortionValue(col, value)
        return

    @QtCore.Slot(str)
    def _sendWarningToUser(self, value):
        self.sendWarning.emit(value)
        return
