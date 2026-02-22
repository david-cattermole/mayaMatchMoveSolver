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

//! Depth-based fallback triangulation.
//!
//! Projects 2D observations to 3D at a fixed depth and aggregates the results.
//! Useful as a fallback when geometric triangulation fails, providing a rough
//! initial estimate for bundle adjustment.

use std::marker::PhantomData;

use nalgebra::{Point3, RealField, Vector3};

use super::common::{TriangulationResult, TriangulationStorage, Triangulator};
use crate::datatype::{CameraPose, NdcPoint2};

/// Aggregation mode for combining reprojected 3D points.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum AggregationMode<T: RealField + Copy> {
    /// Arithmetic mean of all reprojected points.
    Mean,

    /// Geometric median using Weiszfeld's algorithm, more robust to outliers.
    GeometricMedian {
        /// Maximum iterations for Weiszfeld's algorithm.
        max_iterations: usize,
        /// Convergence tolerance.
        tolerance: T,
    },
}

impl<T: RealField + Copy> Default for AggregationMode<T> {
    fn default() -> Self {
        AggregationMode::Mean
    }
}

/// Configuration for depth-based triangulation.
#[derive(Debug, Clone, Copy)]
pub struct DepthAverageConfig<T: RealField + Copy> {
    /// Fixed depth value (must be positive).
    pub depth: T,
    /// Aggregation mode for combining reprojected 3D points.
    pub aggregation_mode: AggregationMode<T>,
}

impl<T: RealField + Copy> Default for DepthAverageConfig<T> {
    fn default() -> Self {
        Self {
            depth: nalgebra::convert(10.0),
            aggregation_mode: AggregationMode::Mean,
        }
    }
}

/// Input data for depth-based triangulation.
pub struct TriangulateDataDepthAverage<T: RealField + Copy> {
    pub camera_poses_a: Vec<CameraPose>,
    pub camera_poses_b: Vec<CameraPose>,
    pub observations_ndc_a: Vec<NdcPoint2<T>>,
    pub observations_ndc_b: Vec<NdcPoint2<T>>,
}

impl<T: RealField + Copy> TriangulateDataDepthAverage<T> {
    /// Create empty.
    pub fn new() -> Self {
        Self {
            camera_poses_a: Vec::new(),
            camera_poses_b: Vec::new(),
            observations_ndc_a: Vec::new(),
            observations_ndc_b: Vec::new(),
        }
    }

    /// Create with initial capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            camera_poses_a: Vec::with_capacity(capacity),
            camera_poses_b: Vec::with_capacity(capacity),
            observations_ndc_a: Vec::with_capacity(capacity),
            observations_ndc_b: Vec::with_capacity(capacity),
        }
    }

    /// Add a stereo observation pair.
    pub fn add_stereo_observation(
        &mut self,
        pose_a: CameraPose,
        pose_b: CameraPose,
        observation_ndc_a: NdcPoint2<T>,
        observation_ndc_b: NdcPoint2<T>,
    ) {
        self.camera_poses_a.push(pose_a);
        self.camera_poses_b.push(pose_b);
        self.observations_ndc_a.push(observation_ndc_a);
        self.observations_ndc_b.push(observation_ndc_b);
    }

    /// Returns the number of stereo pairs.
    pub fn len(&self) -> usize {
        self.camera_poses_a.len()
    }

    /// Returns true if empty.
    pub fn is_empty(&self) -> bool {
        self.camera_poses_a.is_empty()
    }

    /// Clears all observations.
    pub fn clear(&mut self) {
        self.camera_poses_a.clear();
        self.camera_poses_b.clear();
        self.observations_ndc_a.clear();
        self.observations_ndc_b.clear();
    }
}

impl<T: RealField + Copy> Default for TriangulateDataDepthAverage<T> {
    fn default() -> Self {
        Self::new()
    }
}

/// Result of depth-based triangulation.
#[derive(Debug)]
pub struct TriangulationResultDepthAverage<'a, T: RealField + Copy> {
    pub inner: TriangulationResult<'a, T>,
    /// Standard deviation of distances from projected points to result.
    pub spreads: &'a [T],
}

