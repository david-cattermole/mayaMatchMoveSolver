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

use crate::attr::animdense::AnimDenseAttr;
use crate::attr::staticattr::StaticAttr;
use crate::attr::AttrId;
use crate::constant::AttrIndex;
use crate::constant::FrameValue;
use crate::constant::Real;

#[derive(Debug, Clone, Default)]
pub struct AttrDataBlock {
    pub static_attrs: Vec<StaticAttr>,
    pub anim_dense_attrs: Vec<AnimDenseAttr>,
}

impl AttrDataBlock {
    pub fn new() -> AttrDataBlock {
        AttrDataBlock {
            static_attrs: Vec::<StaticAttr>::new(),
            anim_dense_attrs: Vec::<AnimDenseAttr>::new(),
        }
    }

    pub fn clear(&mut self) {
        self.static_attrs.clear();
        self.anim_dense_attrs.clear();
    }

    pub fn create_attr_static(&mut self, value: Real) -> AttrId {
        let mut attr = StaticAttr::new();
        attr.set_value(value);
        let index = self.static_attrs.len() as AttrIndex;
        self.static_attrs.push(attr);
        AttrId::Static(index)
    }

    pub fn create_attr_anim_dense(
        &mut self,
        values: Vec<Real>,
        frame_start: FrameValue,
    ) -> AttrId {
        let mut attr = AnimDenseAttr::new();
        attr.set_values(values);
        attr.frame_start = frame_start;
        let index = self.anim_dense_attrs.len() as AttrIndex;
        self.anim_dense_attrs.push(attr);
        AttrId::AnimDense(index)
    }

    pub fn get_attr_value(&self, attr_id: AttrId, frame: FrameValue) -> Real {
        match attr_id {
            AttrId::Static(index) => self.static_attrs[index].get_value(),
            AttrId::AnimDense(index) => {
                self.anim_dense_attrs[index].get_value(frame)
            }
            AttrId::None => 0.0,
        }
    }

    pub fn set_attr_value(
        &mut self,
        attr_id: AttrId,
        frame: FrameValue,
        value: Real,
    ) {
        match attr_id {
            AttrId::Static(index) => self.static_attrs[index].set_value(value),
            AttrId::AnimDense(index) => {
                self.anim_dense_attrs[index].set_value(frame, value)
            }
            AttrId::None => (),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_static_attr() {
        let mut attrdb = AttrDataBlock::new();
        let attr_id = attrdb.create_attr_static(3.14);
        println!("attr_id: {:?}", attr_id);
        match attr_id {
            AttrId::Static(x) => assert_eq!(x, 0),
            _ => assert!(false),
        }
    }

    #[test]
    fn test_create_anim_dense_attr() {
        let mut attrdb = AttrDataBlock::new();
        let mut values = Vec::new();
        values.push(3.14);
        values.push(4.21);
        values.push(5.52);
        values.push(2.99);
        let frame_start = 1001;
        let attr_id = attrdb.create_attr_anim_dense(values, frame_start);
        println!("attr_id: {:?}", attr_id);
        match attr_id {
            AttrId::AnimDense(x) => assert_eq!(x, 0),
            _ => assert!(false),
        }
    }
}
