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
use crate::math::camera::FilmFit;
use crate::math::rotate::euler::RotateOrder;
use crate::node::traits::NodeCanRotate3D;
use crate::node::traits::NodeCanScale3D;
use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeCanTransformAndView3D;
use crate::node::traits::NodeCanTranslate3D;
use crate::node::traits::NodeCanViewScene;
use crate::node::traits::NodeHasId;
use crate::node::NodeId;

#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
pub struct CameraNode {
    id: NodeId,
    attr_tx: AttrId,
    attr_ty: AttrId,
    attr_tz: AttrId,
    attr_rx: AttrId,
    attr_ry: AttrId,
    attr_rz: AttrId,
    attr_sx: AttrId,
    attr_sy: AttrId,
    attr_sz: AttrId,
    rotate_order: RotateOrder,
    attr_sensor_width: AttrId,
    attr_sensor_height: AttrId,
    attr_focal_length: AttrId,
    attr_lens_offset_x: AttrId,
    attr_lens_offset_y: AttrId,
    attr_near_clip_plane: AttrId,
    attr_far_clip_plane: AttrId,
    attr_camera_scale: AttrId,
    film_fit: FilmFit,
    render_image_width: i32,
    render_image_height: i32,
}

impl Default for CameraNode {
    fn default() -> Self {
        Self {
            id: NodeId::None,
            attr_tx: AttrId::None,
            attr_ty: AttrId::None,
            attr_tz: AttrId::None,
            attr_rx: AttrId::None,
            attr_ry: AttrId::None,
            attr_rz: AttrId::None,
            attr_sx: AttrId::None,
            attr_sy: AttrId::None,
            attr_sz: AttrId::None,
            rotate_order: RotateOrder::XYZ,
            attr_sensor_width: AttrId::None,
            attr_sensor_height: AttrId::None,
            attr_focal_length: AttrId::None,
            attr_lens_offset_x: AttrId::None,
            attr_lens_offset_y: AttrId::None,
            attr_near_clip_plane: AttrId::None,
            attr_far_clip_plane: AttrId::None,
            attr_camera_scale: AttrId::None,
            film_fit: FilmFit::Horizontal,
            render_image_width: 1920,
            render_image_height: 1080,
        }
    }
}

impl NodeHasId for CameraNode {
    fn get_id(&self) -> NodeId {
        self.id
    }

    fn set_id(&mut self, value: NodeId) {
        self.id = value;
    }
}

impl NodeCanTranslate3D for CameraNode {
    fn get_attr_tx(&self) -> AttrId {
        self.attr_tx
    }
    fn get_attr_ty(&self) -> AttrId {
        self.attr_ty
    }
    fn get_attr_tz(&self) -> AttrId {
        self.attr_tz
    }
    fn set_attr_tx(&mut self, attr: AttrId) {
        self.attr_tx = attr;
    }
    fn set_attr_ty(&mut self, attr: AttrId) {
        self.attr_ty = attr;
    }
    fn set_attr_tz(&mut self, attr: AttrId) {
        self.attr_tz = attr;
    }
}

impl NodeCanRotate3D for CameraNode {
    fn get_attr_rx(&self) -> AttrId {
        self.attr_rx
    }
    fn get_attr_ry(&self) -> AttrId {
        self.attr_ry
    }
    fn get_attr_rz(&self) -> AttrId {
        self.attr_rz
    }
    fn set_attr_rx(&mut self, attr: AttrId) {
        self.attr_rx = attr;
    }
    fn set_attr_ry(&mut self, attr: AttrId) {
        self.attr_ry = attr;
    }
    fn set_attr_rz(&mut self, attr: AttrId) {
        self.attr_rz = attr;
    }

    fn get_rotate_order(&self) -> RotateOrder {
        self.rotate_order
    }
    fn set_rotate_order(&mut self, value: RotateOrder) {
        self.rotate_order = value;
    }
}

impl NodeCanScale3D for CameraNode {
    fn get_attr_sx(&self) -> AttrId {
        self.attr_sx
    }
    fn get_attr_sy(&self) -> AttrId {
        self.attr_sy
    }
    fn get_attr_sz(&self) -> AttrId {
        self.attr_sz
    }
    fn set_attr_sx(&mut self, attr: AttrId) {
        self.attr_sx = attr;
    }
    fn set_attr_sy(&mut self, attr: AttrId) {
        self.attr_sy = attr;
    }
    fn set_attr_sz(&mut self, attr: AttrId) {
        self.attr_sz = attr;
    }
}

impl NodeCanViewScene for CameraNode {
    fn get_attr_sensor_width(&self) -> AttrId {
        self.attr_sensor_width
    }

    fn get_attr_sensor_height(&self) -> AttrId {
        self.attr_sensor_height
    }

    fn get_attr_focal_length(&self) -> AttrId {
        self.attr_focal_length
    }

    fn set_attr_sensor_width(&mut self, attr: AttrId) {
        self.attr_sensor_width = attr;
    }

    fn set_attr_sensor_height(&mut self, attr: AttrId) {
        self.attr_sensor_height = attr;
    }

    fn set_attr_focal_length(&mut self, attr: AttrId) {
        self.attr_focal_length = attr;
    }

    fn get_attr_lens_offset_x(&self) -> AttrId {
        self.attr_lens_offset_x
    }

    fn get_attr_lens_offset_y(&self) -> AttrId {
        self.attr_lens_offset_y
    }

    fn set_attr_lens_offset_x(&mut self, attr: AttrId) {
        self.attr_lens_offset_x = attr;
    }

    fn set_attr_lens_offset_y(&mut self, attr: AttrId) {
        self.attr_lens_offset_y = attr;
    }

    fn get_attr_near_clip_plane(&self) -> AttrId {
        self.attr_near_clip_plane
    }

    fn get_attr_far_clip_plane(&self) -> AttrId {
        self.attr_far_clip_plane
    }

    fn set_attr_near_clip_plane(&mut self, attr: AttrId) {
        self.attr_near_clip_plane = attr;
    }

    fn set_attr_far_clip_plane(&mut self, attr: AttrId) {
        self.attr_far_clip_plane = attr;
    }

    fn get_attr_camera_scale(&self) -> AttrId {
        self.attr_camera_scale
    }

    fn set_attr_camera_scale(&mut self, attr: AttrId) {
        self.attr_camera_scale = attr;
    }

    fn get_film_fit(&self) -> FilmFit {
        self.film_fit
    }

    fn set_film_fit(&mut self, value: FilmFit) {
        self.film_fit = value;
    }

    fn get_render_image_width(&self) -> i32 {
        self.render_image_width
    }

    fn get_render_image_height(&self) -> i32 {
        self.render_image_height
    }

    fn set_render_image_width(&mut self, value: i32) {
        self.render_image_width = value;
    }

    fn set_render_image_height(&mut self, value: i32) {
        self.render_image_height = value;
    }
}

impl NodeCanTransform3D for CameraNode {}

impl NodeCanTransformAndView3D for CameraNode {}
