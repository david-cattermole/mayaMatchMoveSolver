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

use petgraph::algo::toposort as PGtoposort;
use petgraph::dot::Config as PGConfig;
use petgraph::dot::Dot as PGDot;
use petgraph::graph::NodeIndex as PGNodeIndex;
use petgraph::visit::Dfs as PGDfs;
use petgraph::visit::EdgeRef as PGEdgeRef;
use petgraph::Direction as PGDirection;
use petgraph::Graph as PGGraph;

use std::collections::hash_set::HashSet;
use std::fmt;

use crate::attr::AttrDataBlock;
use crate::attr::AttrId;
use crate::constant::NodeIndex;
use crate::constant::Real;
use crate::math::rotate::euler::RotateOrder;
use crate::math::transform;
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
use crate::scene::graphiter::UpstreamDepthFirstSearch;

type Graph = PGGraph<NodeId, ()>;

#[derive(Debug, Clone)]
pub struct SceneGraph {
    attr_data_block: AttrDataBlock,
    hierarchy: Graph,
    tfm_nodes: Vec<TransformNode>,
    mkr_nodes: Vec<MarkerNode>,
    bnd_nodes: Vec<BundleNode>,
    cam_nodes: Vec<CameraNode>,
    tfm_indices: Vec<PGNodeIndex>,
    mkr_indices: Vec<PGNodeIndex>,
    bnd_indices: Vec<PGNodeIndex>,
    cam_indices: Vec<PGNodeIndex>,
    mkr_to_cam_node_ids: Vec<NodeId>,
    mkr_to_bnd_node_ids: Vec<NodeId>,
}

impl SceneGraph {
    pub fn new() -> SceneGraph {
        SceneGraph {
            attr_data_block: AttrDataBlock::new(),
            hierarchy: Graph::new(),
            tfm_nodes: Vec::<TransformNode>::new(),
            mkr_nodes: Vec::<MarkerNode>::new(),
            bnd_nodes: Vec::<BundleNode>::new(),
            cam_nodes: Vec::<CameraNode>::new(),
            tfm_indices: Vec::<PGNodeIndex>::new(),
            mkr_indices: Vec::<PGNodeIndex>::new(),
            bnd_indices: Vec::<PGNodeIndex>::new(),
            cam_indices: Vec::<PGNodeIndex>::new(),
            mkr_to_cam_node_ids: Vec::<NodeId>::new(),
            mkr_to_bnd_node_ids: Vec::<NodeId>::new(),
        }
    }

    pub fn attr_data_block_mut(&mut self) -> &mut AttrDataBlock {
        &mut self.attr_data_block
    }

    pub fn attr_data_block(&self) -> &AttrDataBlock {
        &self.attr_data_block
    }

