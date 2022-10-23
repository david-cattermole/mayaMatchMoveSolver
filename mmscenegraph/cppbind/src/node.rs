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
use crate::cxxbridge::ffi::BundleNode as BindBundleNode;
use crate::cxxbridge::ffi::CameraNode as BindCameraNode;
use crate::cxxbridge::ffi::MarkerNode as BindMarkerNode;
use crate::cxxbridge::ffi::NodeId as BindNodeId;
use crate::cxxbridge::ffi::NodeType as BindNodeType;
use crate::cxxbridge::ffi::TransformNode as BindTransformNode;
use crate::math::bind_to_core_film_fit;
use crate::math::bind_to_core_rotate_order;
use crate::math::core_to_bind_film_fit;
use crate::math::core_to_bind_rotate_order;
use mmscenegraph_rust::node::bundle::BundleNode as CoreBundleNode;
use mmscenegraph_rust::node::camera::CameraNode as CoreCameraNode;
use mmscenegraph_rust::node::marker::MarkerNode as CoreMarkerNode;
use mmscenegraph_rust::node::traits::NodeCanRotate3D;
use mmscenegraph_rust::node::traits::NodeCanScale3D;
use mmscenegraph_rust::node::traits::NodeCanTranslate2D;
use mmscenegraph_rust::node::traits::NodeCanTranslate3D;
use mmscenegraph_rust::node::traits::NodeCanViewScene;
use mmscenegraph_rust::node::traits::NodeHasId;
use mmscenegraph_rust::node::traits::NodeHasWeight;
use mmscenegraph_rust::node::transform::TransformNode as CoreTransformNode;
use mmscenegraph_rust::node::NodeId as CoreNodeId;

pub fn bind_to_core_node_id(value: BindNodeId) -> CoreNodeId {
    match value.node_type {
        BindNodeType::Transform => CoreNodeId::Transform(value.index),
        BindNodeType::Marker => CoreNodeId::Marker(value.index),
        BindNodeType::Bundle => CoreNodeId::Bundle(value.index),
        BindNodeType::Camera => CoreNodeId::Camera(value.index),
        BindNodeType::Root => CoreNodeId::Root,
        _ => CoreNodeId::None,
    }
}

pub fn core_to_bind_node_id(value: CoreNodeId) -> BindNodeId {
    match value {
        CoreNodeId::Transform(index) => BindNodeId {
            node_type: BindNodeType::Transform,
            index,
        },
        CoreNodeId::Marker(index) => BindNodeId {
            node_type: BindNodeType::Marker,
            index,
        },
        CoreNodeId::Bundle(index) => BindNodeId {
            node_type: BindNodeType::Bundle,
            index,
        },
        CoreNodeId::Camera(index) => BindNodeId {
            node_type: BindNodeType::Camera,
            index,
        },
        CoreNodeId::Root => BindNodeId {
            node_type: BindNodeType::Root,
            index: 0,
        },
        _ => BindNodeId {
            node_type: BindNodeType::None,
            index: 0,
        },
    }
}

pub fn core_to_bind_transform_node(
    core_node: CoreTransformNode,
) -> BindTransformNode {
    BindTransformNode {
        id: core_to_bind_node_id(core_node.get_id()),
        attr_tx: core_to_bind_attr_id(core_node.get_attr_tx()),
        attr_ty: core_to_bind_attr_id(core_node.get_attr_ty()),
        attr_tz: core_to_bind_attr_id(core_node.get_attr_tz()),
        attr_rx: core_to_bind_attr_id(core_node.get_attr_rx()),
        attr_ry: core_to_bind_attr_id(core_node.get_attr_ry()),
        attr_rz: core_to_bind_attr_id(core_node.get_attr_rz()),
        attr_sx: core_to_bind_attr_id(core_node.get_attr_sx()),
        attr_sy: core_to_bind_attr_id(core_node.get_attr_sy()),
        attr_sz: core_to_bind_attr_id(core_node.get_attr_sz()),
        rotate_order: core_to_bind_rotate_order(core_node.get_rotate_order()),
    }
}

