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

use crate::attr::AttrDataBlock;
use crate::attr::AttrId;
use crate::constant::FrameValue;
use crate::constant::Matrix44;
use crate::constant::MM_TO_INCH;
use crate::math::camera::get_projection_matrix;
use crate::math::transform::calculate_matrix_with_values;
use crate::math::transform::decompose_matrix;
use crate::node::traits::NodeCanTransform3D;
use crate::node::traits::NodeCanViewScene;

pub fn compute_matrix<'a, T>(
    attr_data_block: &'a AttrDataBlock,
    transform: &'a Box<T>,
    frame: FrameValue, // TODO: Assume more frames.
) -> Matrix44
where
    T: NodeCanTransform3D + ?Sized,
{
    println!("Compute Matrix!");
    let roo = transform.get_rotate_order();

    let attr_tx = transform.get_attr_tx();
    let attr_ty = transform.get_attr_ty();
    let attr_tz = transform.get_attr_tz();

    let attr_rx = transform.get_attr_rx();
    let attr_ry = transform.get_attr_ry();
    let attr_rz = transform.get_attr_rz();

    let attr_sx = transform.get_attr_sx();
    let attr_sy = transform.get_attr_sy();
    let attr_sz = transform.get_attr_sz();

    let tx = attr_data_block.get_attr_value(attr_tx, frame);
    let ty = attr_data_block.get_attr_value(attr_ty, frame);
    let tz = attr_data_block.get_attr_value(attr_tz, frame);

    let rx = attr_data_block.get_attr_value(attr_rx, frame);
    let ry = attr_data_block.get_attr_value(attr_ry, frame);
    let rz = attr_data_block.get_attr_value(attr_rz, frame);

    let sx = attr_data_block.get_attr_value(attr_sx, frame);
    let sy = attr_data_block.get_attr_value(attr_sy, frame);
    let sz = attr_data_block.get_attr_value(attr_sz, frame);

    println!("  tx: {} ty: {} tz: {}", tx, ty, tz);
    println!("  rx: {} ry: {} rz: {} roo: {:?}", rx, ry, rz, roo);
    println!("  sx: {} sy: {} sz: {}", sx, sy, sz);

    calculate_matrix_with_values(tx, ty, tz, rx, ry, rz, sx, sy, sz, roo)
}

pub fn compute_projection_matrix_with_attrs(
    attr_data_block: &AttrDataBlock,
    attr_sensor_x: AttrId,
    attr_sensor_y: AttrId,
    attr_focal: AttrId,
    frame: FrameValue, // TODO: Assume more frames.
) -> Matrix44 {
    println!("Compute Projection Matrix!");
    let sensor_x = attr_data_block.get_attr_value(attr_sensor_x, frame);
    let sensor_y = attr_data_block.get_attr_value(attr_sensor_y, frame);
    let focal = attr_data_block.get_attr_value(attr_focal, frame);

    let focal_length = focal;
    let film_back_width = sensor_x * MM_TO_INCH;
    let film_back_height = sensor_y * MM_TO_INCH;
    let film_offset_x = 0.0;
    let film_offset_y = 0.0;
    // TODO: Pass the correct image width and height.
    // let image_width = 2048.0; // 3600.0; // 960.0;
    // let image_height = 1556.0; // 2400.0; // 540.0;
    let image_width = sensor_x * 1000.0;
    let image_height = sensor_y * 1000.0;
    let film_fit = 1; // 1 = horizontal
    let near_clip_plane = 0.1;
    let far_clip_plane = 10000.0;
    let camera_scale = 1.0;

    get_projection_matrix(
        focal_length,
        film_back_width,
        film_back_height,
        film_offset_x,
        film_offset_y,
        image_width,
        image_height,
        film_fit,
        near_clip_plane,
        far_clip_plane,
        camera_scale,
    )
}

