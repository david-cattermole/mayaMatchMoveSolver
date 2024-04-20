//
// Copyright (C) 2023 David Cattermole.
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

// Include all the Rust crates that will be exposed from this crate.
//
// We do this because we are not able to statically link multiple
// libraries that are built with CXX to the same build artifact.
//
// Read 2023-06-10 - June 10th:
// https://cxx.rs/build/other.html#linking-the-c-and-rust-together
//
// In the future hopefully this won't be required.
pub use mmcore;
pub use mmimage;
pub use mmlens;
pub use mmscenegraph;
