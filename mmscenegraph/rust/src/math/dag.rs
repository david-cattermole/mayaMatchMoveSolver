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

use crate::attr::datablock::AttrDataBlock;
use crate::attr::AttrId;
use crate::attr::AttrTransformIds;
use crate::constant::FrameValue;
use crate::constant::Matrix44;
use crate::constant::Real;
use crate::constant::MM_TO_INCH;
use crate::math::camera::get_projection_matrix;
use crate::math::camera::FilmFit;
use crate::math::rotate::euler::RotateOrder;
use crate::math::transform::calculate_matrix_with_values;
// use crate::math::transform::decompose_matrix;
use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeCanViewScene;

pub fn compute_matrix_with_attrs(
    attr_data_block: &AttrDataBlock,
    attr_tx: AttrId,
    attr_ty: AttrId,
    attr_tz: AttrId,
    attr_rx: AttrId,
    attr_ry: AttrId,
    attr_rz: AttrId,
    attr_sx: AttrId,
    attr_sy: AttrId,
    attr_sz: AttrId,
    rotate_order: RotateOrder,
    frame: FrameValue,
) -> Matrix44 {
    // println!("Compute Matrix With Attrs!");
    let tx = attr_data_block.get_attr_value(attr_tx, frame);
    let ty = attr_data_block.get_attr_value(attr_ty, frame);
    let tz = attr_data_block.get_attr_value(attr_tz, frame);

    let rx = attr_data_block.get_attr_value(attr_rx, frame);
    let ry = attr_data_block.get_attr_value(attr_ry, frame);
    let rz = attr_data_block.get_attr_value(attr_rz, frame);

    let sx = attr_data_block.get_attr_value(attr_sx, frame);
    let sy = attr_data_block.get_attr_value(attr_sy, frame);
    let sz = attr_data_block.get_attr_value(attr_sz, frame);

    // println!("  tx: {} ty: {} tz: {}", tx, ty, tz);
    // println!("  rx: {} ry: {} rz: {} roo: {:?}", rx, ry, rz, rotate_order);
    // println!("  sx: {} sy: {} sz: {}", sx, sy, sz);

    calculate_matrix_with_values(
        tx,
        ty,
        tz,
        rx,
        ry,
        rz,
        sx,
        sy,
        sz,
        rotate_order,
    )
}

pub fn compute_matrix<T>(
    attr_data_block: &AttrDataBlock,
    transform: &Box<T>,
    frame: FrameValue,
) -> Matrix44
where
    T: ?Sized + NodeCanTransform3D,
{
    // println!("Compute Matrix!");
    let attr_tx = transform.get_attr_tx();
    let attr_ty = transform.get_attr_ty();
    let attr_tz = transform.get_attr_tz();

    let attr_rx = transform.get_attr_rx();
    let attr_ry = transform.get_attr_ry();
    let attr_rz = transform.get_attr_rz();

    let attr_sx = transform.get_attr_sx();
    let attr_sy = transform.get_attr_sy();
    let attr_sz = transform.get_attr_sz();

    let rotate_order = transform.get_rotate_order();

    compute_matrix_with_attrs(
        attr_data_block,
        attr_tx,
        attr_ty,
        attr_tz,
        attr_rx,
        attr_ry,
        attr_rz,
        attr_sx,
        attr_sy,
        attr_sz,
        rotate_order,
        frame,
    )
}

pub fn compute_projection_matrix_with_attrs(
    attr_data_block: &AttrDataBlock,
    attr_sensor_x: AttrId,
    attr_sensor_y: AttrId,
    attr_focal: AttrId,
    attr_lens_offset_x: AttrId,
    attr_lens_offset_y: AttrId,
    attr_near_clip_plane: AttrId,
    attr_far_clip_plane: AttrId,
    attr_camera_scale: AttrId,
    film_fit: FilmFit,
    render_image_width: i32,
    render_image_height: i32,
    frame: FrameValue,
) -> Matrix44 {
    // println!("Compute Projection Matrix!");
    let focal_length = attr_data_block.get_attr_value(attr_focal, frame);

    let sensor_x = attr_data_block.get_attr_value(attr_sensor_x, frame);
    let sensor_y = attr_data_block.get_attr_value(attr_sensor_y, frame);
    let sensor_x = sensor_x * MM_TO_INCH;
    let sensor_y = sensor_y * MM_TO_INCH;

    let lens_offset_x =
        attr_data_block.get_attr_value(attr_lens_offset_x, frame);
    let lens_offset_y =
        attr_data_block.get_attr_value(attr_lens_offset_y, frame);
    let lens_offset_x = lens_offset_x * MM_TO_INCH;
    let lens_offset_y = lens_offset_y * MM_TO_INCH;

    let near_clip_plane =
        attr_data_block.get_attr_value(attr_near_clip_plane, frame);
    let far_clip_plane =
        attr_data_block.get_attr_value(attr_far_clip_plane, frame);
    let camera_scale = attr_data_block.get_attr_value(attr_camera_scale, frame);

    get_projection_matrix(
        focal_length,
        sensor_x,
        sensor_y,
        lens_offset_x,
        lens_offset_y,
        render_image_width as Real,
        render_image_height as Real,
        film_fit,
        near_clip_plane,
        far_clip_plane,
        camera_scale,
    )
}

