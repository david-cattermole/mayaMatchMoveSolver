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

use crate::cxxbridge::ffi::ImageRegionRectangle as BindImageRegionRectangle;
use crate::cxxbridge::ffi::OptionF32 as BindOptionF32;
use crate::cxxbridge::ffi::Vec2F32 as BindVec2F32;
use crate::cxxbridge::ffi::Vec2I32 as BindVec2I32;

use mmimage_rust::metadata::ImageMetaData as CoreImageMetaData;

#[derive(Debug)]
pub struct ShimImageMetaData {
    inner: CoreImageMetaData,
}

fn convert_option_string(optional_value: &Option<String>) -> &str {
    match optional_value {
        Some(value) => &*value,
        None => "",
    }
}

fn convert_str_to_option_string(value: &str) -> Option<String> {
    if value.len() > 0 {
        Some(value.to_string())
    } else {
        None
    }
}

fn convert_option_f32(optional_value: &Option<f32>) -> BindOptionF32 {
    match optional_value {
        Some(value) => BindOptionF32 {
            exists: true,
            value: *value,
        },
        None => BindOptionF32 {
            exists: false,
            value: f32::NAN,
        },
    }
}

impl ShimImageMetaData {
    pub fn new() -> Self {
        Self {
            inner: CoreImageMetaData::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreImageMetaData {
        &self.inner
    }

    pub fn set_inner(&mut self, pixel_data: CoreImageMetaData) {
        self.inner = pixel_data;
    }

    pub fn get_display_window(&self) -> BindImageRegionRectangle {
        BindImageRegionRectangle {
            position_x: self.inner.display_window.position_x,
            position_y: self.inner.display_window.position_y,
            size_x: self.inner.display_window.size_x,
            size_y: self.inner.display_window.size_y,
        }
    }

    pub fn set_display_window(&mut self, value: BindImageRegionRectangle) {
        self.inner.display_window.position_x = value.position_x;
        self.inner.display_window.position_y = value.position_y;
        self.inner.display_window.size_x = value.size_x;
        self.inner.display_window.size_y = value.size_y;
    }

    pub fn get_pixel_aspect(&self) -> f32 {
        self.inner.pixel_aspect
    }

    pub fn set_pixel_aspect(&mut self, value: f32) {
        self.inner.pixel_aspect = value;
    }

    pub fn get_layer_name(&self) -> &str {
        convert_option_string(&self.inner.layer_name)
    }

    pub fn set_layer_name(&mut self, value: &str) {
        self.inner.layer_name = convert_str_to_option_string(value);
    }

    pub fn get_layer_position(&self) -> BindVec2I32 {
        BindVec2I32 {
            x: self.inner.layer_position.x,
            y: self.inner.layer_position.y,
        }
    }

    pub fn set_layer_position(&mut self, value: BindVec2I32) {
        self.inner.layer_position.x = value.x;
        self.inner.layer_position.y = value.y;
    }

    pub fn get_screen_window_center(&self) -> BindVec2F32 {
        BindVec2F32 {
            x: self.inner.screen_window_center.x,
            y: self.inner.screen_window_center.y,
        }
    }

    pub fn set_screen_window_center(&mut self, value: BindVec2F32) {
        self.inner.screen_window_center.x = value.x;
        self.inner.screen_window_center.y = value.y;
    }

    pub fn get_screen_window_width(&self) -> f32 {
        self.inner.screen_window_width
    }

    pub fn set_screen_window_width(&mut self, value: f32) {
        self.inner.screen_window_width = value;
    }

    pub fn get_owner(&self) -> &str {
        convert_option_string(&self.inner.owner)
    }

    pub fn set_owner(&mut self, value: &str) {
        self.inner.owner = convert_str_to_option_string(value);
    }

    pub fn get_comments(&self) -> &str {
        convert_option_string(&self.inner.comments)
    }

    pub fn set_comments(&mut self, value: &str) {
        self.inner.comments = convert_str_to_option_string(value);
    }

    pub fn get_capture_date(&self) -> &str {
        convert_option_string(&self.inner.capture_date)
    }

    pub fn get_utc_offset(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.utc_offset)
    }

    pub fn get_longitude(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.longitude)
    }

    pub fn get_latitude(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.latitude)
    }

    pub fn get_altitude(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.altitude)
    }

    pub fn get_focus(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.focus)
    }

    pub fn get_exposure(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.exposure)
    }

    pub fn get_aperture(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.aperture)
    }

    pub fn get_iso_speed(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.iso_speed)
    }

    pub fn get_frames_per_second(&self) -> BindOptionF32 {
        convert_option_f32(&self.inner.frames_per_second)
    }

    pub fn get_software_name(&self) -> &str {
        convert_option_string(&self.inner.software_name)
    }

    pub fn set_software_name(&mut self, value: &str) {
        self.inner.software_name = convert_str_to_option_string(value);
    }

    pub fn all_named_attribute_names(&self) -> Vec<String> {
        self.inner.all_named_attribute_names()
    }

    pub fn has_named_attribute(&self, attribute_name: &str) -> bool {
        self.inner.has_named_attribute(attribute_name)
    }

    pub fn get_named_attribute_type_index(&self, attribute_name: &str) -> u8 {
        self.inner.get_named_attribute_type_index(attribute_name)
    }

    pub fn get_named_attribute_as_i32(&self, attribute_name: &str) -> i32 {
        self.inner.get_named_attribute_as_i32(attribute_name)
    }

    pub fn get_named_attribute_as_f32(&self, attribute_name: &str) -> f32 {
        self.inner.get_named_attribute_as_f32(attribute_name)
    }

    pub fn get_named_attribute_as_f64(&self, attribute_name: &str) -> f64 {
        self.inner.get_named_attribute_as_f64(attribute_name)
    }

    pub fn get_named_attribute_as_string(
        &self,
        attribute_name: &str,
    ) -> String {
        self.inner.get_named_attribute_as_string(attribute_name)
    }

    pub fn as_string(&self) -> String {
        self.inner.as_string()
    }
}

pub fn shim_create_image_meta_data_box() -> Box<ShimImageMetaData> {
    Box::new(ShimImageMetaData::new())
}
