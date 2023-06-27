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

use crate::cxxbridge::ffi::OptionParameters3deClassic;
use crate::cxxbridge::ffi::Parameters3deClassic;

impl OptionParameters3deClassic {
    pub fn new_as_none() -> OptionParameters3deClassic {
        OptionParameters3deClassic {
            exists: false,
            value: Parameters3deClassic {
                distortion: 0.0,         // Distortion
                anamorphic_squeeze: 1.0, // Anamorphic Squeeze
                curvature_x: 0.0,        // Curvature X
                curvature_y: 0.0,        // Curvature Y
                quartic_distortion: 0.0, // Quartic Distortion
            },
        }
    }

    pub fn new_as_some(
        distortion: f64,
        anamorphic_squeeze: f64,
        curvature_x: f64,
        curvature_y: f64,
        quartic_distortion: f64,
    ) -> OptionParameters3deClassic {
        OptionParameters3deClassic {
            exists: true,
            value: Parameters3deClassic {
                distortion,
                anamorphic_squeeze,
                curvature_x,
                curvature_y,
                quartic_distortion,
            },
        }
    }
}
