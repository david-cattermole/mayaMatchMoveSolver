//
// Copyright (C) 2026 David Cattermole.
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

//! Kuper ASCII file format writer for camera animation data.
//!
//! The Kuper file format is used by motion control systems in film
//! production.
//!
//! This module writes camera position and rotation data in Kuper
//! ASCII format.
//!
//! ## File Format
//!
//! The Kuper ASCII format consists of:
//! - Header line: `Axes = frame, VTrack, VEW, VNS, Vpan, VTilt, VRoll, focal`
//! - Data lines: Space-separated values for each frame
//!
//! ## Coordinate System
//!
//! The Kuper format uses motion control terminology:
//! - **Track**: Camera dolly movement (along the track direction)
//! - **EW**: East-West movement (horizontal perpendicular to track)
//! - **NS**: North-South movement (vertical, up/down)
//! - **Pan**: Rotation around vertical axis (yaw)
//! - **Tilt**: Rotation around horizontal axis (pitch)
//! - **Roll**: Camera roll around view axis
//!
//! ## Maya Coordinate Mapping
//!
//! Maya uses a right-handed coordinate system with +Y up and -Z as camera view direction.
//! The mapping from Maya to Kuper is:
//! - Frame -> frame column
//! - Maya translate_z -> Kuper Track (Tz, no negation)
//! - Maya translate_x -> Kuper EW (Tx)
//! - Maya translate_y -> Kuper NS (Ty)
//! - Maya -rotate_y -> Kuper Pan (-Ry, negated)
//! - Maya rotate_x -> Kuper Tilt (Rx)
//! - Maya -rotate_z -> Kuper Roll (-Rz, negated)
//! - focal -> focal length column

use anyhow::{Context, Result};
use nalgebra::Matrix3;
use std::f64::consts::PI;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

/// Convert degrees to radians.
#[inline]
#[allow(dead_code)]
fn degrees_to_radians(degrees: f64) -> f64 {
    degrees * PI / 180.0
}

/// Convert radians to degrees.
#[inline]
fn radians_to_degrees(radians: f64) -> f64 {
    radians * 180.0 / PI
}

/// Camera frame data in Kuper format.
///
/// All position values are in scene units (typically centimeters or
/// inches depending on the production).
///
/// All rotation values are in degrees.
#[derive(Debug, Clone, Copy)]
pub struct KuperFrameData {
    /// Frame number.
    pub frame: u32,
    /// Track position (dolly along camera view direction).
    pub track: f64,
    /// East-West position (horizontal offset).
    pub ew: f64,
    /// North-South position (vertical offset).
    pub ns: f64,
    /// Pan rotation in degrees (around vertical axis).
    pub pan: f64,
    /// Tilt rotation in degrees (around horizontal axis).
    pub tilt: f64,
    /// Roll rotation in degrees (around camera view axis).
    pub roll: f64,
    /// Focal length in millimeters.
    pub focal: f64,
}

impl Default for KuperFrameData {
    fn default() -> Self {
        Self {
            frame: 0,
            track: 0.0,
            ew: 0.0,
            ns: 0.0,
            pan: 0.0,
            tilt: 0.0,
            roll: 0.0,
            focal: 0.0,
        }
    }
}

