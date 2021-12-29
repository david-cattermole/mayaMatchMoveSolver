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

use crate::attr::datablock::AttrDataBlock;
use crate::attr::AttrCameraIds;
use crate::attr::AttrMarkerIds;
use crate::attr::AttrTransformIds;
use crate::constant::FrameValue;
use crate::constant::Matrix44;
use crate::constant::Real;
use crate::math::dag::compute_projection_matrix_with_attrs;
use crate::math::dag::compute_world_matrices_with_attrs;
use crate::math::reprojection::reproject_as_normalised_coord;
use crate::math::rotate::euler::RotateOrder;
use crate::node::NodeId;

/// flattened scene data with an un-editable hierarchy.
pub struct FlatScene {
    // The node ids for bundles and cameras. These can be used to look
    // up and filter data.
    pub bnd_ids: Vec<NodeId>,
    pub cam_ids: Vec<NodeId>,
    pub mkr_ids: Vec<NodeId>,

    // Marker links to cameras and bundles.
    pub mkr_cam_indices: Vec<usize>,
    pub mkr_bnd_indices: Vec<usize>,

    // Attributes and data to use during reprojection.
    pub tfm_attr_list: Vec<AttrTransformIds>,
    pub rotate_order_list: Vec<RotateOrder>,
    pub cam_attr_list: Vec<AttrCameraIds>,
    pub mkr_attr_list: Vec<AttrMarkerIds>,

    // The transform metadata for the nodes.
    pub tfm_node_parent_indices: Vec<Option<usize>>,
    pub tfm_node_ids: Vec<NodeId>,
    pub tfm_node_indices: Vec<PGNodeIndex>,
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
        out_deviation_list: &mut Vec<(Real, Real)>,
    ) {
        // println!("EVALUATE! =================================================");
        let num_frames = frame_list.len();
        let num_bundles = self.bnd_ids.len();
        let num_cameras = self.cam_ids.len();
        let num_markers = self.mkr_ids.len();
        let num_transforms = self.tfm_node_ids.len();
        // println!("camera count: {}", num_cameras);
        // println!("bundle count: {}", num_bundles);
        // println!("frame count: {}", num_frames);
        // println!("frames: {:?}", frame_list);
        assert!(num_frames > 0);
        assert!(num_cameras > 0);
        assert!(num_bundles > 0);
        assert!(num_markers > 0);
        assert!(num_transforms > 0);

        out_tfm_world_matrix_list.clear();
        out_bnd_world_matrix_list.clear();
        out_cam_world_matrix_list.clear();
        out_tfm_world_matrix_list.reserve(num_transforms * num_frames);
        out_bnd_world_matrix_list.reserve(num_bundles * num_frames);
        out_cam_world_matrix_list.reserve(num_cameras * num_frames);

        compute_world_matrices_with_attrs(
            &attrdb,
            &self.tfm_attr_list,
            &self.rotate_order_list,
            &self.tfm_node_parent_indices,
            frame_list,
            out_tfm_world_matrix_list,
        );
        // println!("World Matrix count: {}", out_tfm_world_matrix_list.len());
        // println!("World Matrix: {:#?}", out_tfm_world_matrix_list);

        for (i, node_id) in (0..).zip(self.tfm_node_ids.iter()) {
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
        // println!("Camera Matrix count: {}", out_cam_world_matrix_list.len());

        assert!(out_cam_world_matrix_list.len() == (num_cameras * num_frames));
        out_point_list.clear();
        out_deviation_list.clear();
        out_point_list.reserve(num_markers * num_frames);
        out_deviation_list.reserve(num_markers * num_frames);

        let cam_attrs_iter = (0..).zip(self.cam_attr_list.iter());
        for (i, cam_attrs) in cam_attrs_iter {
            let cam_sensor_width = cam_attrs.sensor_width;
            let cam_sensor_height = cam_attrs.sensor_height;
            let cam_focal_length = cam_attrs.focal_length;

            let mkr_attrs_iter = (0..).zip(self.mkr_attr_list.iter());
            for (mkr_index, mkr_attrs) in mkr_attrs_iter {
                let cam_index = self.mkr_cam_indices[mkr_index];
                if cam_index != i {
                    continue;
                }
                let bnd_index = self.mkr_bnd_indices[mkr_index];

                for (f, frame) in (0..).zip(frame_list) {
                    let frame = *frame;
                    let cam_index_at_frame = (i * num_frames) + f;
                    let bnd_index_at_frame = (bnd_index * num_frames) + f;
                    let bnd_matrix = out_bnd_world_matrix_list[bnd_index_at_frame];
                    let cam_tfm_matrix = out_cam_world_matrix_list[cam_index_at_frame];
                    let cam_proj_matrix = compute_projection_matrix_with_attrs(
                        &attrdb,
                        cam_sensor_width,
                        cam_sensor_height,
                        cam_focal_length,
                        frame,
                    );
                    // println!("Camera Transform Matrix: {}", cam_tfm_matrix);
                    // println!("Camera Projection Matrix: {}", cam_proj_matrix);

                    let reproj_mat =
                        reproject_as_normalised_coord(cam_tfm_matrix, cam_proj_matrix, bnd_matrix);
                    let point = (reproj_mat[0], reproj_mat[1]);
                    out_point_list.push(point);

                    let mkr_tx = attrdb.get_attr_value(mkr_attrs.tx, frame);
                    let mkr_ty = attrdb.get_attr_value(mkr_attrs.ty, frame);

                    // // TODO: Use marker weight?
                    // let mkr_weight = attr_data_block.get_attr_value(mkr_attr.weight, frame);

                    let dev_x = mkr_tx - reproj_mat[0];
                    let dev_y = mkr_ty - reproj_mat[1];
                    out_deviation_list.push((dev_x, dev_y));
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
