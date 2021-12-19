# Copyright (C) 2020 David Cattermole
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
The main component of the user interface for the raycast markers
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds

import mmSolver.logger
import mmSolver.tools.raycastmarker.ui.ui_raycastmarker_layout as ui_layout
import mmSolver.tools.raycastmarker.constant as const
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.time as time_utils


LOG = mmSolver.logger.get_logger()


class RayCastMarkerLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(RayCastMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Frame Range Mode
        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frameRangeModeComboBox.addItems(frame_range_modes)
        self.frameRangeModeComboBox.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Start and End Frame
        self.frameRangeStartSpinBox.valueChanged.connect(
            self.startFrameValueChanged
        )
        self.frameRangeEndSpinBox.valueChanged.connect(
            self.endFrameValueChanged
        )

        self.bundleUnlockRelockCheckBox.stateChanged.connect(
            self.bundleUnlockRelockStateChanged
        )

        # Populate the UI with data
        self.populateUi()

    def frameRangeModeIndexChanged(self, index):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = const.FRAME_RANGE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

        enable_custom = value == const.FRAME_RANGE_MODE_CUSTOM_VALUE
        self.frameRangeStartSpinBox.setEnabled(enable_custom)
        self.frameRangeEndSpinBox.setEnabled(enable_custom)

        frame_start = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY,
            default=const.DEFAULT_FRAME_START)
        frame_end = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY,
            default=const.DEFAULT_FRAME_END)
        if value == const.FRAME_RANGE_MODE_CURRENT_FRAME_VALUE:
            frame_start = maya.cmds.currentTime(query=True)
            frame_end = frame_start
        elif value == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
        elif value == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
        self.frameRangeStartSpinBox.setValue(frame_start)
        self.frameRangeEndSpinBox.setValue(frame_end)

    def startFrameValueChanged(self, value):
        name = const.CONFIG_FRAME_START_KEY
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def endFrameValueChanged(self, value):
        name = const.CONFIG_FRAME_END_KEY
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def bundleUnlockRelockStateChanged(self, value):
        name = const.CONFIG_BUNDLE_UNLOCK_RELOCK_KEY
        value = bool(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = const.DEFAULT_FRAME_RANGE_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_FRAME_START_KEY
        value = const.DEFAULT_FRAME_START
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_FRAME_END_KEY
        value = const.DEFAULT_FRAME_END
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_BUNDLE_UNLOCK_RELOCK_KEY
        value = const.DEFAULT_BUNDLE_UNLOCK_RELOCK
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        self.populateUi()
        return

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = configmaya.get_scene_option(
            name,
            default=const.DEFAULT_FRAME_RANGE_MODE)
        index = const.FRAME_RANGE_MODE_VALUES.index(value)
        label = const.FRAME_RANGE_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.frameRangeModeComboBox.setCurrentText(label)

        enable_custom = value == const.FRAME_RANGE_MODE_CUSTOM_VALUE
        self.frameRangeStartSpinBox.setEnabled(enable_custom)
        self.frameRangeEndSpinBox.setEnabled(enable_custom)

        frame_start = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY,
            default=const.DEFAULT_FRAME_START)
        frame_end = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY,
            default=const.DEFAULT_FRAME_END)
        if value == const.FRAME_RANGE_MODE_CURRENT_FRAME_VALUE:
            frame_start = maya.cmds.currentTime(query=True)
            frame_end = frame_start
        elif value == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
        elif value == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
        LOG.debug('key=%r value=%r', const.CONFIG_FRAME_START_KEY, frame_start)
        LOG.debug('key=%r value=%r', const.CONFIG_FRAME_END_KEY, frame_end)
        self.frameRangeStartSpinBox.setValue(frame_start)
        self.frameRangeEndSpinBox.setValue(frame_end)

        name = const.CONFIG_BUNDLE_UNLOCK_RELOCK_KEY
        value = configmaya.get_scene_option(
            name,
            default=const.DEFAULT_BUNDLE_UNLOCK_RELOCK)
        LOG.debug('key=%r value=%r', name, value)
        self.bundleUnlockRelockCheckBox.setChecked(value)
        return
