# Copyright (C) 2019, 2021 David Cattermole, Kazuma Tonegawa.
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
Window for the Center 2D Offset tool.

Usage::

   import mmSolver.tools.smoothkeys.ui.smoothkeys_window as smoothkeys_window
   smoothkeys_window.main()

"""
from functools import partial

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.centertwodee.constant as const
import mmSolver.tools.centertwodee.lib as lib
import mmSolver.tools.centertwodee.ui.centertwodee_layout as centertwodee_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class CenterTwoDeeWindow(BaseWindow):
    name = 'Center2dOffsetWindow'

    def __init__(self, parent=None, name=None):
        super(CenterTwoDeeWindow, self).__init__(parent,
                                                 name=name)
        self.setupUi(self)
        self.addSubForm(centertwodee_layout.CenterTwoDeeLayout)
        self.offset_node, self.camera_shape = lib.get_offset_nodes()
        self.form = self.getSubForm()

        # Set slider defaults in subform
        self.set_initial_values()

        # Connect events in subform
        self.form.horizontal_horizontalSlider.valueChanged.connect(
            partial(self.form.sliderValueChanged, type='horizontal')
        )
        self.form.vertical_horizontalSlider.valueChanged.connect(
            partial(self.form.sliderValueChanged, type='vertical')
        )
        self.form.zoom_horizontalSlider.valueChanged.connect(
            self.form.zoomValueChanged
        )
        self.form.horizontal_signal.connect(self.horizontal_offset_node_update)
        self.form.vertical_signal.connect(self.vertical_offset_node_update)
        self.form.zoom_signal.connect(self.camera_shape_update)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        # self.applyBtn.show()
        self.resetBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        # self.applyBtn.setText('Smooth')

        # self.applyBtn.clicked.connect(tool.smooth_selected_keyframes)
        self.resetBtn.setText('Reset All')
        self.resetBtn.clicked.connect(self.reset_options)
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    @QtCore.Slot(float)
    def horizontal_offset_node_update(self, value):
        output = lib.process_value(
            input_value=value,
            source='slider',
            zoom=False
        )
        if self.offset_node:
            lib.set_horizontal_offset(self.camera_shape, self.offset_node, output)

    @QtCore.Slot(float)
    def vertical_offset_node_update(self, value):
        output = lib.process_value(
            input_value=value,
            source='slider',
            zoom=False
        )
        if self.offset_node:
            lib.set_vertical_offset(self.camera_shape, self.offset_node, output)

    @QtCore.Slot(float)
    def camera_shape_update(self, value):
        output = lib.process_value(
            input_value=value,
            source='slider',
            zoom=True
        )
        if self.camera_shape:
            lib.set_zoom(self.camera_shape, output)

    def reset_options(self):
        self.form.reset_options()
        return

    def help(self):
        src = helputils.get_help_source()
        page = 'tools_generaltools.html#center-2d-on-selection'
        helputils.open_help_in_browser(page=page, help_source=src)
        return

    def set_initial_values(self):
        if not self.offset_node:
            horizontal_slider_value = const.DEFAULT_SLIDER_VALUE
            vertical_slider_value = const.DEFAULT_SLIDER_VALUE
            zoom_slider_value = const.DEFAULT_SLIDER_VALUE
        else:
            offset_values = lib.get_offset_node_values(self.offset_node)
            LOG.info(('centertwodee_window set_values:', offset_values))
            offset_x_value, offset_y_value = offset_values
            zoom_value = lib.get_camera_zoom(self.camera_shape)
            horizontal_slider_value = lib.process_value(
                input_value=offset_x_value,
                source='node',
                zoom=False
            )
            vertical_slider_value = lib.process_value(
                input_value=offset_y_value,
                source='node',
                zoom=False
            )
            zoom_slider_value = lib.process_value(
                input_value=zoom_value,
                source='node',
                zoom=True
            )
            LOG.info(('centertwodee_window set_values converted:', horizontal_slider_value, vertical_slider_value, zoom_slider_value))
        self.form.horizontal_horizontalSlider.setValue(int(horizontal_slider_value))
        self.form.vertical_horizontalSlider.setValue(int(vertical_slider_value))
        self.form.zoom_horizontalSlider.setValue(int(zoom_slider_value))


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Smooth Keyframes UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: SolverWindow or None.
    """
    win = CenterTwoDeeWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
