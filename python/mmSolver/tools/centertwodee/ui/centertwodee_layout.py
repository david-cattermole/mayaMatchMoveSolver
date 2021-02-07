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

import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.centertwodee.ui.ui_centertwodee_layout as ui_centertwodee_layout
import mmSolver.tools.centertwodee.constant as const
# import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.constant as utils_const


LOG = mmSolver.logger.get_logger()


class CenterTwoDeeLayout(QtWidgets.QWidget, ui_centertwodee_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(CenterTwoDeeLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # # Function
        # modes = [
        #     str(utils_const.SMOOTH_TYPE_AVERAGE).title(),
        #     str(utils_const.SMOOTH_TYPE_GAUSSIAN).title(),
        #     str(utils_const.SMOOTH_TYPE_FOURIER).title(),
        # ]
        # self.function_comboBox.addItems(modes)
        # self.function_comboBox.currentIndexChanged.connect(
        #     self.modeIndexChanged
        # )

        # Set slider defaults
        self.horizontal_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)
        self.vertical_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)
        self.zoom_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)


        # Connect events
        self.horizontal_horizontalSlider.valueChanged.connect(
            self.horizontalValueChanged
        )
        # self.width_spinBox.valueChanged.connect(
        #     self.widthSpinBoxValueChanged
        # )

        # self.vertical_horizontalSlider.valueChanged.connect(
        #     self.verticalValueChanged
        # )
        # self.zoom_horizontalSlider.valueChanged.connect(
        #     self.zoomValueChanged
        # )

        # # Populate the UI with data
        # self.populateUi()

    # def modeIndexChanged(self, index):
    #     name = const.CONFIG_MODE_KEY
    #     value = utils_const.SMOOTH_TYPES[index]
    #     configmaya.set_scene_option(name, value, add_attr=True)
    #     LOG.debug('key=%r value=%r', name, value)

    def horizontalValueChanged(self, value):
        output = self.convertRange(
            input_value=value,
            input_range_start=int(self.horizontal_horizontalSlider.minimum()),
            input_range_end=int(self.horizontal_horizontalSlider.maximum()),
            output_range_start=const.PAN_MIN,
            output_range_end=const.PAN_MAX
            )
        # self.horizontal_horizontalSlider.setValue(output)

    # def widthSpinBoxValueChanged(self, value):
    #     self.width_horizontalSlider.setValue(value)
    #     name = const.CONFIG_WIDTH_KEY
    #     value = float(value)
    #     configmaya.set_scene_option(name, value, add_attr=True)
    #     LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        # name = const.CONFIG_MODE_KEY
        # value = const.DEFAULT_MODE
        # configmaya.set_scene_option(name, value)
        # LOG.debug('key=%r value=%r', name, value)
        #
        # name = const.CONFIG_WIDTH_KEY
        # value = const.DEFAULT_WIDTH
        # configmaya.set_scene_option(name, value)
        # LOG.debug('key=%r value=%r', name, value)
        #
        # self.populateUi()
        return

    def convertRange(self, **kwargs):
        # input_value, input_range_start, input_range_end, output_range_start, output_range_end
        # output = output_start + ((output_end - output_start) / (input_end - input_start)) * (input - input_start)
        input_value = kwargs.get('input_value')
        input_range_start = kwargs.get('input_range_start')
        input_range_end = kwargs.get('input_range_end')
        output_range_start = kwargs.get('output_range_start')
        output_range_end = kwargs.get('output_range_end')
        input_diff = input_range_end - input_range_start
        output_diff = output_range_end - output_range_start
        output_value = (
                (output_diff / input_diff) * (input_value - input_range_start)
                ) + output_range_start
        return output_value

    # def populateUi(self):
    #     """
    #     Update the UI for the first time the class is created.
    #     """
    #     name = const.CONFIG_MODE_KEY
    #     value = configmaya.get_scene_option(
    #         name,
    #         default=const.DEFAULT_MODE)
    #     value = str(value).title()
    #     LOG.debug('key=%r value=%r', name, value)
    #     self.function_comboBox.setCurrentText(value)
    #
    #     name = const.CONFIG_WIDTH_KEY
    #     value = configmaya.get_scene_option(
    #         name,
    #         default=const.DEFAULT_WIDTH)
    #     LOG.debug('key=%r value=%r', name, value)
    #     self.width_horizontalSlider.setValue(value)
    #     self.width_spinBox.setValue(value)
    #     return
