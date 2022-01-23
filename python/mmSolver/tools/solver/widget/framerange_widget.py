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
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.converttypes as converttypes
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.widget.ui_framerange_widget as ui_framerange_widget
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class FrameRangeWidget(QtWidgets.QWidget,
                       ui_framerange_widget.Ui_Form):

    rangeTypeChanged = QtCore.Signal()
    framesChanged = QtCore.Signal()
    incrementByFrameChanged = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        super(FrameRangeWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Range Type Combo Box.
        self.model = uimodels.StringDataListModel()
        self.rangeType_comboBox.setModel(self.model)
        self.rangeType_comboBox.currentIndexChanged.connect(
            self.rangeTypeIndexChanged)

        # Frames Line Edit
        self.frames_lineEdit.editingFinished.connect(
            self.framesTextEntered)

        # Increment by Frames Line Edit
        self.incrementByFrame_spinBox.valueChanged.connect(
            self.incrementByFrameValueChanged)

        self.rangeTypeChanged.connect(self.updateModel)
        return

    def getRangeTypeStringDataList(self):
        values = zip(const.RANGE_TYPE_NAME_LIST,
                     const.RANGE_TYPE_VALUE_LIST)
        return list(values)

    def getRangeTypeValue(self, col):
        raise NotImplementedError

    def setRangeTypeValue(self, col, value):
        raise NotImplementedError

    def getFramesValue(self, col):
        raise NotImplementedError

    def setFramesValue(self, col, value):
        raise NotImplementedError

    def getIncrementByFrameValue(self, col):
        raise NotImplementedError

    def setIncrementByFrameValue(self, col, value):
        raise NotImplementedError

    def populateModel(self, model):
        """
        Set the model based on the current Maya scene state.
        """
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        string_data_list = self.getRangeTypeStringDataList()
        model.setStringDataList(string_data_list)
        return

    def getRangeTypeActiveIndex(self, model, col):
        """
        Get the index for the 'currently selected' frame range type.
        """
        valid = uiutils.isValidQtObject(model)
        if valid is False:
            return
        if col is None:
            return None
        active_node = col.get_node()
        if active_node is None:
            return None
        value = self.getRangeTypeValue(col)
        string_data_list = model.stringDataList()
        data_list = [data for string, data in string_data_list]
        index = None
        if value in data_list:
            index = data_list.index(value)
        return index

    def updateModel(self):
        """
        Refresh the name_comboBox with the current Maya scene state.
        """
        self.populateModel(self.model)

        col = lib_state.get_active_collection()
        if col is None:
            return

        # range_type_value = self.getRangeTypeValue(col)
        index = self.getRangeTypeActiveIndex(self.model, col)
        if index is None:
            LOG.error('Could not get the active range type index.')
            return

        frames_string = '1001-1101'
        increment = self.getIncrementByFrameValue(col)
        frames_enabled = False
        increment_enabled = False
        if index == const.RANGE_TYPE_CURRENT_FRAME_VALUE:
            frames_string = 'CURRENT FRAME'
            frames_enabled = False
            increment_enabled = False
        elif index == const.RANGE_TYPE_TIMELINE_INNER_VALUE:
            start, end = utils_time.get_maya_timeline_range_inner()
            frames_string = '{0}-{1}'.format(int(start), int(end))
            frames_enabled = False
            increment_enabled = True
        elif index == const.RANGE_TYPE_TIMELINE_OUTER_VALUE:
            start, end = utils_time.get_maya_timeline_range_outer()
            frames_string = '{0}-{1}'.format(int(start), int(end))
            frames_enabled = False
            increment_enabled = True
        elif index == const.RANGE_TYPE_CUSTOM_FRAMES_VALUE:
            frames_string = self.getFramesValue(col)
            if frames_string is None:
                start, end = utils_time.get_maya_timeline_range_outer()
                frames_string = '{0}-{1}'.format(int(start), int(end))
            frames_enabled = True
            increment_enabled = True
        else:
            msg = "Not a valid 'range type' value: %r" % index
            raise ValueError(msg)

        block = self.blockSignals(True)
        self.rangeType_comboBox.setCurrentIndex(index)
        self.frames_lineEdit.setEnabled(frames_enabled)
        self.frames_lineEdit.setText(frames_string)
        self.incrementByFrame_spinBox.setEnabled(increment_enabled)
        self.incrementByFrame_spinBox.setValue(increment)
        self.blockSignals(block)
        return

    @QtCore.Slot(int)
    def rangeTypeIndexChanged(self, index):
        """
        Run when the rangeType_comboBox index is changed.
        """
        if index < 0:
            return
        col = lib_state.get_active_collection()
        if col is None:
            return
        model_index = self.model.index(index, 0)
        data = self.model.data(
            model_index,
            role=QtCore.Qt.UserRole
        )
        if data is None:
            return
        assert isinstance(data, pycompat.INT_TYPES)
        self.setRangeTypeValue(col, data)
        self.rangeTypeChanged.emit()
        return

    @QtCore.Slot()
    def framesTextEntered(self):
        """
        Run when the frames_lineEdit text is has been entered (for example
        the user presses the <Enter> key to confirm the field value).
        """
        text = self.frames_lineEdit.text()

        col = lib_state.get_active_collection()
        if col is None:
            return

        # Round-trip conversion will make sure there are no syntax
        # errors given by the user.
        int_list = converttypes.stringToIntList(text)
        frames_string = converttypes.intListToString(int_list)

        self.frames_lineEdit.setText(frames_string)
        self.setFramesValue(col, frames_string)
        self.framesChanged.emit()
        return

    @QtCore.Slot(int)
    def incrementByFrameValueChanged(self, value):
        """
        Run when the incrementByFrame_spinBox value is changed.
        """
        assert value > 0
        col = lib_state.get_active_collection()
        if col is None:
            return
        self.setIncrementByFrameValue(col, value)
        self.incrementByFrameChanged.emit()
        return
