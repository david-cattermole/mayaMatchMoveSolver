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

//! Reader for the `.mmcamera` JSON file format.

use anyhow::{bail, Context, Result};
use std::path::Path;

use crate::json_common::JsonValue;
use crate::json_parser::parse_json;
pub use crate::mmcamera_common::*;

/// Parse an `.mmcamera` file from disk.
///
/// Returns `(version, data)`.
pub fn parse_mmcamera_file(path: &Path) -> Result<(i32, MmCameraData)> {
    let content = std::fs::read_to_string(path).with_context(|| {
        format!("Failed to read mmcamera file: {}", path.display())
    })?;
    parse_mmcamera_string(&content)
}

/// Parse an `.mmcamera` JSON string.
///
/// Returns `(version, data)`.
pub fn parse_mmcamera_string(content: &str) -> Result<(i32, MmCameraData)> {
    let root = parse_json(content).map_err(|e| anyhow::anyhow!("{}", e))?;

    let _obj = root
        .as_object()
        .context("mmcamera root must be a JSON object")?;

    let version =
        root.get("version")
            .and_then(|v| v.as_i64())
            .context("missing or invalid 'version' field")? as i32;

    let data_val = root.get("data").context("missing 'data' field")?;

    let _data_obj = data_val
        .as_object()
        .context("'data' must be a JSON object")?;

    let name = data_val
        .get("name")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();

    let start_frame = data_val
        .get("start_frame")
        .and_then(|v| v.as_i64())
        .context("missing 'start_frame'")?;

    let end_frame = data_val
        .get("end_frame")
        .and_then(|v| v.as_i64())
        .context("missing 'end_frame'")?;

    let image = parse_image_data(data_val.get("image"))?;
    let attr = parse_attr_data(data_val.get("attr"))?;

    Ok((
        version,
        MmCameraData {
            name,
            start_frame,
            end_frame,
            image,
            attr,
        },
    ))
}

fn parse_image_data(val: Option<&JsonValue>) -> Result<MmCameraImageData> {
    let val = match val {
        Some(v) => v,
        None => {
            return Ok(MmCameraImageData {
                file_path: None,
                width: None,
                height: None,
                pixel_aspect_ratio: None,
            })
        }
    };

    let file_path = val
        .get("file_path")
        .and_then(|v| if v.is_null() { None } else { v.as_str() })
        .map(|s| s.to_string());

    let width =
        val.get("width")
            .and_then(|v| if v.is_null() { None } else { v.as_i64() });

    let height =
        val.get("height")
            .and_then(|v| if v.is_null() { None } else { v.as_i64() });

    let pixel_aspect_ratio = val.get("pixel_aspect_ratio").and_then(|v| {
        if v.is_null() {
            None
        } else {
            v.as_f64()
        }
    });

    Ok(MmCameraImageData {
        file_path,
        width,
        height,
        pixel_aspect_ratio,
    })
}

fn parse_attr_data(val: Option<&JsonValue>) -> Result<MmCameraAttrData> {
    let val = val.context("missing 'attr' field")?;

    Ok(MmCameraAttrData {
        translate_x: parse_frame_values(val.get("translateX"))?,
        translate_y: parse_frame_values(val.get("translateY"))?,
        translate_z: parse_frame_values(val.get("translateZ"))?,
        rotate_x: parse_frame_values(val.get("rotateX"))?,
        rotate_y: parse_frame_values(val.get("rotateY"))?,
        rotate_z: parse_frame_values(val.get("rotateZ"))?,
        focal_length: parse_frame_values(val.get("focalLength"))?,
        film_back_width: parse_frame_values(val.get("filmBackWidth"))?,
        film_back_height: parse_frame_values(val.get("filmBackHeight"))?,
        film_back_offset_x: parse_frame_values(val.get("filmBackOffsetX"))?,
        film_back_offset_y: parse_frame_values(val.get("filmBackOffsetY"))?,
    })
}

