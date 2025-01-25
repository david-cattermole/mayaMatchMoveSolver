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
Solver Settings 'Basic' widget.
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
import mmSolver.tools.solver.widget.ui_solver_basic_widget as ui_solver_basic_widget
import mmSolver.tools.solver.widget.framerange_widget as framerange_widget
import mmSolver.tools.solver.constant as const

LOG = mmSolver.logger.get_logger()


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class BasicFrameRangeWidget(framerange_widget.FrameRangeWidget):
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


class SolverBasicWidget(QtWidgets.QWidget, ui_solver_basic_widget.Ui_Form):
    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()
    solverTypeChanged = QtCore.Signal()
    sceneGraphModeChanged = QtCore.Signal()
    evalComplexGraphsChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverBasicWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frameRange_widget = BasicFrameRangeWidget(self)
        self.frameRange_layout.addWidget(self.frameRange_widget)

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

        self.evalComplexGraphs_checkBox.toggled.connect(
            self.evalComplexGraphsValueToggled
        )

        self.solveFocalLength_checkBox.toggled.connect(
            self.solveFocalLengthValueToggled
        )
        self.solveLensDistortion_checkBox.toggled.connect(
            self.solveLensDistortionValueToggled
        )

        e = time.time()
        LOG.debug('SolverBasicWidget init: %r seconds', e - s)
        return

    def getDescriptionText(self):
        return const.SOLVER_BASIC_DESC_DEFAULT

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
        LOG.debug('UpdateModel Basic')
        self.frameRange_widget.updateModel()

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

        eval_complex_graphs = self.getEvalComplexGraphsValue(col)

        solve_focal_length = self.getSolveFocalLengthValue(col)
        solve_lens_distortion = self.getSolveLensDistortionValue(col)

        block = self.blockSignals(True)
        self.solverType_comboBox.setCurrentIndex(solver_type_index)
        self.sceneGraphMode_comboBox.setCurrentIndex(scene_graph_mode)
        self.evalComplexGraphs_checkBox.setChecked(eval_complex_graphs)
        self.solveFocalLength_checkBox.setChecked(solve_focal_length)
        self.solveLensDistortion_checkBox.setChecked(solve_lens_distortion)
        self.blockSignals(block)

        self.setSolverTypeValue(col, solver_type_value)
        self.setSceneGraphModeValue(col, scene_graph_mode)
        self.setEvalComplexGraphsValue(col, eval_complex_graphs)
        self.setSolveFocalLengthValue(col, solve_focal_length)
        self.setSolveLensDistortionValue(col, solve_lens_distortion)
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
