# Copyright (C) 2026 David Cattermole.
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
Camera Solver layout - all interactive logic for the Camera Solver window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import uuid

import maya.cmds

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.ui.uiutils as uiutils

import mmSolver.tools.camerasolver.constant as const
import mmSolver.tools.camerasolver.lib as lib

import mmSolver.tools.camerasolver.ui.ui_camerasolver_layout as ui_camerasolver_layout


LOG = mmSolver.logger.get_logger()

# Lookup tables derived from the ordered index lists in constant.py.
#
# TODO: Hard-code these variables and move them to the constant.py
# file.
_ADJUSTMENT_SOLVER_CONST_TO_INDEX = {
    v: i for i, v in enumerate(const.ADJUSTMENT_SOLVER_TYPE_INDEX_LIST)
}
_LOG_LEVEL_CONST_TO_INDEX = {v: i for i, v in enumerate(const.LOG_LEVEL_INDEX_LIST)}


def find_group_box_spacer(outer_layout, widget_before, widget_after):
    """Return the QSpacerItem sitting between two widgets in a layout, or None.

    Searches for the first spacer item in *outer_layout* that is positioned
    between the indices of *widget_before* and *widget_after*.
    """
    # type: (...) -> QtWidgets.QSpacerItem | None
    before_index = -1
    after_index = -1
    for i in range(outer_layout.count()):
        item = outer_layout.itemAt(i)
        widget = item.widget() if item is not None else None
        if widget is widget_before:
            before_index = i
        elif widget is widget_after:
            after_index = i
    if before_index >= 0 and after_index > before_index:
        for i in range(before_index + 1, after_index):
            item = outer_layout.itemAt(i)
            if item is not None and item.spacerItem() is not None:
                return item.spacerItem()
    return None


def build_adjustment_attributes(
    focal_length_range_mode,
    focal_length_percentage,
    focal_length_min,
    focal_length_max,
    focal_length_samples,
    camera,
):
    """Build an AdjustmentAttributes object from UI widget values.

    When *focal_length_range_mode* is
    ``FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX`` the min/max are derived
    from the camera's current focal length and *focal_length_percentage*.
    Otherwise *focal_length_min* and *focal_length_max* are used directly.

    :param focal_length_range_mode: One of the ``FOCAL_LENGTH_RANGE_MODE_*`` constants.
    :type focal_length_range_mode: int

    :param focal_length_percentage: Search range percentage (e.g. 20.0).
    :type focal_length_percentage: float

    :param focal_length_min: Explicit minimum focal length (mm).
    :type focal_length_min: float

    :param focal_length_max: Explicit maximum focal length (mm).
    :type focal_length_max: float

    :param focal_length_samples: Number of samples in the search range.
    :type focal_length_samples: int

    :param camera: Camera used to read the current focal length when in
                   percentage mode.  May be None.
    :type camera: mmapi.Camera or None

    :rtype: lib.AdjustmentAttributes
    """
    # type: (...) -> lib.AdjustmentAttributes
    assert isinstance(focal_length_range_mode, int)
    assert isinstance(focal_length_percentage, float)
    assert isinstance(focal_length_min, float)
    assert isinstance(focal_length_max, float)
    assert isinstance(focal_length_samples, int)
    assert focal_length_samples > 0
    assert camera is None or isinstance(camera, mmapi.Camera)
    if focal_length_range_mode == const.FOCAL_LENGTH_RANGE_MODE_MIN_MAX_INDEX:
        computed_min = focal_length_min
        computed_max = focal_length_max
    else:
        # FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX: derive bounds from the
        # camera's current focal length.
        focal_length_mm = lib.get_camera_focal_length(camera)
        computed_min, computed_max = lib.compute_focal_length_min_max_from_percentage(
            focal_length_mm, focal_length_percentage
        )

    if computed_max <= computed_min:
        computed_max = computed_min + 0.1

    return lib.make_adjustment_attributes(
        computed_min, computed_max, focal_length_samples
    )


