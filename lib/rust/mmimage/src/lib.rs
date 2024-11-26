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

use crate::encoder::ImageExrEncoder;
use crate::metadata::ImageMetaData;
use crate::pixelbuffer::ImagePixelBuffer;
use crate::pixeldata::ImagePixelDataF32x4;
use anyhow::bail;
use anyhow::Result;
use exr::prelude::traits::*;
use half::f16;
use log::debug;

pub mod datatype;
pub mod encoder;
pub mod metadata;
pub mod pixelbuffer;
pub mod pixeldata;

/// Read the Metadata from an EXR image.
//
// https://github.com/johannesvollmer/exrs/blob/master/examples/0b_read_meta.rs
pub fn image_read_metadata_exr(file_path: &str) -> Result<ImageMetaData> {
    // 'pedantic = false' means "do not throw an error for invalid or
    // missing attributes", skipping them instead.
    let pedantic = false;

    let exr_meta_data =
        exr::meta::MetaData::read_from_file(file_path, pedantic)?;

    let image_metadata = if exr_meta_data.headers.len() == 0 {
        ImageMetaData::new()
    } else {
        let exr_header = &exr_meta_data.headers[0];
        // TODO: Get the EXR encoding from the header and return it.
        let image_attributes = &exr_header.shared_attributes;
        let layer_attributes = &exr_header.own_attributes;
        ImageMetaData::with_attributes(image_attributes, layer_attributes)
    };

    Ok(image_metadata)
}

/// Read an EXR image from a file path.
///
/// Allows vertically flipping the exported pixel data as we read the
/// data.
//
// https://github.com/johannesvollmer/exrs/blob/master/GUIDE.md
// https://github.com/johannesvollmer/exrs/blob/master/examples/0c_read_rgba.rs
pub fn image_read_pixels_exr_f32x4(
    file_path: &str,
    vertical_flip: bool,
) -> Result<(ImageMetaData, ImagePixelBuffer)> {
    debug!("Opening file: {}", file_path);

    let image = exr::image::read::read()
        .no_deep_data()
        .largest_resolution_level()
        .rgba_channels(
            |resolution, _channels: &exr::image::RgbaChannels| {
                let pixel_buffer = ImagePixelBuffer::new_f32x4(
                    resolution.width(),
                    resolution.height(),
                );
                pixel_buffer
            },
            move |pixel_buffer,
                  position,
                  (r, g, b, a): (f32, f32, f32, f32)| {
                // transfer the colors from the file to your image type,
                // requesting all values to be converted to f32 numbers (you
                // can also directly use f16 instead) and you could also use
                // `Sample` instead of `f32` to keep the original data type
                // from the file.

                let image_width = pixel_buffer.image_width();
                let image_height = pixel_buffer.image_height();

                let position_x = position.x();
                let position_y = match vertical_flip {
                    false => position.y(),
                    true => (image_height - 1) - position.y(),
                };
                let index = (position_y * image_width) + position_x;

                let pixel_buffer_slice = pixel_buffer.as_slice_f32x4_mut();
                pixel_buffer_slice[index] = (r, g, b, a)
            },
        )
        .first_valid_layer()
        .all_attributes()
        .from_file(file_path)?;

    // printing all pixels might kill the console, so only print some
    // meta data about the image.
    let data_window = image.layer_data.absolute_bounds();
    let layer_attributes = image.layer_data.attributes;
    let _image_width = image.layer_data.size.width();
    let _image_height = image.layer_data.size.height();

    debug!("Opened file: {}", file_path);
    debug!("Layer Attributes: {:#?}", layer_attributes);
    debug!("Data Window: {:?}", data_window);

    let image_data = image.layer_data.channel_data.pixels;
    let image_metadata =
        ImageMetaData::with_attributes(&image.attributes, &layer_attributes);

    Ok((image_metadata, image_data))
}

