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

//! Pre-bundle adjustment validation for filtering invalid or poorly-conditioned 3D bundles.
//!
//! Implements cheirality, MAD-based statistical outlier removal, and camera
//! position collapse detection to ensure bundle adjustment stability.

use mmcore::statistics::{SortedDataSliceOps, UnsortedDataSlice};
use mmio::uvtrack_reader::MarkersData;
use nalgebra::Point3;

use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Systems with fewer bundles than this are considered under-determined.
///
/// Bundle adjustment requires at least 6 bundles to constrain the camera
/// parameters (3 for translation, 3 for rotation).
const MINIMUM_BUNDLE_COUNT: usize = 6;

// ============================================================
// Configuration
// ============================================================

/// Configuration for pre-bundle adjustment validation thresholds.
#[derive(Debug, Clone)]
pub struct BundleValidationConfig {
    /// Enable cheirality check (points must be in front of all observing cameras).
    pub enable_cheirality: bool,
    /// Enable MAD-based statistical outlier removal.
    pub enable_mad_filtering: bool,
    /// MAD threshold multiplier for depth outlier detection.
    pub mad_threshold: f64,
}

impl Default for BundleValidationConfig {
    fn default() -> Self {
        Self {
            enable_cheirality: true,
            enable_mad_filtering: true,
            mad_threshold: 10.0,
        }
    }
}

/// Result of bundle validation containing statistics.
#[derive(Debug, Clone, Default)]
pub struct BundleValidationResult {
    /// Number of bundles before validation.
    pub initial_bundle_count: usize,
    /// Number of bundles after validation.
    pub final_bundle_count: usize,
    /// Bundles removed by cheirality check.
    pub removed_by_cheirality: usize,
    /// Bundles removed by MAD outlier check.
    pub removed_by_mad: usize,
}

impl BundleValidationResult {
    /// Total number of bundles removed.
    pub fn total_removed(&self) -> usize {
        self.initial_bundle_count - self.final_bundle_count
    }

    /// Percentage of bundles retained.
    pub fn retention_percentage(&self) -> f64 {
        if self.initial_bundle_count == 0 {
            return 100.0;
        }
        (self.final_bundle_count as f64 / self.initial_bundle_count as f64)
            * 100.0
    }
}

// ============================================================
// Helper Functions
// ============================================================

/// Compute camera centroid from all solved poses.
fn compute_camera_centroid(camera_poses: &CameraPoses) -> Point3<f64> {
    if camera_poses.is_empty() {
        return Point3::origin();
    }

    let mut sum = nalgebra::Vector3::zeros();
    for pose in camera_poses.values() {
        sum += pose.center().coords;
    }
    Point3::from(sum / camera_poses.len() as f64)
}

/// Compute depth of a bundle point from a reference point.
fn compute_depth_from_reference(
    point: &Point3<f64>,
    reference: &Point3<f64>,
) -> f64 {
    (point - reference).norm()
}

/// Compute median of a slice.
fn compute_median(values: &mut [f64]) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    let unsorted = UnsortedDataSlice::new(values, None)
        .expect("Non-empty data");
    let mut sort_workspace = vec![0.0; values.len()];
    let sorted = unsorted
        .into_sorted(&mut sort_workspace)
        .expect("Sort workspace matches data length");
    sorted.median()
}

// ============================================================
// Validation Functions
// ============================================================

/// Remove bundles that are behind any observing camera (cheirality check).
///
/// Returns the count of bundles removed.
pub fn validate_cheirality(
    bundle_positions: &mut BundlePositions,
    markers: &MarkersData,
    marker_indices: &[usize],
    camera_poses: &CameraPoses,
) -> usize {
    let mut to_remove = Vec::new();

    for &marker_idx in marker_indices {
        if !bundle_positions.contains_key(&marker_idx) {
            continue;
        }
        if marker_idx >= markers.frame_data.len() {
            continue;
        }

        let point_3d = &bundle_positions[&marker_idx];
        let frame_data = &markers.frame_data[marker_idx];

        // Check cheirality against all observing cameras.
        let mut is_valid = true;
        for &frame_num in &frame_data.frames {
            if let Some(pose) = camera_poses.get(&frame_num) {
                if !pose.is_point_in_front(point_3d) {
                    is_valid = false;
                    break;
                }
            }
        }

        if !is_valid {
            to_remove.push(marker_idx);
        }
    }

    let removed_count = to_remove.len();
    for idx in to_remove {
        bundle_positions.remove(&idx);
        mm_eprintln_debug!("    Cheirality: removed bundle {}", idx);
    }

    removed_count
}

