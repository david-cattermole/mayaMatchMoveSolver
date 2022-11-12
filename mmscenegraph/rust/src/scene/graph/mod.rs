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

pub mod hierarchy;
pub mod links;
pub mod nodes;

use crate::scene::graph::hierarchy::HierarchyGraph;
use crate::scene::graph::links::SceneLinks;
use crate::scene::graph::nodes::SceneNodes;

use petgraph::graph::NodeIndex as PGNodeIndex;
use petgraph::Graph as PGGraph;

use crate::attr::AttrId;
use crate::math::camera::FilmFit;
use crate::math::rotate::euler::RotateOrder;
use crate::node::bundle::BundleNode;
use crate::node::camera::CameraNode;
use crate::node::marker::MarkerNode;
use crate::node::traits::NodeCanRotate3D;
use crate::node::traits::NodeCanScale3D;
use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeCanTranslate2D;
use crate::node::traits::NodeCanTranslate3D;
use crate::node::traits::NodeCanViewScene;
use crate::node::traits::NodeHasId;
use crate::node::traits::NodeHasWeight;
use crate::node::transform::TransformNode;
use crate::node::NodeId;

type Graph = PGGraph<NodeId, ()>;

#[derive(Debug, Clone)]
pub struct SceneGraph {
    hierarchy: HierarchyGraph,
    scene_nodes: SceneNodes,
    scene_links: SceneLinks,
}

impl SceneGraph {
    pub fn new() -> SceneGraph {
        SceneGraph {
            hierarchy: HierarchyGraph::new(),
            scene_nodes: SceneNodes::new(),
            scene_links: SceneLinks::new(),
        }
    }

    pub fn clear(&mut self) {
        self.hierarchy.clear();
        self.scene_nodes.clear();
        self.scene_links.clear();
    }

    pub fn create_transform_node(
        &mut self,
        translate_attrs: (AttrId, AttrId, AttrId),
        rotate_attrs: (AttrId, AttrId, AttrId),
        scale_attrs: (AttrId, AttrId, AttrId),
        rotate_order: RotateOrder,
    ) -> TransformNode {
        let mut node = TransformNode::default();

        let (tx, ty, tz) = translate_attrs;
        node.set_attr_tx(tx);
        node.set_attr_ty(ty);
        node.set_attr_tz(tz);

        let (rx, ry, rz) = rotate_attrs;
        node.set_attr_rx(rx);
        node.set_attr_ry(ry);
        node.set_attr_rz(rz);
        node.set_rotate_order(rotate_order);

        let (sx, sy, sz) = scale_attrs;
        node.set_attr_sx(sx);
        node.set_attr_sy(sy);
        node.set_attr_sz(sz);

        let node = self.scene_nodes.add_transform_node(node);
        self.hierarchy.add_node_id(node.get_id());

        node
    }

    pub fn create_bundle_node(
        &mut self,
        translate_attrs: (AttrId, AttrId, AttrId),
        rotate_attrs: (AttrId, AttrId, AttrId),
        scale_attrs: (AttrId, AttrId, AttrId),
        rotate_order: RotateOrder,
    ) -> BundleNode {
        let mut node = BundleNode::default();

        let (tx, ty, tz) = translate_attrs;
        node.set_attr_tx(tx);
        node.set_attr_ty(ty);
        node.set_attr_tz(tz);

        let (rx, ry, rz) = rotate_attrs;
        node.set_attr_rx(rx);
        node.set_attr_ry(ry);
        node.set_attr_rz(rz);
        node.set_rotate_order(rotate_order);

        let (sx, sy, sz) = scale_attrs;
        node.set_attr_sx(sx);
        node.set_attr_sy(sy);
        node.set_attr_sz(sz);

        let node = self.scene_nodes.add_bundle_node(node);
        self.hierarchy.add_node_id(node.get_id());

        node
    }

