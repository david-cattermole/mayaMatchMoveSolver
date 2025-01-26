# Copyright (C) 2019, 2022 David Cattermole.
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
Solver Settings 'Camera' widget.
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
import mmSolver.tools.solver.widget.ui_solver_camera_widget as ui_solver_camera_widget
import mmSolver.tools.solver.widget.framerange_widget as framerange_widget
import mmSolver.tools.solver.widget.rootframe_widget as rootframe_widget
import mmSolver.tools.solver.constant as const
import mmSolver.tools.userpreferences.constant as userprefs_const
import mmSolver.tools.userpreferences.lib as userprefs_lib


LOG = mmSolver.logger.get_logger()


def get_user_prefs_solver_options_as_developer():
    config = userprefs_lib.get_config()
    key = userprefs_const.SOLVER_UI_SOLVER_OPTIONS_KEY
    value = userprefs_lib.get_value(config, key)
    return value == userprefs_const.SOLVER_UI_SOLVER_OPTIONS_DEVELOPER_VALUE


def _populateWidgetsEnabled(widgets):
    col = lib_state.get_active_collection()
    enabled = col is not None
    for widget in widgets:
        widget.setEnabled(enabled)
    return


class CameraRootFrameWidget(rootframe_widget.RootFrameWidget):
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


class CameraFrameRangeWidget(framerange_widget.FrameRangeWidget):
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


class SolverCameraWidget(QtWidgets.QWidget, ui_solver_camera_widget.Ui_Form):
    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()
    solverTypeChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverCameraWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frameRange_widget = CameraFrameRangeWidget(self)
        self.frameRange_layout.addWidget(self.frameRange_widget)

        self.rootFrames_widget = CameraRootFrameWidget(self)
        self.rootFrames_layout.addWidget(self.rootFrames_widget)

        self.originFrame_spinBox.valueChanged.connect(self.originFrameValueChanged)
        self.sceneScale_doubleSpinBox.valueChanged.connect(self.sceneScaleValueChanged)

        developer_options = get_user_prefs_solver_options_as_developer()
        solver_type_widget_visible = developer_options

        # Solver Type Combo Box.
        self.solverType_model = uimodels.StringDataListModel()
        self.solverType_model.setStringDataList(const.SOLVER_TYPE_LABEL_VALUE_LIST)
        self.solverType_comboBox.setModel(self.solverType_model)
        self.solverType_comboBox.currentIndexChanged.connect(
            self.solverTypeIndexChanged
        )
        self.solverType_comboBox.setVisible(solver_type_widget_visible)
        self.solverType_label.setVisible(solver_type_widget_visible)

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
        LOG.debug('SolverCameraWidget init: %r seconds', e - s)
        return

    def getDescriptionText(self):
        return const.SOLVER_CAM_DESC_DEFAULT

    def getSolverTypeValue(self, col):
        value = lib_col_state.get_solver_type_from_collection(col)
        return value

    def setSolverTypeValue(self, col, value):
        lib_col_state.set_solver_type_on_collection(col, value)
        return

    def getOriginFrameValue(self, col):
        value = lib_col_state.get_solver_origin_frame_from_collection(col)
        return value

    def setOriginFrameValue(self, col, value):
        lib_col_state.set_solver_origin_frame_on_collection(col, value)
        return

    def getSceneScaleValue(self, col):
        value = lib_col_state.get_solver_scene_scale_from_collection(col)
        return value

    def setSceneScaleValue(self, col, value):
        lib_col_state.set_solver_scene_scale_on_collection(col, value)
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

        range_type = self.frameRange_widget.getRangeTypeValue(col)
        origin_frame = self.getOriginFrameValue(col)
        scene_scale = self.getSceneScaleValue(col)
        solve_focal_length = self.getSolveFocalLengthValue(col)
        solve_lens_distortion = self.getSolveLensDistortionValue(col)
        origin_frame_enabled = True
        scene_scale_enabled = True
        frameRange_enabled = True
        rootFrames_enabled = True
        if range_type == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
            origin_frame_enabled = False
            scene_scale_enabled = False
            frameRange_enabled = True
            rootFrames_enabled = False

        block = self.blockSignals(True)
        self.solverType_comboBox.setCurrentIndex(solver_type_index)
        self.originFrame_spinBox.setValue(origin_frame)
        self.originFrame_spinBox.setEnabled(origin_frame_enabled)
        self.sceneScale_doubleSpinBox.setValue(scene_scale)
        self.sceneScale_doubleSpinBox.setEnabled(scene_scale_enabled)
        self.solveFocalLength_checkBox.setChecked(solve_focal_length)
        self.solveLensDistortion_checkBox.setChecked(solve_lens_distortion)
        self.frameRange_widget.setEnabled(frameRange_enabled)
        self.rootFrames_widget.setEnabled(rootFrames_enabled)
        self.blockSignals(block)

        self.setSolverTypeValue(col, solver_type_value)
        self.setOriginFrameValue(col, origin_frame)
        self.setSceneScaleValue(col, scene_scale)
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
    def originFrameValueChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setOriginFrameValue(col, value)
        return

    @QtCore.Slot(float)
    def sceneScaleValueChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setSceneScaleValue(col, value)
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
