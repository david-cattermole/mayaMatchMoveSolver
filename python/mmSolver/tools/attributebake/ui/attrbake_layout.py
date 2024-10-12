# Copyright (C) 2021 Patcha Saheb Binginapalli.
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
The main component of the user interface for the attribute (fast) bake
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
import mmSolver.tools.attributebake.ui.ui_attrbake_layout as ui_layout
import mmSolver.tools.attributebake.constant as const
import mmSolver.tools.attributebake.lib as lib

LOG = mmSolver.logger.get_logger()


class AttributeBakeLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeBakeLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Frame Range Mode
        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frame_range_combo.addItems(frame_range_modes)
        self.frame_range_combo.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Create connections
        self.start_frame_spinbox.valueChanged.connect(self.startFrameValueChanged)
        self.end_frame_spinbox.valueChanged.connect(self.endFrameValueChanged)
        self.smart_bake_cbox.stateChanged.connect(self.smartBakeValueChanged)
        self.channel_box_cbox.stateChanged.connect(self.fromChannelBoxValueChanged)
        self.preserve_outside_keys_cbox.stateChanged.connect(
            self.preserveOutsideKeysValueChanged
        )

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
        frame_range = lib.get_bake_frame_range(
            frame_range_mode, custom_start_frame, custom_end_frame
        )

        # Set frame range widgets
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)

        # Disable and enable widgets based on frame range mode.
        if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
            self.smart_bake_cbox.setEnabled(True)
        elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
            self.smart_bake_cbox.setEnabled(True)
        elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
            self.start_frame_spinbox.setEnabled(True)
            self.end_frame_spinbox.setEnabled(True)
            self.smart_bake_cbox.setEnabled(False)
            self.smart_bake_cbox.setChecked(False)

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

    def smartBakeValueChanged(self):
        name = const.CONFIG_SMART_BAKE_KEY
        value = self.smart_bake_cbox.isChecked()
        configmaya.set_scene_option(name, value, add_attr=True)

    def fromChannelBoxValueChanged(self):
        name = const.CONFIG_FROM_CHANNELBOX_KEY
        value = self.channel_box_cbox.isChecked()
        configmaya.set_scene_option(name, value, add_attr=True)

    def preserveOutsideKeysValueChanged(self):
        name = const.CONFIG_PRESERVE_OUTSIDE_KEYS_KEY
        value = self.preserve_outside_keys_cbox.isChecked()
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

        name = const.CONFIG_SMART_BAKE_KEY
        value = const.DEFAULT_SMART_BAKE_STATE
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_FROM_CHANNELBOX_KEY
        value = const.DEFAULT_FROM_CHANNELBOX_STATE
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_PRESERVE_OUTSIDE_KEYS_KEY
        value = const.DEFAULT_PRESERVE_OUTSIDE_KEYS_STATE
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
        smart_bake_state = configmaya.get_scene_option(
            const.CONFIG_SMART_BAKE_KEY, default=const.DEFAULT_SMART_BAKE_STATE
        )
        from_channelbox_state = configmaya.get_scene_option(
            const.CONFIG_FROM_CHANNELBOX_KEY,
            default=const.DEFAULT_FROM_CHANNELBOX_STATE,
        )
        preserve_outside_keys_state = configmaya.get_scene_option(
            const.CONFIG_PRESERVE_OUTSIDE_KEYS_KEY,
            default=const.DEFAULT_PRESERVE_OUTSIDE_KEYS_STATE,
        )

        label = const.FRAME_RANGE_MODE_VALUE_LABEL_MAP[frame_range_mode]
        self.frame_range_combo.setCurrentText(label)

        frame_range = lib.get_bake_frame_range(frame_range_mode, start_frame, end_frame)
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)

        self.frameRangeModeIndexChangedHelper(frame_range_mode)

        self.smart_bake_cbox.setChecked(bool(smart_bake_state))
        self.channel_box_cbox.setChecked(bool(from_channelbox_state))
        self.preserve_outside_keys_cbox.setChecked(bool(preserve_outside_keys_state))
        return
