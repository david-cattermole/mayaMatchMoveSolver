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
A widget for visualising a specific set of (integer) frame numbers.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.time as utils_time
import mmSolver.api as mmapi

import mmSolver.ui.converttypes as convert_types
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.navigaterootframes.lib as navigaterootframes_lib
import mmSolver.tools.solver.widget.ui_rootframe_widget as ui_rootframe_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def calculate_root_frames(
    mkr_list,
    start_frame,
    end_frame,
    extra_frames,
    use_per_marker_frames,
    per_marker_frames,
    use_span_frames,
    span_frames,
):
    frames = extra_frames
    if use_per_marker_frames and len(mkr_list) > 0:
        frames = mmapi.get_root_frames_from_markers(
            mkr_list, per_marker_frames, start_frame, end_frame
        )
    frames = mmapi.root_frames_list_combine(frames, extra_frames)

    if use_span_frames:
        frames = mmapi.root_frames_subdivide(frames, span_frames)

    return frames


class RootFrameWidget(QtWidgets.QWidget, ui_rootframe_widget.Ui_Form):

    userFramesChanged = QtCore.Signal()
    rootFramesChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        super(RootFrameWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.userFrames_lineEdit.editingFinished.connect(self.userFramesTextEntered)

        self.perMarkerFrames_checkBox.toggled.connect(self.usePerMarkerFramesToggled)
        self.perMarkerFrames_spinBox.valueChanged.connect(
            self.perMarkerFramesValueChanged
        )

        self.spanFrames_checkBox.toggled.connect(self.useSpanFramesToggled)
        self.spanFrames_spinBox.valueChanged.connect(self.spanFramesValueChanged)

        self.add_toolButton.clicked.connect(self.addClicked)
        self.remove_toolButton.clicked.connect(self.removeClicked)
        self.next_toolButton.clicked.connect(self.nextClicked)
        self.previous_toolButton.clicked.connect(self.previousClicked)
        return

    def getUserFramesValue(self, col):
        raise NotImplementedError

    def setUserFramesValue(self, col, value):
        raise NotImplementedError

    def getUsePerMarkerFramesValue(self, col):
        raise NotImplementedError

    def setUsePerMarkerFramesValue(self, col, value):
        raise NotImplementedError

    def getPerMarkerFramesValue(self, col):
        raise NotImplementedError

    def setPerMarkerFramesValue(self, col, value):
        raise NotImplementedError

    def getUseSpanFramesValue(self, col):
        raise NotImplementedError

    def setUseSpanFramesValue(self, col, value):
        raise NotImplementedError

    def getSpanFramesValue(self, col):
        raise NotImplementedError

    def setSpanFramesValue(self, col, value):
        raise NotImplementedError

    def getRootFramesValue(self, col):
        raise NotImplementedError

    def setRootFramesValue(self, col, value):
        raise NotImplementedError

    def updateModel(self):
        """
        Refresh the widgets with the current Maya scene state.
        """
        col = lib_state.get_active_collection()
        if col is None:
            return

        start_frame, end_frame = utils_time.get_maya_timeline_range_inner()

        user_int_list = []
        user_string = self.getUserFramesValue(col)
        root_string = self.getRootFramesValue(col)
        if user_string is None and root_string is None:
            user_int_list = list(set([start_frame, end_frame]))
            user_string = convert_types.intListToString(user_int_list)
            self.setUserFramesValue(col, user_string)
        if user_string is None and root_string is not None:
            user_int_list = convert_types.stringToIntList(root_string)
            user_string = convert_types.intListToString(user_int_list)
        else:
            user_int_list = convert_types.stringToIntList(user_string)
            user_string = convert_types.intListToString(user_int_list)
        assert user_string is not None

        use_per_marker_frames = self.getUsePerMarkerFramesValue(col)
        use_span_frames = self.getUseSpanFramesValue(col)
        per_marker_frames = self.getPerMarkerFramesValue(col)
        span_frames = self.getSpanFramesValue(col)

        mkr_list = col.get_marker_list()
        root_frames = calculate_root_frames(
            mkr_list,
            start_frame,
            end_frame,
            user_int_list,
            use_per_marker_frames,
            per_marker_frames,
            use_span_frames,
            span_frames,
        )
        if len(root_frames) < 2:
            LOG.warn('Auto Root Frames failed to calculate.')
        root_string = convert_types.intListToString(root_frames)

        self.setUserFramesValue(col, user_string)
        self.setRootFramesValue(col, root_string)

        block = self.blockSignals(True)
        self.userFrames_lineEdit.setText(user_string)
        self.rootFrames_lineEdit.setText(root_string)
        self.perMarkerFrames_checkBox.setChecked(use_per_marker_frames)
        self.perMarkerFrames_spinBox.setValue(per_marker_frames)
        self.spanFrames_checkBox.setChecked(use_span_frames)
        self.spanFrames_spinBox.setValue(span_frames)
        self.blockSignals(block)
        return

    @QtCore.Slot()
    def userFramesTextEntered(self):
        """
        Run when the userFrames_lineEdit text is has been entered (for example
        the user presses the <Enter> key to confirm the field value).
        """
        text = self.userFrames_lineEdit.text()

        col = lib_state.get_active_collection()
        if col is None:
            return

        # Round-trip conversion will make sure there are no syntax
        # errors given by the user.
        int_list = convert_types.stringToIntList(text)
        frames_string = convert_types.intListToString(int_list)
        if len(int_list) < 2:
            msg = 'Must have at least 2 user frames to solve.'
            LOG.warn(msg)
            msg = 'WARNING: ' + msg
            self.sendWarning.emit(msg)
        else:
            msg = const.STATUS_READY
            self.sendWarning.emit(msg)

        # Save the integer list, but present the user with a string.
        self.userFrames_lineEdit.setText(frames_string)
        self.setUserFramesValue(col, frames_string)
        self.userFramesChanged.emit()
        self.updateModel()
        return

    @QtCore.Slot()
    def usePerMarkerFramesToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setUsePerMarkerFramesValue(col, value)
        self.updateModel()

    @QtCore.Slot()
    def perMarkerFramesValueChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setPerMarkerFramesValue(col, value)
        self.updateModel()

    @QtCore.Slot()
    def useSpanFramesToggled(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setUseSpanFramesValue(col, value)
        self.updateModel()

    @QtCore.Slot()
    def spanFramesValueChanged(self, value):
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setSpanFramesValue(col, value)
        self.updateModel()

    def addClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        user_string = self.getUserFramesValue(col)
        if user_string is None:
            int_list = [frame]
            user_string = convert_types.intListToString(int_list)
            self.setUserFramesValue(col, user_string)
            self.userFrames_lineEdit.setText(user_string)
        else:
            int_list = convert_types.stringToIntList(user_string)
        if frame not in int_list:
            int_list.append(frame)
            user_string = convert_types.intListToString(int_list)
            self.setUserFramesValue(col, user_string)
            self.userFrames_lineEdit.setText(user_string)
        self.userFramesChanged.emit()
        self.updateModel()
        return

    def removeClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        frames_string = self.getUserFramesValue(col)
        if frames_string is None:
            int_list = [frame]
            frames_string = convert_types.intListToString(int_list)
            self.setUserFramesValue(col, frames_string)
            self.userFrames_lineEdit.setText(frames_string)
        else:
            int_list = convert_types.stringToIntList(frames_string)
        if frame in int_list:
            int_list.remove(frame)
            frames_string = convert_types.intListToString(int_list)
            self.setUserFramesValue(col, frames_string)
            self.userFrames_lineEdit.setText(frames_string)
        self.userFramesChanged.emit()
        self.updateModel()
        return

    def nextClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frames_string = self.getUserFramesValue(col)
        if frames_string is None:
            LOG.warn('User Frames are not valid')
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = convert_types.stringToIntList(frames_string)
        next_frame = navigaterootframes_lib.get_next_frame(cur_frame, int_list)
        if next_frame is None:
            next_frame = cur_frame
        lib_maya_utils.set_current_frame(next_frame)
        return

    def previousClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frames_string = self.getUserFramesValue(col)
        if frames_string is None:
            LOG.warn('User Frames are not valid')
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = convert_types.stringToIntList(frames_string)
        previous_frame = navigaterootframes_lib.get_prev_frame(
            cur_frame,
            int_list,
        )
        if previous_frame is None:
            previous_frame = cur_frame
        lib_maya_utils.set_current_frame(previous_frame)
        return
