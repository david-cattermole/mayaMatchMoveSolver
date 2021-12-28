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

use petgraph::graph::NodeIndex as PGNodeIndex;

use crate::attr::AttrDataBlock;
use crate::attr::AttrId;
use crate::constant::FrameValue;
use crate::constant::Matrix44;
use crate::constant::Real;
use crate::math::dag::compute_projection_matrix_with_attrs;
use crate::math::dag::compute_world_matrices;
use crate::math::reprojection::reproject_as_normalised_coord;
use crate::node::traits::NodeCanTransform3D;
use crate::node::NodeId;

// TODO: Contain the flattened down scene data in an efficient but
// un-editable hierarchy.
pub struct FlatScene {
    // cam_nodes: Vec<Box<dyn NodeCanTransformAndView3D>>,
    pub cam_ids: Vec<NodeId>,
    pub cam_sensor_widths: Vec<AttrId>,
    pub cam_sensor_heights: Vec<AttrId>,
    pub cam_focal_lengths: Vec<AttrId>,
    pub sorted_nodes: Vec<Box<dyn NodeCanTransform3D>>,
    pub sorted_node_parent_indices: Vec<Option<usize>>,
    pub sorted_node_ids: Vec<NodeId>,
    pub sorted_node_indices: Vec<PGNodeIndex>, // world_matrix_list:,
}

fn reproject_nodes(
    cam_tfm_matrix: Matrix44,
    cam_proj_matrix: Matrix44,
    tfm_matrix_list: &Vec<Matrix44>,
) -> Vec<(Real, Real)> {
    let mut point_list = Vec::new();
    for tfm_matrix in tfm_matrix_list {
        let reproj_mat =
            reproject_as_normalised_coord(cam_tfm_matrix, cam_proj_matrix, *tfm_matrix);
        // println!("reproj_mat: {:?}", reproj_mat);
        let point = (reproj_mat[0], reproj_mat[1]);
        point_list.push(point);
    }
    point_list
}

impl FlatScene {
    pub fn evaluate(
        &self,
        attrdb: &AttrDataBlock,
        cam_index: usize,
        frame: FrameValue,
        out_tfm_world_matrix_list: &mut Vec<Matrix44>,
        out_bnd_world_matrix_list: &mut Vec<Matrix44>,
        out_reproj_point_list: &mut Vec<(Real, Real)>,
    ) {
        // Calculate the bundle positions.

        // let mut world_matrix_list = Vec::new();
        // let attr_data_block = sg.attr_data_block();
        compute_world_matrices(
            &attrdb,
            &self.sorted_nodes,
            &self.sorted_node_parent_indices,
            frame,
            out_tfm_world_matrix_list,
        );
        println!("World Matrix count: {}", out_tfm_world_matrix_list.len());
        // println!("World Matrix: {:#?}", out_tfm_world_matrix_list);

        let mut cam_tfm_matrix = Matrix44::identity();
        let node_ids_and_matrix_iter = self
            .sorted_node_ids
            .iter()
            .zip(out_tfm_world_matrix_list.iter());
        for (node_id, world_matrix) in node_ids_and_matrix_iter {
            match node_id {
                NodeId::Camera(_) => cam_tfm_matrix = *world_matrix,
                NodeId::Bundle(_) => out_bnd_world_matrix_list.push(*world_matrix),
                _ => (),
            }
        }
        println!("Bundle Matrix count: {}", out_bnd_world_matrix_list.len());
        // let cam_tfm_matrix2 = compute_matrix(attr_data_block, &cam_box, frame);
        println!("Camera Transform Matrix1: {}", cam_tfm_matrix);
        // println!("Camera Transform Matrix2: {}", cam_tfm_matrix2);

        let cam_index = 0;
        let cam_sensor_width = self.cam_sensor_widths[cam_index];
        let cam_sensor_height = self.cam_sensor_heights[cam_index];
        let cam_focal_length = self.cam_focal_lengths[cam_index];
        let cam_proj_matrix = compute_projection_matrix_with_attrs(
            &attrdb,
            cam_sensor_width,
            cam_sensor_height,
            cam_focal_length,
            frame,
        );
        println!("Camera Projection Matrix: {}", cam_proj_matrix);

        let point_list =
            reproject_nodes(cam_tfm_matrix, cam_proj_matrix, &out_bnd_world_matrix_list);
        println!("Reprojected Points count: {}", point_list.len());
        println!("Reprojected Points: {:#?}", point_list);
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