pub fn core_to_bind_bundle_node(core_node: CoreBundleNode) -> BindBundleNode {
    BindBundleNode {
        id: core_to_bind_node_id(core_node.get_id()),
        attr_tx: core_to_bind_attr_id(core_node.get_attr_tx()),
        attr_ty: core_to_bind_attr_id(core_node.get_attr_ty()),
        attr_tz: core_to_bind_attr_id(core_node.get_attr_tz()),
        attr_rx: core_to_bind_attr_id(core_node.get_attr_rx()),
        attr_ry: core_to_bind_attr_id(core_node.get_attr_ry()),
        attr_rz: core_to_bind_attr_id(core_node.get_attr_rz()),
        attr_sx: core_to_bind_attr_id(core_node.get_attr_sx()),
        attr_sy: core_to_bind_attr_id(core_node.get_attr_sy()),
        attr_sz: core_to_bind_attr_id(core_node.get_attr_sz()),
        rotate_order: core_to_bind_rotate_order(core_node.get_rotate_order()),
    }
}

pub fn bind_to_core_bundle_node(bind_node: BindBundleNode) -> CoreBundleNode {
    let mut core_node = CoreBundleNode::default();
    core_node.set_id(bind_to_core_node_id(bind_node.id));
    core_node.set_attr_tx(bind_to_core_attr_id(bind_node.attr_tx));
    core_node.set_attr_ty(bind_to_core_attr_id(bind_node.attr_ty));
    core_node.set_attr_tz(bind_to_core_attr_id(bind_node.attr_tz));
    core_node.set_attr_rx(bind_to_core_attr_id(bind_node.attr_rx));
    core_node.set_attr_ry(bind_to_core_attr_id(bind_node.attr_ry));
    core_node.set_attr_rz(bind_to_core_attr_id(bind_node.attr_rz));
    core_node.set_attr_sx(bind_to_core_attr_id(bind_node.attr_sx));
    core_node.set_attr_sy(bind_to_core_attr_id(bind_node.attr_sy));
    core_node.set_attr_sz(bind_to_core_attr_id(bind_node.attr_sz));
    core_node
        .set_rotate_order(bind_to_core_rotate_order(bind_node.rotate_order));
    core_node
}

pub fn core_to_bind_camera_node(core_node: CoreCameraNode) -> BindCameraNode {
    BindCameraNode {
        id: core_to_bind_node_id(core_node.get_id()),
        attr_tx: core_to_bind_attr_id(core_node.get_attr_tx()),
        attr_ty: core_to_bind_attr_id(core_node.get_attr_ty()),
        attr_tz: core_to_bind_attr_id(core_node.get_attr_tz()),
        attr_rx: core_to_bind_attr_id(core_node.get_attr_rx()),
        attr_ry: core_to_bind_attr_id(core_node.get_attr_ry()),
        attr_rz: core_to_bind_attr_id(core_node.get_attr_rz()),
        attr_sx: core_to_bind_attr_id(core_node.get_attr_sx()),
        attr_sy: core_to_bind_attr_id(core_node.get_attr_sy()),
        attr_sz: core_to_bind_attr_id(core_node.get_attr_sz()),
        attr_sensor_width: core_to_bind_attr_id(
            core_node.get_attr_sensor_width(),
        ),
        attr_sensor_height: core_to_bind_attr_id(
            core_node.get_attr_sensor_height(),
        ),
        attr_focal_length: core_to_bind_attr_id(
            core_node.get_attr_focal_length(),
        ),
        attr_lens_offset_x: core_to_bind_attr_id(
            core_node.get_attr_lens_offset_x(),
        ),
        attr_lens_offset_y: core_to_bind_attr_id(
            core_node.get_attr_lens_offset_y(),
        ),
        attr_near_clip_plane: core_to_bind_attr_id(
            core_node.get_attr_near_clip_plane(),
        ),
        attr_far_clip_plane: core_to_bind_attr_id(
            core_node.get_attr_far_clip_plane(),
        ),
        attr_camera_scale: core_to_bind_attr_id(
            core_node.get_attr_camera_scale(),
        ),
        rotate_order: core_to_bind_rotate_order(core_node.get_rotate_order()),
        film_fit: core_to_bind_film_fit(core_node.get_film_fit()),
        render_image_width: core_node.get_render_image_width(),
        render_image_height: core_node.get_render_image_height(),
    }
}