pub fn compute_projection_matrix<'a, T>(
    attr_data_block: &'a AttrDataBlock,
    camera: &'a Box<T>,
    frame: FrameValue,
) -> Matrix44
where
    T: NodeCanViewScene + ?Sized,
{
    // println!("Compute Projection Matrix!");
    let attr_sensor_x = camera.get_attr_sensor_width();
    let attr_sensor_y = camera.get_attr_sensor_height();
    let attr_focal = camera.get_attr_focal_length();
    let attr_lens_offset_x = camera.get_attr_lens_offset_x();
    let attr_lens_offset_y = camera.get_attr_lens_offset_y();
    let attr_near_clip_plane = camera.get_attr_near_clip_plane();
    let attr_far_clip_plane = camera.get_attr_far_clip_plane();
    let attr_camera_scale = camera.get_attr_camera_scale();

    // Constants per-camera.
    let film_fit = camera.get_film_fit();
    let render_image_width = camera.get_render_image_width();
    let render_image_height = camera.get_render_image_height();

    compute_projection_matrix_with_attrs(
        attr_data_block,
        attr_sensor_x,
        attr_sensor_y,
        attr_focal,
        attr_lens_offset_x,
        attr_lens_offset_y,
        attr_near_clip_plane,
        attr_far_clip_plane,
        attr_camera_scale,
        film_fit,
        render_image_width,
        render_image_height,
        frame,
    )
}

pub fn compute_matrices<'a>(
    attr_data_block: &'a AttrDataBlock,
    transforms: &'a Vec<Box<dyn NodeCanTransform3D>>,
    frame: FrameValue,
    out_matrix_list: &'a mut Vec<Matrix44>,
) {
    // println!("Compute DAG Matrices!");
    out_matrix_list.clear();
    out_matrix_list.reserve(transforms.len());

    // Compute local Matrix
    for i in 0..transforms.len() {
        // println!("i: {}", i);

        let matrix = compute_matrix(attr_data_block, &transforms[i], frame);
        // println!("matrix: {}", matrix);
        out_matrix_list.push(matrix);
    }
}

