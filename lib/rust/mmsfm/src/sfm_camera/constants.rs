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

//! Constant values.
// TODO: If these values are only used in one module, move them to that module.

// TODO: Consolidate these different constants as needed.
pub const DEFAULT_MIN_NUM_ITERATIONS: usize = 1000;
pub const DEFAULT_BUNDLE_ITER_NUM: usize = 1000;
pub const DEFAULT_ROOT_ITER_NUM: usize = 1000;
pub const DEFAULT_ANIM_ITER_NUM: usize = 1000;

// The scene scale that cameras will be remapped to.
pub const DEFAULT_SCENE_SCALE: f64 = 1.0;

// If a 3D triangulation has an error higher than this, skip it.
pub const MARKER_EXPANSION_MAX_ERROR_PX: f64 = 100.0;

// The absolute minimum number of markers that can be used for camera PnP.
pub const MIN_MARKERS_FOR_PNP: usize = 3;

// How many markers are recommended to be used for camera PnP.
pub const RECOMENDED_MARKERS_FOR_PNP: usize = 5;

// The distance between marker/bundle re-projections that will count
// as an error if the "origin frame" algorithm produces a larger error
// than this.
pub const ORIGIN_FRAME_TOLERANCE_PIXELS: f64 = 0.1;

// Constants controlling how the solver works.
pub const SKELETON_DENSIFY_ITERATIONS: u32 = 1;

// The size of the frame scoring grid, for measuring uniformity.
pub const UNIFORMITY_GRID_SIZE_MAX: u8 = 5;
