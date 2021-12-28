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
use petgraph::graph::NodeIndex as PGNodeIndex;
use petgraph::visit::EdgeRef as PGEdgeRef;
use petgraph::Direction as PGDirection;

use std::collections::hash_set::HashSet;

use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeCanViewScene;
use crate::node::traits::NodeHasId;
use crate::node::NodeId;
use crate::scene::flat::FlatScene;
use crate::scene::graph::SceneGraph;
use crate::scene::graphiter::UpstreamDepthFirstSearch;

// Get upstream node_indices from node_index.
//
// Get the node indices, including all parents required.
fn upstream_node_indices_set(sg: &SceneGraph, node_ids: &Vec<NodeId>) -> HashSet<PGNodeIndex> {
    let graph = &sg.get_graph();
    let mut node_indices_set = HashSet::new();
    for node_id in node_ids {
        let node_index = match sg.get_node_index_from_node_id(*node_id) {
            Some(value) => value,
            None => continue,
        };

        let mut walker = UpstreamDepthFirstSearch::new(graph, node_index);
        while let Some((node, _depth)) = walker.next(graph) {
            // println!("node: {:?}", node);
            // println!("depth: {:?}", _depth);
            node_indices_set.insert(node);
        }
    }
    node_indices_set
}

fn sort_hierarchy(
    sg: &SceneGraph,
    node_ids: Vec<NodeId>,
) -> Option<(Vec<PGNodeIndex>, Vec<NodeId>)> {
    let debug_string = sg.graph_debug_string();
    println!("{}", debug_string);

    // Get the node indices, including all parents required.
    let node_indices_set = upstream_node_indices_set(&sg, &node_ids);
    println!("Node Indices to keep: {:#?}", node_indices_set);

    // Filter-topo-sort.
    let graph = &sg.get_graph();
    match PGtoposort(graph, None) {
        Ok(nodes) => {
            println!("Toposort nodes: {:#?}", nodes);

            let filtered_nodes: Vec<_> = nodes
                .iter()
                .filter(|node_index| node_indices_set.contains(&node_index))
                .map(|node_index| *node_index)
                .collect();
            println!("Toposort filtered nodes: {:#?}", filtered_nodes);

            let filtered_node_ids: Vec<_> = filtered_nodes
                .iter()
                .map(|node_index| *graph.node_weight(*node_index).unwrap())
                .collect();

            Some((filtered_nodes, filtered_node_ids))
        }
        Err(cycle) => {
            println!("Cycle: {:#?}", cycle);
            None
        }
    }
}

// Get the parent index for each node index given.
fn get_parent_list(sg: &SceneGraph, node_indices: &Vec<PGNodeIndex>) -> Vec<Option<usize>> {
    let mut list = Vec::<Option<usize>>::new();
    let dir = PGDirection::Incoming;
    let graph = &sg.get_graph();
    for (i, node_index) in (0..).zip(node_indices) {
        let edges: Vec<_> = graph.edges_directed(*node_index, dir).collect();
        assert!(edges.len() < 2);
        if edges.len() == 0 {
            list.push(None);
            continue;
        }
        let parent_node_index = edges[0].source();

        let mut parent_index = None;
        let previous_node_indices_iter = node_indices[0..i].iter();
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

// TODO: bake down graph into a more efficient representation that has
// a un-editable hierarchy.
pub fn bake_scene_graph<T, U>(
    sg: &SceneGraph,
    active_tfm_nodes: &Vec<Box<T>>,
    // bnd_nodes: &Vec<Box<T>>,
    cam_nodes: &Vec<Box<U>>,
    // mkr_nodes: &Vec<Box<V>>,
) -> FlatScene
where
    T: NodeCanTransform3D + ?Sized,
    U: NodeHasId + NodeCanViewScene + ?Sized,
    // V: NodeCanTransform2D + ?Sized,
{
    let active_tfm_node_ids = active_tfm_nodes.iter().map(|x| x.get_id()).collect();

    let (sorted_node_indices, sorted_node_ids) = sort_hierarchy(&sg, active_tfm_node_ids).unwrap();
    println!("sorted_node_indices: {:#?}", sorted_node_indices.len());
    println!("sorted_node_ids: {:#?}", sorted_node_ids.len());

    let sorted_nodes = sg.get_transformable_nodes(&sorted_node_ids).unwrap();
    println!("sorted_nodes: {:#?}", sorted_nodes.len());

    let sorted_node_parent_indices = get_parent_list(&sg, &sorted_node_indices);
    println!(
        "sorted_node_parent_indices: {}",
        sorted_node_parent_indices.len()
    );

    let mut cam_ids = Vec::new();
    let mut cam_sensor_widths = Vec::new();
    let mut cam_sensor_heights = Vec::new();
    let mut cam_focal_lengths = Vec::new();
    for cam_node in cam_nodes {
        cam_ids.push(cam_node.get_id());
        cam_sensor_widths.push(cam_node.get_attr_sensor_width());
        cam_sensor_heights.push(cam_node.get_attr_sensor_height());
        cam_focal_lengths.push(cam_node.get_attr_focal_length());
    }

    FlatScene {
        // cam_nodes: cam_nodes.to_vec(),
        cam_ids,
        cam_sensor_widths,
        cam_sensor_heights,
        cam_focal_lengths,
        sorted_nodes,
        sorted_node_parent_indices,
        sorted_node_ids,
        sorted_node_indices,
    }
}

// #[cfg(test)]
// mod tests {
//     use super::*;
//     #[test]
//     fn test_bake_scene_graph() {}
// }