/// Extract ZXY Euler angles from a rotation matrix.
///
/// Maya cameras use ZXY rotation order by default.
/// This function extracts (rotate_x, rotate_y, rotate_z) in degrees.
///
/// # Arguments
/// * `rotation` - 3x3 rotation matrix (world-to-camera)
///
/// # Returns
/// Tuple of (rotate_x, rotate_y, rotate_z) in degrees
pub fn extract_zxy_euler_angles(rotation: &Matrix3<f64>) -> (f64, f64, f64) {
    // For a ZXY rotation order, the matrix is: R = Ry * Rx * Rz
    //
    // The rotation matrix for ZXY order is:
    // [  cy*cz + sx*sy*sz,   cz*sx*sy - cy*sz,   cx*sy ]
    // [  cx*sz,              cx*cz,              -sx   ]
    // [  cy*sx*sz - cz*sy,   cy*cz*sx + sy*sz,   cx*cy ]
    //
    // Where cx = cos(rx), sx = sin(rx), etc.
    //
    // From this we can extract:
    // rx = asin(-m[1,2]) = asin(-rotation[(1,2)])
    // ry = atan2(m[0,2], m[2,2]) = atan2(rotation[(0,2)], rotation[(2,2)])
    // rz = atan2(m[1,0], m[1,1]) = atan2(rotation[(1,0)], rotation[(1,1)])

    // However, CameraPose stores world-to-camera rotation, and we need
    // Maya's object rotation which is the transpose (camera-to-world).
    let maya_rotation = rotation.transpose();

    // Extract angles from ZXY decomposition.
    let sin_rx = -maya_rotation[(1, 2)];

    // Clamp to avoid numerical issues at gimbal lock.
    let sin_rx_clamped = sin_rx.clamp(-1.0, 1.0);
    let rx = sin_rx_clamped.asin();

    // Check for gimbal lock (when cos(rx) is close to zero).
    let cos_rx = rx.cos();
    let (ry, rz) = if cos_rx.abs() > 1e-6 {
        // Normal case.
        let ry = maya_rotation[(0, 2)].atan2(maya_rotation[(2, 2)]);
        let rz = maya_rotation[(1, 0)].atan2(maya_rotation[(1, 1)]);
        (ry, rz)
    } else {
        // Gimbal lock: rx is approximately +/-90 degrees.
        //
        // In this case, ry and rz are coupled. We set rz = 0 and solve for ry.
        let ry = (-maya_rotation[(2, 0)]).atan2(maya_rotation[(0, 0)]);
        (ry, 0.0)
    };

    (
        radians_to_degrees(rx),
        radians_to_degrees(ry),
        radians_to_degrees(rz),
    )
}

/// Convert Maya camera pose to Kuper frame data.
///
/// # Arguments
/// * `frame` - Frame number
/// * `center` - Camera center position in Maya world coordinates
/// * `rotation` - Camera rotation matrix (world-to-camera)
/// * `focal` - Focal length in millimeters
///
/// # Returns
/// KuperFrameData with position and rotation values
pub fn maya_pose_to_kuper(
    frame: u32,
    center: &nalgebra::Point3<f64>,
    rotation: &Matrix3<f64>,
    focal: f64,
) -> KuperFrameData {
    // Extract Euler angles from rotation matrix.
    let (rotate_x, rotate_y, rotate_z) = extract_zxy_euler_angles(rotation);

    // Map Maya coordinates to Kuper:
    // order is = Frame, Tz, Tx, Ty, -Ry, Rx, -Rz, focal
    KuperFrameData {
        frame,
        track: center.z,
        ew: center.x,
        ns: center.y,
        pan: -rotate_y,
        tilt: rotate_x,
        roll: -rotate_z,
        focal,
    }
}