/// Read an EXR image from a file path.
///
/// Allows vertically flipping the exported pixel data as we read the
/// data.
//
// https://github.com/johannesvollmer/exrs/blob/master/GUIDE.md
// https://github.com/johannesvollmer/exrs/blob/master/examples/0c_read_rgba.rs
pub fn image_read_pixels_exr_f16x4(
    file_path: &str,
    vertical_flip: bool,
) -> Result<(ImageMetaData, ImagePixelBuffer)> {
    debug!("Opening file: {}", file_path);

    let image = exr::image::read::read()
        .no_deep_data()
        .largest_resolution_level()
        .rgba_channels(
            |resolution, _channels: &exr::image::RgbaChannels| {
                let pixel_buffer = ImagePixelBuffer::new_f16x4(
                    resolution.width(),
                    resolution.height(),
                );
                pixel_buffer
            },
            move |pixel_buffer,
                  position,
                  (r, g, b, a): (f16, f16, f16, f16)| {
                // transfer the colors from the file to your image type,
                // requesting all values to be converted to f32 numbers (you
                // can also directly use f16 instead) and you could also use
                // `Sample` instead of `f32` to keep the original data type
                // from the file.

                let image_width = pixel_buffer.image_width();
                let image_height = pixel_buffer.image_height();

                let position_x = position.x();
                let position_y = match vertical_flip {
                    false => position.y(),
                    true => (image_height - 1) - position.y(),
                };
                let index = (position_y * image_width) + position_x;

                let pixel_buffer_slice = pixel_buffer.as_slice_f16x4_mut();
                pixel_buffer_slice[index] = (r, g, b, a)
            },
        )
        .first_valid_layer()
        .all_attributes()
        .from_file(file_path)?;

    // printing all pixels might kill the console, so only print some
    // meta data about the image.
    let data_window = image.layer_data.absolute_bounds();
    let layer_attributes = image.layer_data.attributes;
    let _image_width = image.layer_data.size.width();
    let _image_height = image.layer_data.size.height();

    debug!("Opened file: {}", file_path);
    debug!("Layer Attributes: {:#?}", layer_attributes);
    debug!("Data Window: {:?}", data_window);

    let image_data = image.layer_data.channel_data.pixels;
    let image_metadata =
        ImageMetaData::with_attributes(&image.attributes, &layer_attributes);

    Ok((image_metadata, image_data))
}

/// Write a 32-bit float image to an EXR file.
//
// https://github.com/johannesvollmer/exrs/blob/master/examples/0a_write_rgba.rs
// https://github.com/johannesvollmer/exrs/blob/master/examples/1a_write_rgba_with_metadata.rs
// https://github.com/johannesvollmer/exrs/blob/master/examples/7_write_raw_blocks.rs
pub fn image_write_pixels_exr_f32x4(
    file_path: &str,
    encoder: ImageExrEncoder,
    meta_data: &ImageMetaData,
    pixel_buffer: &ImagePixelBuffer,
) -> Result<()> {
    // TODO: How can we control the number of threads used for
    // compression?

    let layer_attributes = meta_data.as_layer_attributes();

    let pixel_data = ImagePixelDataF32x4::from_buffer(pixel_buffer);
    let generate_pixels =
        |position: exr::math::Vec2<usize>| (pixel_data.get_pixel(position));

    let encoding = ImageExrEncoder::as_exr_encoding(encoder);
    let layer = exr::image::Layer::new(
        (pixel_buffer.image_width(), pixel_buffer.image_height()),
        layer_attributes,
        encoding,
        exr::image::SpecificChannels::rgba(generate_pixels),
    );

    let mut image = exr::image::Image::from_layer(layer);
    image.attributes = meta_data.as_image_attributes();

    // TODO: Set a specific number of threads to be used by the
    // thread-pool.
    let use_threads = true;
    let ok = if use_threads {
        // Write it to a file with all cores in parallel.
        image.write().to_file(file_path)
    } else {
        // Sequentially compress and write the images (in a single
        // thread).
        image.write().non_parallel().to_file(file_path)
    };

    match ok {
        Ok(..) => Ok(()),
        Err(err) => bail!(err),
    }
}
