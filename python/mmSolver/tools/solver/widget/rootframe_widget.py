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
        self.auto_pushButton.clicked.connect(self.autoClicked)

        # These buttons don't work, yet.
        self.selectNode_pushButton.setHidden(True)
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
        roots_string = self.getRootFramesValue(col)
        if roots_string is None:
            frame = lib_maya_utils.get_current_frame()
            start, end = utils_time.get_maya_timeline_range_inner()
            int_list = list(set([start, frame, end]))
            roots_string = convert_types.intListToString(int_list)
            self.setRootFramesValue(col, roots_string)
        else:
            int_list = convert_types.stringToIntList(roots_string)
            roots_string = convert_types.intListToString(int_list)
        assert roots_string is not None

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
        int_list = convert_types.stringToIntList(text)
        frames_string = convert_types.intListToString(int_list)
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
        self.setRootFramesValue(col, frames_string)
        self.rootFramesChanged.emit()
        return

    def addClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        roots_string = self.getRootFramesValue(col)
        if roots_string is None:
            int_list = [frame]
            roots_string = convert_types.intListToString(int_list)
            self.setRootFramesValue(col, roots_string)
            self.rootFrames_lineEdit.setText(roots_string)
        else:
            int_list = convert_types.stringToIntList(roots_string)
        if frame not in int_list:
            int_list.append(frame)
            roots_string = convert_types.intListToString(int_list)
            self.setRootFramesValue(col, roots_string)
            self.rootFrames_lineEdit.setText(roots_string)
        return

    def removeClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frame = lib_maya_utils.get_current_frame()
        frames_string = self.getRootFramesValue(col)
        if frames_string is None:
            int_list = [frame]
            frames_string = convert_types.intListToString(int_list)
            self.setRootFramesValue(col, frames_string)
            self.rootFrames_lineEdit.setText(frames_string)
        else:
            int_list = convert_types.stringToIntList(frames_string)
        if frame in int_list:
            int_list.remove(frame)
            frames_string = convert_types.intListToString(int_list)
            self.setRootFramesValue(col, frames_string)
            self.rootFrames_lineEdit.setText(frames_string)
        return

    def nextClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frames_string = self.getRootFramesValue(col)
        if frames_string is None:
            LOG.warn('Root Frames are not valid')
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = convert_types.stringToIntList(frames_string)
        next_frame = navigaterootframes_lib.get_next_frame(
            cur_frame, int_list
        )
        if next_frame is None:
            next_frame = cur_frame
        lib_maya_utils.set_current_frame(next_frame)
        return

    def previousClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        frames_string = self.getRootFramesValue(col)
        if frames_string is None:
            LOG.warn('Root Frames are not valid')
            return
        cur_frame = lib_maya_utils.get_current_frame()
        int_list = convert_types.stringToIntList(frames_string)
        previous_frame = navigaterootframes_lib.get_prev_frame(
            cur_frame, int_list,
        )
        if previous_frame is None:
            previous_frame = cur_frame
        lib_maya_utils.set_current_frame(previous_frame)
        return

    def autoClicked(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        mkr_list = col.get_marker_list()
        start_frame, end_frame = utils_time.get_maya_timeline_range_inner()
        min_frames_per_marker = 2
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        if len(frame_nums) < 2:
            LOG.warn('Auto Root Frames failed to calculate - not enough markers.')
            return
        roots_string = convert_types.intListToString(frame_nums)
        self.setRootFramesValue(col, roots_string)
        self.rootFrames_lineEdit.setText(roots_string)
        return
