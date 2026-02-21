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