fn parse_frame_values(val: Option<&JsonValue>) -> Result<Vec<(i64, f64)>> {
    let arr = match val {
        Some(v) => v.as_array().context("attr value must be an array")?,
        None => return Ok(Vec::new()),
    };

    let mut result = Vec::with_capacity(arr.len());
    for item in arr {
        let pair = item
            .as_array()
            .context("frame/value pair must be an array")?;
        if pair.len() != 2 {
            bail!("frame/value pair must have exactly 2 elements");
        }
        let frame = pair[0].as_i64().context("frame must be an integer")?;
        let value = pair[1].as_f64().context("value must be a number")?;
        result.push((frame, value));
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn test_data_dir() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("..")
            .join("..")
            .join("tests")
            .join("data")
            .join("mmcamera")
    }

    #[test]
    fn test_parse_default_camera_2_frames() {
        let path =
            test_data_dir().join("default_maya_camera_2_frames.mmcamera");
        let (version, data) = parse_mmcamera_file(&path).unwrap();
        assert_eq!(version, 1);
        assert_eq!(data.name, "camera1");
        assert_eq!(data.start_frame, 0);
        assert_eq!(data.end_frame, 1);
        assert_eq!(data.attr.translate_x.len(), 2);
        assert_eq!(data.attr.focal_length.len(), 2);
        assert!(data.image.file_path.is_none());
        assert!(data.image.width.is_none());
    }

    #[test]
    fn test_parse_default_persp_camera_2_frames() {
        let path =
            test_data_dir().join("default_maya_persp_camera_2_frames.mmcamera");
        let (version, data) = parse_mmcamera_file(&path).unwrap();
        assert_eq!(version, 1);
        assert_eq!(data.start_frame, 0);
        assert_eq!(data.end_frame, 1);
    }

    #[test]
    fn test_parse_default_persp_camera() {
        let path = test_data_dir().join("default_maya_persp_camera.mmcamera");
        let (version, data) = parse_mmcamera_file(&path).unwrap();
        assert_eq!(version, 1);
        assert_eq!(data.name, "persp");
        assert_eq!(data.start_frame, 1);
        assert_eq!(data.end_frame, 120);
        assert!(data.image.file_path.is_none());
    }

    #[test]
    fn test_parse_sta_animated_focal_length() {
        let path = test_data_dir().join("stA_animatedFocalLength.mmcamera");
        let (version, data) = parse_mmcamera_file(&path).unwrap();
        assert_eq!(version, 1);
        assert_eq!(data.name, "trackCam");
        assert_eq!(data.start_frame, 0);
        assert_eq!(data.end_frame, 94);
        assert_eq!(data.attr.focal_length.len(), 95);
        assert_eq!(data.image.width, Some(1936));
        assert_eq!(data.image.height, Some(1288));
        assert!(data.image.file_path.is_some());
    }

    #[test]
    fn test_parse_sta_copy_camera() {
        let path = test_data_dir().join("stA_copyCamera.mmcamera");
        let (version, data) = parse_mmcamera_file(&path).unwrap();
        assert_eq!(version, 1);
        assert!(data.attr.translate_x.len() > 0);
    }

    #[test]
    fn test_roundtrip_all_files() {
        use crate::mmcamera_writer::generate_mmcamera_string;

        let dir = test_data_dir();
        for entry in std::fs::read_dir(&dir).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.extension().map_or(true, |e| e != "mmcamera") {
                continue;
            }

            let (version, data) = parse_mmcamera_file(&path).unwrap();
            let written = generate_mmcamera_string(&data);
            let (version2, data2) = parse_mmcamera_string(&written).unwrap();

            assert_eq!(version, version2, "version mismatch for {:?}", path);
            assert_eq!(data.name, data2.name, "name mismatch for {:?}", path);
            assert_eq!(
                data.start_frame, data2.start_frame,
                "start_frame mismatch for {:?}",
                path
            );
            assert_eq!(
                data.end_frame, data2.end_frame,
                "end_frame mismatch for {:?}",
                path
            );
            assert_eq!(
                data.attr.translate_x.len(),
                data2.attr.translate_x.len(),
                "translate_x length mismatch for {:?}",
                path
            );
            assert_eq!(
                data.attr.focal_length.len(),
                data2.attr.focal_length.len(),
                "focal_length length mismatch for {:?}",
                path
            );
        }
    }
}