    pub fn create_camera_node(
        &mut self,
        translate_attrs: (AttrId, AttrId, AttrId),
        rotate_attrs: (AttrId, AttrId, AttrId),
        scale_attrs: (AttrId, AttrId, AttrId),
        sensor_width_attr: AttrId,
        sensor_height_attr: AttrId,
        focal_length_attr: AttrId,
        lens_offset_x_attr: AttrId,
        lens_offset_y_attr: AttrId,
        near_clip_plane_attr: AttrId,
        far_clip_plane_attr: AttrId,
        camera_scale_attr: AttrId,
        rotate_order: RotateOrder,
        film_fit: FilmFit,
        render_image_width: i32,
        render_image_height: i32,
    ) -> CameraNode {
        let mut node = CameraNode::default();

        let (tx, ty, tz) = translate_attrs;
        node.set_attr_tx(tx);
        node.set_attr_ty(ty);
        node.set_attr_tz(tz);

        let (rx, ry, rz) = rotate_attrs;
        node.set_attr_rx(rx);
        node.set_attr_ry(ry);
        node.set_attr_rz(rz);
        node.set_rotate_order(rotate_order);

        let (sx, sy, sz) = scale_attrs;
        node.set_attr_sx(sx);
        node.set_attr_sy(sy);
        node.set_attr_sz(sz);

        node.set_attr_sensor_width(sensor_width_attr);
        node.set_attr_sensor_height(sensor_height_attr);
        node.set_attr_focal_length(focal_length_attr);
        node.set_attr_lens_offset_x(lens_offset_x_attr);
        node.set_attr_lens_offset_y(lens_offset_y_attr);
        node.set_attr_near_clip_plane(near_clip_plane_attr);
        node.set_attr_far_clip_plane(far_clip_plane_attr);
        node.set_attr_camera_scale(camera_scale_attr);

        node.set_film_fit(film_fit);
        node.set_render_image_width(render_image_width);
        node.set_render_image_height(render_image_height);

        let node = self.scene_nodes.add_camera_node(node);
        self.hierarchy.add_node_id(node.get_id());

        node
    }

    pub fn create_marker_node(
        &mut self,
        translate_attrs: (AttrId, AttrId),
        weight_attr: AttrId,
    ) -> MarkerNode {
        let mut node = MarkerNode::default();

        let (tx, ty) = translate_attrs;
        node.set_attr_tx(tx);
        node.set_attr_ty(ty);
        node.set_attr_weight(weight_attr);

        let node = self.scene_nodes.add_marker_node(node);
        let node_id = node.get_id();
        self.hierarchy.add_node_id(node_id);

        // Markers do not link to any camera by default.
        self.scene_links.add_marker_to_camera_node_ids(NodeId::None);

        // Markers are not linked to any bundle by default.
        self.scene_links.add_marker_to_bundle_node_ids(NodeId::None);

        node
    }

    pub fn num_transform_nodes(&self) -> usize {
        let num = self.scene_nodes.num_transform_nodes();
        assert_eq!(num, self.hierarchy.num_transform_indices());
        num
    }

    pub fn num_camera_nodes(&self) -> usize {
        let num = self.scene_nodes.num_camera_nodes();
        assert_eq!(num, self.hierarchy.num_camera_indices());
        num
    }

    pub fn num_marker_nodes(&self) -> usize {
        let num = self.scene_nodes.num_marker_nodes();
        assert_eq!(num, self.hierarchy.num_marker_indices());
        num
    }

    pub fn num_bundle_nodes(&self) -> usize {
        let num = self.scene_nodes.num_bundle_nodes();
        assert_eq!(num, self.hierarchy.num_bundle_indices());
        num
    }

    pub fn get_transformable_nodes(
        &self,
        node_ids: &[NodeId],
    ) -> Option<Vec<Box<dyn NodeCanTransform3D>>> {
        self.scene_nodes.get_transformable_nodes(node_ids)
    }

    pub fn link_marker_to_camera(
        &mut self,
        mkr_node_id: NodeId,
        cam_node_id: NodeId,
    ) -> bool {
        self.scene_links
            .link_marker_to_camera(mkr_node_id, cam_node_id)
    }

    pub fn link_marker_to_bundle(
        &mut self,
        mkr_node_id: NodeId,
        bnd_node_id: NodeId,
    ) -> bool {
        self.scene_links
            .link_marker_to_bundle(mkr_node_id, bnd_node_id)
    }

    pub fn get_camera_node_id_from_marker_node_id(
        &self,
        node_id: NodeId,
    ) -> Option<NodeId> {
        self.scene_links
            .get_camera_node_id_from_marker_node_id(node_id)
    }

