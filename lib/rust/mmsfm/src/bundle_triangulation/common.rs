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

use anyhow::{anyhow, Result};
use nalgebra::{Point2, Point3, RealField, Vector3};

use crate::bundle_triangulation::{
    TriangulateDataLineLine, TriangulatorLineLine,
};
use crate::camera_relative_pose::RelativePoseInfo;
use crate::datatype::conversions::uv_point_to_camera_coord_point_inverted;
use crate::datatype::{CameraIntrinsics, CameraPose, UnitValue, UvPoint2};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Triangulation result referencing pre-allocated storage.
#[derive(Debug)]
pub struct TriangulationResult<'a, T: RealField + Copy> {
    // TODO: Change Point3 datatype to ScenePoint3.
    pub points: &'a [Point3<T>],
    pub errors: &'a [T],
    pub valid: &'a [bool],
}

/// Triangulation algorithm trait for batch processing.
pub trait Triangulator<T: RealField + Copy> {
    /// Input data type for this triangulation method.
    type InputData;

    /// Result type with method-specific metrics.
    type Result<'a>: AsRef<TriangulationResult<'a, T>>
    where
        Self: 'a;

    /// Create with initial capacity.
    fn new(initial_capacity: usize) -> Self;

    /// Ensure buffers handle at least `required_capacity` triangulations.
    fn reserve(&mut self, required_capacity: usize);

    /// Triangulate multiple 3D points.
    fn triangulate_points<'a>(
        &'a mut self,
        input_data: &Self::InputData,
    ) -> Self::Result<'a>;

    /// Get current buffer capacity.
    fn capacity(&self) -> usize;
}

/// Pre-allocated storage shared by all triangulation methods.
pub struct TriangulationStorage<T: RealField + Copy> {
    pub triangulated_points: Vec<Point3<T>>,
    pub errors: Vec<T>,
    pub valid_flags: Vec<bool>,
    pub capacity: usize,
}

impl<T: RealField + Copy> TriangulationStorage<T> {
    /// Create with initial capacity.
    pub fn new(initial_capacity: usize) -> Self {
        Self {
            triangulated_points: Vec::with_capacity(initial_capacity),
            errors: Vec::with_capacity(initial_capacity),
            valid_flags: Vec::with_capacity(initial_capacity),
            capacity: initial_capacity,
        }
    }

    /// Ensure storage handles at least `required_capacity` triangulations.
    pub fn reserve(&mut self, required_capacity: usize) {
        if required_capacity > self.capacity {
            let additional = required_capacity - self.capacity;
            self.triangulated_points.reserve(additional);
            self.errors.reserve(additional);
            self.valid_flags.reserve(additional);
            self.capacity = required_capacity;
        }
    }

    /// Resize storage to exactly `size` elements.
    ///
    /// # Safety
    /// Sets vector lengths directly without initialization.
    pub unsafe fn resize_to(&mut self, size: usize) {
        self.triangulated_points.set_len(size);
        self.errors.set_len(size);
        self.valid_flags.set_len(size);
    }

    /// Get a result view of the first `n` elements.
    pub fn get_result(&self, n: usize) -> TriangulationResult<'_, T> {
        TriangulationResult {
            points: &self.triangulated_points[..n],
            errors: &self.errors[..n],
            valid: &self.valid_flags[..n],
        }
    }

    /// Mark the result at `index` as invalid.
    pub fn mark_invalid(&mut self, index: usize) {
        self.triangulated_points[index] = Point3::origin();
        self.errors[index] = T::max_value().unwrap_or(T::one());
        self.valid_flags[index] = false;
    }

    /// Set the result at `index`.
    pub fn set_result(
        &mut self,
        index: usize,
        point: Point3<T>,
        error: T,
        valid: bool,
    ) {
        self.triangulated_points[index] = point;
        self.errors[index] = error;
        self.valid_flags[index] = valid;
    }
}

/// Returns true if the point is in front of both cameras (negative Z in camera space).
pub fn is_point_in_front_of_cameras(
    point_3d: &Point3<f64>,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
) -> bool {
    // Transform point to camera coordinates.
    let point_a_cam = pose_a.apply_transform(point_3d);
    let point_b_cam = pose_b.apply_transform(point_3d);

    // Maya convention: -Z is forward, so negative Z means in front.
    point_a_cam.z < 0.0 && point_b_cam.z < 0.0
}

/// Returns true if the triangulation quality is acceptable.
pub fn is_triangulation_quality_good(
    point_3d: &Point3<f64>,
    point_a: Point2<f64>,
    point_b: Point2<f64>,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
) -> bool {
    is_triangulation_quality_good_with_diagnostics(
        point_3d, point_a, point_b, pose_a, pose_b,
    )
    .0
}

