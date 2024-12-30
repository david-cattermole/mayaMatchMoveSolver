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

use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg4 as BindOptionParameters3deAnamorphicStdDeg4;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg4Rescaled as BindOptionParameters3deAnamorphicStdDeg4Rescaled;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg6 as BindOptionParameters3deAnamorphicStdDeg6;
use crate::cxxbridge::ffi::OptionParameters3deAnamorphicStdDeg6Rescaled as BindOptionParameters3deAnamorphicStdDeg6Rescaled;
use crate::cxxbridge::ffi::OptionParameters3deClassic as BindOptionParameters3deClassic;
use crate::cxxbridge::ffi::OptionParameters3deRadialStdDeg4 as BindOptionParameters3deRadialStdDeg4;

use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4 as BindParameters3deAnamorphicStdDeg4;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4Rescaled as BindParameters3deAnamorphicStdDeg4Rescaled;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6 as BindParameters3deAnamorphicStdDeg6;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6Rescaled as BindParameters3deAnamorphicStdDeg6Rescaled;
use crate::cxxbridge::ffi::Parameters3deClassic as BindParameters3deClassic;
use crate::cxxbridge::ffi::Parameters3deRadialStdDeg4 as BindParameters3deRadialStdDeg4;

use crate::lens_parameters::LensParameters;

/// A trait for optional parameters with an existence flag.
pub trait OptionParametersTrait {
    type InnerType;

    /// Create a new instance with no value
    fn new_as_none() -> Self;

    /// Create a new instance with a specific value
    fn new_as_some_from_vec(args: &[f64]) -> Self;
}

macro_rules! impl_option_parameters_trait {
    ($option_type:ty, $inner_type:ty) => {
        impl OptionParametersTrait for $option_type {
            type InnerType = $inner_type;

            fn new_as_none() -> Self {
                let value: Self::InnerType = Default::default();
                Self {
                    exists: false,
                    value,
                }
            }

            fn new_as_some_from_vec(args: &[f64]) -> Self {
                Self {
                    exists: true,
                    value: Self::InnerType::from_slice(args),
                }
            }
        }
    };
}

impl_option_parameters_trait!(
    BindOptionParameters3deClassic,
    BindParameters3deClassic
);

impl_option_parameters_trait!(
    BindOptionParameters3deRadialStdDeg4,
    BindParameters3deRadialStdDeg4
);

impl_option_parameters_trait!(
    BindOptionParameters3deAnamorphicStdDeg4,
    BindParameters3deAnamorphicStdDeg4
);

impl_option_parameters_trait!(
    BindOptionParameters3deAnamorphicStdDeg4Rescaled,
    BindParameters3deAnamorphicStdDeg4Rescaled
);

impl_option_parameters_trait!(
    BindOptionParameters3deAnamorphicStdDeg6,
    BindParameters3deAnamorphicStdDeg6
);

impl_option_parameters_trait!(
    BindOptionParameters3deAnamorphicStdDeg6Rescaled,
    BindParameters3deAnamorphicStdDeg6Rescaled
);