impl<'a, T: RealField + Copy> AsRef<TriangulationResult<'a, T>>
    for TriangulationResultDepthAverage<'a, T>
{
    fn as_ref(&self) -> &TriangulationResult<'a, T> {
        &self.inner
    }
}

/// Depth-based triangulator using fixed-depth projection and aggregation.
pub struct TriangulatorDepthAverage<T: RealField + Copy> {
    storage: TriangulationStorage<T>,
    spreads: Vec<T>,
    config: DepthAverageConfig<T>,
    reprojected_buffer: Vec<Point3<T>>,
    _phantom: PhantomData<T>,
}

impl<T: RealField + Copy> TriangulatorDepthAverage<T> {
    /// Create with initial capacity and config.
    pub fn new(initial_capacity: usize, config: DepthAverageConfig<T>) -> Self {
        Self {
            storage: TriangulationStorage::new(initial_capacity),
            spreads: Vec::with_capacity(initial_capacity),
            config,
            reprojected_buffer: Vec::with_capacity(2),
            _phantom: PhantomData,
        }
    }

    /// Create with default configuration (depth=10.0, mean aggregation).
    pub fn new_with_defaults(initial_capacity: usize) -> Self {
        Self::new(initial_capacity, DepthAverageConfig::default())
    }

    /// Ensure buffers handle at least `required_capacity` triangulations.
    pub fn reserve(&mut self, required_capacity: usize) {
        self.storage.reserve(required_capacity);
        if self.spreads.capacity() < required_capacity {
            self.spreads
                .reserve(required_capacity - self.spreads.capacity());
        }
    }

