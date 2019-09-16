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

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.time as utils_time
import mmSolver.ui.converttypes as converttypes
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.maya_utils as lib_maya_utils
import mmSolver.tools.solver.widget.ui_rootframe_widget as ui_rootframe_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class RootFrameWidget(QtWidgets.QWidget, ui_rootframe_widget.Ui_Form):

    rootFramesChanged = QtCore.Signal()
    sendWarning = QtCore.Signal(str)

    def __init__(self, parent=None, *args, **kwargs):
        super(RootFrameWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Root Frames Line Edit
        self.rootFrames_lineEdit.editingFinished.connect(self.rootFramesTextEntered)

        self.add_toolButton.clicked.connect(self.addClicked)
        self.remove_toolButton.clicked.connect(self.removeClicked)
        self.next_toolButton.clicked.connect(self.nextClicked)
        self.previous_toolButton.clicked.connect(self.previousClicked)

        # These buttons don't work, yet.
        self.selectNode_pushButton.setHidden(True)
        self.auto_pushButton.setHidden(True)
        return

    def getRootFramesValue(self, col):
        raise NotImplementedError

    def setRootFramesValue(self, col, value):
        raise NotImplementedError

    def updateModel(self):
        """
        Refresh the name_comboBox with the current Maya scene state.
        """
        col = lib_state.get_active_collection()
        if col is None:
            return

        roots_enabled = True
        int_list = self.getRootFramesValue(col)
        if int_list is None:
            frame = lib_maya_utils.get_current_frame()
            start, end = utils_time.get_maya_timeline_range_inner()
            int_list = list(set([start, frame, end]))
            self.setRootFramesValue(col, int_list)
        roots_string = converttypes.intListToString(int_list)

        block = self.blockSignals(True)
        self.rootFrames_lineEdit.setEnabled(roots_enabled)
        self.rootFrames_lineEdit.setText(roots_string)
        self.blockSignals(block)
        return

    @QtCore.Slot()
    def rootFramesTextEntered(self):
        """
        Run when the rootFrames_lineEdit text is has been entered (for example
        the user presses the <Enter> key to confirm the field value).
        """
        text = self.rootFrames_lineEdit.text()

        col = lib_state.get_active_collection()
        if col is None:
            return

        # Round-trip conversion will make sure there are no syntax
        # errors given by the user.
        int_list = converttypes.stringToIntList(text)
        frames_string = converttypes.intListToString(int_list)
        if len(int_list) < 2:
            msg = 'Must have at least 2 root frames to solve.'
            LOG.warn(msg)
            msg = 'WARNING: ' + msg
            self.sendWarning.emit(msg)
        else:
            msg = const.STATUS_READY
            self.sendWarning.emit(msg)

        # Save the integer list, but present the user with a string.
        self.rootFrames_lineEdit.setText(frames_string)
        self.setRootFramesValue(col, int_list)
        self.rootFramesChanged.emit()
        return

    def addClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        int_list = self.getRootFramesValue(col)
        if int_list is None:
            int_list = [frame]
            self.setRootFramesValue(col, int_list)
            frames_string = converttypes.intListToString(int_list)
            self.rootFrames_lineEdit.setText(frames_string)
        if frame not in int_list:
            int_list.append(frame)
            frames_string = converttypes.intListToString(int_list)
            self.setRootFramesValue(col, int_list)
            self.rootFrames_lineEdit.setText(frames_string)
        return

    def removeClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        int_list = self.getRootFramesValue(col)
        if int_list is None:
            int_list = [frame]
            self.setRootFramesValue(col, int_list)
            frames_string = converttypes.intListToString(int_list)
            self.rootFrames_lineEdit.setText(frames_string)
        if frame in int_list:
            int_list.remove(frame)
            frames_string = converttypes.intListToString(int_list)
            self.setRootFramesValue(col, int_list)
            self.rootFrames_lineEdit.setText(frames_string)
        return

    def nextClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = self.getRootFramesValue(col)
        future_frames = [int(f) for f in int_list if int(f) > cur_frame]
        future_frames = list(sorted(future_frames))
        next_frame = cur_frame
        if len(future_frames) == 0:
            # Wrap-around the frame values.
            if len(int_list) > 0:
                next_frame = list(sorted(int_list))[0]
        else:
            # The next future frame.
            next_frame = future_frames[0]
        lib_maya_utils.set_current_frame(next_frame)
        return

    def previousClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = self.getRootFramesValue(col)
        past_frames = [f for f in int_list if f < cur_frame]
        past_frames = list(sorted(past_frames))
        previous_frame = cur_frame
        if len(past_frames) == 0:
            # Wrap-around the frame values.
            if len(int_list) > 0:
                previous_frame = list(sorted(int_list))[-1]
        else:
            # The last previous frame.
            previous_frame = past_frames[-1]
        lib_maya_utils.set_current_frame(previous_frame)
        return
