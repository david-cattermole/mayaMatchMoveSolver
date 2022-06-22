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

use crate::node::bundle::BundleNode;
use crate::node::camera::CameraNode;
use crate::node::marker::MarkerNode;

/// The objects stored and required for an evaluation of the scene graph.
#[derive(Debug, Clone)]
pub struct EvaluationObjects {
    bnd_nodes: Vec<Box<BundleNode>>,
    cam_nodes: Vec<Box<CameraNode>>,
    mkr_nodes: Vec<Box<MarkerNode>>,
}

impl EvaluationObjects {
    pub fn new() -> Self {
        Self {
            bnd_nodes: Vec::new(),
            cam_nodes: Vec::new(),
            mkr_nodes: Vec::new(),
        }
    }

    pub fn clear_all(&mut self) {
        self.bnd_nodes.clear();
        self.cam_nodes.clear();
        self.mkr_nodes.clear();
    }

    pub fn clear_bundles(&mut self) {
        self.bnd_nodes.clear();
    }

    pub fn clear_cameras(&mut self) {
        self.cam_nodes.clear();
    }

    pub fn clear_markers(&mut self) {
        self.cam_nodes.clear();
    }

    pub fn num_bundles(&self) -> usize {
        self.cam_nodes.len()
    }

    pub fn num_cameras(&self) -> usize {
        self.cam_nodes.len()
    }

    pub fn num_markers(&self) -> usize {
        self.mkr_nodes.len()
    }

    pub fn add_bundle(&mut self, node: BundleNode) {
        self.bnd_nodes.push(Box::new(node));
    }

    pub fn add_camera(&mut self, node: CameraNode) {
        self.cam_nodes.push(Box::new(node));
    }

    pub fn add_marker(&mut self, node: MarkerNode) {
        self.mkr_nodes.push(Box::new(node));
    }

    pub fn get_bundles(&self) -> &[Box<BundleNode>] {
        &self.bnd_nodes[..]
    }

    pub fn get_cameras(&self) -> &[Box<CameraNode>] {
        &self.cam_nodes[..]
    }

    pub fn get_markers(&self) -> &[Box<MarkerNode>] {
        &self.mkr_nodes[..]
    }
}

// #[cfg(test)]
// mod tests {
//     use super::*;
//     #[test]
//     fn test_scene_flat_evaluate() {
//         let frame = 1001;
//     }
// }
