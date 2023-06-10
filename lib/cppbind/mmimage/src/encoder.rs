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

use crate::cxxbridge::ffi::ExrCompression as BindExrCompression;
use crate::cxxbridge::ffi::ExrLineOrder as BindExrLineOrder;
use crate::cxxbridge::ffi::ExrPixelLayout as BindExrPixelLayout;
use crate::cxxbridge::ffi::ExrPixelLayoutMode as BindExrPixelLayoutMode;
use crate::cxxbridge::ffi::ImageExrEncoder as BindImageExrEncoder;

use mmimage_rust::encoder::ExrCompression as CoreExrCompression;
use mmimage_rust::encoder::ExrLineOrder as CoreExrLineOrder;
use mmimage_rust::encoder::ExrPixelLayout as CoreExrPixelLayout;
use mmimage_rust::encoder::ImageExrEncoder as CoreImageExrEncoder;

fn bind_to_core_exr_compression(
    value: BindExrCompression,
) -> CoreExrCompression {
    match value {
        BindExrCompression::Uncompressed => CoreExrCompression::Uncompressed,
        BindExrCompression::RLE => CoreExrCompression::RLE,
        BindExrCompression::ZIP1 => CoreExrCompression::ZIP1,
        BindExrCompression::ZIP16 => CoreExrCompression::ZIP16,
        BindExrCompression::PIZ => CoreExrCompression::PIZ,
        BindExrCompression::PXR24 => CoreExrCompression::PXR24,
        BindExrCompression::B44 => CoreExrCompression::B44,
        BindExrCompression::B44A => CoreExrCompression::B44A,
        BindExrCompression::Unknown => {
            panic!("ExrCompression has invalid Unknown value.")
        }
        _ => panic!("ExrCompression has invalid value."),
    }
}

fn bind_to_core_exr_pixel_layout(
    value: BindExrPixelLayout,
) -> CoreExrPixelLayout {
    match value.mode {
        BindExrPixelLayoutMode::ScanLines => CoreExrPixelLayout::ScanLines,
        BindExrPixelLayoutMode::Tiles => {
            CoreExrPixelLayout::Tiles((value.tile_size_x, value.tile_size_y))
        }
        BindExrPixelLayoutMode::Unknown => {
            panic!("ExrPixelLayoutMode has invalid Unknown value.")
        }
        _ => panic!("ExrPixelLayoutMode has invalid value."),
    }
}

fn bind_to_core_exr_line_order(value: BindExrLineOrder) -> CoreExrLineOrder {
    match value {
        BindExrLineOrder::Increasing => CoreExrLineOrder::Increasing,
        BindExrLineOrder::Decreasing => CoreExrLineOrder::Decreasing,
        BindExrLineOrder::Unspecified => CoreExrLineOrder::Unspecified,
        BindExrLineOrder::Unknown => {
            panic!("ExrLineOrder has invalid Unknown value.")
        }
        _ => panic!("ExrLineOrder has invalid value."),
    }
}

pub fn bind_to_core_image_exr_encoder(
    value: BindImageExrEncoder,
) -> CoreImageExrEncoder {
    let compression = bind_to_core_exr_compression(value.compression);
    let pixel_layout = bind_to_core_exr_pixel_layout(value.pixel_layout);
    let line_order = bind_to_core_exr_line_order(value.line_order);
    CoreImageExrEncoder {
        compression,
        pixel_layout,
        line_order,
    }
}
