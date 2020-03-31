# Copyright (C) 2020 David Cattermole.
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
Attribute Min/Max value delegate.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.api as mmapi
import mmSolver.tools.setattributedetails.constant as const
import mmSolver.tools.setattributedetails.lib as lib
import mmSolver.tools.setattributedetails.ui.ui_dialog as ui_dialog

LOG = mmSolver.logger.get_logger()


class Dialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setObjectName(const.DIALOG_OBJECT_NAME)
        self.ui = ui_dialog.Ui_Form()
        self.ui.setupUi(self)
        self.create_connections()
        self.set_default_values()
        return

    def create_connections(self):
        self.ui.locked_radioButton.toggled.connect(self.ui.valueRange_groupBox.setDisabled)
        self.ui.locked_radioButton.toggled.connect(self.ui.animCurve_groupBox.setDisabled)

        self.ui.static_radioButton.toggled.connect(self.ui.valueRange_groupBox.setEnabled)
        self.ui.static_radioButton.toggled.connect(self.ui.animCurve_groupBox.setDisabled)

        self.ui.animated_radioButton.toggled.connect(self.ui.valueRange_groupBox.setEnabled)
        self.ui.animated_radioButton.toggled.connect(self.ui.animCurve_groupBox.setEnabled)

        self.ui.max_checkBox.toggled.connect(self.ui.max_doubleSpinBox.setEnabled)
        self.ui.min_checkBox.toggled.connect(self.ui.min_doubleSpinBox.setEnabled)
        self.ui.stiffness_checkBox.toggled.connect(self.ui.stiffness_doubleSpinBox.setEnabled)
        self.ui.smoothness_checkBox.toggled.connect(self.ui.smoothness_doubleSpinBox.setEnabled)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def set_default_values(self):
        self.ui.animCurve_groupBox.setVisible(False)

        self.ui.min_doubleSpinBox.setEnabled(False)
        self.ui.max_doubleSpinBox.setEnabled(False)
        self.ui.stiffness_doubleSpinBox.setEnabled(False)
        self.ui.smoothness_doubleSpinBox.setEnabled(False)

        self.ui.min_checkBox.setChecked(False)
        self.ui.max_checkBox.setChecked(False)
        self.ui.stiffness_checkBox.setChecked(False)
        self.ui.smoothness_checkBox.setChecked(False)

        self.window().setWindowTitle(const.WINDOW_TITLE_BAR)
        return

    def get_state(self):
        state = mmapi.ATTR_STATE_INVALID
        is_locked = self.ui.locked_radioButton.isChecked()
        is_static = self.ui.static_radioButton.isChecked()
        is_animated = self.ui.animated_radioButton.isChecked()
        if is_locked is True:
            state = mmapi.ATTR_STATE_LOCKED
        elif is_static is True:
            state = mmapi.ATTR_STATE_STATIC
        elif is_animated is True:
            state = mmapi.ATTR_STATE_ANIMATED
        else:
            # Invalid state.
            pass
        return state

    def set_state(self, state):
        assert isinstance(state, int)
        self.ui.locked_radioButton.setChecked(state == mmapi.ATTR_STATE_LOCKED)
        self.ui.static_radioButton.setChecked(state == mmapi.ATTR_STATE_STATIC)
        self.ui.animated_radioButton.setChecked(state == mmapi.ATTR_STATE_ANIMATED)
        return

    def get_min_enable(self):
        return self.ui.min_checkBox.isChecked()

    def set_min_enable(self, value):
        assert isinstance(value, bool)
        self.ui.min_checkBox.setChecked(value)
        return

    def get_min_value(self):
        return self.ui.min_doubleSpinBox.value()

    def set_min_value(self, value):
        assert isinstance(value, float)
        self.ui.min_doubleSpinBox.setValue(value)
        return

    def get_max_enable(self):
        return self.ui.max_checkBox.isChecked()

    def set_max_enable(self, value):
        assert isinstance(value, bool)
        self.ui.max_checkBox.setChecked(value)
        return

    def get_max_value(self):
        return self.ui.max_doubleSpinBox.value()

    def set_max_value(self, value):
        assert isinstance(value, float)
        self.ui.max_doubleSpinBox.setValue(value)
        return

    def get_stiffness_enable(self):
        return self.ui.stiffness_checkBox.isChecked()

    def set_stiffness_enable(self, value):
        assert isinstance(value, bool)
        self.ui.stiffness_checkBox.setChecked(value)
        return

    def get_stiffness_value(self):
        return self.ui.stiffness_doubleSpinBox.value() * 0.01

    def set_stiffness_value(self, value):
        assert isinstance(value, float)
        self.ui.stiffness_doubleSpinBox.setValue(value * 100.0)
        return

    def get_smoothness_enable(self):
        return self.ui.smoothness_checkBox.isChecked()

    def set_smoothness_enable(self, value):
        assert isinstance(value, bool)
        self.ui.smoothness_checkBox.setChecked(value)
        return

    def get_smoothness_value(self):
        return self.ui.smoothness_doubleSpinBox.value() * 0.01

    def set_smoothness_value(self, value):
        assert isinstance(value, float)
        self.ui.smoothness_doubleSpinBox.setValue(value * 100.0)
        return

    def set_detail_values(self, value):
        assert isinstance(value, lib.AttrDetail)
        self.set_state(value.state)
        self.set_min_enable(value.min_enable)
        self.set_min_value(value.min_value)
        self.set_max_enable(value.max_enable)
        self.set_max_value(value.max_value)
        self.set_stiffness_enable(value.stiffness_enable)
        self.set_stiffness_value(value.stiffness_value)
        self.set_smoothness_enable(value.smoothness_enable)
        self.set_smoothness_value(value.smoothness_value)
        return

    def get_detail_values(self):
        value = lib.AttrDetail(
            state=self.get_state(),
            min_enable=self.get_min_enable(),
            min_value=self.get_min_value(),
            max_enable=self.get_max_enable(),
            max_value=self.get_max_value(),
            stiffness_enable=self.get_stiffness_enable(),
            stiffness_value=self.get_stiffness_value(),
            smoothness_enable=self.get_smoothness_enable(),
            smoothness_value=self.get_smoothness_value()
        )
        return value


def main(detail_values):
    assert isinstance(detail_values, lib.AttrDetail)
    app, parent_window = uiutils.getParent()
    dialog = Dialog(parent=parent_window)
    dialog.set_detail_values(detail_values)
    ret = dialog.exec_()
    status = ret == QtWidgets.QDialog.Accepted
    return status, dialog


def warn_user(title, text):
    LOG.warn(text.replace('\n', ' '))
    app, parent_window = uiutils.getParent()
    Qt.QtWidgets.QMessageBox.warning(parent_window, title, text)
    return
