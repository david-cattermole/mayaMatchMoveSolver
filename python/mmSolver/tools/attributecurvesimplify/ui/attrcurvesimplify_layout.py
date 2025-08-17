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
The main component of the user interface for the attribute curve
simplify window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

# import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets
import mmSolver.ui.Qt.QtGui as QtGui

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.uisliderspinbox as uisliderspinbox
import mmSolver.tools.attributecurvesimplify.constant as const
import mmSolver.tools.attributecurvesimplify.lib as lib
import mmSolver.tools.attributecurvesimplify.ui.ui_attrcurvesimplify_layout as ui_layout
import mmSolver.tools.attributecurvesimplify.widget.curve_display as curve_display

LOG = mmSolver.logger.get_logger()

# These colours were determined because of maximum visibility for most
# people (even if they are colour blind).
COLOR_LOWER = 16
COLOR_HIGHER = 255
GREEN_COLOR = QtGui.QColor(COLOR_LOWER, COLOR_HIGHER, COLOR_LOWER)
MAGENTA_COLOR = QtGui.QColor(COLOR_HIGHER, COLOR_LOWER, COLOR_HIGHER)
PRIMARY_COLOR = GREEN_COLOR
SECONDARY_COLOR = MAGENTA_COLOR


def _get_selected_anim_curves_and_node_attrs():
    anim_curve_nodes = lib.get_selected_anim_curves()
    node_attrs = lib.node_attr_from_anim_curve_nodes(anim_curve_nodes)

    sorted_anim_curve_nodes, sorted_node_attrs = lib.sort_anim_curves_by_node_attrs(
        anim_curve_nodes, node_attrs
    )
    return sorted_anim_curve_nodes, sorted_node_attrs


def _generate_curve_name(anim_curve_node):
    return str(anim_curve_node)


def _generate_curve_name_simplified(anim_curve_node):
    return anim_curve_node + "_simplified"


def _in_bounds(index, values):
    return index >= 0 and index < len(values)


class AttributeCurveSimplifyLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeCurveSimplifyLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.__active_curve_index = -1
        self.__anim_curve_nodes = []
        self.__node_attrs = []
        self.__curve_match_percentages = dict()
        self.__dirty_curves = set()  # Used to trigger re-calculations.

        # Remove placeholder widget.
        self.control_points_spinbox.setParent(None)
        # Add slider spin-box, replacing placeholder widget from the
        # .ui file.
        widget = uisliderspinbox.SliderSpinBox(
            parent=self,
            min_value=2,
            max_value=32,
            default_value=2,
            page_step=1,
            use_float=False,
            show_ticks=True,
        )
        self.options_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, widget)
        self.control_points_sliderSpinBox = widget

        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frame_range_combo.addItems(frame_range_modes)
        self.frame_range_combo.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Create connections
        self.start_frame_spinbox.valueChanged.connect(self.startFrameValueChanged)
        self.end_frame_spinbox.valueChanged.connect(self.endFrameValueChanged)
        self.control_points_sliderSpinBox.valueChanged.connect(
            self.controlPointsValueChanged
        )

        distributions = const.DISTRIBUTION_LABELS
        self.distribution_combo.addItems(distributions)
        self.distribution_combo.currentIndexChanged.connect(
            self.distributionIndexChanged
        )

        interpolations = const.INTERPOLATION_LABELS
        self.interpolation_combo.addItems(interpolations)
        self.interpolation_combo.currentIndexChanged.connect(
            self.interpolationIndexChanged
        )

        # Add slider spin-box for selecting a curve.
        self.curve_num_sliderSpinBox = uisliderspinbox.SliderSpinBox(
            parent=self,
            min_value=0,
            max_value=0,
            default_value=0,
            page_step=1,
            use_float=False,
            show_ticks=True,
        )
        self.curve_num_layout.insertWidget(1, self.curve_num_sliderSpinBox, stretch=1)
        self.curve_num_sliderSpinBox.valueChanged.connect(self.curveNumValueChanged)
        self.curve_num_update_button.clicked.connect(self.populateUi)

        # QSizePolicy sizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Fixed);
        # preview_curve_num_spinbox->setSizePolicy(sizePolicy);

        # Add Curve Display
        normalization_value = curve_display.NORMALISATION_MODE_GLOBAL_VALUE
        self.curve_display = curve_display.CurveDisplay(self)
        self.curve_display.set_normalization_mode(normalization_value)
        self.anim_curve_xy_data_map = dict()
        self.preview_groupBox.layout().addWidget(self.curve_display)

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

        # Set frame range widgets.
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)

        # Disable and enable widgets based on frame range mode.
        if frame_range_mode == const.FRAME_RANGE_MODE_INPUT_ANIM_CURVE_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
        elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
        elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)
        elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
            self.start_frame_spinbox.setEnabled(True)
            self.end_frame_spinbox.setEnabled(True)

            # Set the custom frame values.
            configmaya.set_scene_option(start_name, frame_range.start, add_attr=True)
            configmaya.set_scene_option(end_name, frame_range.end, add_attr=True)
        return

    def frameRangeModeIndexChanged(self):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        index = self.frame_range_combo.currentIndex()
        value = const.FRAME_RANGE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        self.frameRangeModeIndexChangedHelper(value)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

    def startFrameValueChanged(self):
        name = const.CONFIG_FRAME_START_KEY
        value = self.start_frame_spinbox.value()
        configmaya.set_scene_option(name, value, add_attr=True)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

    def endFrameValueChanged(self):
        name = const.CONFIG_FRAME_END_KEY
        value = self.end_frame_spinbox.value()
        configmaya.set_scene_option(name, value, add_attr=True)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

    def controlPointsValueChanged(self, value):
        self.control_points_sliderSpinBox.setValue(value)
        name = const.CONFIG_CONTROL_POINTS_KEY
        value = int(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

    def distributionIndexChanged(self):
        name = const.CONFIG_DISTRIBUTION_KEY
        index = self.distribution_combo.currentIndex()
        value = const.DISTRIBUTION_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

    def interpolationIndexChanged(self):
        name = const.CONFIG_INTERPOLATION_KEY
        index = self.interpolation_combo.currentIndex()
        value = const.INTERPOLATION_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        self.setAllCurvesDirtyStatus(self.__anim_curve_nodes, True)
        self.populateCurveDisplayUi()

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

        name = const.CONFIG_CONTROL_POINTS_KEY
        value = const.DEFAULT_CONTROL_POINTS
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_INTERPOLATION_KEY
        value = const.DEFAULT_INTERPOLATION
        configmaya.set_scene_option(name, value)

        name = const.CONFIG_DISTRIBUTION_KEY
        value = const.DEFAULT_DISTRIBUTION
        configmaya.set_scene_option(name, value)

        self.populateUi()
        return

    def getCurveDirtyStatus(self, node_name):
        dirty = node_name in self.__dirty_curves
        return dirty

    def setCurveDirtyStatus(self, node_name, value):
        if value is True:
            self.__dirty_curves.add(node_name)
        else:
            if node_name in self.__dirty_curves:
                self.__dirty_curves.remove(node_name)
        return

    def setAllCurvesDirtyStatus(self, node_names, value):
        for node_name in node_names:
            self.setCurveDirtyStatus(node_name, value)
        return

    def getActiveCurveNodeName(self):
        active_index = self.__active_curve_index
        assert isinstance(active_index, pycompat.INT_TYPES)
        anim_curve_node = None
        if _in_bounds(active_index, self.__anim_curve_nodes):
            anim_curve_node = self.__anim_curve_nodes[active_index]
        return anim_curve_node

    def setActiveCurve(self, active_index):
        assert isinstance(active_index, pycompat.INT_TYPES)
        if not _in_bounds(active_index, self.__anim_curve_nodes):
            LOG.warn("setActiveCurve: invalid index: %r", active_index)
            return

        anim_curve_node = self.__anim_curve_nodes[active_index]
        dirty = self.getCurveDirtyStatus(anim_curve_node)
        if dirty is True:
            num_control_points, distribution, interpolation = self.queryOptions()
            self.updateSimplifiedCurve(
                active_index, num_control_points, distribution, interpolation
            )
            self.setCurveDirtyStatus(anim_curve_node, False)

        self.curve_num_sliderSpinBox.setValue(active_index)
        self.updateCurveNameLabel()

        # quality_of_fit = lib.calc_quality_of_fit(x_data, y_data, curve_y_data)
        # label = "{}<curve name> (0 of 0)".format(prefix)
        # self.curve_name_label.setText(label)

    def curveNumValueChanged(self, value):
        assert isinstance(value, (int, float))
        value = int(value)

        # Hide previous curve.
        previous_curve_index = self.__active_curve_index
        if _in_bounds(previous_curve_index, self.__anim_curve_nodes):
            previous_anim_curve_node = self.__anim_curve_nodes[previous_curve_index]

            curve_name = _generate_curve_name(previous_anim_curve_node)
            self.curve_display.set_curve_visibility(curve_name, False)

            curve_name = _generate_curve_name_simplified(previous_anim_curve_node)
            self.curve_display.set_curve_visibility(curve_name, False)

        self.__active_curve_index = value
        self.setActiveCurve(self.__active_curve_index)

        # Show new curve.
        if _in_bounds(self.__active_curve_index, self.__anim_curve_nodes):
            active_anim_curve_node = self.__anim_curve_nodes[value]

            curve_name = _generate_curve_name(active_anim_curve_node)
            self.curve_display.set_curve_visibility(curve_name, True)

            curve_name = _generate_curve_name_simplified(active_anim_curve_node)
            self.curve_display.set_curve_visibility(curve_name, True)
        return

    def updateCurveNameLabel(self):
        prefix = "Active Curve: "
        if not _in_bounds(self.__active_curve_index, self.__anim_curve_nodes):
            label = "{}<curve name> (0 of 0)".format(prefix)
            self.curve_name_label.setText(label)
            return
        active_curve_name = self.__node_attrs[self.__active_curve_index]
        curve_count = len(self.__node_attrs)
        label = "{}{} ({} of {})".format(
            prefix, active_curve_name, self.__active_curve_index + 1, curve_count
        )
        self.curve_name_label.setText(label)

        active_anim_curve_node = self.__anim_curve_nodes[self.__active_curve_index]
        quality_of_fit = self.__curve_match_percentages.get(active_anim_curve_node)
        if quality_of_fit is not None:
            # We use an old method to display the percentage, because
            # we must support Python 2.7 and 3.x. See
            # stackoverflow.com for details:
            # https://stackoverflow.com/questions/5306756/how-to-print-a-percentage-value
            percentage_str = "%.2f%%" % quality_of_fit
            label = "Curve Match: {}".format(percentage_str)
            self.curve_match_label.setText(label.ljust(30))
        return

    def updateSimplifiedCurve(
        self, active_index, num_control_points, distribution, interpolation
    ):
        assert isinstance(active_index, pycompat.INT_TYPES)
        anim_curve_node = self.__anim_curve_nodes[active_index]

        x_data, y_data = self.anim_curve_xy_data_map[anim_curve_node]
        frame_start = int(x_data[0])
        frame_end = int(x_data[-1])
        curves_data = lib.simplify_curves(
            [anim_curve_node],
            frame_start,
            frame_end,
            num_control_points,
            distribution,
            interpolation,
            return_results=True,
        )
        assert len(curves_data) == 1
        curve_data = curves_data[0]
        curve_x_data, curve_y_data = curve_data
        curve_name = _generate_curve_name_simplified(anim_curve_node)
        self.curve_display.set_curve_data_by_name(
            curve_name,
            curve_x_data,
            curve_y_data,
        )

        quality_of_fit = lib.calc_quality_of_fit(x_data, y_data, curve_y_data)
        self.__curve_match_percentages[anim_curve_node] = quality_of_fit

    def updateCurveDisplay(
        self,
        anim_curve_nodes,
        node_attrs,
        frame_range,
        num_control_points,
        distribution,
        interpolation,
    ):
        assert isinstance(anim_curve_nodes, list)
        assert isinstance(node_attrs, list)
        assert isinstance(frame_range, time_utils.FrameRange)
        assert isinstance(num_control_points, pycompat.INT_TYPES)
        assert distribution in const.DISTRIBUTION_VALUES
        assert interpolation in const.INTERPOLATION_VALUES

        self.__anim_curve_nodes = anim_curve_nodes
        self.__node_attrs = node_attrs
        self.__curve_match_percentages = dict()

        self.anim_curve_xy_data_map = dict()
        for anim_curve_node in anim_curve_nodes:
            x_data, y_data = lib.query_anim_curve_data(anim_curve_node, frame_range)
            self.anim_curve_xy_data_map[anim_curve_node] = (x_data, y_data)

        self.curve_display.clear_curves()
        for i, (anim_curve_node, node_attr) in enumerate(
            zip(anim_curve_nodes, node_attrs)
        ):
            x_data, y_data = self.anim_curve_xy_data_map[anim_curve_node]
            curve_name = _generate_curve_name(anim_curve_node)
            self.curve_display.add_curve(
                curve_name,
                x_data,
                y_data,
                label=node_attr,
                color=PRIMARY_COLOR,
                opacity=1.0,
            )

            curve_name_simplified = _generate_curve_name_simplified(anim_curve_node)
            self.curve_display.add_curve(
                curve_name_simplified,
                x_data,
                y_data,
                label=node_attr + " (simplified)",
                color=SECONDARY_COLOR,
                opacity=1.0,
            )

            # We don't want any of the curves to be visible, until
            # they are activated, because we want the other code to
            # control the curve visibility.
            visible = False
            self.curve_display.set_curve_visibility(curve_name, visible)
            self.curve_display.set_curve_visibility(curve_name_simplified, visible)

        curve_count = len(anim_curve_nodes)
        self.curve_num_sliderSpinBox.setMinimum(0)
        self.curve_num_sliderSpinBox.setMaximum(curve_count - 1)
        return

    def queryOptions(self):
        num_control_points = configmaya.get_scene_option(
            const.CONFIG_CONTROL_POINTS_KEY, default=const.DEFAULT_CONTROL_POINTS
        )
        distribution = configmaya.get_scene_option(
            const.CONFIG_DISTRIBUTION_KEY, default=const.DEFAULT_DISTRIBUTION
        )
        interpolation = configmaya.get_scene_option(
            const.CONFIG_INTERPOLATION_KEY, default=const.DEFAULT_INTERPOLATION
        )

        assert isinstance(num_control_points, pycompat.INT_TYPES)
        assert distribution in const.DISTRIBUTION_VALUES
        assert interpolation in const.INTERPOLATION_VALUES
        return num_control_points, distribution, interpolation

    def queryFrameRangeData(self):
        frame_range_mode = configmaya.get_scene_option(
            const.CONFIG_FRAME_RANGE_MODE_KEY,
            default=const.DEFAULT_FRAME_RANGE_MODE,
        )
        start_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        end_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )
        frame_range = lib.get_frame_range(frame_range_mode, start_frame, end_frame)
        return frame_range, frame_range_mode

    def getCurrentCurve(self):
        node_attr = None
        anim_curve_node = None
        curve_index = self.__active_curve_index
        if _in_bounds(curve_index, self.__anim_curve_nodes):
            anim_curve_node = self.__anim_curve_nodes[self.__active_curve_index]
            node_attr = self.__node_attrs[self.__active_curve_index]
        return anim_curve_node, node_attr

    def getNewCurveIndex(
        self, previous_anim_curve_node, previous_node_attr, anim_curve_nodes, node_attrs
    ):
        # Find the previously selected curve.
        try:
            new_curve_index = node_attrs.index(previous_node_attr)
        except ValueError:
            try:
                new_curve_index = anim_curve_nodes.index(previous_anim_curve_node)
            except ValueError:
                # It's not valid, so the index is outside the bounds.
                new_curve_index = -1
        return new_curve_index

    def populateCurveDisplayUi(self):
        previous_anim_curve_node, previous_node_attr = self.getCurrentCurve()
        anim_curve_nodes, node_attrs = _get_selected_anim_curves_and_node_attrs()
        new_curve_index = self.getNewCurveIndex(
            previous_anim_curve_node, previous_node_attr, anim_curve_nodes, node_attrs
        )
        same_anim_curve_nodes = self.__anim_curve_nodes == anim_curve_nodes
        same_node_attrs = self.__node_attrs == node_attrs
        different_inputs = (not same_anim_curve_nodes) or (not same_node_attrs)
        if different_inputs is True:
            self.__anim_curve_nodes = anim_curve_nodes
            self.__node_attrs = node_attrs
            self.__curve_match_percentages = dict()
        self.setAllCurvesDirtyStatus(anim_curve_nodes, True)
        if new_curve_index >= 0:
            self.__active_curve_index = new_curve_index
            self.setActiveCurve(self.__active_curve_index)
        return

    def populateUi(self):
        frame_range, frame_range_mode = self.queryFrameRangeData()
        num_control_points, distribution, interpolation = self.queryOptions()

        label = const.FRAME_RANGE_MODE_VALUE_LABEL_MAP[frame_range_mode]
        self.frame_range_combo.setCurrentText(label)
        self.start_frame_spinbox.setValue(frame_range.start)
        self.end_frame_spinbox.setValue(frame_range.end)
        self.frameRangeModeIndexChangedHelper(frame_range_mode)
        self.control_points_sliderSpinBox.setValue(num_control_points)

        label = const.DISTRIBUTION_VALUE_LABEL_MAP[distribution]
        self.distribution_combo.setCurrentText(label)

        label = const.INTERPOLATION_VALUE_LABEL_MAP[interpolation]
        self.interpolation_combo.setCurrentText(label)

        previous_anim_curve_node, previous_node_attr = self.getCurrentCurve()
        anim_curve_nodes, node_attrs = _get_selected_anim_curves_and_node_attrs()
        self.setAllCurvesDirtyStatus(anim_curve_nodes, True)
        if len(anim_curve_nodes) > 0:
            new_curve_index = self.getNewCurveIndex(
                previous_anim_curve_node,
                previous_node_attr,
                anim_curve_nodes,
                node_attrs,
            )
            self.__active_curve_index = max(0, new_curve_index)

        self.updateCurveDisplay(
            anim_curve_nodes,
            node_attrs,
            frame_range,
            num_control_points,
            distribution,
            interpolation,
        )
        self.curveNumValueChanged(self.__active_curve_index)

    def applyToActiveCurve(self):
        # To avoid cyclical import dependencies, we import inline.
        import mmSolver.tools.attributecurvesimplify.tool as tool

        anim_curve_node, _node_attr = self.getCurrentCurve()
        anim_curve_nodes = [anim_curve_node]
        return tool.main(anim_curve_nodes=anim_curve_nodes)
