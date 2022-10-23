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
use crate::math::camera::FilmFit;
use crate::math::dag::compute_projection_matrix_with_attrs;
use crate::math::dag::compute_world_matrices_with_attrs;
use crate::math::reprojection::reproject_as_normalised_coord;
use crate::math::rotate::euler::RotateOrder;
use crate::node::NodeId;

const NUM_VALUES_PER_POINT: usize = 2;
const NUM_VALUES_PER_MARKER: usize = 2;

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
    pub cam_film_fit_list: Vec<FilmFit>,
    pub cam_render_res_list: Vec<(i32, i32)>,
    pub mkr_attr_list: Vec<AttrMarkerIds>,

    // The transform metadata for the nodes.
    pub tfm_node_ids: Vec<NodeId>,
    pub tfm_node_indices: Vec<PGNodeIndex>,
    pub tfm_node_parent_indices: Vec<Option<usize>>,

    // The computed data is stored here for access by the user.
    out_tfm_world_matrix_list: Vec<Matrix44>,
    out_bnd_world_matrix_list: Vec<Matrix44>,
    out_cam_world_matrix_list: Vec<Matrix44>,
    out_marker_list: Vec<Real>,
    out_point_list: Vec<Real>,
}

impl FlatScene {
    pub fn new(
        bnd_ids: Vec<NodeId>,
        cam_ids: Vec<NodeId>,
        mkr_ids: Vec<NodeId>,

        mkr_cam_indices: Vec<usize>,
        mkr_bnd_indices: Vec<usize>,

        tfm_attr_list: Vec<AttrTransformIds>,
        rotate_order_list: Vec<RotateOrder>,
        cam_attr_list: Vec<AttrCameraIds>,
        cam_film_fit_list: Vec<FilmFit>,
        cam_render_res_list: Vec<(i32, i32)>,
        mkr_attr_list: Vec<AttrMarkerIds>,

        tfm_node_ids: Vec<NodeId>,
        tfm_node_indices: Vec<PGNodeIndex>,
        tfm_node_parent_indices: Vec<Option<usize>>,
    ) -> Self {
        Self {
            bnd_ids,
            cam_ids,
            mkr_ids,

            mkr_cam_indices,
            mkr_bnd_indices,

            tfm_attr_list,
            rotate_order_list,
            cam_attr_list,
            cam_film_fit_list,
            cam_render_res_list,
            mkr_attr_list,

            tfm_node_ids,
            tfm_node_indices,
            tfm_node_parent_indices,

            out_tfm_world_matrix_list: Vec::new(),
            out_bnd_world_matrix_list: Vec::new(),
            out_cam_world_matrix_list: Vec::new(),
            out_marker_list: Vec::new(),
            out_point_list: Vec::new(),
        }
    }

    pub fn markers(&self) -> &[Real] {
        &self.out_marker_list[..]
    }

    pub fn points(&self) -> &[Real] {
        &self.out_point_list[..]
    }

    pub fn num_markers(&self) -> usize {
        let len = self.out_marker_list.len();
        if len > 0 {
            len / NUM_VALUES_PER_MARKER
        } else {
            0
        }
    }

    pub fn num_points(&self) -> usize {
        let len = self.out_point_list.len();
        if len > 0 {
            len / NUM_VALUES_PER_POINT
        } else {
            0
        }
    }

