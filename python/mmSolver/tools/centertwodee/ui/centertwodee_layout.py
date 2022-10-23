# Copyright (C) 2019, 2021 David Cattermole, Kazuma Tonegawa
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
The main component of the user interface for the Center 2D Offset
window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets
import mmSolver.ui.Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.tools.centertwodee.ui.ui_centertwodee_layout as ui_centertwodee_layout
import mmSolver.tools.centertwodee.constant as const


LOG = mmSolver.logger.get_logger()


class CenterTwoDeeLayout(QtWidgets.QWidget, ui_centertwodee_layout.Ui_Form):
    horizontal_signal = QtCore.Signal(float)
    vertical_signal = QtCore.Signal(float)
    zoom_signal = QtCore.Signal(float)

    def __init__(self, parent=None, *args, **kwargs):
        super(CenterTwoDeeLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # TODO: Add a combo-box to allow choosing a a camera
        # explicitly, or a label to print out what camera the UI is
        # connected to.

        self.horzontal_reset_pushButton.clicked.connect(
            self.reset_horizontal_pan_slider
        )
        self.vertical_reset_pushButton.clicked.connect(self.reset_vertical_pan_slider)
        self.zoom_reset_pushButton.clicked.connect(self.reset_zoom_slider)

    def sliderValueChanged(self, value, type=None):
        if type == 'horizontal':
            self.horizontal_signal.emit(value)
        elif type == 'vertical':
            self.vertical_signal.emit(value)

    def zoomValueChanged(self, value):
        self.zoom_signal.emit(value)

    def reset_horizontal_pan_slider(self):
        self.horizontal_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)

    def reset_vertical_pan_slider(self):
        self.vertical_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)

    def reset_zoom_slider(self):
        self.zoom_horizontalSlider.setValue(const.DEFAULT_SLIDER_VALUE)

    def reset_options(self):
        self.reset_horizontal_pan_slider()
        self.reset_vertical_pan_slider()
        self.reset_zoom_slider()
        return
