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

use crate::datatype::ImageRegionRectangle;
use crate::datatype::Vec2F32;
use crate::datatype::Vec2I32;
use num::Integer;
use std::collections::HashMap;

/// Converts a f32 number to a rational number compatible with the
/// OpenEXR standard.
//
// Taken from (2023-06-13 June 13th):
// https://rosettacode.org/wiki/Convert_decimal_number_to_rational#Rust
fn f32_to_rational(mut n: f32) -> exr::meta::attribute::Rational {
    // Based on Farey sequences
    assert!(n.is_finite());
    let flag_neg = n < 0.0;
    if flag_neg {
        n = n * (-1.0)
    }
    if n < std::f32::MIN_POSITIVE {
        let dividend: i32 = 0;
        let divisor: u32 = 1;
        return (dividend, divisor);
    }
    if (n - n.round()).abs() < std::f32::EPSILON {
        let dividend: i32 = n.round() as i32;
        let divisor: u32 = 1;
        return (dividend, divisor);
    }

    let mut a: isize = 0;
    let mut b: isize = 1;
    let mut c: isize = n.ceil() as isize;
    let mut d: isize = 1;
    let aux1 = isize::max_value() / 2;
    while c < aux1 && d < aux1 {
        let aux2: f32 = (a as f32 + c as f32) / (b as f32 + d as f32);
        if (n - aux2).abs() < std::f32::EPSILON {
            break;
        }
        if n > aux2 {
            a = a + c;
            b = b + d;
        } else {
            c = a + c;
            d = b + d;
        }
    }

    // Make sure that the fraction is irreducible.
    //
    // gcd is short for "Greatest Common Divisor".
    let dividend: i32;
    let divisor: u32;
    let gcd = (a + c).gcd(&(b + d));
    if flag_neg {
        dividend = (-(a + c) / gcd) as i32;
        divisor = ((b + d) / gcd) as u32;
    } else {
        dividend = ((a + c) / gcd) as i32;
        divisor = ((b + d) / gcd) as u32;
    }
    (dividend, divisor)
}

fn convert_rational_to_option_f32(
    value: &exr::meta::attribute::Rational,
) -> Option<f32> {
    let (dividend, divisor) = value;
    if *divisor > 0 {
        Some((*dividend as f32) / (*divisor as f32))
    } else {
        None
    }
}

fn convert_f32_to_option_rational(
    value: f32,
) -> Option<exr::meta::attribute::Rational> {
    if !value.is_finite() || (value.abs() < std::f32::EPSILON) {
        None
    } else {
        Some(f32_to_rational(value))
    }
}

fn convert_option_text_to_option_string(
    value: &Option<exr::meta::attribute::Text>,
) -> Option<String> {
    match value {
        Some(text) => Some(text.to_string()),
        None => None,
    }
}

fn convert_option_string_to_option_text(
    value: &Option<String>,
) -> Option<exr::meta::attribute::Text> {
    match value {
        Some(string) => exr::meta::attribute::Text::new_or_none(string),
        None => None,
    }
}

fn convert_option_rational_to_option_f32(
    value: &Option<exr::meta::attribute::Rational>,
) -> Option<f32> {
    match value {
        Some(v) => convert_rational_to_option_f32(v),
        None => None,
    }
}

fn convert_option_f32_to_option_rational(
    value: &Option<f32>,
) -> Option<exr::meta::attribute::Rational> {
    match value {
        Some(v) => convert_f32_to_option_rational(*v),
        None => None,
    }
}

#[derive(Debug)]
pub enum AttributeValue {
    None,
    String(String),
    F32(f32),
    F64(f64),
    I32(i32),
    Vec2F32((f32, f32)),
    Vec2I32((i32, i32)),
    Vec3F32((f32, f32, f32)),
    Vec3I32((i32, i32, i32)),
}

