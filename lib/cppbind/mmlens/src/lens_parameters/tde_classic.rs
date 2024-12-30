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
/// 3DE Classic
use crate::cxxbridge::ffi::Parameters3deClassic as BindParameters3deClassic;
use crate::impl_LensParameters_hash_parameters_method;
use crate::lens_parameters::LensParameters;
use std::hash::Hash;

impl Default for BindParameters3deClassic {
    fn default() -> Self {
        Self {
            distortion: 0.0,
            anamorphic_squeeze: 1.0,
            curvature_x: 0.0,
            curvature_y: 0.0,
            quartic_distortion: 0.0,
        }
    }
}

impl LensParameters for BindParameters3deClassic {
    impl_LensParameters_hash_parameters_method!(
        distortion,
        anamorphic_squeeze,
        curvature_x,
        curvature_y,
        quartic_distortion
    );

    fn from_slice(data: &[f64]) -> Self {
        Self {
            distortion: data[0],
            anamorphic_squeeze: data[1],
            curvature_x: data[2],
            curvature_y: data[3],
            quartic_distortion: data[4],
        }
    }

    fn into_args(self) -> Vec<f64> {
        vec![
            self.distortion,
            self.anamorphic_squeeze,
            self.curvature_x,
            self.curvature_y,
            self.quartic_distortion,
        ]
    }
}
