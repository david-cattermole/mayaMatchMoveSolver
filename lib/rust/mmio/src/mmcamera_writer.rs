//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Writer for the `.mmcamera` JSON file format.

use anyhow::{Context, Result};
use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

use crate::json_common::JsonValue;
use crate::json_writer::write_json;
use crate::mmcamera_common::*;

/// Write `MmCameraData` to an `.mmcamera` file on disk.
pub fn write_mmcamera_file(path: &Path, data: &MmCameraData) -> Result<()> {
    let content = generate_mmcamera_string(data);
    let file = File::create(path).with_context(|| {
        format!("Failed to create mmcamera file: {}", path.display())
    })?;
    let mut w = BufWriter::new(file);
    w.write_all(content.as_bytes())
        .with_context(|| "Failed to write mmcamera data")?;
    w.flush().with_context(|| "Failed to flush mmcamera file")?;
    Ok(())
}

/// Generate an `.mmcamera` JSON string from `MmCameraData`.
pub fn generate_mmcamera_string(data: &MmCameraData) -> String {
    let value = build_mmcamera_json(data);
    write_json(&value)
}

fn build_mmcamera_json(data: &MmCameraData) -> JsonValue {
    let mut root = BTreeMap::new();
    root.insert("version".to_string(), JsonValue::Integer(1));

    let mut data_map = BTreeMap::new();
    data_map.insert("name".to_string(), JsonValue::String(data.name.clone()));
    data_map.insert(
        "start_frame".to_string(),
        JsonValue::Integer(data.start_frame),
    );
    data_map
        .insert("end_frame".to_string(), JsonValue::Integer(data.end_frame));
    data_map.insert("image".to_string(), build_image_json(&data.image));
    data_map.insert("attr".to_string(), build_attr_json(&data.attr));

    root.insert("data".to_string(), JsonValue::Object(data_map));
    JsonValue::Object(root)
}

fn build_image_json(image: &MmCameraImageData) -> JsonValue {
    let mut map = BTreeMap::new();
    map.insert(
        "file_path".to_string(),
        match &image.file_path {
            Some(s) => JsonValue::String(s.clone()),
            None => JsonValue::Null,
        },
    );
    map.insert(
        "width".to_string(),
        match image.width {
            Some(w) => JsonValue::Integer(w),
            None => JsonValue::Null,
        },
    );
    map.insert(
        "height".to_string(),
        match image.height {
            Some(h) => JsonValue::Integer(h),
            None => JsonValue::Null,
        },
    );
    map.insert(
        "pixel_aspect_ratio".to_string(),
        match image.pixel_aspect_ratio {
            Some(p) => JsonValue::Number(p),
            None => JsonValue::Null,
        },
    );
    JsonValue::Object(map)
}

fn build_attr_json(attr: &MmCameraAttrData) -> JsonValue {
    let mut map = BTreeMap::new();
    map.insert(
        "translateX".to_string(),
        build_frame_values(&attr.translate_x),
    );
    map.insert(
        "translateY".to_string(),
        build_frame_values(&attr.translate_y),
    );
    map.insert(
        "translateZ".to_string(),
        build_frame_values(&attr.translate_z),
    );
    map.insert("rotateX".to_string(), build_frame_values(&attr.rotate_x));
    map.insert("rotateY".to_string(), build_frame_values(&attr.rotate_y));
    map.insert("rotateZ".to_string(), build_frame_values(&attr.rotate_z));
    map.insert(
        "focalLength".to_string(),
        build_frame_values(&attr.focal_length),
    );
    map.insert(
        "filmBackWidth".to_string(),
        build_frame_values(&attr.film_back_width),
    );
    map.insert(
        "filmBackHeight".to_string(),
        build_frame_values(&attr.film_back_height),
    );
    map.insert(
        "filmBackOffsetX".to_string(),
        build_frame_values(&attr.film_back_offset_x),
    );
    map.insert(
        "filmBackOffsetY".to_string(),
        build_frame_values(&attr.film_back_offset_y),
    );
    JsonValue::Object(map)
}

fn build_frame_values(pairs: &[(i64, f64)]) -> JsonValue {
    JsonValue::Array(
        pairs
            .iter()
            .map(|(frame, value)| {
                JsonValue::Array(vec![
                    JsonValue::Integer(*frame),
                    JsonValue::Number(*value),
                ])
            })
            .collect(),
    )
}
