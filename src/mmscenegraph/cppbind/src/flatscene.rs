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

use crate::attrdatablock::ShimAttrDataBlock;
use mmscenegraph_rust::constant::FrameValue as CoreFrameValue;
use mmscenegraph_rust::scene::flat::FlatScene as CoreFlatScene;

pub struct ShimFlatScene {
    inner: CoreFlatScene,
}

impl ShimFlatScene {
    pub fn new(core_flat_scene: CoreFlatScene) -> Self {
        Self {
            inner: core_flat_scene,
        }
    }

    pub fn get_inner(&self) -> &CoreFlatScene {
        &self.inner
    }

    pub fn evaluate(
        &mut self,
        attrdb: &ShimAttrDataBlock,
        frame_list: &[CoreFrameValue],
    ) {
        let attrdb = attrdb.get_inner();
        self.inner.evaluate(attrdb, frame_list)
    }
}