/// Remove statistical depth outliers using Median Absolute Deviation (MAD).
///
/// Normalizes depths by the median before computing MAD, making it scale-invariant.
/// The scale factor 1.4826 makes MAD consistent with standard deviation for
/// normally distributed data. Returns the count of bundles removed.
pub fn validate_mad_outliers(
    bundle_positions: &mut BundlePositions,
    camera_poses: &CameraPoses,
    mad_threshold: f64,
) -> usize {
    if bundle_positions.is_empty() {
        return 0;
    }

    let reference = compute_camera_centroid(camera_poses);

    // Compute all depths.
    let depths: Vec<(usize, f64)> = bundle_positions
        .iter()
        .map(|(&idx, point)| {
            (idx, compute_depth_from_reference(point, &reference))
        })
        .collect();

    if depths.is_empty() {
        return 0;
    }

    // Compute median depth.
    let mut depth_values: Vec<f64> = depths.iter().map(|(_, d)| *d).collect();
    let median_depth = compute_median(&mut depth_values);

    // Guard against zero median (all points at origin).
    if median_depth < 1e-10 {
        return 0;
    }

    // Normalize depths by median to make filtering scale-invariant.
    let normalized_depths: Vec<(usize, f64)> = depths
        .iter()
        .map(|&(idx, d)| (idx, d / median_depth))
        .collect();

    // Compute MAD on normalized depths (centered around 1.0).
    let mut absolute_deviations: Vec<f64> = normalized_depths
        .iter()
        .map(|(_, normalized_d)| (*normalized_d - 1.0).abs())
        .collect();
    let mad = compute_median(&mut absolute_deviations);

    // Scale factor to make MAD consistent with standard deviation for
    // normal distribution.
    const MAD_SCALE: f64 = 1.4826;
    let scaled_mad = MAD_SCALE * mad;

    mm_eprintln_debug!(
        "    MAD stats: median_depth={:.3}, normalized_MAD={:.3}, scaled_MAD={:.3}, threshold={:.1}",
        median_depth, mad, scaled_mad, mad_threshold
    );

    // Guard against zero MAD (all points at same depth).
    if scaled_mad < 1e-10 {
        return 0;
    }

    let cutoff = mad_threshold * scaled_mad;

    let mut to_remove = Vec::new();
    for (idx, normalized_depth) in normalized_depths {
        let deviation = (normalized_depth - 1.0).abs();
        if deviation > cutoff {
            to_remove.push(idx);
            mm_eprintln_debug!(
                "    MAD: bundle {} has normalized_depth={:.3}, deviation={:.3} (> cutoff {:.3})",
                idx, normalized_depth, deviation, cutoff
            );
        }
    }

    let removed_count = to_remove.len();
    for idx in to_remove {
        bundle_positions.remove(&idx);
    }

    removed_count
}

// ============================================================
// Degenerate Case Detection
// ============================================================

/// Minimum baseline threshold for camera position collapse detection.
const MIN_BASELINE_THRESHOLD: f64 = 0.001;

/// Detect if camera positions have collapsed to the same location.
///
/// Returns Ok if cameras have sufficient spread, Err if max spread is below
/// MIN_BASELINE_THRESHOLD (indicating planar scene or small baseline).
pub fn detect_camera_position_collapse(
    camera_poses: &CameraPoses,
) -> anyhow::Result<()> {
    if camera_poses.len() < 2 {
        return Ok(());
    }

    // Find maximum distance between any two cameras.
    let centers: Vec<_> = camera_poses.values().map(|p| p.center()).collect();
    let mut max_spread = 0.0_f64;
    for i in 0..centers.len() {
        for j in (i + 1)..centers.len() {
            let dist = (centers[i] - centers[j]).norm();
            max_spread = max_spread.max(dist);
        }
    }

    if max_spread < MIN_BASELINE_THRESHOLD {
        anyhow::bail!(
            "Camera position collapse detected: max spread {:.6} < min {:.6}. \
             All cameras at same position. This typically indicates degenerate \
             geometry (planar scene, small baseline).",
            max_spread,
            MIN_BASELINE_THRESHOLD
        );
    }

    mm_eprintln_debug!(
        "[Validation] Camera spread check passed: max_spread={:.6} >= {:.6}",
        max_spread,
        MIN_BASELINE_THRESHOLD
    );

    Ok(())
}

