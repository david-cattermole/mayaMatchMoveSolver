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

mod tde_anamorphic_deg_4_rotate_squeeze_xy;
mod tde_anamorphic_deg_4_rotate_squeeze_xy_rescaled;
mod tde_anamorphic_deg_6_rotate_squeeze_xy;
mod tde_anamorphic_deg_6_rotate_squeeze_xy_rescaled;
mod tde_classic;
mod tde_radial_decentered_deg_4_cylindric;

use rustc_hash::FxHasher;

pub trait LensParameters {
    fn hash_parameters(&self, state: &mut FxHasher);
    fn from_slice(data: &[f64]) -> Self;
    fn into_args(self) -> Vec<f64>;
}

#[macro_export]
macro_rules! impl_LensParameters_hash_parameters_method {
    ($($field:ident),*) => {
            fn hash_parameters(&self, state: &mut rustc_hash::FxHasher) {
                $(
                    crate::hash_float::HashableF64::new(self.$field).hash(state);
                )*
            }
    };
}
