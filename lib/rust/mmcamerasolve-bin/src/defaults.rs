//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Default values for CLI parameters and solver configuration.

// --- Camera parameters ---

/// Default focal length in millimeters (standard 35mm lens).
pub const DEFAULT_FOCAL_LENGTH_MM: f64 = 35.0;

pub const DEFAULT_LENS_CENTER_X_MM: f64 = 0.0;
pub const DEFAULT_LENS_CENTER_Y_MM: f64 = 0.0;

pub const DEFAULT_IMAGE_WIDTH: u32 = 3600;
pub const DEFAULT_IMAGE_HEIGHT: u32 = 2400;

/// Default film back width in millimeters (full-frame 35mm sensor).
pub const DEFAULT_FILM_BACK_WIDTH_MM: f64 = 36.0;

/// Default film back height in millimeters (full-frame 35mm sensor).
pub const DEFAULT_FILM_BACK_HEIGHT_MM: f64 = 24.0;

pub const DEFAULT_OUTPUT_DIR: &str = "./output";

// --- Focal length solver bounds ---

/// Minimum focal length the solver can use.
pub const MIN_FOCAL_LENGTH_MM: f64 = 0.1;

/// Maximum focal length the solver can use.
pub const MAX_FOCAL_LENGTH_MM: f64 = 200.0;

/// Lower bound factor for refine mode (multiplied against input focal length).
pub const REFINE_BOUNDS_LOWER_FACTOR: f64 = 0.8;

/// Upper bound factor for refine mode (multiplied against input focal length).
pub const REFINE_BOUNDS_UPPER_FACTOR: f64 = 1.2;

/// Minimum focal length for unknown-mode search.
pub const UNKNOWN_FL_MIN_MM: f64 = 10.0;

/// Maximum focal length for unknown-mode search.
pub const UNKNOWN_FL_MAX_MM: f64 = 120.0;

/// Minimum focal length for uniform grid search.
pub const UNIFORM_GRID_FL_MIN_MM: f64 = 0.1;

/// Maximum focal length for uniform grid search.
pub const UNIFORM_GRID_FL_MAX_MM: f64 = 120.0;

// --- Differential Evolution parameters ---

pub const REFINE_EVO_GENERATIONS: usize = 200;
pub const UNKNOWN_EVO_GENERATIONS: usize = 500;
pub const REFINE_EVO_SEED: u64 = 42;
pub const UNKNOWN_EVO_SEED: u64 = 12345;
pub const UNIFORM_GRID_DEFAULT_SAMPLES: usize = 21;
