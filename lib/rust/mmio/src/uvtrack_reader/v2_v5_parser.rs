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

//! Parser for UVTrack v2-v5 (JSON) formats.

use anyhow::Result;

use crate::json_parser::{parse_json, JsonValue};

use super::types::*;

/// Determine format version from parsed JSON.
pub fn determine_format_version_from_json(
    json: &JsonValue,
) -> UVTrackFormatVersion {
    json.get("version")
        .and_then(|v| v.as_i64())
        .map(|v| UVTrackFormatVersion::from_i32(v as i32))
        .unwrap_or(UVTrackFormatVersion::Unknown)
}

/// Parse a v2-v5 JSON UV track string.
pub fn parse_json_string(content: &str) -> Result<(FileInfo, MarkersData)> {
    let json = parse_json(content).map_err(|e| {
        UVTrackError::ParseError(format!("JSON parse error: {e}"))
    })?;

    let version = determine_format_version_from_json(&json);
    match version {
        UVTrackFormatVersion::Version2
        | UVTrackFormatVersion::Version3
        | UVTrackFormatVersion::Version4
        | UVTrackFormatVersion::Version5 => {}
        _ => {
            return Err(UVTrackError::InvalidFormat(format!(
                "Expected JSON UV track version 2-5, got {:?}",
                version
            ))
            .into());
        }
    }

    let is_undistorted = json
        .get("is_undistorted")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);

    let has_distorted = version.to_i32() >= 3;

    // Parse points.
    let points_json = json
        .get("points")
        .and_then(|v| v.as_array())
        .ok_or_else(|| {
            UVTrackError::InvalidFormat("missing 'points' array".to_string())
        })?;

    if points_json.is_empty() {
        return Err(UVTrackError::NoPoints.into());
    }

    let mut markers = MarkersData::with_capacity(points_json.len());
    let mut any_bundle_positions = false;

    for point in points_json {
        let name = point
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let set_name = point.get("set_name").and_then(|v| {
            if v.is_null() {
                None
            } else {
                v.as_str().map(|s| s.to_string())
            }
        });

        let id = point.get("id").and_then(|v| {
            if v.is_null() {
                None
            } else {
                v.as_str().map(|s| s.to_string())
            }
        });

        // Parse 3D data (v3+)
        let point_3d = point.get("3d").and_then(|v| {
            if v.is_null() {
                return None;
            }
            let obj = v.as_object()?;
            if obj.is_empty() {
                return None;
            }
            let x = v.get("x").and_then(|n| {
                if n.is_null() {
                    None
                } else {
                    n.as_f64()
                }
            });
            let y = v.get("y").and_then(|n| {
                if n.is_null() {
                    None
                } else {
                    n.as_f64()
                }
            });
            let z = v.get("z").and_then(|n| {
                if n.is_null() {
                    None
                } else {
                    n.as_f64()
                }
            });
            let x_lock = v.get("x_lock").and_then(|n| n.as_bool());
            let y_lock = v.get("y_lock").and_then(|n| n.as_bool());
            let z_lock = v.get("z_lock").and_then(|n| n.as_bool());

            if x.is_some() || y.is_some() || z.is_some() {
                any_bundle_positions = true;
            }

            Some(Point3dData {
                x,
                y,
                z,
                x_lock,
                y_lock,
                z_lock,
            })
        });

        // Parse per-frame data
        let per_frame = point
            .get("per_frame")
            .and_then(|v| v.as_array())
            .ok_or_else(|| {
                UVTrackError::InvalidFormat(format!(
                    "missing 'per_frame' for point '{name}'"
                ))
            })?;

        let mut frame_data = FrameData::with_capacity(per_frame.len());

        for frame_entry in per_frame {
            let frame = frame_entry
                .get("frame")
                .and_then(|v| v.as_i64())
                .ok_or_else(|| {
                    UVTrackError::ParseError(
                        "missing 'frame' in per_frame entry".to_string(),
                    )
                })? as FrameNumber;

            let weight = frame_entry
                .get("weight")
                .and_then(|v| v.as_f64())
                .unwrap_or(1.0);

            let pos = frame_entry
                .get("pos")
                .and_then(|v| v.as_array())
                .ok_or_else(|| {
                    UVTrackError::ParseError(
                        "missing 'pos' in per_frame entry".to_string(),
                    )
                })?;

            if pos.len() < 2 {
                return Err(UVTrackError::ParseError(
                    "'pos' must have at least 2 elements".to_string(),
                )
                .into());
            }

            let u = pos[0].as_f64().unwrap_or(0.0);
            let v = pos[1].as_f64().unwrap_or(0.0);

            if has_distorted {
                if let Some(pos_dist) =
                    frame_entry.get("pos_dist").and_then(|v| v.as_array())
                {
                    if pos_dist.len() >= 2 {
                        let u_dist = pos_dist[0].as_f64().unwrap_or(0.0);
                        let v_dist = pos_dist[1].as_f64().unwrap_or(0.0);
                        frame_data.push_with_distorted(
                            frame, u, v, weight, u_dist, v_dist,
                        );
                        continue;
                    }
                }
            }

            frame_data.push(frame, u, v, weight);
        }

        markers.push_marker_full(name, frame_data, set_name, id, point_3d);
    }

    // Parse camera data (v4+).
    let camera = if version.to_i32() >= 4 {
        json.get("camera").and_then(|cam| {
            let resolution_arr = cam.get("resolution")?.as_array()?;
            let film_back_arr = cam.get("film_back_cm")?.as_array()?;
            let lens_offset_arr =
                cam.get("lens_center_offset_cm")?.as_array()?;

            let resolution = [
                resolution_arr.get(0)?.as_i64()? as u32,
                resolution_arr.get(1)?.as_i64()? as u32,
            ];
            let film_back_cm = [
                film_back_arr.get(0)?.as_f64()?,
                film_back_arr.get(1)?.as_f64()?,
            ];
            let lens_center_offset_cm = [
                lens_offset_arr.get(0)?.as_f64()?,
                lens_offset_arr.get(1)?.as_f64()?,
            ];

            let mut focal_lengths = Vec::new();
            if let Some(per_frame) =
                cam.get("per_frame").and_then(|v| v.as_array())
            {
                for entry in per_frame {
                    let frame = entry.get("frame")?.as_i64()? as FrameNumber;
                    let fl = entry.get("focal_length_cm")?.as_f64()?;
                    focal_lengths.push((frame, fl));
                }
            }

            Some(CameraData {
                resolution,
                film_back_cm,
                lens_center_offset_cm,
                focal_lengths,
            })
        })
    } else {
        None
    };

    // Parse scene data (v5).
    let scene = if version == UVTrackFormatVersion::Version5 {
        json.get("scene").and_then(|s| {
            let transform_arr = s.get("transform")?.as_array()?;
            if transform_arr.len() != 16 {
                return None;
            }
            let mut transform = [0.0f64; 16];
            for (i, val) in transform_arr.iter().enumerate() {
                transform[i] = val.as_f64()?;
            }
            Some(SceneData { transform })
        })
    } else {
        None
    };

    // Parse point group data (v5).
    let point_group = if version == UVTrackFormatVersion::Version5 {
        json.get("point_group").and_then(|pg| {
            let name = pg.get("name")?.as_str()?.to_string();
            let group_type = pg.get("type")?.as_str()?.to_string();

            let mut transforms = Vec::new();
            if let Some(tf_obj) =
                pg.get("transform").and_then(|v| v.as_object())
            {
                for (frame_str, matrix_val) in tf_obj {
                    let frame: FrameNumber = frame_str.parse().ok()?;
                    let matrix_arr = matrix_val.as_array()?;
                    if matrix_arr.len() != 16 {
                        continue;
                    }
                    let mut mat = [0.0f64; 16];
                    for (i, val) in matrix_arr.iter().enumerate() {
                        mat[i] = val.as_f64().unwrap_or(0.0);
                    }
                    transforms.push((frame, mat));
                }
                // Sort by frame number since BTreeMap iteration may
                // not match numeric order of string keys.
                transforms.sort_by_key(|(f, _)| *f);
            }

            Some(PointGroupData {
                name,
                group_type,
                transforms,
            })
        })
    } else {
        None
    };

    let file_info = FileInfo {
        version,
        marker_undistorted: is_undistorted || !has_distorted,
        marker_distorted: has_distorted,
        bundle_positions: any_bundle_positions,
        camera,
        scene,
        point_group,
    };

    Ok((file_info, markers))
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::{bail, Result};
    use std::ffi::OsStr;
    use std::fs::File;
    use std::io::Read;
    use std::path::PathBuf;

    fn find_data_dir() -> Result<PathBuf> {
        let mut directory = PathBuf::from(std::env::current_exe().unwrap());
        assert!(directory.pop()); // deps
        assert!(directory.pop()); // debug
        assert!(directory.pop()); // target
        assert!(directory.pop()); // project root
        directory.push("tests");
        directory.push("data");
        directory.push("uvtrack");
        if directory.is_dir() {
            Ok(directory)
        } else {
            bail!("Could not find data directory {:?}.", directory)
        }
    }

    fn read_file(file_name: &str) -> Result<String> {
        let data_dir = find_data_dir()?;
        let mut path = data_dir;
        path.push(file_name);
        if !path.is_file() {
            bail!("Could not find file {:?}", path);
        }
        let mut file = File::open(&path)?;
        let mut buffer = String::new();
        file.read_to_string(&mut buffer)?;
        Ok(buffer)
    }

    #[test]
    fn test_parse_v2_sta() -> Result<()> {
        let content = read_file("stA.uv")?;
        let (file_info, markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version2);
        assert!(!file_info.marker_distorted);
        assert!(file_info.marker_undistorted);
        assert_eq!(markers.len(), 14);

        // Check first marker.
        assert_eq!(markers.names[0], "01");
        assert!(!markers.frame_data[0].is_empty());

        // Check first frame of first marker.
        let fd = &markers.frame_data[0];
        assert_eq!(fd.frames[0], 0);
        assert!((fd.u_coords[0] - 0.8486498665411976).abs() < 1e-12);
        assert!((fd.v_coords[0] - 0.4623098291673672).abs() < 1e-12);
        assert_eq!(fd.weights[0], 1.0);

        Ok(())
    }

    #[test]
    fn test_parse_v3() -> Result<()> {
        let content = read_file("test_v3.uv")?;
        let (file_info, markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version3);
        assert!(file_info.marker_distorted);
        assert_eq!(markers.len(), 1);
        assert_eq!(markers.names[0], "01");

        // v3 should have distorted coords.
        let fd = &markers.frame_data[0];
        assert!(fd.has_distorted());
        assert!(!fd.u_coords_dist.is_empty());

        Ok(())
    }

    #[test]
    fn test_parse_v3_with_3d_point() -> Result<()> {
        let content = read_file("test_v3_with_3d_point.uv")?;
        let (file_info, markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version3);
        assert!(file_info.bundle_positions);

        let p3d = markers.point_3d[0].as_ref().unwrap();
        assert!((p3d.x.unwrap() - (-0.123)).abs() < 1e-6);
        assert!((p3d.y.unwrap() - 0.123).abs() < 1e-6);
        assert!((p3d.z.unwrap() - 42.0).abs() < 1e-6);

        Ok(())
    }

    #[test]
    fn test_parse_v4() -> Result<()> {
        let content = read_file("test_v4.uv")?;
        let (file_info, markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version4);
        assert!(file_info.camera.is_some());

        let camera = file_info.camera.unwrap();
        assert_eq!(camera.resolution[0], 1280);
        assert_eq!(camera.resolution[1], 1080);
        assert!(!camera.focal_lengths.is_empty());

        assert!(!markers.is_empty());

        Ok(())
    }

    #[test]
    fn test_parse_v5_camera() -> Result<()> {
        let content = read_file("test_v5_pgroup_camera_single_point.uv")?;
        let (file_info, markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version5);
        assert!(file_info.scene.is_some());
        assert!(file_info.point_group.is_some());
        assert!(file_info.camera.is_some());

        let pg = file_info.point_group.unwrap();
        assert_eq!(pg.group_type, "CAMERA");
        assert!(!pg.transforms.is_empty());

        assert!(!markers.is_empty());

        Ok(())
    }

    #[test]
    fn test_parse_v5_object() -> Result<()> {
        let content = read_file("test_v5_pgroup_object_single_point.uv")?;
        let (file_info, _markers) = parse_json_string(&content)?;

        assert_eq!(file_info.version, UVTrackFormatVersion::Version5);
        let pg = file_info.point_group.unwrap();
        assert_eq!(pg.group_type, "OBJECT");

        Ok(())
    }

    #[test]
    fn test_determine_version_from_json() -> Result<()> {
        let content = read_file("stA.uv")?;
        let json = parse_json(&content).unwrap();
        let version = determine_format_version_from_json(&json);
        assert_eq!(version, UVTrackFormatVersion::Version2);

        let content = read_file("test_v3.uv")?;
        let json = parse_json(&content).unwrap();
        let version = determine_format_version_from_json(&json);
        assert_eq!(version, UVTrackFormatVersion::Version3);

        let content = read_file("test_v4.uv")?;
        let json = parse_json(&content).unwrap();
        let version = determine_format_version_from_json(&json);
        assert_eq!(version, UVTrackFormatVersion::Version4);

        Ok(())
    }
}
