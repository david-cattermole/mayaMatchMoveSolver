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
/// 3DE Anamorphic Standard Degree 6
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6 as BindParameters3deAnamorphicStdDeg6;
use crate::impl_LensParameters_hash_parameters_method;
use crate::lens_parameters::LensParameters;
use std::hash::Hash;

impl Default for BindParameters3deAnamorphicStdDeg6 {
    fn default() -> Self {
        Self {
            degree2_cx02: 0.0,
            degree2_cy02: 0.0,
            degree2_cx22: 0.0,
            degree2_cy22: 0.0,
            degree4_cx04: 0.0,
            degree4_cy04: 0.0,
            degree4_cx24: 0.0,
            degree4_cy24: 0.0,
            degree4_cx44: 0.0,
            degree4_cy44: 0.0,
            degree6_cx06: 0.0,
            degree6_cy06: 0.0,
            degree6_cx26: 0.0,
            degree6_cy26: 0.0,
            degree6_cx46: 0.0,
            degree6_cy46: 0.0,
            degree6_cx66: 0.0,
            degree6_cy66: 0.0,
            lens_rotation: 0.0,
            squeeze_x: 1.0,
            squeeze_y: 1.0,
        }
    }
}

impl LensParameters for BindParameters3deAnamorphicStdDeg6 {
    impl_LensParameters_hash_parameters_method!(
        degree2_cx02,
        degree2_cy02,
        degree2_cx22,
        degree2_cy22,
        degree4_cx04,
        degree4_cy04,
        degree4_cx24,
        degree4_cy24,
        degree4_cx44,
        degree4_cy44,
        degree6_cx06,
        degree6_cy06,
        degree6_cx26,
        degree6_cy26,
        degree6_cx46,
        degree6_cy46,
        degree6_cx66,
        degree6_cy66,
        lens_rotation,
        squeeze_x,
        squeeze_y
    );

    fn from_slice(data: &[f64]) -> Self {
        Self {
            degree2_cx02: data[0],
            degree2_cy02: data[1],
            degree2_cx22: data[2],
            degree2_cy22: data[3],
            degree4_cx04: data[4],
            degree4_cy04: data[5],
            degree4_cx24: data[6],
            degree4_cy24: data[7],
            degree4_cx44: data[8],
            degree4_cy44: data[9],
            degree6_cx06: data[10],
            degree6_cy06: data[11],
            degree6_cx26: data[12],
            degree6_cy26: data[13],
            degree6_cx46: data[14],
            degree6_cy46: data[15],
            degree6_cx66: data[16],
            degree6_cy66: data[17],
            lens_rotation: data[18],
            squeeze_x: data[19],
            squeeze_y: data[20],
        }
    }

    fn into_args(self) -> Vec<f64> {
        vec![
            self.degree2_cx02,
            self.degree2_cy02,
            self.degree2_cx22,
            self.degree2_cy22,
            self.degree4_cx04,
            self.degree4_cy04,
            self.degree4_cx24,
            self.degree4_cy24,
            self.degree4_cx44,
            self.degree4_cy44,
            self.degree6_cx06,
            self.degree6_cy06,
            self.degree6_cx26,
            self.degree6_cy26,
            self.degree6_cx46,
            self.degree6_cy46,
            self.degree6_cx66,
            self.degree6_cy66,
            self.lens_rotation,
            self.squeeze_x,
            self.squeeze_y,
        ]
    }
}
