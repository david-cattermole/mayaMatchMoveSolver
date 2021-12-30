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

use crate::attr::core_to_bind_attr_id;
use crate::cxxbridge::ffi::BundleNode as BindBundleNode;
use crate::cxxbridge::ffi::CameraNode as BindCameraNode;
use crate::cxxbridge::ffi::MarkerNode as BindMarkerNode;
use crate::cxxbridge::ffi::NodeId as BindNodeId;
use crate::cxxbridge::ffi::NodeType as BindNodeType;
use crate::cxxbridge::ffi::TransformNode as BindTransformNode;
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

pub fn core_to_bind_transform_node(core_node: CoreTransformNode) -> BindTransformNode {
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
        attr_sensor_width: core_to_bind_attr_id(core_node.get_attr_sensor_width()),
        attr_sensor_height: core_to_bind_attr_id(core_node.get_attr_sensor_height()),
        attr_focal_length: core_to_bind_attr_id(core_node.get_attr_focal_length()),
        rotate_order: core_to_bind_rotate_order(core_node.get_rotate_order()),
    }
}

pub fn core_to_bind_marker_node(core_node: CoreMarkerNode) -> BindMarkerNode {
    BindMarkerNode {
        id: core_to_bind_node_id(core_node.get_id()),
        attr_tx: core_to_bind_attr_id(core_node.get_attr_tx()),
        attr_ty: core_to_bind_attr_id(core_node.get_attr_ty()),
        attr_weight: core_to_bind_attr_id(core_node.get_attr_weight()),
    }
}
