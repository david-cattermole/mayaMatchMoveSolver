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

//! Writer for the `.mmresiduals` JSON file format.

use anyhow::{Context, Result};
use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

use crate::json_common::JsonValue;
use crate::json_writer::write_json;
use crate::mmresiduals_common::*;

/// Write `MmResidualsData` to an `.mmresiduals` file on disk.
pub fn write_mmresiduals_file(
    path: &Path,
    data: &MmResidualsData,
) -> Result<()> {
    let content = generate_mmresiduals_string(data);
    let file = File::create(path).with_context(|| {
        format!("Failed to create mmresiduals file: {}", path.display())
    })?;
    let mut w = BufWriter::new(file);
    w.write_all(content.as_bytes())
        .with_context(|| "Failed to write mmresiduals data")?;
    w.flush()
        .with_context(|| "Failed to flush mmresiduals file")?;
    Ok(())
}

/// Generate an `.mmresiduals` JSON string from `MmResidualsData`.
pub fn generate_mmresiduals_string(data: &MmResidualsData) -> String {
    let value = build_mmresiduals_json(data);
    write_json(&value)
}

fn build_mmresiduals_json(data: &MmResidualsData) -> JsonValue {
    let mut root = BTreeMap::new();
    root.insert("version".to_string(), JsonValue::Integer(1));

    let mut data_map = BTreeMap::new();

    // marker_names
    data_map.insert(
        "marker_names".to_string(),
        JsonValue::Array(
            data.marker_names
                .iter()
                .map(|n| JsonValue::String(n.clone()))
                .collect(),
        ),
    );

    // frame_numbers
    data_map.insert(
        "frame_numbers".to_string(),
        JsonValue::Array(
            data.frame_numbers
                .iter()
                .map(|&f| JsonValue::Integer(f))
                .collect(),
        ),
    );

    // image_width / image_height
    data_map.insert(
        "image_width".to_string(),
        match data.image_width {
            Some(w) => JsonValue::Integer(w),
            None => JsonValue::Null,
        },
    );
    data_map.insert(
        "image_height".to_string(),
        match data.image_height {
            Some(h) => JsonValue::Integer(h),
            None => JsonValue::Null,
        },
    );

    // statistics
    data_map.insert(
        "statistics".to_string(),
        build_statistics_json(&data.statistics),
    );

    // per_frame_per_marker
    data_map.insert(
        "per_frame_per_marker".to_string(),
        JsonValue::Array(
            data.per_frame_per_marker
                .iter()
                .map(|fd| build_frame_data_json(fd))
                .collect(),
        ),
    );

    root.insert("data".to_string(), JsonValue::Object(data_map));
    JsonValue::Object(root)
}

fn build_statistics_json(stats: &MmResidualsStatistics) -> JsonValue {
    let mut map = BTreeMap::new();
    map.insert("mean".to_string(), JsonValue::Number(stats.mean));
    map.insert("median".to_string(), JsonValue::Number(stats.median));
    map.insert("std_dev".to_string(), JsonValue::Number(stats.std_dev));
    map.insert("min".to_string(), JsonValue::Number(stats.min));
    map.insert("max".to_string(), JsonValue::Number(stats.max));
    map.insert("count".to_string(), JsonValue::Integer(stats.count as i64));
    JsonValue::Object(map)
}

fn build_frame_data_json(fd: &MmResidualsFrameData) -> JsonValue {
    let mut map = BTreeMap::new();
    map.insert("frame".to_string(), JsonValue::Integer(fd.frame));
    map.insert(
        "errors".to_string(),
        JsonValue::Array(
            fd.errors
                .iter()
                .map(|&e| {
                    if e.is_finite() {
                        JsonValue::Number(e)
                    } else {
                        JsonValue::Null
                    }
                })
                .collect(),
        ),
    );
    JsonValue::Object(map)
}