    pub fn evaluate(
        &mut self,
        attrdb: &AttrDataBlock,
        frame_list: &[FrameValue],
    ) {
        // println!("EVALUATE! ==============================================");
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

        let num_total_bundles = num_bundles * num_frames;
        let num_total_cameras = num_cameras * num_frames;
        let _num_total_transforms = num_transforms * num_frames;

        self.out_bnd_world_matrix_list = Vec::with_capacity(num_total_bundles);
        self.out_cam_world_matrix_list = Vec::with_capacity(num_total_cameras);
        self.out_bnd_world_matrix_list
            .resize(num_total_bundles, Matrix44::identity());
        self.out_cam_world_matrix_list
            .resize(num_total_cameras, Matrix44::identity());

        compute_world_matrices_with_attrs(
            &attrdb,
            &self.tfm_attr_list,
            &self.rotate_order_list,
            &self.tfm_node_parent_indices,
            frame_list,
            &mut self.out_tfm_world_matrix_list,
        );
        // println!(
        //     "World Matrix count: {}",
        //     self.out_tfm_world_matrix_list.len()
        // );
        // println!("World Matrix: {:#?}", self.out_tfm_world_matrix_list);

        for (i, node_id) in (0..).zip(self.tfm_node_ids.iter()) {
            match node_id {
                NodeId::Camera(index) => {
                    // println!("Camera node: {:?} index: {}", node_id, index);
                    for f in 0..num_frames {
                        let i_at_frame = (i * num_frames) + f;
                        let index_at_frame = (*index as usize * num_frames) + f;

                        let world_matrix =
                            self.out_tfm_world_matrix_list[i_at_frame];
                        self.out_cam_world_matrix_list[index_at_frame] =
                            world_matrix;
                    }
                }
                NodeId::Bundle(index) => {
                    // println!("Bundle node: {:?} index: {}", node_id, index);
                    for f in 0..num_frames {
                        let i_at_frame = (i * num_frames) + f;
                        let index_at_frame = (*index as usize * num_frames) + f;
                        let world_matrix =
                            self.out_tfm_world_matrix_list[i_at_frame];
                        self.out_bnd_world_matrix_list[index_at_frame] =
                            world_matrix;
                    }
                }
                _ => (),
            }
        }
        // println!(
        //     "Bundle Matrix count: {}",
        //     self.out_bnd_world_matrix_list.len()
        // );
        // println!(
        //     "Camera Matrix count: {}",
        //     self.out_cam_world_matrix_list.len()
        // );

        assert!(self.out_cam_world_matrix_list.len() == num_total_cameras);
        self.out_marker_list.clear();
        self.out_point_list.clear();
        self.out_marker_list
            .reserve(num_markers * NUM_VALUES_PER_MARKER * num_frames);
        self.out_point_list
            .reserve(num_markers * NUM_VALUES_PER_POINT * num_frames);

        let cam_attrs_iter = (0..).zip(
            self.cam_attr_list.iter().zip(
                self.cam_film_fit_list
                    .iter()
                    .zip(self.cam_render_res_list.iter()),
            ),
        );

        for (
            i,
            (cam_attrs, (cam_film_fit, (cam_render_width, cam_render_height))),
        ) in cam_attrs_iter
        {
            let attr_cam_sensor_width = cam_attrs.sensor_width;
            let attr_cam_sensor_height = cam_attrs.sensor_height;
            let attr_cam_focal_length = cam_attrs.focal_length;
            let attr_cam_lens_offset_x = cam_attrs.lens_offset_x;
            let attr_cam_lens_offset_y = cam_attrs.lens_offset_y;
            let attr_cam_near_clip_plane = cam_attrs.near_clip_plane;
            let attr_cam_far_clip_plane = cam_attrs.far_clip_plane;
            let attr_cam_camera_scale = cam_attrs.camera_scale;

            let mkr_attrs_iter = (0..).zip(self.mkr_attr_list.iter());
            for (mkr_index, mkr_attrs) in mkr_attrs_iter {
                let cam_index = self.mkr_cam_indices[mkr_index];
                if cam_index != i {
                    continue;
                }
                let bnd_index = self.mkr_bnd_indices[mkr_index];

                for (f, frame) in (0..).zip(frame_list) {
                    let frame = *frame;
                    let cam_index_at_frame = (cam_index * num_frames) + f;
                    let bnd_index_at_frame = (bnd_index * num_frames) + f;
                    let bnd_matrix =
                        self.out_bnd_world_matrix_list[bnd_index_at_frame];
                    let cam_tfm_matrix =
                        self.out_cam_world_matrix_list[cam_index_at_frame];
                    let cam_proj_matrix = compute_projection_matrix_with_attrs(
                        &attrdb,
                        attr_cam_sensor_width,
                        attr_cam_sensor_height,
                        attr_cam_focal_length,
                        attr_cam_lens_offset_x,
                        attr_cam_lens_offset_y,
                        attr_cam_near_clip_plane,
                        attr_cam_far_clip_plane,
                        attr_cam_camera_scale,
                        *cam_film_fit,
                        *cam_render_width,
                        *cam_render_height,
                        frame,
                    );
                    // println!("Camera Transform Matrix: {}", cam_tfm_matrix);
                    // println!("Camera Projection Matrix: {}", cam_proj_matrix);

                    let reproj_mat = reproject_as_normalised_coord(
                        cam_tfm_matrix,
                        cam_proj_matrix,
                        bnd_matrix,
                    );
                    self.out_point_list.push(reproj_mat[0]);
                    self.out_point_list.push(reproj_mat[1]);

                    // Scale the Marker Y for deviation calculation.
                    let cam_sensor_width =
                        attrdb.get_attr_value(attr_cam_sensor_width, frame);
                    let cam_sensor_height =
                        attrdb.get_attr_value(attr_cam_sensor_height, frame);
                    let sensor_aspect = cam_sensor_width / cam_sensor_height;
                    let render_aspect = (*cam_render_width as Real)
                        / (*cam_render_height as Real);
                    let aspect = render_aspect / sensor_aspect;

                    let mkr_tx = attrdb.get_attr_value(mkr_attrs.tx, frame);
                    let mkr_ty = attrdb.get_attr_value(mkr_attrs.ty, frame);
                    let mkr_ty = mkr_ty * aspect;
                    self.out_marker_list.push(mkr_tx);
                    self.out_marker_list.push(mkr_ty);

                    // // TODO: Use marker weight?
                    // let mkr_weight = attr_data_block.get_attr_value(mkr_attr.weight, frame);

                    // TODO: Compute the dot product of the camera
                    // forward vector and the direction to the bundle.
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
