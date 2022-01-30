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

use crate::attr::bind_to_core_attr_id;
use crate::attr::core_to_bind_attr_id;
use crate::cxxbridge::ffi::AttrId as BindAttrId;
use mmscenegraph_rust::attr::datablock::AttrDataBlock as CoreAttrDataBlock;
use mmscenegraph_rust::constant::FrameValue as CoreFrameValue;
use mmscenegraph_rust::constant::Real as CoreReal;

#[derive(Debug, Clone)]
pub struct ShimAttrDataBlock {
    inner: CoreAttrDataBlock,
}

impl ShimAttrDataBlock {
    fn new() -> Self {
        Self {
            inner: CoreAttrDataBlock::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreAttrDataBlock {
        &self.inner
    }

    pub fn clear(&mut self) {
        self.inner.clear()
    }

    pub fn num_attr_static(&self) -> usize {
        self.inner.num_attr_static()
    }

    pub fn num_attr_anim_dense(&self) -> usize {
        self.inner.num_attr_anim_dense()
    }

    pub fn create_attr_static(&mut self, value: CoreReal) -> BindAttrId {
        let attr_id = self.inner.create_attr_static(value);
        core_to_bind_attr_id(attr_id)
    }

    pub fn create_attr_anim_dense(
        &mut self,
        values: Vec<CoreReal>,
        frame_start: CoreFrameValue,
    ) -> BindAttrId {
        let attr_id = self.inner.create_attr_anim_dense(values, frame_start);
        core_to_bind_attr_id(attr_id)
    }

    pub fn get_attr_value(
        &self,
        attr_id: BindAttrId,
        frame: CoreFrameValue,
    ) -> CoreReal {
        let attr_id = bind_to_core_attr_id(attr_id);
        self.inner.get_attr_value(attr_id, frame)
    }

    pub fn set_attr_value(
        &mut self,
        attr_id: BindAttrId,
        frame: CoreFrameValue,
        value: CoreReal,
    ) {
        let attr_id = bind_to_core_attr_id(attr_id);
        self.inner.set_attr_value(attr_id, frame, value)
    }
}

pub fn shim_create_attr_data_block_box() -> Box<ShimAttrDataBlock> {
    Box::new(ShimAttrDataBlock::new())
}
