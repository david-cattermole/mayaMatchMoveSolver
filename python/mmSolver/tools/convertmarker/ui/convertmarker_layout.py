# Copyright (C) 2019, 2021 David Cattermole
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
The main component of the user interface for the Convert To Marker
window.

This UI offers the ability to change options for converting Markers,
including:

- Frame Range (start and end frames)
- Bundle Position
- Delete Static AnimCurves or not.

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.convertmarker.ui.ui_convertmarker_layout as ui_convertmarker_layout
import mmSolver.tools.convertmarker.constant as const


LOG = mmSolver.logger.get_logger()


class ConvertMarkerLayout(QtWidgets.QWidget, ui_convertmarker_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ConvertMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Frame Range Mode
        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frameRangeModeComboBox.addItems(frame_range_modes)
        self.frameRangeModeComboBox.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Start and End Frame
        self.frameRangeStartSpinBox.valueChanged.connect(self.startFrameValueChanged)
        self.frameRangeEndSpinBox.valueChanged.connect(self.endFrameValueChanged)

        # Bundle Position Mode
        bundle_position_modes = const.BUNDLE_POSITION_MODE_LABELS
        self.bundlePositionModeComboBox.addItems(bundle_position_modes)
        self.bundlePositionModeComboBox.currentIndexChanged.connect(
            self.bundlePositionModeIndexChanged
        )

        # Delete Static AnimCurves
        self.deleteStaticAnimCurvesCheckBox.stateChanged.connect(
            self.deleteStaticAnimCurvesStateChanged
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
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        frame_end = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )
        frame_start, frame_end = time_utils.get_frame_range(
            value, start_frame=frame_start, end_frame=frame_end
        )
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

    def bundlePositionModeIndexChanged(self, index):
        name = const.CONFIG_BUNDLE_POSITION_MODE_KEY
        value = const.BUNDLE_POSITION_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def deleteStaticAnimCurvesStateChanged(self, value):
        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
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

        name = const.CONFIG_BUNDLE_POSITION_MODE_KEY
        value = const.DEFAULT_BUNDLE_POSITION_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
        value = const.DEFAULT_DELETE_STATIC_ANIM_CURVES
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
            name, default=const.DEFAULT_FRAME_RANGE_MODE
        )
        index = const.FRAME_RANGE_MODE_VALUES.index(value)
        label = const.FRAME_RANGE_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.frameRangeModeComboBox.setCurrentText(label)

        enable_custom = value == const.FRAME_RANGE_MODE_CUSTOM_VALUE
        self.frameRangeStartSpinBox.setEnabled(enable_custom)
        self.frameRangeEndSpinBox.setEnabled(enable_custom)

        name_start = const.CONFIG_FRAME_START_KEY
        name_end = const.CONFIG_FRAME_END_KEY
        frame_start = configmaya.get_scene_option(
            name_start, default=const.DEFAULT_FRAME_START
        )
        frame_end = configmaya.get_scene_option(
            name_end, default=const.DEFAULT_FRAME_END
        )
        frame_start, frame_end = time_utils.get_frame_range(
            value, start_frame=frame_start, end_frame=frame_end
        )
        LOG.debug('key=%r value=%r', name_start, frame_start)
        LOG.debug('key=%r value=%r', name_end, frame_end)
        self.frameRangeStartSpinBox.setValue(frame_start)
        self.frameRangeEndSpinBox.setValue(frame_end)

        name = const.CONFIG_BUNDLE_POSITION_MODE_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_BUNDLE_POSITION_MODE
        )
        index = const.BUNDLE_POSITION_MODE_VALUES.index(value)
        label = const.BUNDLE_POSITION_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.bundlePositionModeComboBox.setCurrentText(label)

        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_DELETE_STATIC_ANIM_CURVES
        )
        LOG.debug('key=%r value=%r', name, value)
        self.deleteStaticAnimCurvesCheckBox.setChecked(value)
        return