/// Write camera animation data to a Kuper ASCII file.
///
/// # Arguments
/// * `file_path` - Output file path
/// * `frames` - Vector of KuperFrameData, one per frame
///
/// # Returns
/// Result indicating success or failure
pub fn write_kuper_file<P: AsRef<Path>>(
    file_path: P,
    frames: &[KuperFrameData],
) -> Result<()> {
    let file_path = file_path.as_ref();
    let file = File::create(file_path).with_context(|| {
        format!("Failed to create Kuper file: {}", file_path.display())
    })?;
    let mut writer = BufWriter::new(file);

    // Write header line
    writeln!(
        writer,
        "Axes = frame, VTrack, VEW, VNS, Vpan, VTilt, VRoll, focal"
    )
    .with_context(|| "Failed to write Kuper header")?;

    // Write data lines
    for frame_data in frames {
        writeln!(
            writer,
            "{:.6} {:.9} {:.9} {:.9} {:.9} {:.9} {:.9} {:.9}",
            frame_data.frame as f64,
            frame_data.track,
            frame_data.ew,
            frame_data.ns,
            frame_data.pan,
            frame_data.tilt,
            frame_data.roll,
            frame_data.focal
        )
        .with_context(|| {
            format!("Failed to write frame {} data", frame_data.frame)
        })?;
    }

    writer
        .flush()
        .with_context(|| "Failed to flush Kuper file")?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;
    use nalgebra::{Matrix3, Point3};

    #[test]
    fn test_kuper_frame_data_default() {
        let data = KuperFrameData::default();
        assert_eq!(data.frame, 0);
        assert_eq!(data.track, 0.0);
        assert_eq!(data.ew, 0.0);
        assert_eq!(data.ns, 0.0);
        assert_eq!(data.pan, 0.0);
        assert_eq!(data.tilt, 0.0);
        assert_eq!(data.roll, 0.0);
        assert_eq!(data.focal, 0.0);
    }

    #[test]
    fn test_extract_zxy_euler_identity() {
        // Identity rotation should give zero angles.
        let rotation = Matrix3::identity();
        let (rx, ry, rz) = extract_zxy_euler_angles(&rotation);
        assert_relative_eq!(rx, 0.0, epsilon = 1e-10);
        assert_relative_eq!(ry, 0.0, epsilon = 1e-10);
        assert_relative_eq!(rz, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_extract_zxy_euler_y_rotation() {
        // Test 45 degree rotation around Y axis.
        let angle = 45.0 * PI / 180.0;
        let (sin_y, cos_y) = angle.sin_cos();

        // Maya object rotation for +45 degrees Y.
        let maya_rot =
            Matrix3::new(cos_y, 0.0, sin_y, 0.0, 1.0, 0.0, -sin_y, 0.0, cos_y);

        // CameraPose stores world-to-camera (transpose of Maya object rotation).
        let camera_rotation = maya_rot.transpose();

        let (rx, ry, rz) = extract_zxy_euler_angles(&camera_rotation);
        assert_relative_eq!(rx, 0.0, epsilon = 1e-6);
        assert_relative_eq!(ry, 45.0, epsilon = 1e-6);
        assert_relative_eq!(rz, 0.0, epsilon = 1e-6);
    }

    #[test]
    fn test_maya_pose_to_kuper_translation() {
        let frame = 1;
        let center = Point3::new(10.0, 20.0, -30.0);
        let rotation = Matrix3::identity();

        let kuper = maya_pose_to_kuper(frame, &center, &rotation, 35.0);

        assert_eq!(kuper.frame, 1);
        assert_relative_eq!(kuper.ew, 10.0, epsilon = 1e-10);
        assert_relative_eq!(kuper.ns, 20.0, epsilon = 1e-10);
        assert_relative_eq!(kuper.track, -30.0, epsilon = 1e-10); // Tz directly
        assert_relative_eq!(kuper.focal, 35.0, epsilon = 1e-10);
    }

    #[test]
    fn test_write_kuper_file() {
        let frames = vec![
            KuperFrameData {
                frame: 1,
                track: 0.0,
                ew: 0.0,
                ns: 5.0,
                pan: 0.0,
                tilt: 0.0,
                roll: 0.0,
                focal: 35.0,
            },
            KuperFrameData {
                frame: 2,
                track: 1.0,
                ew: 0.5,
                ns: 5.0,
                pan: 2.0,
                tilt: 0.0,
                roll: 0.0,
                focal: 35.0,
            },
        ];

        let temp_dir = std::env::temp_dir();
        let temp_file = temp_dir.join("test_kuper.kup");

        let result = write_kuper_file(&temp_file, &frames);
        assert!(result.is_ok());

        // Read back and verify.
        let content = std::fs::read_to_string(&temp_file).unwrap();
        let lines: Vec<&str> = content.lines().collect();

        assert_eq!(
            lines[0],
            "Axes = frame, VTrack, VEW, VNS, Vpan, VTilt, VRoll, focal"
        );
        // Format: frame track ew ns pan tilt roll focal
        assert!(lines[1]
            .starts_with("1.000000 0.000000000 0.000000000 5.000000000"));
        assert!(lines[2]
            .starts_with("2.000000 1.000000000 0.500000000 5.000000000"));

        // Clean up.
        let _ = std::fs::remove_file(&temp_file);
    }
}
