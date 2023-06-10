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

use petgraph::dot::Config as PGConfig;
use petgraph::dot::Dot as PGDot;
use petgraph::graph::NodeIndex as PGNodeIndex;
use petgraph::Graph as PGGraph;

use crate::node::NodeId;

type Graph = PGGraph<NodeId, ()>;

#[derive(Debug, Clone)]
pub struct HierarchyGraph {
    hierarchy: Graph,
    tfm_indices: Vec<PGNodeIndex>,
    mkr_indices: Vec<PGNodeIndex>,
    bnd_indices: Vec<PGNodeIndex>,
    cam_indices: Vec<PGNodeIndex>,
}

impl HierarchyGraph {
    pub fn new() -> HierarchyGraph {
        HierarchyGraph {
            hierarchy: Graph::new(),
            tfm_indices: Vec::<PGNodeIndex>::new(),
            mkr_indices: Vec::<PGNodeIndex>::new(),
            bnd_indices: Vec::<PGNodeIndex>::new(),
            cam_indices: Vec::<PGNodeIndex>::new(),
        }
    }

    pub fn clear(&mut self) {
        self.hierarchy.clear();
        self.tfm_indices.clear();
        self.mkr_indices.clear();
        self.bnd_indices.clear();
        self.cam_indices.clear();
    }

    pub fn num_transform_indices(&self) -> usize {
        self.tfm_indices.len()
    }

    pub fn num_camera_indices(&self) -> usize {
        self.cam_indices.len()
    }

    pub fn num_marker_indices(&self) -> usize {
        self.mkr_indices.len()
    }

    pub fn num_bundle_indices(&self) -> usize {
        self.bnd_indices.len()
    }

    pub fn get_node_index(&self, node_id: NodeId) -> Option<PGNodeIndex> {
        match node_id {
            NodeId::Transform(index) => Some(self.tfm_indices[index]),
            NodeId::Bundle(index) => Some(self.bnd_indices[index]),
            NodeId::Camera(index) => Some(self.cam_indices[index]),
            NodeId::Marker(index) => Some(self.mkr_indices[index]),
            _ => None,
        }
    }

    pub fn add_node_id(&mut self, node_id: NodeId) {
        let hierarchy_node_index = self.hierarchy.add_node(node_id);

        match node_id {
            NodeId::Transform(_) => self.tfm_indices.push(hierarchy_node_index),
            NodeId::Bundle(_) => self.bnd_indices.push(hierarchy_node_index),
            NodeId::Camera(_) => self.cam_indices.push(hierarchy_node_index),
            NodeId::Marker(_) => self.mkr_indices.push(hierarchy_node_index),
            _ => (),
        }
    }

    /// Set the parent of child_node_id to parent_node_id.
    ///
    /// Note: `set_node_parent` cannot be used to "unparent" a node to
    /// the root.
    pub fn set_node_parent(
        &mut self,
        child_node_id: NodeId,
        parent_node_id: NodeId,
    ) -> bool {
        let child_node_index = self.get_node_index(child_node_id);
        let parent_node_index = self.get_node_index(parent_node_id);

        if child_node_index == None {
            return false;
        }
        if parent_node_index == None {
            return false;
        }

        let child_node_index = child_node_index.unwrap();
        let parent_node_index = parent_node_index.unwrap();

        self.hierarchy
            .update_edge(parent_node_index, child_node_index, ());
        return true;
    }

    /// Set all the child_node_ids to have the same parent_node_id.
    pub fn set_nodes_parent(
        &mut self,
        child_node_ids: &[NodeId],
        parent_node_id: NodeId,
    ) -> bool {
        let node_indices: Vec<PGNodeIndex> = child_node_ids
            .iter()
            .filter_map(|x| self.get_node_index(*x))
            .collect();
        if node_indices.len() == 0 {
            return false;
        }

        let parent_node_index = self.get_node_index(parent_node_id);
        if parent_node_index == None {
            return false;
        }
        let parent_node_index = parent_node_index.unwrap();

        for node_index in node_indices {
            self.hierarchy
                .update_edge(parent_node_index, node_index, ());
        }
        return true;
    }

    /// Users can inspect the internal graph structure, but they are
    /// not allowed to edit it.
    pub fn get_graph(&self) -> &Graph {
        &self.hierarchy
    }

    /// Return a nice string for the user to use to debug the graph.
    pub fn graph_debug_string(&self) -> String {
        String::from(format!(
            "Graph: {:?}",
            PGDot::with_config(&self.hierarchy, &[PGConfig::EdgeNoLabel])
        ))
    }
}