    pub fn get_bundle_node_id_from_marker_node_id(
        &self,
        node_id: NodeId,
    ) -> Option<NodeId> {
        self.scene_links
            .get_bundle_node_id_from_marker_node_id(node_id)
    }

    pub fn get_node_index_from_node_id(
        &self,
        node_id: NodeId,
    ) -> Option<PGNodeIndex> {
        self.hierarchy.get_node_index(node_id)
    }

    pub fn set_node_parent(
        &mut self,
        child_node_id: NodeId,
        parent_node_id: NodeId,
    ) -> bool {
        self.hierarchy
            .set_node_parent(child_node_id, parent_node_id)
    }

    pub fn set_nodes_parent(
        &mut self,
        child_node_ids: &[NodeId],
        parent_node_id: NodeId,
    ) -> bool {
        self.hierarchy
            .set_nodes_parent(child_node_ids, parent_node_id)
    }

    pub fn get_hierarchy_graph(&self) -> &Graph {
        self.hierarchy.get_graph()
    }

    pub fn hierarchy_graph_debug_string(&self) -> String {
        self.hierarchy.graph_debug_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use crate::attr::datablock::AttrDataBlock;
    use crate::scene::helper::create_static_bundle;
    use crate::scene::helper::create_static_camera;
    use crate::scene::helper::create_static_marker;
    use crate::scene::helper::create_static_transform;

    #[test]
    fn test_create_transform_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_transform_nodes(), 0);