pub fn compute_world_matrices_with_attrs(
    attr_data_block: &AttrDataBlock,
    tfm_attr_list: &Vec<AttrTransformIds>,
    rotate_order_list: &Vec<RotateOrder>,
    transform_parents: &Vec<Option<usize>>,
    frame_list: &[FrameValue],
    out_matrix_list: &mut Vec<Matrix44>,
) {
    // println!("Compute World Matrices!");
    let transform_num = transform_parents.len();
    let num_frames = frame_list.len();

    // println!("transform_num: {}", transform_num);
    // println!("num_frames: {}", num_frames);
    // println!("tfm_attr_list.len(): {}", tfm_attr_list.len());
    assert!(tfm_attr_list.len() == transform_num);
    assert!(rotate_order_list.len() == transform_num);

    out_matrix_list.clear();
    out_matrix_list.reserve(transform_num * num_frames);

    for (i, (tfm_attrs, rotate_order)) in
        (0..).zip(tfm_attr_list.iter().zip(rotate_order_list.iter()))
    {
        // println!("compute_world_matrices i: {}", i);
        let rotate_order = *rotate_order;

        let attr_tx = tfm_attrs.tx;
        let attr_ty = tfm_attrs.ty;
        let attr_tz = tfm_attrs.tz;

        let attr_rx = tfm_attrs.rx;
        let attr_ry = tfm_attrs.ry;
        let attr_rz = tfm_attrs.rz;

        let attr_sx = tfm_attrs.sx;
        let attr_sy = tfm_attrs.sy;
        let attr_sz = tfm_attrs.sz;

        for (f, frame) in (0..).zip(frame_list) {
            let frame = *frame;

            let local_matrix = compute_matrix_with_attrs(
                attr_data_block,
                attr_tx,
                attr_ty,
                attr_tz,
                attr_rx,
                attr_ry,
                attr_rz,
                attr_sx,
                attr_sy,
                attr_sz,
                rotate_order,
                frame,
            );
            // println!("  local_matrix {} at {}: {}", i, f, local_matrix);

            let world_matrix = match transform_parents[i] {
                Some(parent_index) => {
                    assert!(parent_index < i);
                    let parent_index_at_frame = (parent_index * num_frames) + f;
                    let parent_world_matrix =
                        out_matrix_list[parent_index_at_frame];
                    // println!(
                    //     "  parent_world_matrix {} at {}: {}",
                    //     parent_index, f, parent_world_matrix
                    // );

                    // let proo = rotate_order;
                    // let (ptx, pty, ptz, prx, pry, prz, psx, psy, psz) =
                    //     decompose_matrix(parent_world_matrix, proo);
                    // println!("  ptx: {} pty: {} ptz: {}", ptx, pty, ptz);
                    // println!("  prx: {} pry: {} prz: {} proo: {:?}", prx, pry, prz, proo);
                    // println!("  psx: {} psy: {} psz: {}", psx, psy, psz);

                    parent_world_matrix * local_matrix
                }
                // node has no parent, so just use the local matrix.
                None => local_matrix,
            };

            // let wroo = rotate_order;
            // let (wtx, wty, wtz, wrx, wry, wrz, wsx, wsy, wsz) =
            //     decompose_matrix(world_matrix, wroo);
            // println!("  wtx: {} wty: {} wtz: {}", wtx, wty, wtz);
            // println!("  wrx: {} wry: {} wrz: {} wroo: {:?}", wrx, wry, wrz, wroo);
            // println!("  wsx: {} wsy: {} wsz: {}", wsx, wsy, wsz);

            out_matrix_list.push(world_matrix);
        }
        // println!("------------------------------------------------");
    }
}

pub fn compute_world_matrices(
    attr_data_block: &AttrDataBlock,
    transforms: &Vec<Box<dyn NodeCanTransform3D>>,
    transform_parents: &Vec<Option<usize>>,
    frame: FrameValue,
    out_matrix_list: &mut Vec<Matrix44>,
) {
    // println!("Compute World Matrices!");
    assert!(transforms.len() == transform_parents.len());
    out_matrix_list.clear();
    out_matrix_list.reserve(transforms.len());

    for i in 0..transforms.len() {
        let tfm = &transforms[i];
        // println!("compute_world_matrices i: {} id: {:?}", i, tfm.get_id());

        let local_matrix = compute_matrix(attr_data_block, tfm, frame);
        // println!("  local_matrix {}: {}", i, local_matrix);

        let world_matrix = match transform_parents[i] {
            Some(parent_index) => {
                assert!(parent_index < i);
                let parent_world_matrix = out_matrix_list[parent_index];
                // println!(
                //     "  parent_world_matrix {}: {}",
                //     parent_index, parent_world_matrix
                // );

                // let proo = tfm.get_rotate_order();
                // let (ptx, pty, ptz, prx, pry, prz, psx, psy, psz) =
                //     decompose_matrix(parent_world_matrix, proo);
                // println!("  ptx: {} pty: {} ptz: {}", ptx, pty, ptz);
                // println!("  prx: {} pry: {} prz: {} proo: {:?}", prx, pry, prz, proo);
                // println!("  psx: {} psy: {} psz: {}", psx, psy, psz);

                parent_world_matrix * local_matrix
            }
            // node has no parent, so just use the local matrix.
            None => local_matrix,
        };

        // let wroo = tfm.get_rotate_order();
        // let (wtx, wty, wtz, wrx, wry, wrz, wsx, wsy, wsz) = decompose_matrix(world_matrix, wroo);
        // println!("  wtx: {} wty: {} wtz: {}", wtx, wty, wtz);
        // println!("  wrx: {} wry: {} wrz: {} wroo: {:?}", wrx, wry, wrz, wroo);
        // println!("  wsx: {} wsy: {} wsz: {}", wsx, wsy, wsz);

        out_matrix_list.push(world_matrix);
        // println!("------------------------------------------------");
    }
}
