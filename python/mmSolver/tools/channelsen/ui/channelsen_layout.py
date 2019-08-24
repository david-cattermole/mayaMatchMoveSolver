# Copyright (C) 2019 Anil Reddy.
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
The main component of the user interface for the channel sensitivity
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.channelsen.ui.ui_channelsen_layout as ui_channelsen_layout
import mmSolver.tools.channelsen.lib as lib


LOG = mmSolver.logger.get_logger()


class ChannelSenLayout(QtWidgets.QWidget, ui_channelsen_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ChannelSenLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Connect Buttons
        self.up_pushButton.clicked.connect(
            self.upValueClicked
        )
        self.down_pushButton.clicked.connect(
            self.downValueClicked
        )
        self.default_pushButton.clicked.connect(
            self.defaultValueClicked
        )

        # Populate the UI with data
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        value = lib.get_value()
        self.setSensitivityText(value)
        return

    def upValueClicked(self):
        """
        Increase the channel box sensitivity.
        """
        value = lib.get_value()
        value *= 10
        lib.set_value(value)
        self.setSensitivityText(value)

    def downValueClicked(self):
        """
        Decrease the channel box sensitivity
        """
        value = lib.get_value()
        value *= 0.1
        lib.set_value(value)
        self.setSensitivityText(value)

    def defaultValueClicked(self):
        """
        Make the channel box sensitivity default value.
        """
        value = 1.0
        lib.set_value(value)
        self.setSensitivityText(value)

    def setSensitivityText(self, value):
        """
        Set the 'self.sensitivity_label' using the sensitivity value.

        :param value: Sensitivity float value to set to.
        :type value: float or str
        """
        text = str(value)
        if isinstance(value, (float, int)):
            text = '{0:= .3g}'.format(value)
        text = 'Value: ' + text
        self.sensitivity_label.setText(text)
        return