        let (tx, ty, tz) = (0.0, 0.0, 0.0);
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = (0.0, 0.0, 0.0);
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = (1.0, 1.0, 1.0);
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        let _node = sg.create_transform_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            RotateOrder::XYZ,
        );
        assert_eq!(sg.num_transform_nodes(), 1);
    }

    #[test]
    fn test_create_bundle_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_bundle_nodes(), 0);

        let (tx, ty, tz) = (0.0, 0.0, 0.0);
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = (0.0, 0.0, 0.0);
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = (1.0, 1.0, 1.0);
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        let _node = sg.create_bundle_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            RotateOrder::XYZ,
        );
        assert_eq!(sg.num_bundle_nodes(), 1);
    }

    #[test]
    fn test_create_camera_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_camera_nodes(), 0);

        let (tx, ty, tz) = (0.0, 0.0, 0.0);
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = (0.0, 0.0, 0.0);
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = (1.0, 1.0, 1.0);
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        let (sensor_width, sensor_height) = (36.0, 24.0);
        let (lens_offset_x, lens_offset_y) = (0.0, 0.0);
        let focal_length = 50.0;
        let near_clip_plane = 0.1;
        let far_clip_plane = 0.1;
        let camera_scale = 1.0;
        let rotate_order = RotateOrder::XYZ;
        let film_fit = FilmFit::Horizontal;
        let render_image_width = 2048;
        let render_image_height = 2048;

        let attr_sensor_width = attrdb.create_attr_static(sensor_width);
        let attr_sensor_height = attrdb.create_attr_static(sensor_height);
        let attr_focal_length = attrdb.create_attr_static(focal_length);
        let attr_lens_offset_x = attrdb.create_attr_static(lens_offset_x);
        let attr_lens_offset_y = attrdb.create_attr_static(lens_offset_y);
        let attr_near_clip_plane = attrdb.create_attr_static(near_clip_plane);
        let attr_far_clip_plane = attrdb.create_attr_static(far_clip_plane);
        let attr_camera_scale = attrdb.create_attr_static(camera_scale);

        let _node = sg.create_camera_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            attr_sensor_width,
            attr_sensor_height,
            attr_focal_length,
            attr_lens_offset_x,
            attr_lens_offset_y,
            attr_near_clip_plane,
            attr_far_clip_plane,
            attr_camera_scale,
            rotate_order,
            film_fit,
            render_image_width,
            render_image_height,
        );
        assert_eq!(sg.num_camera_nodes(), 1);
    }

    #[test]
    fn test_create_marker_node() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_marker_nodes(), 0);

        let weight = 1.0;
        let (tx, ty) = (0.0, 0.0);
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_weight = attrdb.create_attr_static(weight);
        let _node = sg.create_marker_node((attr_tx, attr_ty), attr_weight);
        assert_eq!(sg.num_marker_nodes(), 1);
    }

    #[test]
    fn test_link_marker_to_camera() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        assert_eq!(sg.num_camera_nodes(), 0);

        let mkr = create_static_marker(&mut sg, &mut attrdb, (0.5, 0.5), 1.0);
        let cam = create_static_camera(
            &mut sg,
            &mut attrdb,
            (1.0, 10.0, -1.0),
            (-10.0, 5.0, 1.0),
            (1.0, 1.0, 1.0),
            (36.0, 24.0),
            50.0,
            (0.0, 0.0),
            1.0,
            10000.0,
            1.0,
            RotateOrder::ZXY,
            FilmFit::Horizontal,
            2048,
            2048,
        );

        // Link the Marker to the camera.
        sg.link_marker_to_camera(mkr.get_id(), cam.get_id());

        assert_eq!(sg.num_marker_nodes(), 1);
        assert_eq!(sg.num_camera_nodes(), 1);
    }

    #[test]
    fn test_link_marker_to_bundle() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        assert_eq!(sg.num_bundle_nodes(), 0);

        let mkr = create_static_marker(&mut sg, &mut attrdb, (0.5, 0.5), 1.0);
        let bnd = create_static_bundle(
            &mut sg,
            &mut attrdb,
            (1.0, 1.0, 1.0),
            (00.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            RotateOrder::XYZ,
        );

        // Link the Marker to the bundle.
        sg.link_marker_to_bundle(mkr.get_id(), bnd.get_id());

        assert_eq!(sg.num_marker_nodes(), 1);
        assert_eq!(sg.num_bundle_nodes(), 1);
    }

    // This test creates a non-cycling scene graph which is correct.
    #[test]
    fn test_create_node_hierachy() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_transform_nodes(), 0);

        let rotate_order = RotateOrder::XYZ;

        // nodes
        let tfm_a = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_b = create_static_transform(
            &mut sg,
            &mut attrdb,
            (42.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_c = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 0.0, 42.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        sg.set_node_parent(tfm_b.get_id(), tfm_a.get_id());
        sg.set_node_parent(tfm_c.get_id(), tfm_b.get_id());
        sg.set_node_parent(tfm_a.get_id(), NodeId::Root);

        assert_eq!(sg.num_transform_nodes(), 3);
    }

    // This test creates a cycling scene graph which is invalid.
    #[test]
    fn test_create_bad_hierachy() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_transform_nodes(), 0);

        let rotate_order = RotateOrder::XYZ;

        // nodes
        let tfm_a = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_b = create_static_transform(
            &mut sg,
            &mut attrdb,
            (42.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_c = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 0.0, 42.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        sg.set_node_parent(tfm_b.get_id(), tfm_a.get_id());
        sg.set_node_parent(tfm_a.get_id(), tfm_b.get_id());
        sg.set_node_parent(tfm_c.get_id(), tfm_b.get_id());

        assert_eq!(sg.num_transform_nodes(), 3);
    }

    // Creates two transform nodes that both share the same translateY
    // value - AKA, it's a connection from one attribute to the other
    // so both share the same value.
    #[test]
    fn test_create_input_only_attr_connection() {
        let mut sg = SceneGraph::new();
        let mut attrdb = AttrDataBlock::new();
        assert_eq!(sg.num_transform_nodes(), 0);

        let rotate_order = RotateOrder::XYZ;
        let tfm_a = create_static_transform(
            &mut sg,
            &mut attrdb,
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let (tx, _ty, tz) = (42.0, 0.0, 0.0);
        let attr_tx = attrdb.create_attr_static(tx);
        // Connection from tfm_a.ty to tfm_b.ty.
        let attr_ty = tfm_a.get_attr_ty();
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = (0.0, 0.0, 0.0);
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = (1.0, 1.0, 1.0);
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        let tfm_b = sg.create_transform_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            rotate_order,
        );

        sg.set_node_parent(tfm_a.get_id(), NodeId::Root);
        sg.set_node_parent(tfm_b.get_id(), NodeId::Root);
        assert_eq!(sg.num_transform_nodes(), 2);
    }
}
