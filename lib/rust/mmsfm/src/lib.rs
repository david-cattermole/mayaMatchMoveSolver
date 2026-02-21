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

//! # mmsfm - Structure from Motion for Maya
//!
//! This crate provides Structure from Motion (SfM) algorithms and utilities
//! designed for integration with Autodesk Maya.
//!
//! ## Coordinate System Convention
//!
//! This crate follows the **Maya coordinate system convention**:
//!
//! 1. **Right-hand coordinate system**: Uses the standard mathematical right-hand rule
//! 2. **+Y axis is world-up**: The positive Y-axis points upward in world space
//! 3. **"Looking down the camera" axis is -Z**: When looking through a camera,
//!    the view direction is along the negative Z-axis
//!
//! This means:
//! - Points with negative Z coordinates are **in front of** the camera.
//! - Points with positive Z coordinates are **behind** the camera.
//! - Camera depth calculations use `depth < 0.0` to check if points are visible.
//!
//! All algorithms, including triangulation, camera pose estimation,
//! bundle adjustment, are designed to work consistently with this
//! coordinate system.
//!
//! ## Note on OpenMVG Compatibility
//!
//! When interfacing with OpenMVG (which uses a different coordinate system),
//! use the conversion functions provided in the main mmSolver C++ codebase:
//! `convert_openmvg_transform_to_maya_transform_matrix` in `src/mmSolver/sfm/sfm_utils.cpp`.

#![allow(non_snake_case)]

/// Debug print macro that expands to `if DEBUG { eprintln!(...) }`.
///
/// Requires a `const DEBUG: bool` in the calling scope. When `DEBUG`
/// is `false`, the compiler optimizes the branch away entirely.
macro_rules! mm_debug_eprintln {
    ($($arg:tt)*) => {
        if DEBUG {
            eprintln!($($arg)*);
        }
    };
}

pub mod camera_residual_error;
pub mod datatype;