/// Returns the angle (radians) between the two camera rays to the point.
///
/// `point_a` and `point_b` must be in normalized camera coordinates.
pub fn calculate_point_angle_radian(
    // TODO: Convert Point2 here to a normalized camera coordinate data type.
    point_a: Point2<f64>,
    point_b: Point2<f64>,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
) -> f64 {
    // NOTE: point_a and point_b are expected to already be normalized
    // camera coordinates.

    let camera_ray_a = Vector3::new(point_a.x, point_a.y, -1.0).normalize();
    let camera_ray_b = Vector3::new(point_b.x, point_b.y, -1.0).normalize();

    // Transform rays to world space.
    let ray_a_world = pose_a.rotation().transpose() * camera_ray_a;
    let ray_b_world = pose_b.rotation().transpose() * camera_ray_b;

    let dot_product = ray_a_world.dot(&ray_b_world).clamp(-1.0, 1.0);
    dot_product.acos()
}

const ANGLE_RADIAN_MINIMUM: f64 = 1.0_f64.to_radians();
const ANGLE_RADIAN_MAXIMUM: f64 = 90.0_f64.to_radians();

pub fn is_triangulation_quality_good_with_diagnostics(
    point_3d: &Point3<f64>,
    point_a: Point2<f64>,
    point_b: Point2<f64>,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
) -> (bool, String) {
    // Check 1: Reasonable depth in both cameras (Maya convention: -Z forward)
    let depth_a = pose_a.apply_transform(point_3d).z;
    let depth_b = pose_b.apply_transform(point_3d).z;

    // Depths should be negative (in front of camera) and reasonable.
    if depth_a >= 0.0 || depth_b >= 0.0 {
        let reason = format!(
            "behind camera (depth_a={:.3}, depth_b={:.3})",
            depth_a, depth_b
        );
        mm_eprintln_debug!("      Triangulation FAIL: {}", reason);
        return (false, reason);
    }

    // Check 2: Triangulation angle should be reasonable (not too small)
    let angle_radian =
        calculate_point_angle_radian(point_a, point_b, pose_a, pose_b);

    // Reject triangulations with very small angles (poor triangulation geometry).
    let angle_radian_min = ANGLE_RADIAN_MINIMUM;
    let angle_radian_max = ANGLE_RADIAN_MAXIMUM;
    if angle_radian < angle_radian_min || angle_radian > angle_radian_max {
        let reason = format!(
            "bad angle ({:.2} degrees, range=[{} degrees, {} degrees])",
            angle_radian.to_degrees(),
            angle_radian_min.to_degrees(),
            angle_radian_max.to_degrees()
        );
        mm_eprintln_debug!("      Triangulation FAIL: {}", reason);
        return (false, reason);
    }

    mm_eprintln_debug!(
        "      Triangulation OK: depth_a={:.3}, depth_b={:.3}, angle={:.2}deg",
        depth_a,
        depth_b,
        angle_radian.to_degrees()
    );
    (
        true,
        format!("OK (angle={:.2}deg)", angle_radian.to_degrees()),
    )
}

/// Triangulates multiple 3D points in batch and validates quality.
///
/// Input points must be in normalized camera coordinates (focal length and
/// principal point already removed). Returns the number of valid triangulations.
pub fn triangulate_points_batch(
    // TODO: Change the Point2 data type to the expected data type -
    // what are the coordinate system for the points here?
    points_a: &[Point2<f64>],
    points_b: &[Point2<f64>],
    pose_a: &CameraPose,
    pose_b: &CameraPose,
    triangulator: &mut TriangulatorLineLine<f64>,
    triangulate_data: &mut TriangulateDataLineLine<f64>,
    triangulated_points: &mut [Point3<f64>],
    triangulated_points_valid: &mut [bool],
) -> Result<usize> {
    assert_eq!(points_a.len(), points_b.len());
    assert_eq!(points_a.len(), triangulated_points.len());
    assert_eq!(points_a.len(), triangulated_points_valid.len());

    // Prepare output vectors.
    for point in triangulated_points.iter_mut() {
        point.x = 0.0;
        point.y = 0.0;
        point.z = 0.0;
    }
    for valid in triangulated_points_valid.iter_mut() {
        *valid = false;
    }

    let num_points = points_a.len();
    if num_points == 0 {
        return Ok(0);
    }

    // Check for degenerate case: same camera position.
    let distance_between_cameras = (*pose_a.center() - *pose_b.center()).norm();
    if distance_between_cameras < 1e-10 {
        return Err(anyhow!(
            "Cannot triangulate: cameras are at the same position."
        ));
    }

    triangulator.reserve(num_points);

    let camera_center_a = *pose_a.center();
    let camera_center_b = *pose_b.center();

    // Camera-to-world rotations.
    let rotation_transpose_a = pose_a.rotation().transpose();
    let rotation_transpose_b = pose_b.rotation().transpose();

    triangulate_data.clear();

    for (point_a, point_b) in points_a.iter().zip(points_b.iter()) {
        // Convert normalized camera coordinates to world-space rays.
        // Maya convention: camera looks down -Z axis.
        let ray_camera_a = Vector3::new(point_a.x, point_a.y, -1.0).normalize();
        let ray_camera_b = Vector3::new(point_b.x, point_b.y, -1.0).normalize();

        let ray_world_a = rotation_transpose_a * ray_camera_a;
        let ray_world_b = rotation_transpose_b * ray_camera_b;

        let scene_origin_a = crate::datatype::ScenePoint3::new(
            crate::datatype::SceneUnit(camera_center_a.x),
            crate::datatype::SceneUnit(camera_center_a.y),
            crate::datatype::SceneUnit(camera_center_a.z),
        );
        let scene_direction_a = crate::datatype::SceneVector3::new(
            crate::datatype::SceneUnit(ray_world_a.x),
            crate::datatype::SceneUnit(ray_world_a.y),
            crate::datatype::SceneUnit(ray_world_a.z),
        );

        let scene_origin_b = crate::datatype::ScenePoint3::new(
            crate::datatype::SceneUnit(camera_center_b.x),
            crate::datatype::SceneUnit(camera_center_b.y),
            crate::datatype::SceneUnit(camera_center_b.z),
        );
        let scene_direction_b = crate::datatype::SceneVector3::new(
            crate::datatype::SceneUnit(ray_world_b.x),
            crate::datatype::SceneUnit(ray_world_b.y),
            crate::datatype::SceneUnit(ray_world_b.z),
        );

        triangulate_data.add_ray_pair(
            scene_origin_a,
            scene_direction_a,
            scene_origin_b,
            scene_direction_b,
        );
    }

    let result = triangulator.triangulate_points(triangulate_data);
    let triangulation_results = result.as_ref();

    // Validate each result.
    let mut successful_count = 0;
    for (result_idx, &is_valid) in
        triangulation_results.valid.iter().enumerate()
    {
        if result_idx < num_points && is_valid {
            let triangulated_point = &triangulation_results.points[result_idx];
            let point_a = points_a[result_idx];
            let point_b = points_b[result_idx];

            let is_point_finite =
                triangulated_point.coords.iter().all(|&x| x.is_finite());
            if is_point_finite {
                let triangulation_is_good =
                    is_triangulation_quality_good_with_diagnostics(
                        triangulated_point,
                        point_a,
                        point_b,
                        pose_a,
                        pose_b,
                    )
                    .0;

                if triangulation_is_good {
                    triangulated_points[result_idx] = *triangulated_point;
                    triangulated_points_valid[result_idx] = true;
                    successful_count += 1;
                }
            }
        }
    }

    Ok(successful_count)
}