    /// Triangulates multiple points in batch.
    pub fn triangulate_points<'a>(
        &'a mut self,
        data: &TriangulateDataDepthAverage<T>,
    ) -> TriangulationResultDepthAverage<'a, T> {
        let n = data.len();

        self.reserve(n);

        unsafe {
            self.storage.resize_to(n);
            self.spreads.set_len(n);
        }

        for i in 0..n {
            self.triangulate_point_inplace(i, data);
        }

        TriangulationResultDepthAverage {
            inner: self.storage.get_result(n),
            spreads: &self.spreads[..n],
        }
    }

    /// Returns current capacity.
    pub fn capacity(&self) -> usize {
        self.storage.capacity
    }

    /// Returns current configuration.
    pub fn config(&self) -> &DepthAverageConfig<T> {
        &self.config
    }

    /// Updates configuration.
    pub fn set_config(&mut self, config: DepthAverageConfig<T>) {
        self.config = config;
    }

    /// Triangulates a single point, writing to storage at `index`.
    #[inline]
    fn triangulate_point_inplace(
        &mut self,
        index: usize,
        data: &TriangulateDataDepthAverage<T>,
    ) {
        let depth = self.config.depth;

        // Validate depth.
        if !depth.is_finite() || depth <= T::zero() {
            self.storage.mark_invalid(index);
            self.spreads[index] = T::max_value().unwrap_or(T::one());
            return;
        }

        // Clear and reuse the buffer.
        self.reprojected_buffer.clear();

        // Unproject both observations to 3D.
        let pose_a = &data.camera_poses_a[index];
        let pose_b = &data.camera_poses_b[index];
        let obs_a = &data.observations_ndc_a[index];
        let obs_b = &data.observations_ndc_b[index];

        let point_a = Self::unproject_to_world(obs_a, pose_a, depth);
        let point_b = Self::unproject_to_world(obs_b, pose_b, depth);

        self.reprojected_buffer.push(point_a);
        self.reprojected_buffer.push(point_b);

        // Aggregate based on mode
        let point = match self.config.aggregation_mode {
            AggregationMode::Mean => {
                Self::compute_mean(&self.reprojected_buffer)
            }
            AggregationMode::GeometricMedian {
                max_iterations,
                tolerance,
            } => Self::compute_geometric_median(
                &self.reprojected_buffer,
                max_iterations,
                tolerance,
            ),
        };

        // Compute spread
        let spread = Self::compute_spread(&self.reprojected_buffer, &point);

        // Check validity - point should be finite
        let is_valid = point.coords.iter().all(|&x| x.is_finite());

        self.storage.set_result(index, point, spread, is_valid);
        self.spreads[index] = spread;
    }

    /// Unprojects a 2D NDC point to 3D world coordinates at fixed depth.
    #[inline]
    fn unproject_to_world(
        observation_ndc: &NdcPoint2<T>,
        camera_pose: &CameraPose,
        depth: T,
    ) -> Point3<T> {
        let x_ndc: T = observation_ndc.x.0;
        let y_ndc: T = observation_ndc.y.0;

        // Maya convention: -Z is forward, so z = -depth.
        let point_camera = Vector3::new(x_ndc * depth, y_ndc * depth, -depth);

        // Transform from camera space to world space: R^T * p + center.
        let rotation_transpose = camera_pose.rotation().transpose();
        let center = camera_pose.center();

        let rot_t: nalgebra::Matrix3<T> = nalgebra::convert(rotation_transpose);
        let center_t: Vector3<T> = nalgebra::convert(center.coords);

        let world_coords = rot_t * point_camera + center_t;

        Point3::from(world_coords)
    }

    /// Returns the arithmetic mean of a slice of 3D points.
    #[inline]
    fn compute_mean(points: &[Point3<T>]) -> Point3<T> {
        debug_assert!(!points.is_empty());

        let mut sum = Vector3::zeros();
        for p in points {
            sum += p.coords;
        }
        let n: T = nalgebra::convert(points.len() as f64);
        Point3::from(sum / n)
    }

    /// Returns the geometric median using Weiszfeld's algorithm.
    fn compute_geometric_median(
        points: &[Point3<T>],
        max_iterations: usize,
        tolerance: T,
    ) -> Point3<T> {
        debug_assert!(!points.is_empty());

        let mut estimate = Self::compute_mean(points);

        let eps: T = nalgebra::convert(1e-10);

        for _ in 0..max_iterations {
            let mut numerator = Vector3::zeros();
            let mut denominator = T::zero();

            for point in points {
                let diff = point.coords - estimate.coords;
                let distance = diff.norm();

                // Avoid division by zero
                if distance > eps {
                    let weight = T::one() / distance;
                    numerator += point.coords * weight;
                    denominator += weight;
                }
            }

            if denominator < eps {
                break;
            }

            let new_estimate = Point3::from(numerator / denominator);
            let change = (new_estimate.coords - estimate.coords).norm();

            estimate = new_estimate;

            if change < tolerance {
                break;
            }
        }

        estimate
    }

    /// Returns the standard deviation of distances from `points` to `reference`.
    #[inline]
    fn compute_spread(points: &[Point3<T>], reference: &Point3<T>) -> T {
        if points.is_empty() {
            return T::zero();
        }

        let n: T = nalgebra::convert(points.len() as f64);
        let mut sum_dist = T::zero();
        let mut sum_dist_sq = T::zero();

        for p in points {
            let dist = (p.coords - reference.coords).norm();
            sum_dist += dist;
            sum_dist_sq += dist * dist;
        }

        let mean_dist = sum_dist / n;
        let variance = (sum_dist_sq / n) - (mean_dist * mean_dist);

        // Guard against floating-point rounding making variance slightly negative.
        if variance > T::zero() {
            variance.sqrt()
        } else {
            T::zero()
        }
    }
}

impl<T: RealField + Copy> Triangulator<T> for TriangulatorDepthAverage<T> {
    type InputData = TriangulateDataDepthAverage<T>;
    type Result<'a>
        = TriangulationResultDepthAverage<'a, T>
    where
        Self: 'a;

    fn new(initial_capacity: usize) -> Self {
        Self::new_with_defaults(initial_capacity)
    }

    fn reserve(&mut self, required_capacity: usize) {
        self.reserve(required_capacity)
    }

