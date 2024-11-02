//
// Copyright (C) 2020, 2021, 2022 David Cattermole.
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
use crate::evaluationobjects::shim_create_evaluation_objects_box;
use crate::evaluationobjects::ShimEvaluationObjects;
use crate::fit_plane::shim_fit_plane_to_points;
use crate::flatscene::shim_create_flat_scene_box;
use crate::flatscene::ShimFlatScene;
use crate::line::shim_fit_line_to_points_type2;
use crate::line::shim_fit_straight_line_to_ordered_points;
use crate::line::shim_line_point_intersection;
use crate::scenebake::shim_bake_scene_graph;
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

    #[derive(Copy, Clone, Debug, PartialEq)]
    pub(crate) struct Point3 {
        pub x: f64,
        pub y: f64,
        pub z: f64,
    }

    // #[derive(Copy, Clone, Debug, PartialEq)]
    // pub(crate) struct Vector3 {
    //     pub x: f64,
    //     pub y: f64,
    //     pub z: f64,
    // }

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
        lens_offset_x: AttrId,
        lens_offset_y: AttrId,
        near_clip_plane: AttrId,
        far_clip_plane: AttrId,
        camera_scale: AttrId,
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

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum FilmFit {
        #[cxx_name = "kFill"]
        Fill = 0,

        #[cxx_name = "kHorizontal"]
        Horizontal = 1,

        #[cxx_name = "kVertical"]
        Vertical = 2,

        #[cxx_name = "kOverscan"]
        Overscan = 3,

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
        attr_lens_offset_x: AttrId,
        attr_lens_offset_y: AttrId,
        attr_near_clip_plane: AttrId,
        attr_far_clip_plane: AttrId,
        attr_camera_scale: AttrId,
        film_fit: FilmFit,
        render_image_width: i32,
        render_image_height: i32,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) struct MarkerNode {
        id: NodeId,
        attr_tx: AttrId,
        attr_ty: AttrId,
        attr_weight: AttrId,
    }

    extern "Rust" {
        type ShimAttrDataBlock;

        fn clear(&mut self);

        fn num_attr_static(&self) -> usize;
        fn num_attr_anim_dense(&self) -> usize;

        fn create_attr_static(&mut self, value: f64) -> AttrId;
        fn create_attr_anim_dense(
            &mut self,
            values: Vec<f64>,
            frame_start: u32,
        ) -> AttrId;

        fn get_attr_value(&self, attr_id: AttrId, frame: u32) -> f64;
        fn set_attr_value(
            &mut self,
            attr_id: AttrId,
            frame: u32,
            value: f64,
        ) -> bool;

        fn shim_create_attr_data_block_box() -> Box<ShimAttrDataBlock>;
    }

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
            film_fit: FilmFit,
            render_image_width: i32,
            render_image_height: i32,
        ) -> CameraNode;
        fn create_marker_node(
            &mut self,
            marker_attrs: MarkerAttrIds,
        ) -> MarkerNode;

        fn link_marker_to_camera(
            &mut self,
            mkr_node_id: NodeId,
            cam_node_id: NodeId,
        ) -> bool;
        fn link_marker_to_bundle(
            &mut self,
            mkr_node_id: NodeId,
            bnd_node_id: NodeId,
        ) -> bool;

        fn set_node_parent(
            &mut self,
            child_node_id: NodeId,
            parent_node_id: NodeId,
        ) -> bool;

        fn shim_create_scene_graph_box() -> Box<ShimSceneGraph>;
    }

    extern "Rust" {
        type ShimFlatScene;

        fn markers(&self) -> &[f64];
        fn points(&self) -> &[f64];

        fn num_markers(&self) -> usize;
        fn num_points(&self) -> usize;

        fn evaluate(
            &mut self,
            attrdb: &Box<ShimAttrDataBlock>,
            frame_list: &[u32],
        );

        fn shim_bake_scene_graph(
            sg: &Box<ShimSceneGraph>,
            eval_objects: &Box<ShimEvaluationObjects>,
        ) -> Box<ShimFlatScene>;

        fn shim_create_flat_scene_box() -> Box<ShimFlatScene>;
    }

    extern "Rust" {
        type ShimEvaluationObjects;

        fn clear_all(&mut self);
        fn clear_bundles(&mut self);
        fn clear_markers(&mut self);
        fn clear_cameras(&mut self);

        fn num_bundles(&self) -> usize;
        fn num_markers(&self) -> usize;
        fn num_cameras(&self) -> usize;

        fn add_bundle(&mut self, bnd_node: &BundleNode);
        fn add_camera(&mut self, cam_node: &CameraNode);
        fn add_marker(&mut self, mkr_node: &MarkerNode);

        fn shim_create_evaluation_objects_box() -> Box<ShimEvaluationObjects>;
    }

    // Line
    extern "Rust" {
        fn shim_fit_line_to_points_type2(
            x: &[f64],
            y: &[f64],
            out_point_x: &mut f64,
            out_point_y: &mut f64,
            out_dir_x: &mut f64,
            out_dir_y: &mut f64,
        ) -> bool;

        fn shim_fit_straight_line_to_ordered_points(
            points_coord_x: &[f64],
            points_coord_y: &[f64],
            out_point_x: &mut f64,
            out_point_y: &mut f64,
            out_dir_x: &mut f64,
            out_dir_y: &mut f64,
        ) -> bool;

        pub fn shim_line_point_intersection(
            point: Point3,
            line_a: Point3,
            line_b: Point3,
            out_point: &mut Point3,
        ) -> bool;
    }

    // Fit Plane
    extern "Rust" {
        fn shim_fit_plane_to_points(
            points_xyz: &[f64],
            out_point_x: &mut f64,
            out_point_y: &mut f64,
            out_point_z: &mut f64,
            out_dir_x: &mut f64,
            out_dir_y: &mut f64,
            out_dir_z: &mut f64,
            out_rms_error: &mut f64,
        ) -> bool;
    }
}
