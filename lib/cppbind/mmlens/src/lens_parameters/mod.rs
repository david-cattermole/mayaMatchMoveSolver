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

use crate::constants::MAX_LENS_PARAMETER_COUNT;
use crate::cxxbridge::ffi::LensModelType as BindLensModelType;
use crate::cxxbridge::ffi::LensParameters as BindLensParameters;
use crate::cxxbridge::ffi::Parameters3deClassic as BindParameters3deClassic;

mod tde_classic;

impl BindLensParameters {
    pub fn new() -> BindLensParameters {
        BindLensParameters {
            mode: BindLensModelType::Uninitialized,
            values: [0.0; MAX_LENS_PARAMETER_COUNT],
        }
    }

    pub fn as_tde_classic(&self) -> BindParameters3deClassic {
        if self.mode != BindLensModelType::TdeClassic {
            BindParameters3deClassic::default()
        } else {
            BindParameters3deClassic::new(
                self.values[0],
                self.values[1],
                self.values[2],
                self.values[3],
                self.values[4],
            )
        }
    }
}
