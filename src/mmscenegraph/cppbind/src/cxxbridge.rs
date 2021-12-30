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

use crate::attrdatablock::shim_create_attr_data_block_box;
use crate::attrdatablock::ShimAttrDataBlock;

use crate::scenegraph::shim_create_scene_graph_box;
use crate::scenegraph::ShimSceneGraph;

#[cxx::bridge(namespace = "mmscenegraph")]
pub mod ffi {
    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmscenegraph/_cxx.h");
        include!("mmscenegraph/_symbol_export.h");
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum NodeType {
        #[cxx_name = "kTransform"]
        Transform = 0,

        #[cxx_name = "kBundle"]
        Bundle = 1,

        #[cxx_name = "kMarker"]
        Marker = 2,

        #[cxx_name = "kCamera"]
        Camera = 3,

        #[cxx_name = "kRoot"]
        Root = 4,

        #[cxx_name = "kNone"]
        None = 5,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    struct NodeId {
        node_type: NodeType,
        index: usize,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum AttrType {
        #[cxx_name = "kAnimDense"]
        AnimDense = 0,

        #[cxx_name = "kStatic"]
        Static = 1,

        #[cxx_name = "kNone"]
        None = 2,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct AttrId {
        attr_type: AttrType,
        index: usize,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct Translate2DAttrIds {
        tx: AttrId,
        ty: AttrId,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct Translate3DAttrIds {
        tx: AttrId,
        ty: AttrId,
        tz: AttrId,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct Rotate3DAttrIds {
        rx: AttrId,
        ry: AttrId,
        rz: AttrId,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct Scale3DAttrIds {
        sx: AttrId,
        sy: AttrId,
        sz: AttrId,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct CameraAttrIds {
        sensor_width: AttrId,
        sensor_height: AttrId,
        focal_length: AttrId,
    }

    #[derive(Debug, Copy, Clone, Hash)]
    pub(crate) struct MarkerAttrIds {
        tx: AttrId,
        ty: AttrId,
        weight: AttrId,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum RotateOrder {
        #[cxx_name = "kXYZ"]
        XYZ = 0,

        #[cxx_name = "kYXZ"]
        YXZ = 4,

        #[cxx_name = "kZXY"]
        ZXY = 2,

        #[cxx_name = "kXZY"]
        XZY = 3,

        #[cxx_name = "kZYX"]
        ZYX = 5,

        #[cxx_name = "kYZX"]
        YZX = 1,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct TransformNode {
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
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct BundleNode {
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
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct CameraNode {
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
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct MarkerNode {
        id: NodeId,
        attr_tx: AttrId,
        attr_ty: AttrId,
        attr_weight: AttrId,
    }

    // // 3D Vector.
    // #[derive(Debug, Copy, Clone)]
    // pub struct Vec3D {
    //     x: f64,
    //     y: f64,
    //     z: f64,
    // }

    // // 2D Vector.
    // #[derive(Debug, Copy, Clone)]
    // pub struct Vec2D {
    //     x: f64,
    //     y: f64,
    // }

    // AttrDataBlock (Rust)
    extern "Rust" {
        type ShimAttrDataBlock;

        fn clear(&mut self);

        fn create_attr_static(&mut self, value: f64) -> AttrId;
        fn create_attr_anim_dense(&mut self, values: Vec<f64>, frame_start: u32) -> AttrId;

        fn get_attr_value(&self, attr_id: AttrId, frame: u32) -> f64;
        fn set_attr_value(&mut self, attr_id: AttrId, frame: u32, value: f64);

        fn shim_create_attr_data_block_box() -> Box<ShimAttrDataBlock>;
    }

    // SceneGraph (Rust)
    extern "Rust" {
        type ShimSceneGraph;

        fn clear(&mut self);

        fn num_transform_nodes(&self) -> usize;
        fn num_bundle_nodes(&self) -> usize;
        fn num_camera_nodes(&self) -> usize;
        fn num_marker_nodes(&self) -> usize;

        fn create_transform_node(
            &mut self,
            translate_attrs: Translate3DAttrIds,
            rotate_attrs: Rotate3DAttrIds,
            scale_attrs: Scale3DAttrIds,
            rotate_order: RotateOrder,
        ) -> TransformNode;
        fn create_bundle_node(
            &mut self,
            translate_attrs: Translate3DAttrIds,
            rotate_attrs: Rotate3DAttrIds,
            scale_attrs: Scale3DAttrIds,
            rotate_order: RotateOrder,
        ) -> BundleNode;
        fn create_camera_node(
            &mut self,
            translate_attrs: Translate3DAttrIds,
            rotate_attrs: Rotate3DAttrIds,
            scale_attrs: Scale3DAttrIds,
            camera_attrs: CameraAttrIds,
            rotate_order: RotateOrder,
        ) -> CameraNode;
        fn create_marker_node(&mut self, marker_attrs: MarkerAttrIds) -> MarkerNode;

        fn link_marker_to_camera(&mut self, mkr_node_id: NodeId, cam_node_id: NodeId) -> bool;
        fn link_marker_to_bundle(&mut self, mkr_node_id: NodeId, bnd_node_id: NodeId) -> bool;

        fn shim_create_scene_graph_box() -> Box<ShimSceneGraph>;
    }

    ////////////////////////////////////////////////////////////////////
    // Simple test functions.

    #[derive(Debug, Copy, Clone, Default, PartialEq, PartialOrd)]
    struct Camera {
        sensor_width_mm: f64,
        focal_length_mm: f64,
    }

    extern "Rust" {
        fn foo(number: u32);
        fn foobar(number: u32) -> u32;
    }

    extern "Rust" {
        fn make_camera(width: f64, focal: f64) -> Camera;
    }
}

////////////////////////////////////////////////////////////////////
// Simple test functions.
fn foo(number: u32) {
    println!("called Rust with number={}", number);
}

fn foobar(number: u32) -> u32 {
    println!("called Rust with number={}", number);
    number + 1
}

pub fn make_camera(width: f64, focal: f64) -> ffi::Camera {
    let cam = mmscenegraph_rust::make_camera(width, focal);
    ffi::Camera {
        sensor_width_mm: cam.sensor_width_mm,
        focal_length_mm: cam.focal_length_mm,
    }
}
