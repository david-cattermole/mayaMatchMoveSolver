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

use crate::attr::bind_to_core_camera_attr_ids;
use crate::attr::bind_to_core_marker_attr_ids;
use crate::attr::bind_to_core_rotate_3d_attr_ids;
use crate::attr::bind_to_core_scale_3d_attr_ids;
use crate::attr::bind_to_core_translate_3d_attr_ids;
use crate::cxxbridge::ffi::BundleNode as BindBundleNode;
use crate::cxxbridge::ffi::CameraAttrIds as BindCameraAttrIds;
use crate::cxxbridge::ffi::CameraNode as BindCameraNode;
use crate::cxxbridge::ffi::MarkerAttrIds as BindMarkerAttrIds;
use crate::cxxbridge::ffi::MarkerNode as BindMarkerNode;
use crate::cxxbridge::ffi::NodeId as BindNodeId;
use crate::cxxbridge::ffi::Rotate3DAttrIds as BindRotate3DAttrIds;
use crate::cxxbridge::ffi::RotateOrder as BindRotateOrder;
use crate::cxxbridge::ffi::Scale3DAttrIds as BindScale3DAttrIds;
use crate::cxxbridge::ffi::TransformNode as BindTransformNode;
use crate::cxxbridge::ffi::Translate3DAttrIds as BindTranslate3DAttrIds;
use crate::math::bind_to_core_rotate_order;
use crate::node::bind_to_core_node_id;
use crate::node::core_to_bind_bundle_node;
use crate::node::core_to_bind_camera_node;
use crate::node::core_to_bind_marker_node;
use crate::node::core_to_bind_transform_node;
use mmscenegraph_rust::scene::graph::SceneGraph as CoreSceneGraph;

#[derive(Debug, Clone)]
pub struct ShimSceneGraph {
    inner: CoreSceneGraph,
}

impl ShimSceneGraph {
    fn new() -> Self {
        Self {
            inner: CoreSceneGraph::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreSceneGraph {
        &self.inner
    }

    pub fn clear(&mut self) {
        self.inner.clear()
    }

    pub fn create_transform_node(
        &mut self,
        translate_attrs: BindTranslate3DAttrIds,
        rotate_attrs: BindRotate3DAttrIds,
        scale_attrs: BindScale3DAttrIds,
        rotate_order: BindRotateOrder,
    ) -> BindTransformNode {
        let translate_attrs =
            bind_to_core_translate_3d_attr_ids(translate_attrs);
        let rotate_attrs = bind_to_core_rotate_3d_attr_ids(rotate_attrs);
        let scale_attrs = bind_to_core_scale_3d_attr_ids(scale_attrs);

        let core_node = self.inner.create_transform_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            bind_to_core_rotate_order(rotate_order),
        );

        core_to_bind_transform_node(core_node)
    }

    pub fn create_bundle_node(
        &mut self,
        translate_attrs: BindTranslate3DAttrIds,
        rotate_attrs: BindRotate3DAttrIds,
        scale_attrs: BindScale3DAttrIds,
        rotate_order: BindRotateOrder,
    ) -> BindBundleNode {
        let translate_attrs =
            bind_to_core_translate_3d_attr_ids(translate_attrs);
        let rotate_attrs = bind_to_core_rotate_3d_attr_ids(rotate_attrs);
        let scale_attrs = bind_to_core_scale_3d_attr_ids(scale_attrs);

        let core_node = self.inner.create_bundle_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            bind_to_core_rotate_order(rotate_order),
        );

        core_to_bind_bundle_node(core_node)
    }

    pub fn create_camera_node(
        &mut self,
        translate_attrs: BindTranslate3DAttrIds,
        rotate_attrs: BindRotate3DAttrIds,
        scale_attrs: BindScale3DAttrIds,
        camera_attrs: BindCameraAttrIds,
        rotate_order: BindRotateOrder,
    ) -> BindCameraNode {
        let translate_attrs =
            bind_to_core_translate_3d_attr_ids(translate_attrs);
        let rotate_attrs = bind_to_core_rotate_3d_attr_ids(rotate_attrs);
        let scale_attrs = bind_to_core_scale_3d_attr_ids(scale_attrs);
        let (sensor_width_attr, sensor_height_attr, focal_length_attr) =
            bind_to_core_camera_attr_ids(camera_attrs);

        let core_node = self.inner.create_camera_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            sensor_width_attr,
            sensor_height_attr,
            focal_length_attr,
            bind_to_core_rotate_order(rotate_order),
        );

        core_to_bind_camera_node(core_node)
    }

    pub fn create_marker_node(
        &mut self,
        marker_attrs: BindMarkerAttrIds,
    ) -> BindMarkerNode {
        let (tx_attr, ty_attr, weight_attr) =
            bind_to_core_marker_attr_ids(marker_attrs);

        let core_node = self
            .inner
            .create_marker_node((tx_attr, ty_attr), weight_attr);

        core_to_bind_marker_node(core_node)
    }

    pub fn link_marker_to_camera(
        &mut self,
        mkr_node_id: BindNodeId,
        cam_node_id: BindNodeId,
    ) -> bool {
        let mkr_node_id = bind_to_core_node_id(mkr_node_id);
        let cam_node_id = bind_to_core_node_id(cam_node_id);
        self.inner.link_marker_to_camera(mkr_node_id, cam_node_id)
    }

    pub fn link_marker_to_bundle(
        &mut self,
        mkr_node_id: BindNodeId,
        bnd_node_id: BindNodeId,
    ) -> bool {
        let mkr_node_id = bind_to_core_node_id(mkr_node_id);
        let bnd_node_id = bind_to_core_node_id(bnd_node_id);
        self.inner.link_marker_to_bundle(mkr_node_id, bnd_node_id)
    }

    pub fn set_node_parent(
        &mut self,
        child_node_id: BindNodeId,
        parent_node_id: BindNodeId,
    ) -> bool {
        let child_node_id = bind_to_core_node_id(child_node_id);
        let parent_node_id = bind_to_core_node_id(parent_node_id);
        self.inner
            .link_marker_to_bundle(child_node_id, parent_node_id)
    }

    pub fn num_transform_nodes(&self) -> usize {
        self.inner.num_transform_nodes()
    }

    pub fn num_bundle_nodes(&self) -> usize {
        self.inner.num_bundle_nodes()
    }

    pub fn num_camera_nodes(&self) -> usize {
        self.inner.num_camera_nodes()
    }

    pub fn num_marker_nodes(&self) -> usize {
        self.inner.num_marker_nodes()
    }
}

pub fn shim_create_scene_graph_box() -> Box<ShimSceneGraph> {
    println!("shim_create_scene_graph_box()");
    Box::new(ShimSceneGraph::new())
}
