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

TODO: Can we simply delay the root frame calculation until later? This
would avoid a lot of delay in the UI, and speed up the UI a lot.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
from datetime import datetime

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.time as utils_time

import mmSolver.ui.converttypes as convert_types
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.navigaterootframes.lib as navigaterootframes_lib
import mmSolver.tools.solver.widget.ui_rootframe_widget as ui_rootframe_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


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

    def updateModel(self):
        """
        Refresh the widgets with the current Maya scene state.
        """
        s_datetime = datetime.now()
        s_func = time.time()

        col = lib_state.get_active_collection()
        if col is None:
            return

        start_frame, end_frame = utils_time.get_maya_timeline_range_inner()

        s = time.time()
        user_int_list = []
        user_string = self.getUserFramesValue(col)
        if user_string is None:
            user_int_list = list(set([start_frame, end_frame]))
            user_string = convert_types.intListToString(user_int_list)
        else:
            user_int_list = convert_types.stringToIntList(user_string)
            user_string = convert_types.intListToString(user_int_list)
        assert user_string is not None

        use_per_marker_frames = self.getUsePerMarkerFramesValue(col)
        use_span_frames = self.getUseSpanFramesValue(col)
        per_marker_frames = self.getPerMarkerFramesValue(col)
        span_frames = self.getSpanFramesValue(col)
        e = time.time()
        LOG.debug(
            'RootFrameWidget updateModel convert types: %s - %r seconds',
            s_datetime.isoformat(),
            e - s,
        )

        self.setUserFramesValue(col, user_string)

        block = self.blockSignals(True)
        self.userFrames_lineEdit.setText(user_string)
        self.perMarkerFrames_checkBox.setChecked(use_per_marker_frames)
        self.perMarkerFrames_spinBox.setValue(per_marker_frames)
        self.spanFrames_checkBox.setChecked(use_span_frames)
        self.spanFrames_spinBox.setValue(span_frames)
        self.blockSignals(block)

        e_func = time.time()
        LOG.debug(
            'RootFrameWidget updateModel: %s - %r seconds',
            s_datetime.isoformat(),
            e_func - s_func,
        )
        return

    @QtCore.Slot()
    def userFramesTextEntered(self):
        """
        Run when the userFrames_lineEdit text is has been entered (for example
        the user presses the <Enter> key to confirm the field value).
        """
        s = time.time()

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
        e = time.time()
        LOG.debug('RootFrameWidget userFramesTextEntered: %r seconds', e - s)
        return

    @QtCore.Slot()
    def usePerMarkerFramesToggled(self, value):
        s = time.time()
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setUsePerMarkerFramesValue(col, value)
        self.updateModel()
        e = time.time()
        LOG.debug('RootFrameWidget usePerMarkerFramesToggled: %r seconds', e - s)

    @QtCore.Slot()
    def perMarkerFramesValueChanged(self, value):
        s = time.time()
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setPerMarkerFramesValue(col, value)
        self.updateModel()
        e = time.time()
        LOG.debug('RootFrameWidget perMarkerFramesValueChanged: %r seconds', e - s)

    @QtCore.Slot()
    def useSpanFramesToggled(self, value):
        s = time.time()
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setUseSpanFramesValue(col, value)
        self.updateModel()
        e = time.time()
        LOG.debug('RootFrameWidget useSpanFramesToggled: %r seconds', e - s)

    @QtCore.Slot()
    def spanFramesValueChanged(self, value):
        s = time.time()
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setSpanFramesValue(col, value)
        self.updateModel()
        e = time.time()
        LOG.debug('RootFrameWidget spanFramesValueChanged: %r seconds', e - s)

    def addClicked(self):
        s = time.time()
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
        e = time.time()
        LOG.debug('RootFrameWidget addClicked: %r seconds', e - s)
        return

    def removeClicked(self):
        s = time.time()
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
        e = time.time()
        LOG.debug('RootFrameWidget removeClicked: %r seconds', e - s)
        return

    def nextClicked(self):
        s = time.time()
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
        e = time.time()
        LOG.debug('RootFrameWidget nextClicked: %r seconds', e - s)
        return

    def previousClicked(self):
        s = time.time()
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
        e = time.time()
        LOG.debug('RootFrameWidget previousClicked: %r seconds', e - s)
        return