    pub fn clear(&mut self) {
        self.hierarchy.clear();

        self.tfm_nodes.clear();
        self.mkr_nodes.clear();
        self.bnd_nodes.clear();
        self.cam_nodes.clear();

        self.tfm_indices.clear();
        self.mkr_indices.clear();
        self.bnd_indices.clear();
        self.cam_indices.clear();
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

        let node_id = NodeId::Transform(self.tfm_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.tfm_nodes.push(node);

        let node_index = self.hierarchy.add_node(node_id);
        self.tfm_indices.push(node_index);

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

        let node_id = NodeId::Bundle(self.bnd_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.bnd_nodes.push(node);

        let node_index = self.hierarchy.add_node(node_id);
        self.bnd_indices.push(node_index);

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
        rotate_order: RotateOrder,
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

        let node_id = NodeId::Camera(self.cam_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.cam_nodes.push(node);

        let node_index = self.hierarchy.add_node(node_id);
        self.cam_indices.push(node_index);

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

        let node_id = NodeId::Marker(self.mkr_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.mkr_nodes.push(node);

        let node_index = self.hierarchy.add_node(node_id);
        self.mkr_indices.push(node_index);

        // Markers do not link to any camera by default.
        self.mkr_to_cam_node_ids.push(NodeId::None);

        // Markers are not linked to any bundle by default.
        self.mkr_to_bnd_node_ids.push(NodeId::None);

        node
    }

    pub fn create_static_transform(
        &mut self,
        translate: (Real, Real, Real),
        rotate: (Real, Real, Real),
        scale: (Real, Real, Real),
        rotate_order: RotateOrder,
    ) -> TransformNode {
        let attrdb = self.attr_data_block_mut();

        let (tx, ty, tz) = translate;
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = rotate;
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = scale;
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        self.create_transform_node(translate_attrs, rotate_attrs, scale_attrs, rotate_order)
    }

    pub fn create_static_marker(&mut self, translate: (Real, Real), weight: Real) -> MarkerNode {
        let attrdb = self.attr_data_block_mut();
        let (tx, ty) = translate;
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_weight = attrdb.create_attr_static(weight);
        let mkr = self.create_marker_node((attr_tx, attr_ty), attr_weight);
        mkr
    }

    pub fn create_static_bundle(
        &mut self,
        translate: (Real, Real, Real),
        rotate: (Real, Real, Real),
        scale: (Real, Real, Real),
        rotate_order: RotateOrder,
    ) -> BundleNode {
        let attrdb = self.attr_data_block_mut();

        let (tx, ty, tz) = translate;
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = rotate;
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = scale;
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        self.create_bundle_node(translate_attrs, rotate_attrs, scale_attrs, rotate_order)
    }

    pub fn create_static_camera(
        &mut self,
        translate: (Real, Real, Real),
        rotate: (Real, Real, Real),
        scale: (Real, Real, Real),
        sensor: (Real, Real),
        focal_length: Real,
        rotate_order: RotateOrder,
    ) -> CameraNode {
        let attrdb = self.attr_data_block_mut();

        let (tx, ty, tz) = translate;
        let attr_tx = attrdb.create_attr_static(tx);
        let attr_ty = attrdb.create_attr_static(ty);
        let attr_tz = attrdb.create_attr_static(tz);
        let translate_attrs = (attr_tx, attr_ty, attr_tz);

        let (rx, ry, rz) = rotate;
        let attr_rx = attrdb.create_attr_static(rx);
        let attr_ry = attrdb.create_attr_static(ry);
        let attr_rz = attrdb.create_attr_static(rz);
        let rotate_attrs = (attr_rx, attr_ry, attr_rz);

        let (sx, sy, sz) = scale;
        let attr_sx = attrdb.create_attr_static(sx);
        let attr_sy = attrdb.create_attr_static(sy);
        let attr_sz = attrdb.create_attr_static(sz);
        let scale_attrs = (attr_sx, attr_sy, attr_sz);

        let (sensor_width, sensor_height) = sensor;
        let attr_sensor_width = attrdb.create_attr_static(sensor_width);
        let attr_sensor_height = attrdb.create_attr_static(sensor_height);
        let attr_focal_length = attrdb.create_attr_static(focal_length);

        self.create_camera_node(
            translate_attrs,
            rotate_attrs,
            scale_attrs,
            attr_sensor_width,
            attr_sensor_height,
            attr_focal_length,
            rotate_order,
        )
    }

    pub fn link_marker_to_camera(&mut self, mkr_node_id: NodeId, cam_node_id: NodeId) -> bool {
        let mkr_index = match mkr_node_id {
            NodeId::Marker(index) => index as usize,
            _ => return false,
        };
        match cam_node_id {
            NodeId::Camera(cam_index) => self.mkr_to_cam_node_ids[mkr_index] = cam_node_id,
            _ => return false,
        };
        return true;
    }

    pub fn link_marker_to_bundle(&mut self, mkr_node_id: NodeId, bnd_node_id: NodeId) -> bool {
        let mkr_index = match mkr_node_id {
            NodeId::Marker(index) => index as usize,
            _ => return false,
        };
        match bnd_node_id {
            NodeId::Bundle(bnd_index) => self.mkr_to_bnd_node_ids[mkr_index] = bnd_node_id,
            _ => return false,
        };
        return true;
    }

    pub fn get_transform_node(&self, node_id: NodeId) -> Option<TransformNode> {
        match node_id {
            NodeId::Transform(index) => Some(self.tfm_nodes[index as usize]),
            _ => None,
        }
    }

    pub fn get_bundle_node(&self, node_id: NodeId) -> Option<BundleNode> {
        match node_id {
            NodeId::Bundle(index) => Some(self.bnd_nodes[index as usize]),
            _ => None,
        }
    }

    pub fn get_camera_node(&self, node_id: NodeId) -> Option<CameraNode> {
        match node_id {
            NodeId::Camera(index) => Some(self.cam_nodes[index as usize]),
            _ => None,
        }
    }

    pub fn get_marker_node(&self, node_id: NodeId) -> Option<MarkerNode> {
        match node_id {
            NodeId::Marker(index) => Some(self.mkr_nodes[index as usize]),
            _ => None,
        }
    }

    pub fn get_transformable_nodes(
        &self,
        node_ids: &Vec<NodeId>,
    ) -> Option<Vec<Box<dyn NodeCanTransform3D>>> {
        let mut nodes = Vec::<Box<dyn NodeCanTransform3D>>::new();
        for node_id in node_ids {
            match node_id {
                NodeId::Transform(_) => {
                    let node = self.get_transform_node(*node_id).unwrap();
                    let node_box = Box::new(node);
                    nodes.push(node_box);
                }
                NodeId::Camera(_) => {
                    let node = self.get_camera_node(*node_id).unwrap();
                    let node_box = Box::new(node);
                    nodes.push(node_box);
                }
                NodeId::Bundle(_) => {
                    let node = self.get_bundle_node(*node_id).unwrap();
                    let node_box = Box::new(node);
                    nodes.push(node_box);
                }
                _ => {
                    println!("Invalid node id: {:?}", node_id);
                    return None;
                }
            };
        }
        Some(nodes)
    }

    pub fn get_graph_node_index(&self, node_id: NodeId) -> Option<PGNodeIndex> {
        match node_id {
            NodeId::Transform(index) => Some(self.tfm_indices[index as usize]),
            NodeId::Bundle(index) => Some(self.bnd_indices[index as usize]),
            NodeId::Camera(index) => Some(self.cam_indices[index as usize]),
            NodeId::Marker(index) => Some(self.mkr_indices[index as usize]),
            _ => None,
        }
    }

    /// Set the parent of child_node_id to parent_node_id.
    pub fn set_node_parent(&mut self, child_node_id: NodeId, parent_node_id: NodeId) -> bool {
        let node_index = self.get_graph_node_index(child_node_id);
        if node_index == None {
            return false;
        }
        let node_index = node_index.unwrap();

        let parent_node_index = self.get_graph_node_index(parent_node_id);
        if parent_node_index == None {
            return false;
        }
        let parent_node_index = parent_node_index.unwrap();

        self.hierarchy.add_edge(parent_node_index, node_index, ());
        return true;
    }

    /// Set all the child_node_ids to have the same parent_node_id
    pub fn set_nodes_parent(
        &mut self,
        child_node_ids: Vec<NodeId>,
        parent_node_id: NodeId,
    ) -> bool {
        let node_indices: Vec<PGNodeIndex> = child_node_ids
            .iter()
            .filter_map(|x| self.get_graph_node_index(*x))
            .collect();
        if node_indices.len() == 0 {
            return false;
        }

        let parent_node_index = self.get_graph_node_index(parent_node_id);
        if parent_node_index == None {
            return false;
        }
        let parent_node_index = parent_node_index.unwrap();

        for node_index in node_indices {
            self.hierarchy.add_edge(parent_node_index, node_index, ());
        }
        return true;
    }

    pub fn num_transform_nodes(&self) -> usize {
        debug_assert_eq!(self.tfm_nodes.len(), self.tfm_indices.len());
        self.tfm_nodes.len()
    }

    pub fn num_camera_nodes(&self) -> usize {
        debug_assert_eq!(self.cam_nodes.len(), self.cam_indices.len());
        self.cam_nodes.len()
    }

    pub fn num_marker_nodes(&self) -> usize {
        debug_assert_eq!(self.mkr_nodes.len(), self.mkr_indices.len());
        self.mkr_nodes.len()
    }

    pub fn num_bundle_nodes(&self) -> usize {
        debug_assert_eq!(self.bnd_nodes.len(), self.bnd_indices.len());
        self.bnd_nodes.len()
    }

    pub fn sort_hierarchy(
        &mut self,
        node_ids: Vec<NodeId>,
    ) -> Option<(Vec<PGNodeIndex>, Vec<NodeId>)> {
        // println!(
        //     "Graph: {:?}",
        //     PGDot::with_config(&self.hierarchy, &[PGConfig::EdgeNoLabel])
        // );

        let mut node_indices_set = HashSet::new();
        for node_id in node_ids {
            let node_index = match node_id {
                NodeId::Transform(index) => self.tfm_indices[index as usize],
                NodeId::Camera(index) => self.cam_indices[index as usize],
                NodeId::Marker(index) => self.mkr_indices[index as usize],
                NodeId::Bundle(index) => self.bnd_indices[index as usize],
                _ => panic!("Invalid node id."),
            };

            let mut walker = UpstreamDepthFirstSearch::new(&self.hierarchy, node_index);
            while let Some((node, _depth)) = walker.next(&self.hierarchy) {
                node_indices_set.insert(node);
            }
        }
        // println!("Node Indices to keep: {:#?}", node_indices_set);

        match PGtoposort(&self.hierarchy, None) {
            Ok(nodes) => {
                // println!("Toposort nodes: {:#?}", nodes);

                let filtered_nodes: Vec<_> = nodes
                    .iter()
                    .filter(|node_index| node_indices_set.contains(&node_index))
                    .map(|node_index| *node_index)
                    .collect();
                // println!("Toposort filtered nodes: {:#?}", filtered_nodes);

                let filtered_node_ids: Vec<_> = filtered_nodes
                    .iter()
                    .map(|node_index| *self.hierarchy.node_weight(*node_index).unwrap())
                    .collect();

                Some((filtered_nodes, filtered_node_ids))
            }
            Err(cycle) => {
                // println!("Cycle: {:#?}", cycle);
                None
            }
        }
    }

    pub fn get_parent_list(&self, node_indices: &Vec<PGNodeIndex>) -> Vec<Option<usize>> {
        let mut list = Vec::<Option<usize>>::new();
        let dir = PGDirection::Incoming;
        for (i, node_index) in (0..).zip(node_indices) {
            let edges: Vec<_> = self.hierarchy.edges_directed(*node_index, dir).collect();
            assert!(edges.len() < 2);
            if edges.len() == 0 {
                list.push(None);
                continue;
            }
            let parent_node_index = edges[0].source();

            let mut parent_index = None;
            let previous_node_indices_iter = node_indices[0..i].iter(); //.rev();
            for (j, previous_node_index) in (0..).zip(previous_node_indices_iter) {
                if *previous_node_index == parent_node_index {
                    parent_index = Some(j);
                    break;
                }
            }
            list.push(parent_index);
        }
        list
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_transform_node() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_transform_nodes(), 0);

        let tfm = sg.create_static_transform(
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            RotateOrder::XYZ,
        );

        assert_eq!(sg.num_transform_nodes(), 1);
    }

    #[test]
    fn test_create_bundle_node() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_bundle_nodes(), 0);
        let bnd = sg.create_static_bundle(
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            RotateOrder::XYZ,
        );

        assert_eq!(sg.num_bundle_nodes(), 1);
    }

    #[test]
    fn test_create_camera_node() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_camera_nodes(), 0);

