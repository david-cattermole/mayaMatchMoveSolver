# Copyright (C) 2025 David Cattermole.
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
The main component of the user interface for the attribute curve filter pops
window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uisliderspinbox as uisliderspinbox
import mmSolver.tools.attributecurvefilterpops.constant as const
import mmSolver.tools.attributecurvefilterpops.lib as lib
import mmSolver.tools.attributecurvefilterpops.ui.ui_attrcurvefilterpops_layout as ui_layout

LOG = mmSolver.logger.get_logger()


class AttributeCurveFilterPopsLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeCurveFilterPopsLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Remove placeholder widget.
        self.threshold_doubleSpinBox.setParent(None)

        # Add slider spin-box, replacing placeholder widget from the
        # .ui file.
        widget = uisliderspinbox.SliderSpinBox(
            parent=self,
            min_value=0.0,
            max_value=2.0,
            default_value=1.0,
            page_step=0.25,
            use_float=True,
            show_ticks=True,
        )
        self.options_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, widget)
        self.threshold_sliderSpinBox = widget

        # Frame Range Mode
        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frame_range_combo.addItems(frame_range_modes)
        self.frame_range_combo.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Create connections
        self.start_frame_spinbox.valueChanged.connect(self.startFrameValueChanged)
        self.end_frame_spinbox.valueChanged.connect(self.endFrameValueChanged)
        self.threshold_sliderSpinBox.valueChanged.connect(self.thresholdValueChanged)

        self.populateUi()

    def frameRangeModeIndexChangedHelper(self, frame_range_mode):
        assert isinstance(frame_range_mode, pycompat.TEXT_TYPE)
        start_name = const.CONFIG_FRAME_START_KEY
        end_name = const.CONFIG_FRAME_END_KEY

        # Get frame range
        custom_start_frame = configmaya.get_scene_option(
            start_name, const.DEFAULT_FRAME_START
        )
        custom_end_frame = configmaya.get_scene_option(
            end_name, const.DEFAULT_FRAME_END
        )
        frame_range = lib.get_frame_range(
            frame_range_mode, custom_start_frame, custom_end_frame
        )

        # Set frame range widgets
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)

        # Disable and enable widgets based on frame range mode.
        if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
        elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
        elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
            self.start_frame_spinbox.setEnabled(True)
            self.end_frame_spinbox.setEnabled(True)

            # Set the custom frame values
            configmaya.set_scene_option(start_name, frame_range.start, add_attr=True)
            configmaya.set_scene_option(end_name, frame_range.end, add_attr=True)
        return

    def frameRangeModeIndexChanged(self):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        index = self.frame_range_combo.currentIndex()
        value = const.FRAME_RANGE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        self.frameRangeModeIndexChangedHelper(value)

    def startFrameValueChanged(self):
        name = const.CONFIG_FRAME_START_KEY
        value = self.start_frame_spinbox.value()
        configmaya.set_scene_option(name, value, add_attr=True)

    def endFrameValueChanged(self):
        name = const.CONFIG_FRAME_END_KEY
        value = self.end_frame_spinbox.value()
        configmaya.set_scene_option(name, value, add_attr=True)

    def thresholdValueChanged(self, value):
        self.threshold_sliderSpinBox.setValue(value)
        name = const.CONFIG_THRESHOLD_KEY
        value = float(value)
        configmaya.set_scene_option(name, value, add_attr=True)

    def reset_options(self):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = const.DEFAULT_FRAME_RANGE_MODE
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_FRAME_START_KEY
        value = const.DEFAULT_FRAME_START
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_FRAME_END_KEY
        value = const.DEFAULT_FRAME_END
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_THRESHOLD_KEY
        value = const.DEFAULT_THRESHOLD
        configmaya.set_scene_option(name, value)

        self.populateUi()
        return

    def populateUi(self):
        frame_range_mode = configmaya.get_scene_option(
            const.CONFIG_FRAME_RANGE_MODE_KEY, default=const.DEFAULT_FRAME_RANGE_MODE
        )
        start_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        end_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )
        threshold_value = configmaya.get_scene_option(
            const.CONFIG_THRESHOLD_KEY, default=const.DEFAULT_THRESHOLD
        )

        label = const.FRAME_RANGE_MODE_VALUE_LABEL_MAP[frame_range_mode]
        self.frame_range_combo.setCurrentText(label)

        frame_range = lib.get_frame_range(frame_range_mode, start_frame, end_frame)
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)

        self.frameRangeModeIndexChangedHelper(frame_range_mode)

        self.threshold_sliderSpinBox.setValue(threshold_value)
        return