/// Triangulates 3D points from UV coordinates and a relative camera pose.
///
/// Returns the number of valid triangulations.
pub fn triangulate_points_from_relative_pose(
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    relative_pose_info: &RelativePoseInfo,
    // TODO: Switch Point3 to ScenePoint3.
    out_triangulated_points: &mut [Point3<f64>],
    out_triangulated_points_validity: &mut [bool],
) -> Result<usize> {
    assert_eq!(uv_coords_a.len(), uv_coords_b.len());
    assert_eq!(uv_coords_a.len(), out_triangulated_points.len());
    assert_eq!(uv_coords_a.len(), out_triangulated_points_validity.len());

    let num_points = uv_coords_a.len();
    if num_points == 0 {
        return Ok(0);
    }

    let pose_a = CameraPose::default(); // First camera at origin.
    let pose_b = &relative_pose_info.relative_pose;

    // Convert UV coordinates to normalized camera coordinates.
    // TODO: Use existing conversion functions for conversions.
    let normalized_points_a: Vec<Point2<f64>> = uv_coords_a
        .iter()
        .map(|uv_a| {
            let normalized_a =
                uv_point_to_camera_coord_point_inverted(*uv_a, intrinsics_a);
            Point2::new(normalized_a.x.value(), normalized_a.y.value())
        })
        .collect();

    let normalized_points_b: Vec<Point2<f64>> = uv_coords_b
        .iter()
        .map(|uv_b| {
            let normalized_b =
                uv_point_to_camera_coord_point_inverted(*uv_b, intrinsics_b);
            Point2::new(normalized_b.x.value(), normalized_b.y.value())
        })
        .collect();

    let mut triangulator = TriangulatorLineLine::new(num_points);
    let mut triangulate_data =
        TriangulateDataLineLine::with_capacity(num_points);
    let successful_count = triangulate_points_batch(
        &normalized_points_a,
        &normalized_points_b,
        &pose_a,
        pose_b,
        &mut triangulator,
        &mut triangulate_data,
        out_triangulated_points,
        out_triangulated_points_validity,
    )?;

    Ok(successful_count)
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::Matrix3;

    #[test]
    fn test_is_point_in_front_of_cameras() {
        let pose_a = CameraPose::default(); // At origin.
        let rotation_b = Matrix3::identity();
        let center_b = Vector3::new(1.0, 0.0, 0.0); // Moved along X.
        let pose_b = CameraPose::new(rotation_b, center_b.into());

        // Point in front of both cameras (Maya convention: negative Z is forward).
        let point_front = Vector3::new(0.5, 0.0, -2.0);
        assert!(is_point_in_front_of_cameras(
            &point_front.into(),
            &pose_a,
            &pose_b
        ));

        // Point behind first camera (Maya convention: positive Z is behind).
        let point_behind_a = Vector3::new(0.5, 0.0, 1.0);
        assert!(!is_point_in_front_of_cameras(
            &point_behind_a.into(),
            &pose_a,
            &pose_b
        ));
    }
}