pub fn compute_projection_matrix<'a, T>(
    attr_data_block: &'a AttrDataBlock,
    transform: &'a Box<T>,
    frame: FrameValue, // TODO: Assume more frames.
) -> Matrix44
where
    T: NodeCanViewScene + ?Sized,
{
    println!("Compute Projection Matrix!");
    let attr_sensor_x = transform.get_attr_sensor_width();
    let attr_sensor_y = transform.get_attr_sensor_height();
    let attr_focal = transform.get_attr_focal_length();

    let sensor_x = attr_data_block.get_attr_value(attr_sensor_x, frame);
    let sensor_y = attr_data_block.get_attr_value(attr_sensor_y, frame);
    let focal = attr_data_block.get_attr_value(attr_focal, frame);

    let focal_length = focal;
    let film_back_width = sensor_x * MM_TO_INCH;
    let film_back_height = sensor_y * MM_TO_INCH;
    let film_offset_x = 0.0;
    let film_offset_y = 0.0;
    // TODO: Pass the correct image width and height.
    let image_width = sensor_x * 1000.0;
    let image_height = sensor_y * 1000.0;
    let film_fit = 1; // 1 = horizontal
    let near_clip_plane = 0.1;
    let far_clip_plane = 10000.0;
    let camera_scale = 1.0;

    get_projection_matrix(
        focal_length,
        film_back_width,
        film_back_height,
        film_offset_x,
        film_offset_y,
        image_width,
        image_height,
        film_fit,
        near_clip_plane,
        far_clip_plane,
        camera_scale,
    )
}

pub fn compute_matrices<'a>(
    attr_data_block: &'a AttrDataBlock,
    transforms: &'a Vec<Box<dyn NodeCanTransform3D>>,
    frame: FrameValue, // TODO: Assume more frames.
    out_matrix_list: &'a mut Vec<Matrix44>,
) {
    println!("Compute DAG Matrices!");
    let num_frames = 1; // TODO: Update this.
    out_matrix_list.clear();
    out_matrix_list.reserve(transforms.len() * num_frames);

    // Compute local Matrix
    for i in 0..transforms.len() {
        println!("i: {}", i);

        let matrix = compute_matrix(attr_data_block, &transforms[i], frame);
        println!("matrix: {}", matrix);
        out_matrix_list.push(matrix);
    }
}

pub fn compute_world_matrices<'a>(
    attr_data_block: &'a AttrDataBlock,
    transforms: &'a Vec<Box<dyn NodeCanTransform3D>>,
    transform_parents: &'a Vec<Option<usize>>,
    frame: FrameValue, // TODO: Assume more frames.
    out_matrix_list: &'a mut Vec<Matrix44>,
) {
    println!("Compute World Matrices!");
    assert!(transforms.len() == transform_parents.len());
    let num_frames = 1; // TODO: Update this.
    out_matrix_list.clear();
    out_matrix_list.reserve(transforms.len() * num_frames);

    for i in 0..transforms.len() {
        let tfm = &transforms[i];
        println!("compute_world_matrices i: {} id: {:?}", i, tfm.get_id());

        let local_matrix = compute_matrix(attr_data_block, tfm, frame);
        println!("  local_matrix {}: {}", i, local_matrix);

        let world_matrix = match transform_parents[i] {
            Some(parent_index) => {
                assert!(parent_index < i);
                let parent_world_matrix = out_matrix_list[parent_index];
                println!(
                    "  parent_world_matrix {}: {}",
                    parent_index, parent_world_matrix
                );

                let proo = tfm.get_rotate_order();
                let (ptx, pty, ptz, prx, pry, prz, psx, psy, psz) =
                    decompose_matrix(parent_world_matrix, proo);
                println!("  ptx: {} pty: {} ptz: {}", ptx, pty, ptz);
                println!("  prx: {} pry: {} prz: {} proo: {:?}", prx, pry, prz, proo);
                println!("  psx: {} psy: {} psz: {}", psx, psy, psz);

                parent_world_matrix * local_matrix
            }
            // node has no parent, so just use the local matrix.
            None => local_matrix,
        };

        let wroo = tfm.get_rotate_order();
        let (wtx, wty, wtz, wrx, wry, wrz, wsx, wsy, wsz) = decompose_matrix(world_matrix, wroo);
        println!("  wtx: {} wty: {} wtz: {}", wtx, wty, wtz);
        println!("  wrx: {} wry: {} wrz: {} wroo: {:?}", wrx, wry, wrz, wroo);
        println!("  wsx: {} wsy: {} wsz: {}", wsx, wsy, wsz);

        out_matrix_list.push(world_matrix);
        println!("------------------------------------------------");
    }
}