        let cam = sg.create_static_camera(
            (1.0, 10.0, -1.0),
            (-10.0, 5.0, 1.0),
            (1.0, 1.0, 1.0),
            (36.0, 24.0),
            50.0,
            RotateOrder::ZXY,
        );

        assert_eq!(sg.num_camera_nodes(), 1);
    }

    #[test]
    fn test_create_marker_node() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        let mkr = sg.create_static_marker((0.5, 0.5), 1.0);
        assert_eq!(sg.num_marker_nodes(), 1);
    }

    #[test]
    fn test_link_marker_to_camera() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        assert_eq!(sg.num_camera_nodes(), 0);

        let mkr = sg.create_static_marker((0.5, 0.5), 1.0);
        let cam = sg.create_static_camera(
            (1.0, 10.0, -1.0),
            (-10.0, 5.0, 1.0),
            (1.0, 1.0, 1.0),
            (36.0, 24.0),
            50.0,
            RotateOrder::ZXY,
        );

        // Link the Marker to the camera.
        sg.link_marker_to_camera(mkr.get_id(), cam.get_id());

        assert_eq!(sg.num_marker_nodes(), 1);
        assert_eq!(sg.num_camera_nodes(), 1);
    }

    #[test]
    fn test_link_marker_to_bundle() {
        let mut sg = SceneGraph::new();
        assert_eq!(sg.num_marker_nodes(), 0);
        assert_eq!(sg.num_bundle_nodes(), 0);

        let mkr = sg.create_static_marker((0.5, 0.5), 1.0);
        let bnd = sg.create_static_bundle(
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
        assert_eq!(sg.num_transform_nodes(), 0);

        let rotate_order = RotateOrder::XYZ;

        // nodes
        let tfm_a = sg.create_static_transform(
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_b = sg.create_static_transform(
            (42.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_c = sg.create_static_transform(
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
        assert_eq!(sg.num_transform_nodes(), 0);

        let rotate_order = RotateOrder::XYZ;

        // nodes
        let tfm_a = sg.create_static_transform(
            (0.0, 42.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_b = sg.create_static_transform(
            (42.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            rotate_order,
        );

        let tfm_c = sg.create_static_transform(
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
}
