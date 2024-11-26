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

use crate::imagemetadata::shim_create_image_meta_data_box;
use crate::imagemetadata::ShimImageMetaData;
use crate::imagepixelbuffer::shim_create_image_pixel_buffer_box;
use crate::imagepixelbuffer::ShimImagePixelBuffer;
use crate::shim_image_read_metadata_exr;
use crate::shim_image_read_pixels_exr_f32x4;
use crate::shim_image_write_pixels_exr_f32x4;

#[cxx::bridge(namespace = "mmimage")]
pub mod ffi {
    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmimage/_cxx.h");
        include!("mmimage/_symbol_export.h");
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum AttributeValueType {
        #[cxx_name = "kNone"]
        None = 0,

        #[cxx_name = "kString"]
        String = 1,

        #[cxx_name = "kF32"]
        F32 = 2,

        #[cxx_name = "kF64"]
        F64 = 3,

        #[cxx_name = "kI32"]
        I32 = 4,

        #[cxx_name = "kVec2F32"]
        Vec2F32 = 5,

        #[cxx_name = "kVec2I32"]
        Vec2I32 = 6,

        #[cxx_name = "kVec3F32"]
        Vec3F32 = 7,

        #[cxx_name = "kVec3I32"]
        Vec3I32 = 8,

        #[cxx_name = "kBox2F32"]
        Box2F32 = 9,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum ExrCompression {
        #[cxx_name = "kUncompressed"]
        Uncompressed = 0,

        #[cxx_name = "kRLE"]
        RLE = 1,

        #[cxx_name = "kZIP1"]
        ZIP1 = 2,

        #[cxx_name = "kZIP16"]
        ZIP16 = 3,

        #[cxx_name = "kPIZ"]
        PIZ = 4,

        #[cxx_name = "kPXR24"]
        PXR24 = 5,

        #[cxx_name = "kB44"]
        B44 = 6,

        #[cxx_name = "kB44A"]
        B44A = 7,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum ExrPixelLayoutMode {
        #[cxx_name = "kScanLines"]
        ScanLines = 0,

        #[cxx_name = "kTiles"]
        Tiles = 1,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct ExrPixelLayout {
        mode: ExrPixelLayoutMode,
        tile_size_x: usize,
        tile_size_y: usize,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum ExrLineOrder {
        #[cxx_name = "kIncreasing"]
        Increasing = 0,

        #[cxx_name = "kDecreasing"]
        Decreasing = 1,

        #[cxx_name = "kUnspecified"]
        Unspecified = 2,

        #[cxx_name = "kUnknown"]
        Unknown = 255,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct ImageExrEncoder {
        compression: ExrCompression,
        pixel_layout: ExrPixelLayout,
        line_order: ExrLineOrder,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionF32 {
        exists: bool,
        value: f32,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct Vec2F32 {
        x: f32,
        y: f32,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    struct Vec2I32 {
        x: i32,
        y: i32,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct Box2F32 {
        min_x: f32,
        min_y: f32,
        max_x: f32,
        max_y: f32,
    }

    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    struct ImageRegionRectangle {
        position_x: i32,
        position_y: i32,
        size_x: usize,
        size_y: usize,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct PixelF32x4 {
        r: f32,
        g: f32,
        b: f32,
        a: f32,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    struct PixelF64x2 {
        x: f64,
        y: f64,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone)]
    pub(crate) enum BufferDataType {
        #[cxx_name = "kNone"]
        None = 0,

        #[cxx_name = "kF16"]
        F16 = 1,

        #[cxx_name = "kF32"]
        F32 = 2,

        #[cxx_name = "kF64"]
        F64 = 3,
    }

    extern "Rust" {
        type ShimImagePixelBuffer;

        pub fn data_type(&self) -> BufferDataType;
        pub fn image_width(&self) -> usize;
        pub fn image_height(&self) -> usize;
        pub fn num_channels(&self) -> usize;

        pub fn pixel_count(&self) -> usize;
        pub fn element_count(&self) -> usize;

        pub fn as_slice_f32x4(&self) -> &[PixelF32x4];
        pub fn as_slice_f32x4_mut(&mut self) -> &mut [PixelF32x4];

        pub fn resize(
            &mut self,
            data_type: BufferDataType,
            image_width: usize,
            image_height: usize,
            num_channels: usize,
        );

        fn shim_create_image_pixel_buffer_box() -> Box<ShimImagePixelBuffer>;
    }

    extern "Rust" {
        type ShimImageMetaData;

        fn get_display_window(&self) -> ImageRegionRectangle;
        fn set_display_window(&mut self, value: ImageRegionRectangle);
        fn get_pixel_aspect(&self) -> f32;
        fn set_pixel_aspect(&mut self, value: f32);

        fn get_layer_name(&self) -> &str;
        fn set_layer_name(&mut self, value: &str);
        fn get_layer_position(&self) -> Vec2I32;
        fn set_layer_position(&mut self, value: Vec2I32);
        fn get_screen_window_center(&self) -> Vec2F32;
        fn set_screen_window_center(&mut self, value: Vec2F32);
        fn get_screen_window_width(&self) -> f32;
        fn set_screen_window_width(&mut self, value: f32);
        fn get_owner(&self) -> &str;
        fn set_owner(&mut self, value: &str);
        fn get_comments(&self) -> &str;
        fn set_comments(&mut self, value: &str);
        fn get_capture_date(&self) -> &str;
        fn get_utc_offset(&self) -> OptionF32;
        fn get_longitude(&self) -> OptionF32;
        fn get_latitude(&self) -> OptionF32;
        fn get_altitude(&self) -> OptionF32;
        fn get_focus(&self) -> OptionF32;
        fn get_exposure(&self) -> OptionF32;
        fn get_aperture(&self) -> OptionF32;
        fn get_iso_speed(&self) -> OptionF32;
        fn get_frames_per_second(&self) -> OptionF32;
        fn get_software_name(&self) -> &str;
        fn set_software_name(&mut self, value: &str);

        fn all_named_attribute_names(&self) -> Vec<String>;
        fn has_named_attribute(&self, attribute_name: &str) -> bool;
        fn get_named_attribute_type_index(&self, attribute_name: &str) -> u8;
        fn get_named_attribute_as_i32(&self, attribute_name: &str) -> i32;
        fn get_named_attribute_as_f32(&self, attribute_name: &str) -> f32;
        fn get_named_attribute_as_f64(&self, attribute_name: &str) -> f64;
        fn get_named_attribute_as_string(&self, attribute_name: &str)
            -> String;

        fn as_string(&self) -> String;

        fn shim_create_image_meta_data_box() -> Box<ShimImageMetaData>;
    }

    extern "Rust" {
        fn shim_image_read_pixels_exr_f32x4(
            file_path: &str,
            vertical_flip: bool,
            out_meta_data: &mut Box<ShimImageMetaData>,
            out_pixel_buffer: &mut Box<ShimImagePixelBuffer>,
        ) -> bool;

        fn shim_image_read_metadata_exr(
            file_path: &str,
            out_meta_data: &mut Box<ShimImageMetaData>,
        ) -> bool;

        fn shim_image_write_pixels_exr_f32x4(
            file_path: &str,
            exr_encoder: ImageExrEncoder,
            in_meta_data: &Box<ShimImageMetaData>,
            in_pixel_buffer: &Box<ShimImagePixelBuffer>,
        ) -> bool;
    }
}
