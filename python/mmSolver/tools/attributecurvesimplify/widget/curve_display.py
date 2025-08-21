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

import mmSolver.utils.python_compat as pycompat

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets


NORMALISATION_MODE_INDIVIDIAL_VALUE = "individual_normalisation"
NORMALISATION_MODE_GLOBAL_VALUE = "global_normalisation"
NORMALISATION_MODE_VALUES = [
    NORMALISATION_MODE_INDIVIDIAL_VALUE,
    NORMALISATION_MODE_GLOBAL_VALUE,
]


def _calculate_bounds(x_data, y_data):
    """Calculate the original bounds of a data set."""
    assert x_data and y_data

    x_min, x_max = min(x_data), max(x_data)
    y_min, y_max = min(y_data), max(y_data)

    # Handle case where curve is flat
    if x_min == x_max:
        x_min -= 0.5
        x_max += 0.5
    if y_min == y_max:
        y_min -= 0.5
        y_max += 0.5

    original_bounds = QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
    return original_bounds


def _calculate_global_bounds(curves):
    """Calculate the combined bounds of all visible curves."""
    if not curves:
        return None

    visible_curves = [curve for curve in curves.values() if curve.visible]
    if not visible_curves:
        return None

    # Find the overall bounds.
    all_x_values = []
    all_y_values = []
    for curve in visible_curves:
        all_x_values.extend(curve.x_data)
        all_y_values.extend(curve.y_data)
    if not all_x_values or not all_y_values:
        return QtCore.QRectF()
    x_min, x_max = min(all_x_values), max(all_x_values)
    y_min, y_max = min(all_y_values), max(all_y_values)

    # Handle flat curves.
    if x_min == x_max:
        x_min -= 0.5
        x_max += 0.5
    if y_min == y_max:
        y_min -= 0.5
        y_max += 0.5

    return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)


def _calculate_normalized_curve_data(
    target_bounds, x_data, y_data, original_bounds=None
):
    """Get curve data normalized to target bounds"""
    if original_bounds is None:
        original_bounds = _calculate_bounds(x_data, y_data)

    if not x_data or not y_data or original_bounds.isValid() is False:
        return [], []

    # Calculate scale factors.
    x_scale = target_bounds.width() / original_bounds.width()
    y_scale = target_bounds.height() / original_bounds.height()

    # Calculate offsets.
    x_offset = target_bounds.left() - original_bounds.left() * x_scale

    # Fix for Y-axis inversion - flip the Y coordinate system.
    #
    # Map the bottom of original bounds to bottom of target bounds.
    y_offset = target_bounds.bottom() + original_bounds.top() * y_scale

    # Transform data.
    normalized_x = [x * x_scale + x_offset for x in x_data]
    # Invert Y coordinates by subtracting from the flipped offset.
    normalized_y = [y_offset - y * y_scale for y in y_data]

    return normalized_x, normalized_y


class CurveData:
    """Container for curve data and display properties"""

    def __init__(self, x_data, y_data, label="", color=None, opacity=1.0):
        self.x_data = list(x_data)
        self.y_data = list(y_data)
        self.label = label
        self.base_color = color if color else QtGui.QColor(0, 100, 200)
        self.base_opacity = opacity
        self.visible = True
        self.selected = False
        self.curve_item = None

    @property
    def color(self):
        """Get the current color (lighter if selected)"""
        if self.selected:
            # Make color lighter when selected.
            return self.base_color.lighter(120)
        return self.base_color

    @property
    def opacity(self):
        """Get the current opacity (100% if selected)"""
        if self.selected:
            return 1.0
        return self.base_opacity

    @property
    def line_width(self):
        """Get line width (thicker if selected)"""
        return 1.5 if self.selected else 1.0


