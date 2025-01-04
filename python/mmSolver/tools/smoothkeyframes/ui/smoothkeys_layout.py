# Copyright (C) 2019 David Cattermole
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
The main component of the user interface for the smooth keyframes
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.constant as utils_const
import mmSolver.ui.uisliderspinbox as uisliderspinbox
import mmSolver.tools.smoothkeyframes.constant as const
import mmSolver.tools.smoothkeyframes.ui.ui_smoothkeys_layout as ui_smoothkeys_layout


LOG = mmSolver.logger.get_logger()


class SmoothKeysLayout(QtWidgets.QWidget, ui_smoothkeys_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SmoothKeysLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Remove placeholder widgets.
        self.width_spinBox.setParent(None)
        self.width_slider.setParent(None)
        self.width_sliderSpinBox_layout.setParent(None)

        # Add slider spin-box, replacing placeholder widget from the
        # .ui file.
        widget = uisliderspinbox.SliderSpinBox(
            parent=self,
            min_value=1,
            max_value=20,
            default_value=2,
            use_float=False,
            show_ticks=True,
        )
        self.options_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, widget)
        self.width_sliderSpinBox = widget

        # Function
        modes = [
            str(utils_const.SMOOTH_TYPE_AVERAGE).title(),
            str(utils_const.SMOOTH_TYPE_GAUSSIAN).title(),
            str(utils_const.SMOOTH_TYPE_FOURIER).title(),
        ]
        self.function_comboBox.addItems(modes)
        self.function_comboBox.currentIndexChanged.connect(self.modeIndexChanged)

        # Width
        self.width_sliderSpinBox.valueChanged.connect(self.widthValueChanged)

        # Populate the UI with data
        self.populateUi()

    def modeIndexChanged(self, index):
        name = const.CONFIG_MODE_KEY
        value = utils_const.SMOOTH_TYPES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def widthValueChanged(self, value):
        self.width_sliderSpinBox.setValue(value)
        name = const.CONFIG_WIDTH_KEY
        value = float(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        name = const.CONFIG_MODE_KEY
        value = const.DEFAULT_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_WIDTH_KEY
        value = const.DEFAULT_WIDTH
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_MODE_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_MODE)
        value = str(value).title()
        LOG.debug('key=%r value=%r', name, value)
        self.function_comboBox.setCurrentText(value)

        name = const.CONFIG_WIDTH_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_WIDTH)
        LOG.debug('key=%r value=%r', name, value)
        self.width_sliderSpinBox.setValue(value)
        return
