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

// use exr::prelude::*;

#[derive(Debug, Copy, Clone)]
pub enum ExrCompression {
    Uncompressed,
    RLE,
    ZIP1,
    ZIP16,
    PIZ,
    PXR24,
    B44,
    B44A,
    // // TODO: Represent these compression mode.
    // DWAA(Option<f32>),
    // DWAB(Option<f32>),
}

impl ExrCompression {
    #[allow(dead_code)]
    fn from_exr_compression(
        value: exr::compression::Compression,
    ) -> ExrCompression {
        match value {
            exr::compression::Compression::Uncompressed => {
                ExrCompression::Uncompressed
            }
            exr::compression::Compression::RLE => ExrCompression::RLE,
            exr::compression::Compression::ZIP1 => ExrCompression::ZIP1,
            exr::compression::Compression::ZIP16 => ExrCompression::ZIP16,
            exr::compression::Compression::PIZ => ExrCompression::PIZ,
            exr::compression::Compression::PXR24 => ExrCompression::PXR24,
            exr::compression::Compression::B44 => ExrCompression::B44,
            exr::compression::Compression::B44A => ExrCompression::B44A,
            exr::compression::Compression::DWAA(_) => {
                panic!("EXR Compression DWAA mode is not supported yet.")
            }
            exr::compression::Compression::DWAB(_) => {
                panic!("EXR Compression DWAB mode is not supported yet.")
            }
        }
    }

    fn as_exr_compression(
        value: ExrCompression,
    ) -> exr::compression::Compression {
        match value {
            ExrCompression::Uncompressed => {
                exr::compression::Compression::Uncompressed
            }
            ExrCompression::RLE => exr::compression::Compression::RLE,
            ExrCompression::ZIP1 => exr::compression::Compression::ZIP1,
            ExrCompression::ZIP16 => exr::compression::Compression::ZIP16,
            ExrCompression::PIZ => exr::compression::Compression::PIZ,
            ExrCompression::PXR24 => exr::compression::Compression::PXR24,
            ExrCompression::B44 => exr::compression::Compression::B44,
            ExrCompression::B44A => exr::compression::Compression::B44A,
        }
    }
}

#[derive(Debug, Copy, Clone)]
pub enum ExrPixelLayout {
    ScanLines,
    Tiles((usize, usize)),
}

impl ExrPixelLayout {
    #[allow(dead_code)]
    fn from_exr_blocks(value: exr::image::Blocks) -> ExrPixelLayout {
        match value {
            exr::image::Blocks::ScanLines => ExrPixelLayout::ScanLines,
            exr::image::Blocks::Tiles(size) => {
                ExrPixelLayout::Tiles((size.0, size.1))
            }
        }
    }

    fn as_exr_blocks(value: ExrPixelLayout) -> exr::image::Blocks {
        match value {
            ExrPixelLayout::ScanLines => exr::image::Blocks::ScanLines,
            ExrPixelLayout::Tiles(size) => exr::image::Blocks::Tiles(
                exr::math::Vec2::<usize>(size.0, size.1),
            ),
        }
    }
}

#[derive(Debug, Copy, Clone)]
pub enum ExrLineOrder {
    Increasing,
    Decreasing,
    Unspecified,
}

impl ExrLineOrder {
    #[allow(dead_code)]
    fn from_exr_line_order(
        value: exr::meta::attribute::LineOrder,
    ) -> ExrLineOrder {
        match value {
            exr::meta::attribute::LineOrder::Increasing => {
                ExrLineOrder::Increasing
            }
            exr::meta::attribute::LineOrder::Decreasing => {
                ExrLineOrder::Decreasing
            }
            exr::meta::attribute::LineOrder::Unspecified => {
                ExrLineOrder::Unspecified
            }
        }
    }

    fn as_exr_line_order(
        value: ExrLineOrder,
    ) -> exr::meta::attribute::LineOrder {
        match value {
            ExrLineOrder::Increasing => {
                exr::meta::attribute::LineOrder::Increasing
            }
            ExrLineOrder::Decreasing => {
                exr::meta::attribute::LineOrder::Decreasing
            }
            ExrLineOrder::Unspecified => {
                exr::meta::attribute::LineOrder::Unspecified
            }
        }
    }
}

#[derive(Debug, Copy, Clone)]
pub struct ImageExrEncoder {
    pub compression: ExrCompression,
    pub pixel_layout: ExrPixelLayout,
    pub line_order: ExrLineOrder,
}

impl ImageExrEncoder {
    #[allow(dead_code)]
    fn from_exr_encoding(value: exr::image::Encoding) -> ImageExrEncoder {
        let compression =
            ExrCompression::from_exr_compression(value.compression);
        let pixel_layout = ExrPixelLayout::from_exr_blocks(value.blocks);
        let line_order = ExrLineOrder::from_exr_line_order(value.line_order);
        ImageExrEncoder {
            compression,
            pixel_layout,
            line_order,
        }
    }

    pub fn as_exr_encoding(value: ImageExrEncoder) -> exr::image::Encoding {
        let compression = ExrCompression::as_exr_compression(value.compression);
        let blocks = ExrPixelLayout::as_exr_blocks(value.pixel_layout);
        let line_order = ExrLineOrder::as_exr_line_order(value.line_order);
        exr::image::Encoding {
            compression,
            blocks,
            line_order,
        }
    }
}