class CurveGraphicsView(QtWidgets.QGraphicsView):
    """Custom QtWidgets.QGraphicsView that stretches content to fill view"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # Disable all interactions.
        self.setInteractive(False)

    def resizeEvent(self, event):
        """Auto-fit content when view is resized"""
        super().resizeEvent(event)
        if self.scene():
            self.fit_to_view()

    def fit_to_view(self):
        """Stretch the scene content to fill the entire view"""
        if self.scene() and self.scene().sceneRect().isValid():
            # Use IgnoreAspectRatio to stretch content to fill view.
            self.fitInView(self.scene().sceneRect(), QtCore.Qt.IgnoreAspectRatio)


class CurveDisplay(QtWidgets.QWidget):
    """Standalone widget for displaying curves without any controls"""

    # Signal emitted when curve selection changes.
    # Emits the name of selected curve.
    selectionChanged = QtCore.Signal(str)

    # Signal emitted when curves are added/removed.
    curvesUpdated = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid_lines = []
        self.curves = {}

        # Normalisation of the curves on the display may be individually
        # normalised or normalised as a whole.
        self._normalization_mode = NORMALISATION_MODE_INDIVIDIAL_VALUE

        # Use a simple unit square that will be stretched to fill the
        # view.
        self.display_bounds = QtCore.QRectF(0, 0, 100, 100)

        self.view = CurveGraphicsView()
        self.scene = QtWidgets.QGraphicsScene()
        self.view.setScene(self.scene)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

    def set_normalization_mode(self, value):
        """Set whether to use individual curve normalization or global
        normalization.
        """
        assert value in NORMALISATION_MODE_VALUES
        self._normalization_mode = value
        self._update_display()

    def add_curve(self, name, x_data, y_data, label=None, color=None, opacity=1.0):
        """Add a curve to the display."""
        assert isinstance(name, pycompat.TEXT_TYPE)
        if label is None:
            label = name
        curve_data = CurveData(x_data, y_data, label, color, opacity)
        self.curves[name] = curve_data
        self._update_display()
        self.curvesUpdated.emit()

    def remove_curve(self, name):
        """Remove a curve from the display."""
        assert isinstance(name, pycompat.TEXT_TYPE)
        if name in self.curves:
            del self.curves[name]
            self._update_display()
            self.curvesUpdated.emit()
        return

    def clear_curves(self):
        """Remove all curves."""
        self.curves.clear()
        self._update_display()
        self.curvesUpdated.emit()

    def set_curve_visibility(self, name, visible):
        """Set visibility of a specific curve."""
        assert isinstance(name, pycompat.TEXT_TYPE)
        assert isinstance(visible, bool)
        if name in self.curves:
            self.curves[name].visible = visible
            self._update_display()
        return

    def select_curve(self, name, value):
        """Select or deselect a curve."""
        assert isinstance(name, pycompat.TEXT_TYPE)
        assert isinstance(value, bool)
        if name not in self.curves:
            return

        if value is True:
            for curve_name in self.curves:
                self.curves[curve_name].selected = False
            self.curves[name].selected = True
            self.selectionChanged.emit(name)
        else:
            self.curves[name].selected = False

        self._update_display()

    def get_selected_curve_name(self):
        """Get the name of the currently selected curve."""
        for name, curve in self.curves.items():
            if curve.selected:
                return name
        return None

    def get_curve_names(self):
        """Get list of all curve names."""
        return list(sorted(self.curves.keys()))

    def set_curve_data_by_name(self, name, x_data, y_data):
        """Set the underlying curve data."""
        curve = self.curves.get(name)
        if curve is None:
            return False

        curve.x_data = x_data
        curve.y_data = y_data

        self._update_display()
        return True

    def get_curve_info(self, name):
        """Get information about a curve."""
        if name in self.curves:
            curve = self.curves[name]
            return {
                "label": curve.label,
                "visible": curve.visible,
                "selected": curve.selected,
                "color": curve.base_color,
            }
        return None

    def _update_display(self):
        """Update the entire display."""
        self.grid_lines = []

        self.scene.clear()
        self.scene.setSceneRect(self.display_bounds)

        self._draw_grid()

        for curve_data in self.curves.values():
            if curve_data.visible and not curve_data.selected:
                self._draw_curve(curve_data)

        # Draw second, because selected curves should be on top.
        for curve_data in self.curves.values():
            if curve_data.visible and curve_data.selected:
                self._draw_curve(curve_data)

        self.view.fit_to_view()

    def _draw_curve(self, curve_data):
        """Draw a single curve"""
        if len(curve_data.x_data) < 2:
            return

        padding = 0.05
        padded_bounds = QtCore.QRectF(
            self.display_bounds.left() + self.display_bounds.width() * padding,
            self.display_bounds.top() + self.display_bounds.height() * padding,
            self.display_bounds.width() * (1.0 - 2.0 * padding),
            self.display_bounds.height() * (1.0 - 2.0 * padding),
        )

        if self._normalization_mode == NORMALISATION_MODE_INDIVIDIAL_VALUE:
            # Individual curve bounds.
            norm_x, norm_y = _calculate_normalized_curve_data(
                padded_bounds, curve_data.x_data, curve_data.y_data
            )
        elif self._normalization_mode == NORMALISATION_MODE_GLOBAL_VALUE:
            # Global curve bounds.
            global_bounds = _calculate_global_bounds(self.curves)
            if global_bounds is None or not global_bounds.isValid():
                norm_x, norm_y = _calculate_normalized_curve_data(
                    padded_bounds, curve_data.x_data, curve_data.y_data
                )
            else:
                norm_x, norm_y = _calculate_normalized_curve_data(
                    padded_bounds,
                    curve_data.x_data,
                    curve_data.y_data,
                    original_bounds=global_bounds,
                )
        else:
            raise NotImplementedError
        if not norm_x or not norm_y:
            return

        path = QtGui.QPainterPath()
        path.moveTo(norm_x[0], norm_y[0])
        for i in range(1, len(norm_x)):
            path.lineTo(norm_x[i], norm_y[i])

        curve_item = QtWidgets.QGraphicsPathItem(path)

        pen = QtGui.QPen(curve_data.color, curve_data.line_width)
        pen.setCosmetic(True)
        curve_item.setPen(pen)
        curve_item.setOpacity(curve_data.opacity)

        if curve_data.selected:
            # Draw on top. Selected curves are drawn on top so the
            # user can easily see them.
            curve_item.setZValue(1)
        else:
            curve_item.setZValue(0)

        self.scene.addItem(curve_item)
        curve_data.curve_item = curve_item

    def _draw_grid(self):
        """Draw grid lines."""
        num_grid_lines = 10
        x_step = self.display_bounds.width() / num_grid_lines
        y_step = self.display_bounds.height() / num_grid_lines

        # Reduced opacity, because the grid lines are not the focus of
        # the chart, the curve is.
        grid_color = QtGui.QColor(255, 255, 255, 64)
        grid_pen = QtGui.QPen(grid_color, 1)
        grid_pen.setCosmetic(True)

        # Draw vertical lines.
        x = self.display_bounds.left()
        for i in range(num_grid_lines + 1):
            line = QtWidgets.QGraphicsLineItem(
                x, self.display_bounds.top(), x, self.display_bounds.bottom()
            )
            line.setPen(grid_pen)
            self.scene.addItem(line)
            self.grid_lines.append(line)
            x += x_step

        # Draw horizontal lines.
        y = self.display_bounds.top()
        for i in range(num_grid_lines + 1):
            line = QtWidgets.QGraphicsLineItem(
                self.display_bounds.left(), y, self.display_bounds.right(), y
            )
            line.setPen(grid_pen)
            self.scene.addItem(line)
            self.grid_lines.append(line)
            y += y_step

    def resizeEvent(self, event):
        """Handle widget resize to refit the view."""
        super().resizeEvent(event)
        if hasattr(self, "view"):
            self.view.fit_to_view()
