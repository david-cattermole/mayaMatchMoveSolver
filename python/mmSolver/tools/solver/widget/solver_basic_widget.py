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

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.widget.ui_solver_basic_widget as ui_solver_basic_widget
import mmSolver.tools.solver.widget.framerange_widget as framerange_widget


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


class SolverBasicWidget(QtWidgets.QWidget,
                        ui_solver_basic_widget.Ui_Form):

    viewUpdated = QtCore.Signal()
    dataChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super(SolverBasicWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frameRange_widget = BasicFrameRangeWidget(self)
        self.frameRange_layout.addWidget(self.frameRange_widget)

        self.advanced_pushButton.setHidden(True)
        return

    def updateModel(self):
        self.frameRange_widget.updateModel()
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
