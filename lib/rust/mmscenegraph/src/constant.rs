//
// Copyright (C) 2020, 2021 David Cattermole.
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

use nalgebra;

pub type AttrIndex = usize;
pub type HashValue = u64;
pub type NodeIndex = usize;
pub type FrameValue = u32;
pub type FrameTime = f64;
pub type Real = f64;
pub type Matrix44 = nalgebra::Matrix4<Real>;
pub type Matrix33 = nalgebra::Matrix3<Real>;
pub type Matrix14 = nalgebra::Matrix1x4<Real>;
pub type Quaternion = nalgebra::Quaternion<Real>;

// Memory Conversion
pub const BYTES_TO_KILOBYTES: usize = 1024; // int(pow(2, 10))
pub const BYTES_TO_MEGABYTES: usize = 1048576; // int(pow(2, 20))
pub const BYTES_TO_GIGABYTES: usize = 1073741824; // int(pow(2, 30))
pub const KILOBYTES_TO_MEGABYTES: usize = 1024; // int(pow(2, 10))
pub const KILOBYTES_TO_GIGABYTES: usize = 1048576; // int(pow(2, 20))

// Radians to/from Degrees
pub const RADIANS_TO_DEGREES: Real = 57.295779513082323; // 180.0 / pi
pub const DEGREES_TO_RADIANS: Real = 0.017453292519943295; // pi / 180.0

// Conversion constants
pub const MM_TO_INCH: Real = 0.03937007874015748; // 1.0 / 25.4
pub const MM_TO_CM: Real = 0.1;
pub const _CM_TO_MM: Real = 10.0;
pub const INCH_TO_MM: Real = 25.4;
pub const _INCH_TO_CM: Real = 2.54;

// Number constants.
pub const REAL_E: f64 = std::f64::consts::E;
