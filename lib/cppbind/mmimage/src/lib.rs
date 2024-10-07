//
// Copyright (C) 2023 David Cattermole.
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

use crate::cxxbridge::ffi::ImageExrEncoder as BindImageExrEncoder;
use crate::encoder::bind_to_core_image_exr_encoder;
use crate::imagemetadata::ShimImageMetaData;
use crate::imagepixelbuffer::ShimImagePixelBuffer;

pub mod cxxbridge;
pub mod encoder;
pub mod imagemetadata;
pub mod imagepixelbuffer;

use mmimage_rust::image_read_metadata_exr as core_image_read_metadata_exr;
use mmimage_rust::image_read_pixels_exr_f32x4 as core_image_read_pixels_exr_f32x4;
use mmimage_rust::image_write_pixels_exr_f32x4 as core_image_write_pixels_exr_f32x4;

pub fn shim_image_read_metadata_exr(
    file_path: &str,
    out_meta_data: &mut Box<ShimImageMetaData>,
) -> bool {
    // TODO: How to return errors? An enum perhaps?
    let meta_data = core_image_read_metadata_exr(file_path);
    if let Err(_err) = meta_data {
        return false;
    }
    out_meta_data.set_inner(meta_data.unwrap());
    true
}

pub fn shim_image_read_pixels_exr_f32x4(
    file_path: &str,
    vertical_flip: bool,
    out_meta_data: &mut Box<ShimImageMetaData>,
    out_pixel_buffer: &mut Box<ShimImagePixelBuffer>,
) -> bool {
    // TODO: How to return errors? An enum perhaps?
    let image = core_image_read_pixels_exr_f32x4(file_path, vertical_flip);
    if let Err(_err) = image {
        return false;
    }
    let (meta_data, pixel_buffer) = image.unwrap();
    out_meta_data.set_inner(meta_data);
    out_pixel_buffer.set_inner(pixel_buffer);
    true
}

pub fn shim_image_write_pixels_exr_f32x4(
    file_path: &str,
    exr_encoder: BindImageExrEncoder,
    in_meta_data: &Box<ShimImageMetaData>,
    in_pixel_buffer: &Box<ShimImagePixelBuffer>,
) -> bool {
    // TODO: How to return errors? An enum perhaps?
    let meta_data = in_meta_data.get_inner();
    let pixel_buffer = in_pixel_buffer.get_inner();

    let exr_encoder = bind_to_core_image_exr_encoder(exr_encoder);
    let result = core_image_write_pixels_exr_f32x4(
        file_path,
        exr_encoder,
        meta_data,
        pixel_buffer,
    );

    if let Err(_err) = result {
        return false;
    }
    true
}