impl AttributeValue {
    pub fn from_exr_attribute_value(
        exr_attr_value: &exr::prelude::AttributeValue,
    ) -> AttributeValue {
        match exr_attr_value {
            exr::prelude::AttributeValue::Text(v) => {
                AttributeValue::String(v.to_string())
            }
            exr::prelude::AttributeValue::Rational(v) => {
                let v = match convert_rational_to_option_f32(v) {
                    Some(v) => v,
                    None => 0.0,
                };
                AttributeValue::F32(v)
            }
            exr::prelude::AttributeValue::I32(v) => AttributeValue::I32(*v),
            exr::prelude::AttributeValue::F32(v) => AttributeValue::F32(*v),
            exr::prelude::AttributeValue::F64(v) => AttributeValue::F64(*v),
            exr::prelude::AttributeValue::IntVec2(v) => {
                AttributeValue::Vec2I32((v.0, v.1))
            }
            exr::prelude::AttributeValue::FloatVec2(v) => {
                AttributeValue::Vec2F32((v.0, v.1))
            }
            exr::prelude::AttributeValue::IntVec3(v) => {
                AttributeValue::Vec3I32((v.0, v.1, v.2))
            }
            exr::prelude::AttributeValue::FloatVec3(v) => {
                AttributeValue::Vec3F32((v.0, v.1, v.2))
            }
            _ => AttributeValue::None,
        }
    }

    pub fn type_index(&self) -> u8 {
        match self {
            AttributeValue::None => 0,
            AttributeValue::String(_) => 1,
            AttributeValue::F32(_) => 2,
            AttributeValue::F64(_) => 3,
            AttributeValue::I32(_) => 4,
            AttributeValue::Vec2F32(_) => 5,
            AttributeValue::Vec2I32(_) => 6,
            AttributeValue::Vec3F32(_) => 7,
            AttributeValue::Vec3I32(_) => 8,
        }
    }
}

fn generate_named_attributes(
    image_named_attributes: &HashMap<
        exr::prelude::Text,
        exr::prelude::AttributeValue,
    >,
    layer_named_attributes: &HashMap<
        exr::prelude::Text,
        exr::prelude::AttributeValue,
    >,
) -> HashMap<String, AttributeValue> {
    let mut named_attributes = HashMap::new();

    for (key, value) in image_named_attributes.iter() {
        let attr_value = AttributeValue::from_exr_attribute_value(value);
        named_attributes.insert(key.to_string(), attr_value);
    }

    for (key, value) in layer_named_attributes.iter() {
        let attr_value = AttributeValue::from_exr_attribute_value(value);
        named_attributes.insert(key.to_string(), attr_value);
    }

    named_attributes
}

#[derive(Debug)]
pub struct ImageMetaData {
    // ImageAttributes
    // https://docs.rs/exr/latest/exr/meta/header/struct.ImageAttributes.html
    pub display_window: ImageRegionRectangle, // IntegerBounds
    pub pixel_aspect: f32,

    // // https://docs.rs/exr/1.6.3/exr/meta/attribute/struct.Chromaticities.html
    // chromaticities: Option<exr::meta::attribute::Chromaticities>,

    // // https://docs.rs/exr/1.6.3/exr/meta/attribute/struct.TimeCode.html
    // time_code: Option<TimeCode>,

    // LayerAttributes
    // https://docs.rs/exr/latest/exr/meta/header/struct.LayerAttributes.html
    pub layer_name: Option<String>,
    pub layer_position: Vec2I32,
    pub screen_window_center: Vec2F32,
    pub screen_window_width: f32,
    // white_luminance: Option<f32>,
    // adopted_neutral: Option<Vec2<f32>>,
    // rendering_transform_name: Option<String>,
    // look_modification_transform_name: Option<String>,
    // horizontal_density: Option<f32>,
    pub owner: Option<String>,
    pub comments: Option<String>,
    pub capture_date: Option<String>,
    pub utc_offset: Option<f32>,
    pub longitude: Option<f32>,
    pub latitude: Option<f32>,
    pub altitude: Option<f32>,
    pub focus: Option<f32>,
    pub exposure: Option<f32>,
    pub aperture: Option<f32>,
    pub iso_speed: Option<f32>,
    // environment_map: Option<EnvironmentMap>,
    // film_key_code: Option<KeyCode>,
    // wrap_mode_name: Option<String>,
    pub frames_per_second: Option<f32>,
    // multi_view_names: Option<Vec<String>>,
    // world_to_camera: Option<Matrix4x4>,
    // world_to_normalized_device: Option<Matrix4x4>,
    // deep_image_state: Option<f32>,
    // original_data_window: Option<IntegerBounds>,
    // preview: Option<Preview>,
    // view_name: Option<String>,
    pub software_name: Option<String>,
    // near_clip_plane: Option<f32>,
    // far_clip_plane: Option<f32>,
    // horizontal_field_of_view: Option<f32>,
    // vertical_field_of_view: Option<f32>,
    //
    // General Attributes
    named_attributes: HashMap<String, AttributeValue>,
}

