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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


class SliderSpinBox(QtWidgets.QWidget):
    """
    A combined widget that synchronizes a QSlider and Q*SpinBox.

    The widget provides:
    - Synchronized slider and spin box values
    - Configurable min/max range
    - Optional tick marks on slider
    - Value changed signal
    - Integer or float value support
    - Customizable page step size
    - Configurable number of decimal numbers for floating-point numbers.

    Example usage:
    >>> slider_spin = SliderSpinBox(
    ...     parent=self,
    ...     min_value=1,
    ...     max_value=20,
    ...     default_value=2,
    ...     use_float=False,
    ...     show_ticks=True,
    ...     decimals=2
    ... )
    >>> slider_spin.valueChanged.connect(self.on_value_changed)

    """

    valueChanged = QtCore.Signal(object)  # Can be int or float

    def __init__(
        self,
        parent=None,
        min_value=0,
        max_value=100,
        default_value=0,
        use_float=False,
        page_step=1,
        show_ticks=False,
        decimals=3,
    ):
        super(SliderSpinBox, self).__init__(parent=parent)
        assert isinstance(min_value, (int, float))
        assert isinstance(max_value, (int, float))
        assert isinstance(default_value, (int, float))
        assert isinstance(use_float, bool)
        assert isinstance(page_step, (int, float))
        assert isinstance(show_ticks, bool)
        assert isinstance(decimals, int)

        self._use_float = use_float
        self._scale_factor = 1.0
        if use_float:
            self._scale_factor = 1000.0

        margins = 0
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(margins, margins, margins, margins)
        self._layout.setSpacing(7)

        self._slider = QtWidgets.QSlider(self)
        self._slider.setOrientation(QtCore.Qt.Horizontal)
        self._slider.setMinimum(int(min_value * self._scale_factor))
        self._slider.setMaximum(int(max_value * self._scale_factor))
        self._slider.setPageStep(int(page_step * self._scale_factor))
        if show_ticks:
            self._slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self._spin_box = None
        if use_float:
            self._spin_box = QtWidgets.QDoubleSpinBox()
        else:
            self._spin_box = QtWidgets.QSpinBox()
        self._spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._spin_box.setMinimum(min_value)
        self._spin_box.setMaximum(max_value)
        if use_float:
            self._spin_box.setDecimals(decimals)
            self._spin_box.setSingleStep(0.1)

        self._layout.addWidget(self._slider)
        self._layout.addWidget(self._spin_box)

        self._slider.valueChanged.connect(self._on_slider_value_changed)
        self._spin_box.valueChanged.connect(self._on_spin_box_value_changed)

        self.setValue(default_value)

    def _on_slider_value_changed(self, value):
        """Handle slider value changes and update spin box."""
        scaled_value = value / self._scale_factor
        if self._use_float:
            self._spin_box.setValue(float(scaled_value))
        else:
            self._spin_box.setValue(int(scaled_value))
        self.valueChanged.emit(scaled_value)

    def _on_spin_box_value_changed(self, value):
        """Handle spin box value changes and update slider."""
        scaled_value = int(value * self._scale_factor)
        if self._slider.value() != scaled_value:
            self._slider.setValue(scaled_value)
            # Note: valueChanged signal is emitted via slider value change

    def value(self):
        """Get the current value."""
        return self._spin_box.value()

    def setValue(self, value):
        """Set the widget value."""
        if self._use_float:
            self._spin_box.setValue(float(value))
        else:
            self._spin_box.setValue(int(value))

    def setMinimum(self, value):
        """Set the minimum allowed value."""
        self._slider.setMinimum(int(value * self._scale_factor))
        self._spin_box.setMinimum(value)

    def setMaximum(self, value):
        """Set the maximum allowed value."""
        self._slider.setMaximum(int(value * self._scale_factor))
        self._spin_box.setMaximum(value)

    def setRange(self, minimum, maximum):
        """Set both minimum and maximum values."""
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def setPageStep(self, step):
        """Set the page step size for the slider."""
        self._slider.setPageStep(int(step * self._scale_factor))
        if not self._use_float:
            self._spin_box.setSingleStep(step)

    def setDecimals(self, decimals):
        """Set the number of decimal places displayed for float values.

        :param decimals: Number of decimal places to display
        :type decimals: int
        """
        if self._use_float:
            self._spin_box.setDecimals(decimals)