class CameraSolverLayout(QtWidgets.QWidget, ui_camerasolver_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        # type: (...) -> None
        super(CameraSolverLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self._camera = None
        self._lens = None
        self._mkr_list = []
        self._output_directory = None
        self._prefix_name = None
        self._solver_process = None
        self._log_line_count = 0

        self._poll_timer = QtCore.QTimer(self)
        self._poll_timer.setInterval(200)
        self._poll_timer.timeout.connect(self.pollSolve)

        # Stores the long-name camera transforms parallel to the
        # comboBox items for 1:1 direct mapping.
        self._camera_nodes = []

        # Find the expanding spacer between adjustFocalLength_groupBox and
        # log_groupBox so we can collapse/expand it when toggling the log.
        self._group_box_spacer = find_group_box_spacer(
            self.layout(),
            self.adjustFocalLength_groupBox,
            self.log_groupBox,
        )
        self.applyLogLayoutState(log_visible=True)

        self.populateUi()
        self.createConnections()

    def createConnections(self):
        # type: () -> None
        connection_type = QtCore.Qt.UniqueConnection
        self.camera_refresh_pushButton.clicked.connect(
            self.cameraRefreshClicked, connection_type
        )
        self.camera_comboBox.currentIndexChanged.connect(
            self.onCameraChanged, connection_type
        )
        self.frameRange_comboBox.currentIndexChanged.connect(
            self.updateFrameRangeState, connection_type
        )
        self.focalLengthRange_comboBox.currentIndexChanged.connect(
            self.updateFocalLengthRangeState, connection_type
        )
        self.focalLengthPercentage_doubleSpinBox.valueChanged.connect(
            self.updateFocalLengthFromPercentage, connection_type
        )
        self.adjustmentSolver_comboBox.currentIndexChanged.connect(
            self.updateAdjustmentSolverState, connection_type
        )
        self.logToggle_pushButton.clicked.connect(self.toggleLog, connection_type)
        self.solve_pushButton.clicked.connect(self.startSolveClicked, connection_type)
        self.applySolved_pushButton.clicked.connect(
            self.applySolvedClicked, connection_type
        )
        self.cancel_pushButton.clicked.connect(self.cancelSolveClicked, connection_type)
        self.close_pushButton.clicked.connect(
            lambda: self.window().close(), connection_type
        )

        # Persist options to the Maya scene on change.
        self.logLevel_comboBox.currentIndexChanged.connect(
            self.saveLogLevel, connection_type
        )
        self.adjustmentSolver_comboBox.currentIndexChanged.connect(
            self.saveAdjustmentSolverType, connection_type
        )
        self.frameRange_comboBox.currentIndexChanged.connect(
            self.saveFrameRangeMode, connection_type
        )
        self.startFrame_spinBox.valueChanged.connect(
            self.saveFrameStart, connection_type
        )
        self.endFrame_spinBox.valueChanged.connect(self.saveFrameEnd, connection_type)
        self.focalLengthRange_comboBox.currentIndexChanged.connect(
            self.saveFocalLengthRangeMode, connection_type
        )
        self.focalLengthPercentage_doubleSpinBox.valueChanged.connect(
            self.saveFocalLengthPercentage, connection_type
        )
        self.focalLengthMin_doubleSpinBox.valueChanged.connect(
            self.saveFocalLengthMin, connection_type
        )
        self.focalLengthMax_doubleSpinBox.valueChanged.connect(
            self.saveFocalLengthMax, connection_type
        )
        self.focalLengthSamples_spinBox.valueChanged.connect(
            self.saveFocalLengthSamples, connection_type
        )
        return

    def populateUi(self):
        """Read scene options and initialise widget values."""
        # type: () -> None
        self.cameraRefreshClicked()
        inner = time_utils.get_maya_timeline_range_inner()

        # Frame range.
        frame_range_mode = int(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FRAME_RANGE_MODE,
                default=const.DEFAULT_FRAME_RANGE_MODE,
            )
        )
        self.frameRange_comboBox.setCurrentIndex(frame_range_mode)
        frame_start = int(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FRAME_START,
                default=inner.start,
            )
        )
        frame_end = int(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FRAME_END,
                default=inner.end,
            )
        )
        self.startFrame_spinBox.setValue(frame_start)
        self.endFrame_spinBox.setValue(frame_end)
        self.updateFrameRangeState(frame_range_mode)

        # Adjustment solver.
        adjustment_solver_type = configmaya.get_scene_option(
            const.SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE,
            default=const.DEFAULT_ADJUSTMENT_SOLVER_TYPE,
        )
        adjustment_solver_index = _ADJUSTMENT_SOLVER_CONST_TO_INDEX.get(
            adjustment_solver_type, 0
        )
        self.adjustmentSolver_comboBox.setCurrentIndex(adjustment_solver_index)
        self.updateAdjustmentSolverState(adjustment_solver_index)

        # Log level.
        log_level = configmaya.get_scene_option(
            const.SCENE_OPTION_LOG_LEVEL,
            default=const.DEFAULT_LOG_LEVEL,
        )
        log_level_index = _LOG_LEVEL_CONST_TO_INDEX.get(log_level, 2)
        self.logLevel_comboBox.setCurrentIndex(log_level_index)

        # Focal length range.
        focal_length_range_mode = int(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FOCAL_LENGTH_RANGE_MODE,
                default=const.DEFAULT_FOCAL_LENGTH_RANGE_MODE,
            )
        )
        self.focalLengthRange_comboBox.setCurrentIndex(focal_length_range_mode)
        focal_length_percentage = float(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FOCAL_LENGTH_PERCENTAGE,
                default=const.DEFAULT_FOCAL_LENGTH_PERCENTAGE,
            )
        )
        self.focalLengthPercentage_doubleSpinBox.setValue(focal_length_percentage)
        if focal_length_range_mode == const.FOCAL_LENGTH_RANGE_MODE_MIN_MAX_INDEX:
            focal_length_min = float(
                configmaya.get_scene_option(
                    const.SCENE_OPTION_FOCAL_LENGTH_MIN,
                    default=const.DEFAULT_FOCAL_LENGTH_MIN,
                )
            )
            self.focalLengthMin_doubleSpinBox.setValue(focal_length_min)
            focal_length_max = float(
                configmaya.get_scene_option(
                    const.SCENE_OPTION_FOCAL_LENGTH_MAX,
                    default=const.DEFAULT_FOCAL_LENGTH_MAX,
                )
            )
            self.focalLengthMax_doubleSpinBox.setValue(focal_length_max)
        focal_length_samples = int(
            configmaya.get_scene_option(
                const.SCENE_OPTION_FOCAL_LENGTH_SAMPLES,
                default=const.DEFAULT_FOCAL_LENGTH_SAMPLES,
            )
        )
        self.focalLengthSamples_spinBox.setValue(focal_length_samples)
        self.updateFocalLengthRangeState(focal_length_range_mode)
        return

    # ------------------------------------------------------------------
    # Slots: Camera
    # ------------------------------------------------------------------

    def cameraRefreshClicked(self):
        """Repopulate the camera comboBox with all cameras in the scene."""
        # type: () -> None
        mmapi.load_plugin()
        cam_shps = maya.cmds.ls(type='camera', long=True) or []
        self._camera_nodes = []
        previous_index = self.camera_comboBox.currentIndex()
        previous_text = self.camera_comboBox.currentText()

        self.camera_comboBox.blockSignals(True)
        self.camera_comboBox.clear()
        for cam_shp in cam_shps:
            try:
                is_startup = maya.cmds.camera(cam_shp, query=True, startupCamera=True)
            except Exception:
                is_startup = False
            if is_startup:
                continue
            parents = maya.cmds.listRelatives(cam_shp, parent=True, fullPath=True) or []
            tfm_node = parents[0] if parents else cam_shp
            short_name = tfm_node.split('|')[-1]
            self.camera_comboBox.addItem(short_name)
            self._camera_nodes.append(tfm_node)
        self.camera_comboBox.blockSignals(False)

        # Restore previous selection by name if possible.
        restored_index = self.camera_comboBox.findText(previous_text)
        if restored_index >= 0:
            self.camera_comboBox.setCurrentIndex(restored_index)
        elif not previous_text:
            # No previous selection - auto-detect from scene selection / viewport.
            auto_camera = lib.get_camera_from_selection()
            if auto_camera is not None:
                camera_transform_node = auto_camera.get_transform_node() or ''
                short_name = camera_transform_node.split('|')[-1]
                auto_index = self.camera_comboBox.findText(short_name)
                if auto_index >= 0:
                    self.camera_comboBox.setCurrentIndex(auto_index)
        elif previous_index < self.camera_comboBox.count():
            self.camera_comboBox.setCurrentIndex(previous_index)

        self.onCameraChanged(self.camera_comboBox.currentIndex())
        return

    def onCameraChanged(self, index):
        """Update self._camera and the lens/markers labels for the selected camera."""
        # type: (int) -> None
        assert isinstance(index, int)
        self._camera = None
        self._lens = None
        if index < 0 or index >= len(self._camera_nodes):
            self.lens_value_label.setText('<none>')
            self.markers_value_label.setText('0')
            return
        camera_transform_node = self._camera_nodes[index]
        camera_shape_node_list = (
            maya.cmds.listRelatives(
                camera_transform_node, shapes=True, type='camera', fullPath=True
            )
            or []
        )
        if not camera_shape_node_list:
            self.lens_value_label.setText('<none>')
            self.markers_value_label.setText('0')
            return
        camera = mmapi.Camera(shape=camera_shape_node_list[0])
        self._camera = camera
        lens = lib.get_lens_from_camera(camera)
        self._lens = lens
        if lens is not None:
            lens_node = lens.get_node() or ''
            self.lens_value_label.setText(
                lens_node.split('|')[-1] if lens_node else '<none>'
            )
        else:
            self.lens_value_label.setText('<none>')
        mkr_list = lib.get_markers_under_camera(camera)
        self.markers_value_label.setText(str(len(mkr_list)))
        self.updateFocalLengthFromPercentage()
        return

    # ------------------------------------------------------------------
    # Slots: UI state
    # ------------------------------------------------------------------

    def updateFrameRangeState(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        custom = index == const.FRAME_RANGE_MODE_CUSTOM_INDEX
        self.startFrame_spinBox.setEnabled(custom)
        self.endFrame_spinBox.setEnabled(custom)
        return

    def updateFocalLengthRangeState(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        use_percentage = index == const.FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX
        self.focalLengthPercentage_doubleSpinBox.setEnabled(use_percentage)
        self.focalLengthMin_doubleSpinBox.setEnabled(not use_percentage)
        self.focalLengthMax_doubleSpinBox.setEnabled(not use_percentage)
        if use_percentage:
            self.updateFocalLengthFromPercentage()
        return

    def updateFocalLengthFromPercentage(self):
        """Auto-compute min/max from the current camera focal length and percentage."""
        # type: () -> None
        if (
            self.focalLengthRange_comboBox.currentIndex()
            != const.FOCAL_LENGTH_RANGE_MODE_PERCENTAGE_INDEX
        ):
            return
        focal_length_mm = lib.get_camera_focal_length(self._camera)
        percentage_value = self.focalLengthPercentage_doubleSpinBox.value()
        focal_length_min, focal_length_max = (
            lib.compute_focal_length_min_max_from_percentage(
                focal_length_mm, percentage_value
            )
        )
        self.focalLengthMin_doubleSpinBox.blockSignals(True)
        self.focalLengthMax_doubleSpinBox.blockSignals(True)
        self.focalLengthMin_doubleSpinBox.setValue(focal_length_min)
        self.focalLengthMax_doubleSpinBox.setValue(focal_length_max)
        self.focalLengthMin_doubleSpinBox.blockSignals(False)
        self.focalLengthMax_doubleSpinBox.blockSignals(False)
        return

    def updateAdjustmentSolverState(self, adjustment_solver_index):
        # type: (int) -> None
        assert isinstance(adjustment_solver_index, int)
        solver_type = const.ADJUSTMENT_SOLVER_TYPE_INDEX_LIST[adjustment_solver_index]
        is_none = solver_type == const.ADJUSTMENT_SOLVER_TYPE_NONE
        is_uniform_grid = solver_type == const.ADJUSTMENT_SOLVER_TYPE_UNIFORM_GRID
        self.adjustFocalLength_groupBox.setEnabled(not is_none)
        # Samples only relevant for Uniform Grid (checked after groupBox enable).
        self.focalLengthSamples_spinBox.setEnabled(is_uniform_grid)
        return

    # ------------------------------------------------------------------
    # Slots: persist scene options
    # ------------------------------------------------------------------

    def saveLogLevel(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        value = const.LOG_LEVEL_INDEX_LIST[index]
        configmaya.set_scene_option(const.SCENE_OPTION_LOG_LEVEL, value, add_attr=True)
        return

    def saveAdjustmentSolverType(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        value = const.ADJUSTMENT_SOLVER_TYPE_INDEX_LIST[index]
        configmaya.set_scene_option(
            const.SCENE_OPTION_ADJUSTMENT_SOLVER_TYPE, value, add_attr=True
        )
        return

    def saveFrameRangeMode(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FRAME_RANGE_MODE, index, add_attr=True
        )
        return

    def saveFrameStart(self, value):
        # type: (int) -> None
        assert isinstance(value, int)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FRAME_START, value, add_attr=True
        )
        return

    def saveFrameEnd(self, value):
        # type: (int) -> None
        assert isinstance(value, int)
        configmaya.set_scene_option(const.SCENE_OPTION_FRAME_END, value, add_attr=True)
        return

    def saveFocalLengthRangeMode(self, index):
        # type: (int) -> None
        assert isinstance(index, int)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FOCAL_LENGTH_RANGE_MODE, index, add_attr=True
        )
        return

    def saveFocalLengthPercentage(self, value):
        # type: (float) -> None
        assert isinstance(value, float)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FOCAL_LENGTH_PERCENTAGE, value, add_attr=True
        )
        return

    def saveFocalLengthMin(self, value):
        # type: (float) -> None
        assert isinstance(value, float)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FOCAL_LENGTH_MIN, value, add_attr=True
        )
        return

    def saveFocalLengthMax(self, value):
        # type: (float) -> None
        assert isinstance(value, float)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FOCAL_LENGTH_MAX, value, add_attr=True
        )
        return

    def saveFocalLengthSamples(self, value):
        # type: (int) -> None
        assert isinstance(value, int)
        configmaya.set_scene_option(
            const.SCENE_OPTION_FOCAL_LENGTH_SAMPLES, value, add_attr=True
        )
        return

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def applyLogLayoutState(self, log_visible):
        """Collapse/expand the spacer and log_groupBox size policy together."""
        # type: (bool) -> None
        assert isinstance(log_visible, bool)
        if self._group_box_spacer is not None:
            if log_visible:
                self._group_box_spacer.changeSize(
                    0,
                    0,
                    QtWidgets.QSizePolicy.Minimum,
                    QtWidgets.QSizePolicy.Fixed,
                )
            else:
                self._group_box_spacer.changeSize(
                    0,
                    0,
                    QtWidgets.QSizePolicy.Minimum,
                    QtWidgets.QSizePolicy.Expanding,
                )
        size_policy_vertical = (
            QtWidgets.QSizePolicy.Expanding
            if log_visible
            else QtWidgets.QSizePolicy.Preferred
        )
        self.log_groupBox.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, size_policy_vertical
        )
        self.layout().invalidate()
        return

    def toggleLog(self):
        # type: () -> None
        visible = self.log_plainTextEdit.isVisible()
        self.log_plainTextEdit.setVisible(not visible)
        self.applyLogLayoutState(log_visible=not visible)
        if not visible:
            self.logToggle_pushButton.setText('\u25bc Hide Log')
        else:
            self.logToggle_pushButton.setText('\u25b6 Show Log')
        return

    def updateLogFromProcess(self):
        # type: () -> None
        if self._solver_process is None:
            return
        new_lines = self._solver_process._stdout_lines[self._log_line_count :]
        if new_lines:
            self.log_plainTextEdit.appendPlainText('\n'.join(new_lines))
            self._log_line_count += len(new_lines)
        return

    @QtCore.Slot(str)
    def setStatusLine(self, text):
        # type: (pycompat.TEXT_TYPE) -> None
        assert isinstance(text, pycompat.TEXT_TYPE)
        if uiutils.isValidQtObject(self):
            self.status_label.setText(text)
        return

    # ------------------------------------------------------------------
    # Button state helpers
    # ------------------------------------------------------------------

    def setButtonStateIdle(self):
        # type: () -> None
        self.solve_pushButton.setEnabled(True)
        self.applySolved_pushButton.setEnabled(False)
        self.cancel_pushButton.setEnabled(False)
        self.close_pushButton.setEnabled(True)
        return

    def setButtonStateSolving(self):
        # type: () -> None
        self.solve_pushButton.setEnabled(False)
        self.applySolved_pushButton.setEnabled(False)
        self.cancel_pushButton.setEnabled(True)
        self.close_pushButton.setEnabled(True)
        return

    def setButtonStateSuccess(self):
        # type: () -> None
        self.solve_pushButton.setEnabled(True)
        self.applySolved_pushButton.setEnabled(True)
        self.cancel_pushButton.setEnabled(False)
        self.close_pushButton.setEnabled(True)
        return

    # ------------------------------------------------------------------
    # Slots: Solve / Cancel / Apply
    # ------------------------------------------------------------------

    def startSolveClicked(self):
        # type: () -> None
        if self._camera is None:
            self.setStatusLine('No camera selected. Use the Camera drop-down.')
            return

        mkr_list = lib.get_markers_under_camera(self._camera)
        if not mkr_list:
            self.setStatusLine('No markers found under the camera.')
            return

        frame_range = lib.get_frame_range(
            self.frameRange_comboBox.currentIndex(),
            self.startFrame_spinBox.value(),
            self.endFrame_spinBox.value(),
        )

        solver_type = const.ADJUSTMENT_SOLVER_TYPE_INDEX_LIST[
            self.adjustmentSolver_comboBox.currentIndex()
        ]
        adjustment_solver = lib.make_adjustment_solver(solver_type)

        adjustment_attributes = build_adjustment_attributes(
            self.focalLengthRange_comboBox.currentIndex(),
            self.focalLengthPercentage_doubleSpinBox.value(),
            self.focalLengthMin_doubleSpinBox.value(),
            self.focalLengthMax_doubleSpinBox.value(),
            self.focalLengthSamples_spinBox.value(),
            self._camera,
        )

        log_level_index = self.logLevel_comboBox.currentIndex()
        log_level = const.LOG_LEVEL_INDEX_LIST[log_level_index]

        output_directory = lib.get_output_directory()
        prefix_name = lib.get_prefix_name(self._camera)

        # Store for Apply Solved.
        self._mkr_list = mkr_list
        self._output_directory = output_directory
        self._prefix_name = prefix_name

        self.log_plainTextEdit.clear()
        self._log_line_count = 0
        self.setStatusLine('Solving...')
        self.setButtonStateSolving()

        solver_process = lib.launch_solve_async(
            self._camera,
            self._lens,
            mkr_list,
            frame_range,
            adjustment_solver,
            adjustment_attributes,
            log_level,
            prefix_name,
            output_directory,
        )
        if solver_process is None:
            self.setStatusLine('Failed to launch camera solver.')
            self.setButtonStateIdle()
            return

        self._solver_process = solver_process
        self._poll_timer.start()
        return

    def pollSolve(self):
        # type: () -> None
        if self._solver_process is None:
            self._poll_timer.stop()
            return
        self.updateLogFromProcess()
        if self._solver_process.is_done():
            self._poll_timer.stop()
            self.onSolveFinished()
        return

    def onSolveFinished(self):
        # type: () -> None
        self.updateLogFromProcess()
        if self._solver_process is None:
            return
        returncode, _, _ = self._solver_process.result()
        if returncode == 0:
            self.setStatusLine('Solve complete.')
            self.setButtonStateSuccess()
        else:
            self.setStatusLine('Solve failed (exit code %d).' % returncode)
            self.setButtonStateIdle()
        return

    def cancelSolveClicked(self):
        # type: () -> None
        self._poll_timer.stop()
        if self._solver_process is not None:
            self._solver_process.cancel()
        self._solver_process = None
        self.setStatusLine('Solve cancelled.')
        self.setButtonStateIdle()
        return

    def applySolvedClicked(self):
        # type: () -> None
        if (
            self._camera is None
            or not self._mkr_list
            or not self._output_directory
            or not self._prefix_name
        ):
            self.setStatusLine('Nothing to apply.')
            return
        undo_id = 'camerasolver apply: '
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
            lib.load_camera_outputs(
                self._camera, self._prefix_name, self._output_directory
            )
            lib.load_bundle_outputs(
                self._mkr_list, self._prefix_name, self._output_directory
            )
            lib.load_residuals_outputs(
                self._mkr_list, self._prefix_name, self._output_directory
            )
        self.updateFocalLengthFromPercentage()
        self.setStatusLine('Applied solved camera data.')
        return