/// Validate and filter bundles, running all enabled validations in order.
///
/// Runs cheirality first, then MAD-based outlier removal.
/// Returns statistics on how many bundles were removed by each stage.
pub fn validate_and_filter_bundles(
    bundle_positions: &mut BundlePositions,
    markers: &MarkersData,
    marker_indices: &[usize],
    camera_poses: &CameraPoses,
    _camera_intrinsics: &CameraIntrinsics,
    _image_size: &ImageSize<f64>,
    config: &BundleValidationConfig,
) -> BundleValidationResult {
    let initial_count = bundle_positions.len();
    let mut result = BundleValidationResult {
        initial_bundle_count: initial_count,
        ..Default::default()
    };

    if DEBUG {
        // Compute median depth for scale context logging.
        let reference = compute_camera_centroid(camera_poses);
        let mut depth_values: Vec<f64> = bundle_positions
            .values()
            .map(|point| compute_depth_from_reference(point, &reference))
            .collect();
        let median_depth = if !depth_values.is_empty() {
            compute_median(&mut depth_values)
        } else {
            0.0
        };

        let scale_context = if median_depth < 10.0 {
            "gauge-normalized"
        } else {
            "original"
        };

        mm_eprintln_debug!(
            "[Bundle Validation] Starting with {} bundles, median_depth={:.4}, scale={}",
            initial_count, median_depth, scale_context
        );
    }

    // Cheirality validation.
    if config.enable_cheirality {
        result.removed_by_cheirality = validate_cheirality(
            bundle_positions,
            markers,
            marker_indices,
            camera_poses,
        );
        mm_eprintln_debug!(
            "  Cheirality: removed {} bundles ({} remaining)",
            result.removed_by_cheirality,
            bundle_positions.len()
        );
    }

    // MAD-based outlier removal.
    if config.enable_mad_filtering {
        result.removed_by_mad = validate_mad_outliers(
            bundle_positions,
            camera_poses,
            config.mad_threshold,
        );
        mm_eprintln_debug!(
            "  MAD outliers: removed {} bundles ({} remaining)",
            result.removed_by_mad,
            bundle_positions.len()
        );
    }

    result.final_bundle_count = bundle_positions.len();

    // Safety check: ensure we never drop below minimum bundle count.
    if result.final_bundle_count < MINIMUM_BUNDLE_COUNT {
        mm_eprintln_debug!(
            "WARNING: Validation reduced bundles to {} (below minimum {}). \
             Bundle adjustment will be underdetermined.",
            result.final_bundle_count,
            MINIMUM_BUNDLE_COUNT
        );
    }

    mm_eprintln_debug!(
        "[Bundle Validation] Complete: {} -> {} bundles ({} removed, {:.1}% retained)",
        initial_count,
        result.final_bundle_count,
        result.total_removed(),
        result.retention_percentage()
    );

    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::CameraPose;

    #[test]
    fn test_bundle_validation_result_total_removed() {
        let result = BundleValidationResult {
            initial_bundle_count: 100,
            final_bundle_count: 80,
            removed_by_cheirality: 13,
            removed_by_mad: 7,
        };
        assert_eq!(result.total_removed(), 20);
    }

    #[test]
    fn test_bundle_validation_result_retention_percentage() {
        let result = BundleValidationResult {
            initial_bundle_count: 100,
            final_bundle_count: 80,
            ..Default::default()
        };
        assert!((result.retention_percentage() - 80.0).abs() < 0.01);
    }

    #[test]
    fn test_compute_median() {
        let mut values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        assert_eq!(compute_median(&mut values), 3.0);

        let mut values = vec![1.0, 2.0, 3.0, 4.0];
        assert_eq!(compute_median(&mut values), 2.5);

        let mut values = vec![5.0];
        assert_eq!(compute_median(&mut values), 5.0);

        let mut values: Vec<f64> = vec![];
        assert_eq!(compute_median(&mut values), 0.0);
    }

    #[test]
    fn test_compute_camera_centroid_empty() {
        let poses = CameraPoses::new();
        let centroid = compute_camera_centroid(&poses);
        assert_eq!(centroid, Point3::origin());
    }

    #[test]
    fn test_compute_camera_centroid_single() {
        let mut poses = CameraPoses::new();
        let pose = CameraPose::new(
            nalgebra::Matrix3::identity(),
            Point3::new(1.0, 2.0, 3.0),
        );
        poses.insert(1, pose);

        let centroid = compute_camera_centroid(&poses);
        assert!((centroid.x - 1.0).abs() < 1e-10);
        assert!((centroid.y - 2.0).abs() < 1e-10);
        assert!((centroid.z - 3.0).abs() < 1e-10);
    }

    #[test]
    fn test_compute_depth_from_reference() {
        let point = Point3::new(3.0, 4.0, 0.0);
        let reference = Point3::origin();
        let depth = compute_depth_from_reference(&point, &reference);
        assert!((depth - 5.0).abs() < 1e-10);
    }
}
