# Copyright (C) 2026 David Cattermole.
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
Solver-object construction helpers and pure-math utilities.

These functions are shared between the non-UI tool (tool.py) and the
UI layout (camerasolver_layout.py) to avoid duplicating the same
AdjustmentSolver / AdjustmentAttributes construction logic.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.utils.time as time_utils

import mmSolver.tools.camerasolver.constant as const
from mmSolver.tools.camerasolver.lib.types import AdjustmentSolver
from mmSolver.tools.camerasolver.lib.types import AdjustmentAttributes


def compute_focal_length_min_max_from_percentage(focal_length_mm, percentage_value):
    """Compute focal length min/max from a reference value and percentage.

    :param focal_length_mm: Reference focal length in millimetres.
    :type focal_length_mm: float

    :param percentage_value: Search range as a percentage, e.g. ``20.0``
                             means the range spans +/-20% of
                             focal_length_mm.
    :type percentage_value: float

    :returns: ``(focal_length_min, focal_length_max)`` in millimetres.
    :rtype: (float, float)
    """
    factor = percentage_value / 100.0
    # TODO: Define a "standard" range and then create range of values
    # from that.
    focal_length_min = focal_length_mm * (1.0 - factor)
    focal_length_max = focal_length_mm * (1.0 + factor)
    return max(0.1, focal_length_min), focal_length_max


def make_adjustment_solver(
    solver_type,
    thread_count=4,
    evolution_generation_count=100,
    evolution_population_count=100,
):
    """Construct an AdjustmentSolver from explicit values.

    :param solver_type: One of the ``ADJUSTMENT_SOLVER_TYPE_*`` constants.
    :type solver_type: str

    :param thread_count: Number of threads for the solver.
    :type thread_count: int

    :param evolution_generation_count: Number of evolution generations.
    :type evolution_generation_count: int

    :param evolution_population_count: Size of the evolution population.
    :type evolution_population_count: int

    :rtype: AdjustmentSolver
    """
    adjustment_solver = AdjustmentSolver()
    adjustment_solver.set_adjustment_solver_type(solver_type)
    adjustment_solver.set_thread_count(thread_count)
    adjustment_solver.set_evolution_generation_count(evolution_generation_count)
    adjustment_solver.set_evolution_population_count(evolution_population_count)
    return adjustment_solver


def make_adjustment_attributes(
    focal_length_min, focal_length_max, focal_length_samples
):
    """Construct an AdjustmentAttributes for the camera focal length.

    :param focal_length_min: Minimum focal length in millimetres.
    :type focal_length_min: float

    :param focal_length_max: Maximum focal length in millimetres.
    :type focal_length_max: float

    :param focal_length_samples: Number of samples in the search range.
    :type focal_length_samples: int

    :rtype: AdjustmentAttributes
    """
    adjustment_attributes = AdjustmentAttributes()
    adjustment_attributes.set_attribute_bounds(
        const.ATTR_CAMERA_FOCAL_LENGTH,
        float(focal_length_min),
        float(focal_length_max),
    )
    adjustment_attributes.set_attribute_sample_count(
        const.ATTR_CAMERA_FOCAL_LENGTH, int(focal_length_samples)
    )
    return adjustment_attributes


def get_frame_range(frame_range_mode, start_frame=1, end_frame=120):
    """Build a FrameRange from a mode index and optional custom bounds.

    :param frame_range_mode: One of the ``FRAME_RANGE_MODE_*_INDEX`` constants.
    :type frame_range_mode: int

    :param start_frame: Start frame used when mode is Custom.
    :type start_frame: int

    :param end_frame: End frame used when mode is Custom.
    :type end_frame: int

    :rtype: mmSolver.utils.time.FrameRange
    """
    if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_INDEX:
        return time_utils.get_maya_timeline_range_outer()
    if frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_INDEX:
        return time_utils.FrameRange(start_frame, end_frame)
    return time_utils.get_maya_timeline_range_inner()
