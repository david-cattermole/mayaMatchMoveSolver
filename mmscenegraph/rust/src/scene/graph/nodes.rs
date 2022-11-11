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

use crate::constant::NodeIndex;
use crate::node::bundle::BundleNode;
use crate::node::camera::CameraNode;
use crate::node::marker::MarkerNode;
use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeHasId;
use crate::node::transform::TransformNode;
use crate::node::NodeId;

#[derive(Debug, Clone)]
pub struct SceneNodes {
    tfm_nodes: Vec<TransformNode>,
    mkr_nodes: Vec<MarkerNode>,
    bnd_nodes: Vec<BundleNode>,
    cam_nodes: Vec<CameraNode>,
}

impl SceneNodes {
    pub fn new() -> SceneNodes {
        SceneNodes {
            tfm_nodes: Vec::<TransformNode>::new(),
            mkr_nodes: Vec::<MarkerNode>::new(),
            bnd_nodes: Vec::<BundleNode>::new(),
            cam_nodes: Vec::<CameraNode>::new(),
        }
    }

    pub fn clear(&mut self) {
        self.tfm_nodes.clear();
        self.mkr_nodes.clear();
        self.bnd_nodes.clear();
        self.cam_nodes.clear();
    }

    pub fn add_transform_node(
        &mut self,
        mut node: TransformNode,
    ) -> TransformNode {
        let node_id = NodeId::Transform(self.tfm_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.tfm_nodes.push(node);
        node
    }

    pub fn add_camera_node(&mut self, mut node: CameraNode) -> CameraNode {
        let node_id = NodeId::Camera(self.cam_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.cam_nodes.push(node);
        node
    }

    pub fn add_marker_node(&mut self, mut node: MarkerNode) -> MarkerNode {
        let node_id = NodeId::Marker(self.mkr_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.mkr_nodes.push(node);
        node
    }

    pub fn add_bundle_node(&mut self, mut node: BundleNode) -> BundleNode {
        let node_id = NodeId::Bundle(self.bnd_nodes.len() as NodeIndex);
        node.set_id(node_id);
        self.bnd_nodes.push(node);
        node
    }

    pub fn num_transform_nodes(&self) -> usize {
        self.tfm_nodes.len()
    }

    pub fn num_camera_nodes(&self) -> usize {
        self.cam_nodes.len()
    }

    pub fn num_marker_nodes(&self) -> usize {
        self.mkr_nodes.len()
    }

    pub fn num_bundle_nodes(&self) -> usize {
        self.bnd_nodes.len()
    }

    pub fn get_transform_node(&self, node_id: NodeId) -> Option<TransformNode> {
        match node_id {
            NodeId::Transform(index) => Some(self.tfm_nodes[index]),
            _ => None,
        }
    }

    pub fn get_bundle_node(&self, node_id: NodeId) -> Option<BundleNode> {
        match node_id {
            NodeId::Bundle(index) => Some(self.bnd_nodes[index]),
            _ => None,
        }
    }

    pub fn get_camera_node(&self, node_id: NodeId) -> Option<CameraNode> {
        match node_id {
            NodeId::Camera(index) => Some(self.cam_nodes[index]),
            _ => None,
        }
    }

    pub fn get_marker_node(&self, node_id: NodeId) -> Option<MarkerNode> {
        match node_id {
            NodeId::Marker(index) => Some(self.mkr_nodes[index]),
            _ => None,
        }
    }

    pub fn get_transformable_nodes(
        &self,
        node_ids: &[NodeId],
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
}