impl ImageMetaData {
    pub fn new() -> ImageMetaData {
        let display_window = ImageRegionRectangle::default();
        let pixel_aspect = 1.0;
        let layer_name = None;
        let layer_position = Vec2I32::default();
        let screen_window_center = Vec2F32::default();
        let screen_window_width = 0.0;
        let owner = None;
        let comments = None;
        let capture_date = None;
        let utc_offset = None;
        let longitude = None;
        let latitude = None;
        let altitude = None;
        let focus = None;
        let exposure = None;
        let aperture = None;
        let iso_speed = None;
        let frames_per_second = None;
        let software_name = None;
        let named_attributes = HashMap::new();

        ImageMetaData {
            display_window,
            pixel_aspect,
            layer_name,
            layer_position,
            screen_window_center,
            screen_window_width,
            owner,
            comments,
            capture_date,
            utc_offset,
            longitude,
            latitude,
            altitude,
            focus,
            exposure,
            aperture,
            iso_speed,
            frames_per_second,
            software_name,
            named_attributes,
        }
    }

    pub fn with_attributes(
        image_attributes: &exr::meta::header::ImageAttributes,
        layer_attributes: &exr::meta::header::LayerAttributes,
    ) -> ImageMetaData {
        // Image Attributes
        let display_window = ImageRegionRectangle::new(
            image_attributes.display_window.position.0,
            image_attributes.display_window.position.1,
            image_attributes.display_window.size.0,
            image_attributes.display_window.size.1,
        );
        let pixel_aspect = image_attributes.pixel_aspect;

        // Layer Attribute
        let layer_name =
            convert_option_text_to_option_string(&layer_attributes.layer_name);
        let layer_position = Vec2I32::new(
            layer_attributes.layer_position.0,
            layer_attributes.layer_position.1,
        );
        let screen_window_center = Vec2F32::new(
            layer_attributes.screen_window_center.0,
            layer_attributes.screen_window_center.1,
        );
        let screen_window_width = layer_attributes.screen_window_width;
        let owner =
            convert_option_text_to_option_string(&layer_attributes.owner);
        let comments =
            convert_option_text_to_option_string(&layer_attributes.comments);
        let capture_date = convert_option_text_to_option_string(
            &layer_attributes.capture_date,
        );
        let utc_offset = layer_attributes.utc_offset;
        let longitude = layer_attributes.longitude;
        let latitude = layer_attributes.latitude;
        let altitude = layer_attributes.altitude;
        let focus = layer_attributes.focus;
        let exposure = layer_attributes.exposure;
        let aperture = layer_attributes.aperture;
        let iso_speed = layer_attributes.iso_speed;
        let frames_per_second = convert_option_rational_to_option_f32(
            &layer_attributes.frames_per_second,
        );
        let software_name = convert_option_text_to_option_string(
            &layer_attributes.software_name,
        );

        let named_attributes = generate_named_attributes(
            &image_attributes.other,
            &layer_attributes.other,
        );

        ImageMetaData {
            display_window,
            pixel_aspect,
            layer_name,
            layer_position,
            screen_window_center,
            screen_window_width,
            owner,
            comments,
            capture_date,
            utc_offset,
            longitude,
            latitude,
            altitude,
            focus,
            exposure,
            aperture,
            iso_speed,
            frames_per_second,
            software_name,
            named_attributes,
        }
    }

    pub fn as_layer_attributes(&self) -> exr::meta::header::LayerAttributes {
        // TODO: Set LayerAttributes from ImageMetadata.
        let layer_name = match &self.layer_name {
            Some(value) => value.to_string(),
            None => "rgba".to_string(),
        };

        // 'layer_position' is the origin of the data-window. Note
        // that the layer position may not be zero/origin, it is
        // relative to the Display window.
        let layer_position = exr::math::Vec2::<i32>(
            self.layer_position.x,
            self.layer_position.y,
        );

        let screen_window_center = exr::math::Vec2::<f32>(
            self.screen_window_center.x,
            self.screen_window_center.y,
        );

        let comments = convert_option_string_to_option_text(&self.comments);
        let owner = convert_option_string_to_option_text(&self.owner);
        let software_name =
            convert_option_string_to_option_text(&self.software_name);

        let frames_per_second =
            convert_option_f32_to_option_rational(&self.frames_per_second);

        let mut layer_attributes =
            exr::meta::header::LayerAttributes::named(&*layer_name);
        layer_attributes.layer_position = layer_position;
        layer_attributes.screen_window_center = screen_window_center;
        layer_attributes.screen_window_width = self.screen_window_width;
        layer_attributes.comments = comments;
        layer_attributes.owner = owner;
        layer_attributes.exposure = self.exposure;
        layer_attributes.focus = self.focus;
        layer_attributes.frames_per_second = frames_per_second;
        layer_attributes.software_name = software_name;
        // layer_attributes.other.insert(
        //     exr::meta::attribute::Text::from(
        //         "Layer Purpose (Custom Layer Attribute)",
        //     ),
        //     exr::meta::attribute::AttributeValue::Text(
        //         exr::meta::attribute::Text::from(
        //             "This layer contains the rgb pixel data",
        //         ),
        //     ),
        // );

        layer_attributes
    }