pub fn bind_to_core_camera_node(bind_node: BindCameraNode) -> CoreCameraNode {
    let mut core_node = CoreCameraNode::default();
    core_node.set_id(bind_to_core_node_id(bind_node.id));
    core_node.set_attr_tx(bind_to_core_attr_id(bind_node.attr_tx));
    core_node.set_attr_ty(bind_to_core_attr_id(bind_node.attr_ty));
    core_node.set_attr_tz(bind_to_core_attr_id(bind_node.attr_tz));
    core_node.set_attr_rx(bind_to_core_attr_id(bind_node.attr_rx));
    core_node.set_attr_ry(bind_to_core_attr_id(bind_node.attr_ry));
    core_node.set_attr_rz(bind_to_core_attr_id(bind_node.attr_rz));
    core_node.set_attr_sx(bind_to_core_attr_id(bind_node.attr_sx));
    core_node.set_attr_sy(bind_to_core_attr_id(bind_node.attr_sy));
    core_node.set_attr_sz(bind_to_core_attr_id(bind_node.attr_sz));
    core_node.set_attr_sensor_width(bind_to_core_attr_id(
        bind_node.attr_sensor_width,
    ));
    core_node.set_attr_sensor_height(bind_to_core_attr_id(
        bind_node.attr_sensor_height,
    ));
    core_node.set_attr_focal_length(bind_to_core_attr_id(
        bind_node.attr_focal_length,
    ));
    core_node.set_attr_lens_offset_x(bind_to_core_attr_id(
        bind_node.attr_lens_offset_x,
    ));
    core_node.set_attr_lens_offset_y(bind_to_core_attr_id(
        bind_node.attr_lens_offset_y,
    ));
    core_node.set_attr_near_clip_plane(bind_to_core_attr_id(
        bind_node.attr_near_clip_plane,
    ));
    core_node.set_attr_far_clip_plane(bind_to_core_attr_id(
        bind_node.attr_far_clip_plane,
    ));
    core_node.set_attr_camera_scale(bind_to_core_attr_id(
        bind_node.attr_camera_scale,
    ));

    core_node
        .set_rotate_order(bind_to_core_rotate_order(bind_node.rotate_order));
    core_node.set_film_fit(bind_to_core_film_fit(bind_node.film_fit));

    core_node.set_render_image_width(bind_node.render_image_width);
    core_node.set_render_image_height(bind_node.render_image_height);

    core_node
}

pub fn core_to_bind_marker_node(core_node: CoreMarkerNode) -> BindMarkerNode {
    BindMarkerNode {
        id: core_to_bind_node_id(core_node.get_id()),
        attr_tx: core_to_bind_attr_id(core_node.get_attr_tx()),
        attr_ty: core_to_bind_attr_id(core_node.get_attr_ty()),
        attr_weight: core_to_bind_attr_id(core_node.get_attr_weight()),
    }
}

pub fn bind_to_core_marker_node(bind_node: BindMarkerNode) -> CoreMarkerNode {
    let mut core_node = CoreMarkerNode::default();
    core_node.set_id(bind_to_core_node_id(bind_node.id));
    core_node.set_attr_tx(bind_to_core_attr_id(bind_node.attr_tx));
    core_node.set_attr_ty(bind_to_core_attr_id(bind_node.attr_ty));
    core_node.set_attr_weight(bind_to_core_attr_id(bind_node.attr_weight));
    core_node
}
