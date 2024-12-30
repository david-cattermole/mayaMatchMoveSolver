//
// Copyright (C) 2023, 2024 David Cattermole.
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
/// 3DE Radial Standard Degree 4
use crate::cxxbridge::ffi::Parameters3deRadialStdDeg4 as BindParameters3deRadialStdDeg4;
use crate::impl_LensParameters_hash_parameters_method;
use crate::lens_parameters::LensParameters;
use std::hash::Hash;

impl Default for BindParameters3deRadialStdDeg4 {
    fn default() -> Self {
        Self {
            degree2_distortion: 0.0,
            degree2_u: 0.0,
            degree2_v: 0.0,
            degree4_distortion: 0.0,
            degree4_u: 0.0,
            degree4_v: 0.0,
            cylindric_direction: 0.0,
            cylindric_bending: 0.0,
        }
    }
}

impl LensParameters for BindParameters3deRadialStdDeg4 {
    impl_LensParameters_hash_parameters_method!(
        degree2_distortion,
        degree2_u,
        degree2_v,
        degree4_distortion,
        degree4_u,
        degree4_v,
        cylindric_direction,
        cylindric_bending
    );

    fn from_slice(data: &[f64]) -> Self {
        Self {
            degree2_distortion: data[0],
            degree2_u: data[1],
            degree2_v: data[2],
            degree4_distortion: data[3],
            degree4_u: data[4],
            degree4_v: data[5],
            cylindric_direction: data[6],
            cylindric_bending: data[7],
        }
    }

    fn into_args(self) -> Vec<f64> {
        vec![
            self.degree2_distortion,
            self.degree2_u,
            self.degree2_v,
            self.degree4_distortion,
            self.degree4_u,
            self.degree4_v,
            self.cylindric_direction,
            self.cylindric_bending,
        ]
    }
}