    fn triangulate_points<'a>(
        &'a mut self,
        input_data: &Self::InputData,
    ) -> Self::Result<'a> {
        self.triangulate_points(input_data)
    }

    fn capacity(&self) -> usize {
        self.capacity()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::NdcValue;
    use approx::assert_relative_eq;
    use nalgebra::{Matrix3, Point2};

    /// Helper to create NDC point from f64 values.
    fn ndc_point(x: f64, y: f64) -> NdcPoint2<f64> {
        Point2::new(NdcValue(x), NdcValue(y))
    }

    #[test]
    fn test_depth_average_basic() {
        let mut triangulator =
            TriangulatorDepthAverage::<f64>::new_with_defaults(10);

        // Two cameras at origin looking down -Z
        let pose_a = CameraPose::default();
        let pose_b = CameraPose::default();

        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose_a,
            pose_b,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        // Point should be at (0, 0, -10) with default depth=10
        let point = result.inner.points[0];
        assert_relative_eq!(point.x, 0.0, epsilon = 1e-10);
        assert_relative_eq!(point.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(point.z, -10.0, epsilon = 1e-10);

        // Spread should be 0 since both cameras are identical
        assert_relative_eq!(result.spreads[0], 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_depth_average_different_camera_positions() {
        let config = DepthAverageConfig {
            depth: 5.0,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        // Camera A at origin
        let pose_a = CameraPose::default();

        // Camera B at (2, 0, 0)
        let pose_b =
            CameraPose::new(Matrix3::identity(), Point3::new(2.0, 0.0, 0.0));

        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose_a,
            pose_b,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        assert!(result.inner.valid[0]);

        // Both cameras looking at NDC (0,0) at depth 5:
        // Camera A: (0, 0, -5)
        // Camera B: (2, 0, -5)
        // Mean: (1, 0, -5)
        let point = result.inner.points[0];
        assert_relative_eq!(point.x, 1.0, epsilon = 1e-10);
        assert_relative_eq!(point.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(point.z, -5.0, epsilon = 1e-10);

        // Spread should be 1.0 (distance from each point to mean is 1.0)
        // std dev of [1.0, 1.0] is 0
        assert_relative_eq!(result.spreads[0], 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_depth_average_batch_processing() {
        let mut triangulator =
            TriangulatorDepthAverage::<f64>::new_with_defaults(100);

        let pose_a = CameraPose::default();
        let pose_b =
            CameraPose::new(Matrix3::identity(), Point3::new(1.0, 0.0, 0.0));

        let mut data = TriangulateDataDepthAverage::with_capacity(50);
        for i in 0..50 {
            let offset = i as f64 * 0.01;
            data.add_stereo_observation(
                pose_a.clone(),
                pose_b.clone(),
                ndc_point(offset, offset),
                ndc_point(offset, offset),
            );
        }

        let result = triangulator.triangulate_points(&data);

        assert_eq!(result.inner.points.len(), 50);
        assert!(result.inner.valid.iter().all(|&v| v));
    }

    #[test]
    fn test_depth_average_geometric_median() {
        let config = DepthAverageConfig {
            depth: 5.0,
            aggregation_mode: AggregationMode::GeometricMedian {
                max_iterations: 100,
                tolerance: 1e-8,
            },
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        // Two cameras with slightly different positions
        let pose_a = CameraPose::default();
        let pose_b =
            CameraPose::new(Matrix3::identity(), Point3::new(0.5, 0.0, 0.0));

        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose_a,
            pose_b,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        assert!(result.inner.valid[0]);

        // With only 2 points, geometric median should be close to mean
        let point = result.inner.points[0];
        assert_relative_eq!(point.x, 0.25, epsilon = 0.01);
        assert_relative_eq!(point.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(point.z, -5.0, epsilon = 1e-10);
    }

    #[test]
    fn test_depth_average_invalid_depth() {
        let config = DepthAverageConfig {
            depth: 0.0, // Invalid
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);
        assert!(!result.inner.valid[0]);
    }

    #[test]
    fn test_depth_average_negative_depth() {
        let config = DepthAverageConfig {
            depth: -5.0, // Invalid - negative
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);
        assert!(!result.inner.valid[0]);
    }

    #[test]
    fn test_depth_average_off_center_observation() {
        let config = DepthAverageConfig {
            depth: 10.0,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.5, 0.25),
            ndc_point(0.5, 0.25),
        );

        let result = triangulator.triangulate_points(&data);

        assert!(result.inner.valid[0]);

        // NDC (0.5, 0.25) at depth 10 should be (5, 2.5, -10)
        let point = result.inner.points[0];
        assert_relative_eq!(point.x, 5.0, epsilon = 1e-10);
        assert_relative_eq!(point.y, 2.5, epsilon = 1e-10);
        assert_relative_eq!(point.z, -10.0, epsilon = 1e-10);
    }

    #[test]
    fn test_depth_average_rotated_camera() {
        use std::f64::consts::PI;

        let config = DepthAverageConfig {
            depth: 5.0,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        // Camera A at origin, looking down -Z
        let pose_a = CameraPose::default();

        // Camera B at (5, 0, 5), rotated 90 degrees around Y
        // After rotation, its -Z axis points along world -X
        let angle = PI / 2.0;
        let c = angle.cos();
        let s = angle.sin();
        let rotation_b = Matrix3::new(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c);
        let pose_b = CameraPose::new(rotation_b, Point3::new(5.0, 0.0, 5.0));

        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose_a,
            pose_b,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        assert!(result.inner.valid[0]);
        // Both points should be valid and produce some result
        assert!(result.inner.points[0].coords.iter().all(|&x| x.is_finite()));
    }

    #[test]
    fn test_depth_average_f32_precision() {
        let config = DepthAverageConfig {
            depth: 10.0f32,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f32>::new(10, config);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::<f32>::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            Point2::new(NdcValue(0.0f32), NdcValue(0.0f32)),
            Point2::new(NdcValue(0.0f32), NdcValue(0.0f32)),
        );

        let result = triangulator.triangulate_points(&data);

        assert!(result.inner.valid[0]);
        let point = result.inner.points[0];
        assert!((point.z - (-10.0f32)).abs() < 1e-5);
    }

    #[test]
    fn test_depth_average_triangulator_trait() {
        // Test that Triangulator trait works correctly
        let mut triangulator: TriangulatorDepthAverage<f64> =
            Triangulator::new(10);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);
        let common_result = result.as_ref();

        assert_eq!(common_result.points.len(), 1);
        assert!(common_result.valid[0]);
    }

    #[test]
    fn test_depth_average_data_operations() {
        let mut data = TriangulateDataDepthAverage::<f64>::new();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);

        let pose = CameraPose::default();
        data.add_stereo_observation(
            pose.clone(),
            pose.clone(),
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        assert!(!data.is_empty());
        assert_eq!(data.len(), 1);

        data.clear();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);
    }

    #[test]
    fn test_depth_average_config_update() {
        let mut triangulator =
            TriangulatorDepthAverage::<f64>::new_with_defaults(10);

        assert_relative_eq!(triangulator.config().depth, 10.0, epsilon = 1e-10);

        let new_config = DepthAverageConfig {
            depth: 20.0,
            aggregation_mode: AggregationMode::GeometricMedian {
                max_iterations: 50,
                tolerance: 1e-6,
            },
        };
        triangulator.set_config(new_config);

        assert_relative_eq!(triangulator.config().depth, 20.0, epsilon = 1e-10);
    }

    #[test]
    fn test_depth_average_maya_coordinate_system() {
        // Verify that -Z is forward in Maya convention
        let config = DepthAverageConfig {
            depth: 10.0,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        // Point should be at negative Z (in front of camera in Maya convention)
        assert!(
            result.inner.points[0].z < 0.0,
            "Point should be in front of camera (negative Z in Maya convention)"
        );
    }

    #[test]
    fn test_spread_identical_points() {
        let config = DepthAverageConfig {
            depth: 10.0,
            aggregation_mode: AggregationMode::Mean,
        };
        let mut triangulator = TriangulatorDepthAverage::<f64>::new(10, config);

        // Same camera, same observation -> identical reprojected points
        let pose = CameraPose::default();
        let mut data = TriangulateDataDepthAverage::new();
        data.add_stereo_observation(
            pose.clone(),
            pose,
            ndc_point(0.0, 0.0),
            ndc_point(0.0, 0.0),
        );

        let result = triangulator.triangulate_points(&data);

        // Spread should be 0 for identical points
        assert_relative_eq!(result.spreads[0], 0.0, epsilon = 1e-10);
    }
}