    pub fn as_image_attributes(&self) -> exr::meta::header::ImageAttributes {
        let display_window = self.display_window.as_exr_integer_bounds();
        let mut image_attributes =
            exr::meta::header::ImageAttributes::new(display_window);
        image_attributes.pixel_aspect = 1.0;

        // // TODO: Support Chromaticities.
        // pub chromaticities: Option<Chromaticities>,

        // // TODO: Support TimeCode.
        // pub time_code: Option<TimeCode>,
        // image_attributes.time_code = Some(Attribute::TimeCode {
        //     hours: 0,
        //     minutes: 1,
        //     seconds: 59,
        //     frame: 29,
        //     ..Attribute::TimeCode::default()
        // });

        // // TODO: Support named attributes.
        // image_attributes.other.insert(
        //     Text::from("Mice Count (Custom Image Attribute)"),
        //     AttributeValue::I32(23333),
        // );

        image_attributes
    }

    pub fn all_named_attribute_names(&self) -> Vec<String> {
        let mut names: Vec<String> = self
            .named_attributes
            .keys()
            .map(|x| x.to_string())
            .collect();
        names.sort_unstable();
        names
    }

    pub fn has_named_attribute(&self, attribute_name: &str) -> bool {
        self.named_attributes.contains_key(attribute_name)
    }

    pub fn get_named_attribute_type_index(&self, attribute_name: &str) -> u8 {
        match self.named_attributes.get(attribute_name) {
            Some(value) => value.type_index(),
            None => 0, // The zero value means 'None'.
        }
    }

    pub fn get_named_attribute_as_i32(&self, attribute_name: &str) -> i32 {
        match self.named_attributes.get(attribute_name) {
            Some(value) => match value {
                AttributeValue::I32(v) => *v,
                _ => 0,
            },
            None => 0,
        }
    }

    pub fn get_named_attribute_as_f32(&self, attribute_name: &str) -> f32 {
        match self.named_attributes.get(attribute_name) {
            Some(value) => match value {
                AttributeValue::F64(v) => (*v as f32).into(),
                AttributeValue::F32(v) => *v,
                _ => 0.0,
            },
            None => 0.0,
        }
    }

    pub fn get_named_attribute_as_f64(&self, attribute_name: &str) -> f64 {
        match self.named_attributes.get(attribute_name) {
            Some(value) => match value {
                AttributeValue::F64(v) => *v,
                AttributeValue::F32(v) => *v as f64,
                _ => 0.0,
            },
            None => 0.0,
        }
    }

    pub fn get_named_attribute_as_string(
        &self,
        attribute_name: &str,
    ) -> String {
        match self.named_attributes.get(attribute_name) {
            Some(value) => match value {
                AttributeValue::String(v) => v.to_string(),
                _ => String::new(),
            },
            None => String::new(),
        }
    }

    pub fn as_string(&self) -> String {
        format!("{:#?}", self).to_string()
    }
}

// /// Read the Metadata from an EXR image.
// pub fn image_read_metadata_exr(file_path: &str) -> Result<ImageMetaData> {
//     // Do not throw an error for invalid or missing attributes,
//     // skipping them instead.
//     let pedantic = false;
//     let exr_meta_data =
//         exr::meta::MetaData::read_from_file(file_path, pedantic)?;

//     let image_metadata = if exr_meta_data.headers.len() == 0 {
//         ImageMetaData::new()
//     } else {
//         let exr_header = &exr_meta_data.headers[0];
//         let image_attributes = &exr_header.shared_attributes;
//         let layer_attributes = &exr_header.own_attributes;
//         ImageMetaData::with_attributes(image_attributes, layer_attributes)
//     };

//     Ok(image_metadata)
// }
