//
// Copyright (C) 2024 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//
/// Mathematical interpolation functions.
use crate::constant::Real;

/// Return 'min_value' to 'max_value' linearly, for a 'mix' value
/// between 0.0 and 1.0.
///
/// Usage:
/// - Smoothly transition between two values
/// - Generate points along a line
/// - Create gradients or animations
pub fn lerp_f64(min_value: Real, max_value: Real, mix: Real) -> Real {
    ((1.0 - mix) * min_value) + (mix * max_value)
}

/// Return a value between 0.0 and 1.0 for a value in an input range
/// 'from' to 'to'.
///
/// Usage:
/// - Find normalized position in a range
/// - Convert absolute values to percentages
/// - Inverse of lerp operation
pub fn inverse_lerp_f64(from: Real, to: Real, value: Real) -> Real {
    (value - from) / (to - from)
}

/// Remap from an 'original' value range to a 'target' value range.
pub fn remap_f64(
    original_from: Real,
    original_to: Real,
    target_from: Real,
    target_to: Real,
    value: Real,
) -> Real {
    let map_to_original_range =
        inverse_lerp_f64(original_from, original_to, value);
    lerp_f64(target_from, target_to, map_to_original_range)
}
