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

use crate::attr::AttrId;
use crate::math::rotate::euler::RotateOrder;
use crate::node::NodeId;

pub trait NodeHasId {
    fn get_id(&self) -> NodeId;
    fn set_id(&mut self, value: NodeId);
}

pub trait NodeCanTranslate3D {
    fn get_attr_tx(&self) -> AttrId;
    fn get_attr_ty(&self) -> AttrId;
    fn get_attr_tz(&self) -> AttrId;
    fn set_attr_tx(&mut self, attr: AttrId);
    fn set_attr_ty(&mut self, attr: AttrId);
    fn set_attr_tz(&mut self, attr: AttrId);
}

pub trait NodeCanRotate3D {
    fn get_attr_rx(&self) -> AttrId;
    fn get_attr_ry(&self) -> AttrId;
    fn get_attr_rz(&self) -> AttrId;
    fn set_attr_rx(&mut self, attr: AttrId);
    fn set_attr_ry(&mut self, attr: AttrId);
    fn set_attr_rz(&mut self, attr: AttrId);

    fn get_rotate_order(&self) -> RotateOrder;
    fn set_rotate_order(&mut self, order: RotateOrder);
}

pub trait NodeCanScale3D {
    fn get_attr_sx(&self) -> AttrId;
    fn get_attr_sy(&self) -> AttrId;
    fn get_attr_sz(&self) -> AttrId;
    fn set_attr_sx(&mut self, attr: AttrId);
    fn set_attr_sy(&mut self, attr: AttrId);
    fn set_attr_sz(&mut self, attr: AttrId);
}

pub trait NodeCanTranslate2D {
    fn get_attr_tx(&self) -> AttrId;
    fn get_attr_ty(&self) -> AttrId;
    fn set_attr_tx(&mut self, attr: AttrId);
    fn set_attr_ty(&mut self, attr: AttrId);
}

pub trait NodeHasWeight {
    fn get_attr_weight(&self) -> AttrId;
    fn set_attr_weight(&mut self, attr: AttrId);
}

pub trait NodeCanViewScene {
    fn get_attr_sensor_width(&self) -> AttrId;
    fn get_attr_sensor_height(&self) -> AttrId;
    fn get_attr_focal_length(&self) -> AttrId;

    fn set_attr_sensor_width(&mut self, attr: AttrId);
    fn set_attr_sensor_height(&mut self, attr: AttrId);
    fn set_attr_focal_length(&mut self, attr: AttrId);
}

pub trait NodeCanTransform2D: NodeHasId + NodeCanTranslate2D + NodeHasWeight {}

pub trait NodeCanTransform3D:
    NodeHasId + NodeCanTranslate3D + NodeCanRotate3D + NodeCanScale3D
{
}

pub trait NodeCanTransformAndView3D: NodeCanTransform3D + NodeCanViewScene {}
