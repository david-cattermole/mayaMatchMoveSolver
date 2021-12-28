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

use crate::attr::AttrCameraIds;
use crate::attr::AttrDataBlock;
use crate::attr::AttrTransformIds;
use crate::constant::FrameValue;
use crate::constant::Matrix44;
use crate::constant::Real;
use crate::math::dag::compute_projection_matrix_with_attrs;
use crate::math::dag::compute_world_matrices_with_attrs;
use crate::math::reprojection::reproject_as_normalised_coord;
use crate::math::rotate::euler::RotateOrder;
use crate::node::traits::NodeCanTransform3D;
use crate::node::NodeId;

// flattened scene data with an un-editable hierarchy.
pub struct FlatScene {
    pub bnd_ids: Vec<NodeId>,
    pub tfm_attr_list: Vec<AttrTransformIds>,
    pub rotate_order_list: Vec<RotateOrder>,
    pub cam_ids: Vec<NodeId>,
    pub cam_attr_list: Vec<AttrCameraIds>,
    pub sorted_nodes: Vec<Box<dyn NodeCanTransform3D>>,
    pub sorted_node_parent_indices: Vec<Option<usize>>,
    pub sorted_node_ids: Vec<NodeId>,
    pub sorted_node_indices: Vec<PGNodeIndex>,
}

impl FlatScene {
    pub fn evaluate(
        &self,
        attrdb: &AttrDataBlock,
        frame_list: &Vec<FrameValue>,
        out_tfm_world_matrix_list: &mut Vec<Matrix44>,
        out_bnd_world_matrix_list: &mut Vec<Matrix44>,
        out_cam_world_matrix_list: &mut Vec<Matrix44>,
        out_point_list: &mut Vec<(Real, Real)>,
    ) {
        // println!("EVALUATE! =================================================");
        let num_frames = frame_list.len();
        let num_bundles = self.bnd_ids.len();
        let num_cameras = self.cam_ids.len();
        // println!("camera count: {}", num_cameras);
        // println!("bundle count: {}", num_bundles);
        // println!("frame count: {}", num_frames);
        // println!("frames: {:?}", frame_list);
        assert!(num_frames > 0);

        out_tfm_world_matrix_list.clear();
        out_bnd_world_matrix_list.clear();
        out_cam_world_matrix_list.clear();
        out_tfm_world_matrix_list.reserve(self.sorted_node_ids.len() * num_frames);
        out_bnd_world_matrix_list.reserve(num_bundles * num_frames);
        out_cam_world_matrix_list.reserve(num_cameras * num_frames);

        compute_world_matrices_with_attrs(
            &attrdb,
            &self.tfm_attr_list,
            &self.rotate_order_list,
            &self.sorted_node_parent_indices,
            frame_list,
            out_tfm_world_matrix_list,
        );
        // println!("World Matrix count: {}", out_tfm_world_matrix_list.len());
        // println!("World Matrix: {:#?}", out_tfm_world_matrix_list);

        for (i, node_id) in (0..).zip(self.sorted_node_ids.iter()) {
            match node_id {
                NodeId::Camera(_) => {
                    // println!("Camera node: {:?}", node_id);
                    for f in 0..num_frames {
                        let index_at_frame = (i * num_frames) + f;
                        let world_matrix = out_tfm_world_matrix_list[index_at_frame];
                        out_cam_world_matrix_list.push(world_matrix);
                    }
                }
                NodeId::Bundle(_) => {
                    // println!("Bundle node: {:?}", node_id);
                    for f in 0..num_frames {
                        let index_at_frame = (i * num_frames) + f;
                        let world_matrix = out_tfm_world_matrix_list[index_at_frame];
                        out_bnd_world_matrix_list.push(world_matrix)
                    }
                }
                _ => (),
            }
        }
        // println!("Bundle Matrix count: {}", out_bnd_world_matrix_list.len());

        assert!(out_cam_world_matrix_list.len() == (num_cameras * num_frames));
        out_point_list.clear();
        out_point_list.reserve(self.bnd_ids.len() * num_frames);
        let cam_attrs_iter = (0..).zip(self.cam_attr_list.iter());
        for (i, cam_attrs) in cam_attrs_iter {
            let cam_sensor_width = cam_attrs.sensor_width;
            let cam_sensor_height = cam_attrs.sensor_height;
            let cam_focal_length = cam_attrs.focal_length;
            for bnd_index in 0..num_bundles {
                for (f, frame) in (0..).zip(frame_list) {
                    let cam_index_at_frame = (i * num_frames) + f;
                    let bnd_index_at_frame = (bnd_index * num_frames) + f;
                    let bnd_matrix = out_bnd_world_matrix_list[bnd_index_at_frame];
                    let cam_tfm_matrix = out_cam_world_matrix_list[cam_index_at_frame];
                    let cam_proj_matrix = compute_projection_matrix_with_attrs(
                        &attrdb,
                        cam_sensor_width,
                        cam_sensor_height,
                        cam_focal_length,
                        *frame,
                    );
                    // println!("Camera Transform Matrix: {}", cam_tfm_matrix);
                    // println!("Camera Projection Matrix: {}", cam_proj_matrix);

                    let reproj_mat =
                        reproject_as_normalised_coord(cam_tfm_matrix, cam_proj_matrix, bnd_matrix);
                    let point = (reproj_mat[0], reproj_mat[1]);
                    out_point_list.push(point);
                }
            }
        }
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
