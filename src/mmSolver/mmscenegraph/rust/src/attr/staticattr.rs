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

use std::hash::{Hash, Hasher};

use crate::constant::Real;
use crate::core::hashutils::HashableF64;

#[derive(Debug, Copy, Clone, Default)]
pub struct StaticAttr {
    value: Real,
}

impl Hash for StaticAttr {
    fn hash<H: Hasher>(&self, state: &mut H) {
        HashableF64::new(self.value).hash(state);
    }
}

impl StaticAttr {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn get_value(&self) -> Real {
        self.value
    }

    pub fn set_value(&mut self, value: Real) {
        self.value = value;
    }
}
