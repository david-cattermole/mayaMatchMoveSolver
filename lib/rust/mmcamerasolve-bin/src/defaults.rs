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

/// Default focal length in millimeters (35mm standard lens).
pub const DEFAULT_FOCAL_LENGTH_MM: f64 = 35.0;

/// Default lens center X offset in millimeters.
pub const DEFAULT_LENS_CENTER_X_MM: f64 = 0.0;

/// Default lens center Y offset in millimeters.
pub const DEFAULT_LENS_CENTER_Y_MM: f64 = 0.0;

/// Default image width in pixels.
pub const DEFAULT_IMAGE_WIDTH: u32 = 3600;

/// Default image height in pixels.
pub const DEFAULT_IMAGE_HEIGHT: u32 = 2400;

/// Default film back width in millimeters (full-frame 35mm).
pub const DEFAULT_FILM_BACK_WIDTH_MM: f64 = 36.0;

/// Default film back height in millimeters (full-frame 35mm).
pub const DEFAULT_FILM_BACK_HEIGHT_MM: f64 = 24.0;

/// Default output directory.
pub const DEFAULT_OUTPUT_DIR: &str = "./output";

// --- Focal length solver bounds ---

/// Absolute minimum focal length (mm) the solver can represent.
pub const MIN_FOCAL_LENGTH_MM: f64 = 0.1;

/// Absolute maximum focal length (mm) the solver can represent.
pub const MAX_FOCAL_LENGTH_MM: f64 = 200.0;

/// Lower multiplier for refine mode bounds (relative to input focal length).
pub const REFINE_BOUNDS_LOWER_FACTOR: f64 = 0.8;

/// Upper multiplier for refine mode bounds (relative to input focal length).
pub const REFINE_BOUNDS_UPPER_FACTOR: f64 = 1.2;

/// Default minimum focal length (mm) for unknown-mode search.
pub const UNKNOWN_FL_MIN_MM: f64 = 10.0;

/// Default maximum focal length (mm) for unknown-mode search.
pub const UNKNOWN_FL_MAX_MM: f64 = 120.0;

/// Default minimum focal length (mm) for uniform grid search.
pub const UNIFORM_GRID_FL_MIN_MM: f64 = 0.1;

/// Default maximum focal length (mm) for uniform grid search.
pub const UNIFORM_GRID_FL_MAX_MM: f64 = 120.0;

// --- Differential Evolution parameters ---

/// Number of EVO generations for refine mode.
pub const REFINE_EVO_GENERATIONS: usize = 200;

/// Number of EVO generations for unknown-mode search.
pub const UNKNOWN_EVO_GENERATIONS: usize = 500;

/// EVO random seed for refine mode.
pub const REFINE_EVO_SEED: u64 = 42;

/// EVO random seed for unknown mode.
pub const UNKNOWN_EVO_SEED: u64 = 12345;

/// Default number of samples for uniform grid search.
pub const UNIFORM_GRID_DEFAULT_SAMPLES: usize = 21;
