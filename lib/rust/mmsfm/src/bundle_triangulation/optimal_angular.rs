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
//! Triangulation by minimizing angular ray error using Levenberg-Marquardt optimization.
//!
//! For each camera, the residual is `1 - dot(observed_ray, reconstructed_ray)`,
//! minimized using Levenberg-Marquardt. Based on Hartley & Zisserman (2004).

use nalgebra::{Matrix3, Point3, Vector3};

use super::common::{TriangulationResult, TriangulationStorage};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Configuration for optimal angular triangulation.
#[derive(Debug, Clone, Copy)]
pub struct OptimalAngularConfig {
    /// Max Levenberg-Marquardt iterations.
    pub max_iterations: usize,
    /// Convergence threshold for function value change.
    pub function_tolerance: f64,
    /// Convergence threshold for parameter change.
    pub parameter_tolerance: f64,
    /// Convergence threshold for gradient norm.
    pub gradient_tolerance: f64,
    /// Max angular error (radians) for a triangulation to be considered valid.
    pub max_angular_error: f64,
}

impl Default for OptimalAngularConfig {
    fn default() -> Self {
        Self {
            max_iterations: 20,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_angular_error: 0.1, // ~5.7 degrees
        }
    }
}

/// Input data for optimal angular triangulation.
pub struct TriangulateDataOptimalAngular {
    pub camera_centers_a: Vec<Point3<f64>>,
    pub camera_centers_b: Vec<Point3<f64>>,
    /// Camera-to-world rotations (R^T) for camera A.
    pub camera_rotation_transposes_a: Vec<Matrix3<f64>>,
    /// Camera-to-world rotations (R^T) for camera B.
    pub camera_rotation_transposes_b: Vec<Matrix3<f64>>,
    /// Observed ray directions in camera A space (normalized).
    pub observed_rays_camera_a: Vec<Vector3<f64>>,
    /// Observed ray directions in camera B space (normalized).
    pub observed_rays_camera_b: Vec<Vector3<f64>>,
}

impl TriangulateDataOptimalAngular {
    /// Create empty.
    pub fn new() -> Self {
        Self {
            camera_centers_a: Vec::new(),
            camera_centers_b: Vec::new(),
            camera_rotation_transposes_a: Vec::new(),
            camera_rotation_transposes_b: Vec::new(),
            observed_rays_camera_a: Vec::new(),
            observed_rays_camera_b: Vec::new(),
        }
    }

    /// Create with initial capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            camera_centers_a: Vec::with_capacity(capacity),
            camera_centers_b: Vec::with_capacity(capacity),
            camera_rotation_transposes_a: Vec::with_capacity(capacity),
            camera_rotation_transposes_b: Vec::with_capacity(capacity),
            observed_rays_camera_a: Vec::with_capacity(capacity),
            observed_rays_camera_b: Vec::with_capacity(capacity),
        }
    }

    /// Adds a stereo observation pair.
    pub fn add_stereo_observation(
        &mut self,
        center_a: Point3<f64>,
        center_b: Point3<f64>,
        rotation_transpose_a: Matrix3<f64>,
        rotation_transpose_b: Matrix3<f64>,
        camera_ray_a: Vector3<f64>,
        camera_ray_b: Vector3<f64>,
    ) {
        self.camera_centers_a.push(center_a);
        self.camera_centers_b.push(center_b);
        self.camera_rotation_transposes_a.push(rotation_transpose_a);
        self.camera_rotation_transposes_b.push(rotation_transpose_b);
        self.observed_rays_camera_a.push(camera_ray_a.normalize());
        self.observed_rays_camera_b.push(camera_ray_b.normalize());
    }

    /// Adds a stereo observation from normalized camera coordinates.
    pub fn add_stereo_observation_from_coords(
        &mut self,
        center_a: Point3<f64>,
        center_b: Point3<f64>,
        rotation_transpose_a: Matrix3<f64>,
        rotation_transpose_b: Matrix3<f64>,
        camera_coord_a: (f64, f64),
        camera_coord_b: (f64, f64),
    ) {
        // Maya convention: camera looks down -Z axis
        let ray_a = Vector3::new(camera_coord_a.0, camera_coord_a.1, -1.0);
        let ray_b = Vector3::new(camera_coord_b.0, camera_coord_b.1, -1.0);
        self.add_stereo_observation(
            center_a,
            center_b,
            rotation_transpose_a,
            rotation_transpose_b,
            ray_a,
            ray_b,
        );
    }

    /// Returns the number of observations.
    pub fn len(&self) -> usize {
        self.camera_centers_a.len()
    }

    /// Returns true if empty.
    pub fn is_empty(&self) -> bool {
        self.camera_centers_a.is_empty()
    }

    /// Clears all observations.
    pub fn clear(&mut self) {
        self.camera_centers_a.clear();
        self.camera_centers_b.clear();
        self.camera_rotation_transposes_a.clear();
        self.camera_rotation_transposes_b.clear();
        self.observed_rays_camera_a.clear();
        self.observed_rays_camera_b.clear();
    }
}

impl Default for TriangulateDataOptimalAngular {
    fn default() -> Self {
        Self::new()
    }
}

/// Result of optimal angular triangulation.
#[derive(Debug)]
pub struct TriangulationResultOptimalAngular<'a> {
    pub inner: TriangulationResult<'a, f64>,
    /// Number of LM iterations used for each point.
    pub iterations: &'a [usize],
}

impl<'a> AsRef<TriangulationResult<'a, f64>>
    for TriangulationResultOptimalAngular<'a>
{
    fn as_ref(&self) -> &TriangulationResult<'a, f64> {
        &self.inner
    }
}

/// Triangulator using Levenberg-Marquardt to minimize angular ray error.
pub struct TriangulatorOptimalAngular {
    storage: TriangulationStorage<f64>,
    iteration_counts: Vec<usize>,
    config: OptimalAngularConfig,
}

impl TriangulatorOptimalAngular {
    /// Create with initial capacity and config.
    pub fn new(initial_capacity: usize, config: OptimalAngularConfig) -> Self {
        Self {
            storage: TriangulationStorage::new(initial_capacity),
            iteration_counts: Vec::with_capacity(initial_capacity),
            config,
        }
    }

    /// Create with default configuration.
    pub fn new_with_defaults(initial_capacity: usize) -> Self {
        Self::new(initial_capacity, OptimalAngularConfig::default())
    }

    /// Ensure buffers handle at least `required_capacity` triangulations.
    pub fn reserve(&mut self, required_capacity: usize) {
        self.storage.reserve(required_capacity);
        if required_capacity > self.storage.capacity {
            let additional = required_capacity - self.storage.capacity;
            self.iteration_counts.reserve(additional);
        }
    }

    /// Triangulates multiple 3D points using angular error minimization.
    pub fn triangulate_points<'a>(
        &'a mut self,
        data: &TriangulateDataOptimalAngular,
    ) -> TriangulationResultOptimalAngular<'a> {
        let n_points = data.len();

        self.reserve(n_points);

        // SAFETY: All elements are written in triangulate_point_inplace below.
        unsafe {
            self.storage.resize_to(n_points);
            self.iteration_counts.set_len(n_points);
        }

        for i in 0..n_points {
            self.triangulate_point_inplace(i, data);
        }

        TriangulationResultOptimalAngular {
            inner: self.storage.get_result(n_points),
            iterations: &self.iteration_counts[..n_points],
        }
    }

    /// Triangulates a single point using LM optimization, writing to storage at `point_index`.
    #[inline]
    fn triangulate_point_inplace(
        &mut self,
        point_index: usize,
        data: &TriangulateDataOptimalAngular,
    ) {
        let center_a = &data.camera_centers_a[point_index];
        let center_b = &data.camera_centers_b[point_index];
        let rot_t_a = &data.camera_rotation_transposes_a[point_index];
        let rot_t_b = &data.camera_rotation_transposes_b[point_index];
        let ray_cam_a = &data.observed_rays_camera_a[point_index];
        let ray_cam_b = &data.observed_rays_camera_b[point_index];

        let ray_world_a = (rot_t_a * ray_cam_a).normalize();
        let ray_world_b = (rot_t_b * ray_cam_b).normalize();

        mm_debug_eprintln!(
            "DEBUG OA: point {} center_a=({:.3}, {:.3}, {:.3}) center_b=({:.3}, {:.3}, {:.3})",
            point_index, center_a.x, center_a.y, center_a.z,
            center_b.x, center_b.y, center_b.z
        );
        mm_debug_eprintln!(
            "DEBUG OA: ray_world_a=({:.3}, {:.3}, {:.3}) ray_world_b=({:.3}, {:.3}, {:.3})",
            ray_world_a.x, ray_world_a.y, ray_world_a.z,
            ray_world_b.x, ray_world_b.y, ray_world_b.z
        );

        // Initial estimate from line-line intersection.
        let mut point = match self.line_line_midpoint(
            center_a,
            &ray_world_a,
            center_b,
            &ray_world_b,
        ) {
            Some(p) => p,
            None => {
                mm_debug_eprintln!(
                    "DEBUG OA: line-line init failed for point {}",
                    point_index
                );
                self.storage.mark_invalid(point_index);
                self.iteration_counts[point_index] = 0;
                return;
            }
        };

        mm_debug_eprintln!(
            "DEBUG OA: initial=({:.3}, {:.3}, {:.3})",
            point.x,
            point.y,
            point.z
        );

        // Levenberg-Marquardt optimization.
        let mut lambda = 1e-4_f64; // LM damping parameter.
        let lambda_up = 10.0_f64;
        let lambda_down = 0.1_f64;
        let lambda_max = 1e10_f64;
        let lambda_min = 1e-10_f64;

        let mut prev_cost = f64::MAX;
        let mut iterations = 0_usize;
        let mut converged = false;

        for iter in 0..self.config.max_iterations {
            iterations = iter + 1;

            // Compute residuals and Jacobian
            let (r, j) = self.compute_residuals_and_jacobian(
                &point,
                center_a,
                center_b,
                &ray_world_a,
                &ray_world_b,
            );

            let cost = r[0] * r[0] + r[1] * r[1];

            if DEBUG && iter == 0 {
                eprintln!(
                    "DEBUG OA: iter {} cost={:.9} lambda={:.2e}",
                    iter, cost, lambda
                );
            }

            // Check convergence.
            let cost_change = (prev_cost - cost).abs();
            if cost_change < self.config.function_tolerance * cost.max(1.0) {
                converged = true;
                break;
            }

            let grad = [
                j[0][0] * r[0] + j[1][0] * r[1],
                j[0][1] * r[0] + j[1][1] * r[1],
                j[0][2] * r[0] + j[1][2] * r[1],
            ];
            let grad_norm =
                (grad[0] * grad[0] + grad[1] * grad[1] + grad[2] * grad[2])
                    .sqrt();
            if grad_norm < self.config.gradient_tolerance {
                converged = true;
                break;
            }

            // Normal equations: (J^T * J + lambda * I) * delta = -J^T * r
            let mut jtj = [[0.0_f64; 3]; 3];
            for i in 0..3 {
                for k in 0..3 {
                    jtj[i][k] = j[0][i] * j[0][k] + j[1][i] * j[1][k];
                }
                jtj[i][i] += lambda; // Regularization
            }

            let jtr = [-grad[0], -grad[1], -grad[2]];

            let delta = match self.solve_3x3(&jtj, &jtr) {
                Some(d) => d,
                None => {
                    // Singular - increase damping and retry.
                    lambda = (lambda * lambda_up).min(lambda_max);
                    continue;
                }
            };

            // Check parameter step size.
            let param_norm =
                (point.x * point.x + point.y * point.y + point.z * point.z)
                    .sqrt()
                    .max(1.0);
            let delta_norm = (delta[0] * delta[0]
                + delta[1] * delta[1]
                + delta[2] * delta[2])
                .sqrt();
            if delta_norm < self.config.parameter_tolerance * param_norm {
                converged = true;
                break;
            }

            let trial_point = Point3::new(
                point.x + delta[0],
                point.y + delta[1],
                point.z + delta[2],
            );

            let trial_cost = self.compute_cost(
                &trial_point,
                center_a,
                center_b,
                &ray_world_a,
                &ray_world_b,
            );

            if trial_cost < cost {
                point = trial_point;
                prev_cost = cost;
                lambda = (lambda * lambda_down).max(lambda_min);
            } else {
                lambda = (lambda * lambda_up).min(lambda_max);
            }
        }

        let angular_error = self.compute_mean_angular_error(
            &point,
            center_a,
            center_b,
            &ray_world_a,
            &ray_world_b,
        );

        let is_finite = point.coords.iter().all(|x| x.is_finite());
        let is_within_tolerance = angular_error < self.config.max_angular_error;
        let valid = is_finite && converged && is_within_tolerance;

        mm_debug_eprintln!(
            "DEBUG OA: optimized=({:.3}, {:.3}, {:.3}) error={:.6} valid={} iters={}",
            point.x, point.y, point.z, angular_error, valid, iterations
        );

        self.storage
            .set_result(point_index, point, angular_error, valid);
        self.iteration_counts[point_index] = iterations;
    }

    /// Computes residuals and Jacobian for the angular error cost function.
    ///
    /// Residual: `r_i = 1 - dot(observed_ray, normalize(X - camera_center))`
    #[inline]
    fn compute_residuals_and_jacobian(
        &self,
        point: &Point3<f64>,
        center_a: &Point3<f64>,
        center_b: &Point3<f64>,
        observed_ray_a: &Vector3<f64>,
        observed_ray_b: &Vector3<f64>,
    ) -> ([f64; 2], [[f64; 3]; 2]) {
        let mut residuals = [0.0_f64; 2];
        let mut jacobian = [[0.0_f64; 3]; 2];

        // Camera A
        let v_a = point - center_a;
        let dist_a = v_a.norm();
        if dist_a > 1e-12 {
            let d_rec_a = v_a / dist_a;
            let dot_a = observed_ray_a.dot(&d_rec_a);
            residuals[0] = 1.0 - dot_a;

            let scale_a = 1.0 / dist_a;
            let proj_a = d_rec_a * dot_a;
            jacobian[0][0] = -(observed_ray_a.x - proj_a.x) * scale_a;
            jacobian[0][1] = -(observed_ray_a.y - proj_a.y) * scale_a;
            jacobian[0][2] = -(observed_ray_a.z - proj_a.z) * scale_a;
        } else {
            residuals[0] = 1.0;
        }

        // Camera B
        let v_b = point - center_b;
        let dist_b = v_b.norm();
        if dist_b > 1e-12 {
            let d_rec_b = v_b / dist_b;
            let dot_b = observed_ray_b.dot(&d_rec_b);
            residuals[1] = 1.0 - dot_b;

            let scale_b = 1.0 / dist_b;
            let proj_b = d_rec_b * dot_b;
            jacobian[1][0] = -(observed_ray_b.x - proj_b.x) * scale_b;
            jacobian[1][1] = -(observed_ray_b.y - proj_b.y) * scale_b;
            jacobian[1][2] = -(observed_ray_b.z - proj_b.z) * scale_b;
        } else {
            residuals[1] = 1.0;
        }

        (residuals, jacobian)
    }

    /// Computes the cost function value.
    #[inline]
    fn compute_cost(
        &self,
        point: &Point3<f64>,
        center_a: &Point3<f64>,
        center_b: &Point3<f64>,
        observed_ray_a: &Vector3<f64>,
        observed_ray_b: &Vector3<f64>,
    ) -> f64 {
        let v_a = point - center_a;
        let dist_a = v_a.norm();
        let r_a = if dist_a > 1e-12 {
            1.0 - observed_ray_a.dot(&(v_a / dist_a))
        } else {
            1.0
        };

        let v_b = point - center_b;
        let dist_b = v_b.norm();
        let r_b = if dist_b > 1e-12 {
            1.0 - observed_ray_b.dot(&(v_b / dist_b))
        } else {
            1.0
        };

        r_a * r_a + r_b * r_b
    }

    /// Solves a 3x3 linear system using Cramer's rule.
    #[inline]
    fn solve_3x3(&self, a: &[[f64; 3]; 3], b: &[f64; 3]) -> Option<[f64; 3]> {
        let det = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);

        if det.abs() < 1e-15 {
            return None;
        }

        let inv_det = 1.0 / det;

        // Cramer's rule
        let x0 = (b[0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (b[1] * a[2][2] - a[1][2] * b[2])
            + a[0][2] * (b[1] * a[2][1] - a[1][1] * b[2]))
            * inv_det;

        let x1 = (a[0][0] * (b[1] * a[2][2] - a[1][2] * b[2])
            - b[0] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * b[2] - b[1] * a[2][0]))
            * inv_det;

        let x2 = (a[0][0] * (a[1][1] * b[2] - b[1] * a[2][1])
            - a[0][1] * (a[1][0] * b[2] - b[1] * a[2][0])
            + b[0] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
            * inv_det;

        Some([x0, x1, x2])
    }

    /// Returns the midpoint of closest approach between two rays.
    fn line_line_midpoint(
        &self,
        origin_a: &Point3<f64>,
        direction_a: &Vector3<f64>,
        origin_b: &Point3<f64>,
        direction_b: &Vector3<f64>,
    ) -> Option<Point3<f64>> {
        let origin_diff = origin_a - origin_b;
        let dot_aa = direction_a.dot(direction_a);
        let dot_ab = direction_a.dot(direction_b);
        let dot_bb = direction_b.dot(direction_b);
        let dot_a_diff = direction_a.dot(&origin_diff);
        let dot_b_diff = direction_b.dot(&origin_diff);

        let denom = dot_aa * dot_bb - dot_ab * dot_ab;
        let eps = 1e-12;

        if denom.abs() < eps {
            // Parallel rays.
            Some(Point3::from((origin_a.coords + origin_b.coords) / 2.0))
        } else {
            let param_a = (dot_ab * dot_b_diff - dot_bb * dot_a_diff) / denom;
            let param_b = (dot_aa * dot_b_diff - dot_ab * dot_a_diff) / denom;

            let closest_a = origin_a + direction_a * param_a;
            let closest_b = origin_b + direction_b * param_b;

            // Negative parameter means the point is behind the camera.
            if param_a < -eps || param_b < -eps {
                mm_debug_eprintln!(
                    "DEBUG OA: line-line behind camera param_a={:.3} param_b={:.3}",
                    param_a,
                    param_b
                );
                return None;
            }

            Some(Point3::from((closest_a.coords + closest_b.coords) / 2.0))
        }
    }

    /// Returns the mean angular error between observed and reconstructed rays.
    fn compute_mean_angular_error(
        &self,
        point: &Point3<f64>,
        center_a: &Point3<f64>,
        center_b: &Point3<f64>,
        observed_ray_a: &Vector3<f64>,
        observed_ray_b: &Vector3<f64>,
    ) -> f64 {
        let rec_ray_a = (point - center_a).normalize();
        let error_a = 1.0 - observed_ray_a.dot(&rec_ray_a).clamp(-1.0, 1.0);

        let rec_ray_b = (point - center_b).normalize();
        let error_b = 1.0 - observed_ray_b.dot(&rec_ray_b).clamp(-1.0, 1.0);

        (error_a + error_b) / 2.0
    }

    /// Returns current capacity.
    pub fn capacity(&self) -> usize {
        self.storage.capacity
    }

    /// Returns current configuration.
    pub fn config(&self) -> OptimalAngularConfig {
        self.config
    }

    /// Updates configuration.
    pub fn set_config(&mut self, config: OptimalAngularConfig) {
        self.config = config;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    /// Create test cameras: identity and translated along X axis.
    fn create_simple_test_cameras(
    ) -> (Point3<f64>, Point3<f64>, Matrix3<f64>, Matrix3<f64>) {
        let center_a = Point3::new(0.0, 0.0, 0.0);
        let center_b = Point3::new(2.0, 0.0, 0.0); // 2 units along X

        // Identity rotations (both cameras facing -Z)
        let rot_t_a = Matrix3::identity();
        let rot_t_b = Matrix3::identity();

        (center_a, center_b, rot_t_a, rot_t_b)
    }

    #[test]
    fn test_optimal_angular_basic() {
        let mut triangulator =
            TriangulatorOptimalAngular::new_with_defaults(10);
        let mut data = TriangulateDataOptimalAngular::new();

        let (center_a, center_b, rot_t_a, rot_t_b) =
            create_simple_test_cameras();

        // Point at (1, 0, -5) - should be visible from both cameras
        // Camera A at (0,0,0): ray direction toward point is (1, 0, -5).normalize
        // Camera B at (2,0,0): ray direction toward point is (-1, 0, -5).normalize
        let target = Point3::new(1.0, 0.0, -5.0);

        let ray_a = (target - center_a).normalize();
        let ray_b = (target - center_b).normalize();

        // Convert to camera space rays (for identity rotation, world = camera)
        data.add_stereo_observation(
            center_a, center_b, rot_t_a, rot_t_b, ray_a, ray_b,
        );

        let result = triangulator.triangulate_points(&data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0], "Triangulation should be valid");

        let triangulated = &result.inner.points[0];
        assert_relative_eq!(triangulated.x, target.x, epsilon = 1e-6);
        assert_relative_eq!(triangulated.y, target.y, epsilon = 1e-6);
        assert_relative_eq!(triangulated.z, target.z, epsilon = 1e-6);
    }

    #[test]
    fn test_optimal_angular_multiple_points() {
        let mut triangulator =
            TriangulatorOptimalAngular::new_with_defaults(100);
        let mut data = TriangulateDataOptimalAngular::with_capacity(10);

        let (center_a, center_b, rot_t_a, rot_t_b) =
            create_simple_test_cameras();

        // Add multiple points at different depths
        let targets = vec![
            Point3::new(1.0, 0.0, -3.0),
            Point3::new(1.0, 1.0, -5.0),
            Point3::new(0.5, -0.5, -10.0),
            Point3::new(1.5, 0.5, -7.0),
        ];

        for target in &targets {
            let ray_a = (target - center_a).normalize();
            let ray_b = (target - center_b).normalize();
            data.add_stereo_observation(
                center_a, center_b, rot_t_a, rot_t_b, ray_a, ray_b,
            );
        }

        let result = triangulator.triangulate_points(&data);

        assert_eq!(result.inner.points.len(), targets.len());

        for (i, target) in targets.iter().enumerate() {
            assert!(result.inner.valid[i], "Point {} should be valid", i);
            let triangulated = &result.inner.points[i];
            assert_relative_eq!(triangulated.x, target.x, epsilon = 1e-5);
            assert_relative_eq!(triangulated.y, target.y, epsilon = 1e-5);
            assert_relative_eq!(triangulated.z, target.z, epsilon = 1e-5);
        }
    }

    #[test]
    fn test_optimal_angular_with_coords() {
        let mut triangulator =
            TriangulatorOptimalAngular::new_with_defaults(10);
        let mut data = TriangulateDataOptimalAngular::new();

        let (center_a, center_b, rot_t_a, rot_t_b) =
            create_simple_test_cameras();

        // Use normalized camera coordinates
        // For a point at (1, 0, -5):
        // Camera A sees it at direction (0.2, 0.0, -1) normalized
        // Camera B sees it at direction (-0.2, 0.0, -1) normalized
        data.add_stereo_observation_from_coords(
            center_a,
            center_b,
            rot_t_a,
            rot_t_b,
            (0.2, 0.0),  // camera_coord_a
            (-0.2, 0.0), // camera_coord_b
        );

        let result = triangulator.triangulate_points(&data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        // The triangulated point should be approximately at the expected location
        let triangulated = &result.inner.points[0];
        assert!(triangulated.z < 0.0, "Point should be in front of cameras");
    }

    #[test]
    fn test_optimal_angular_parallel_rays() {
        let mut triangulator =
            TriangulatorOptimalAngular::new_with_defaults(10);
        let mut data = TriangulateDataOptimalAngular::new();

        let center_a = Point3::new(0.0, 0.0, 0.0);
        let center_b = Point3::new(2.0, 0.0, 0.0);
        let rot_t = Matrix3::identity();

        // Parallel rays (looking straight ahead from both cameras)
        let ray = Vector3::new(0.0, 0.0, -1.0);

        data.add_stereo_observation(center_a, center_b, rot_t, rot_t, ray, ray);

        let result = triangulator.triangulate_points(&data);

        // Parallel rays have no unique intersection - should still produce
        // a result (midpoint at infinity or a fallback)
        assert_eq!(result.inner.points.len(), 1);
        // The result might not be valid depending on implementation
    }

    #[test]
    fn test_optimal_angular_configuration() {
        let config = OptimalAngularConfig {
            max_iterations: 50,
            function_tolerance: 1e-10,
            parameter_tolerance: 1e-10,
            gradient_tolerance: 1e-10,
            max_angular_error: 0.05,
        };

        let mut triangulator = TriangulatorOptimalAngular::new(10, config);
        assert_eq!(triangulator.config().max_iterations, 50);
        assert_eq!(triangulator.config().max_angular_error, 0.05);

        // Update config
        triangulator.set_config(OptimalAngularConfig::default());
        assert_eq!(triangulator.config().max_iterations, 20);
    }

    #[test]
    fn test_optimal_angular_data_operations() {
        let mut data = TriangulateDataOptimalAngular::new();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);

        let (center_a, center_b, rot_t_a, rot_t_b) =
            create_simple_test_cameras();
        let ray = Vector3::new(0.0, 0.0, -1.0);

        data.add_stereo_observation(
            center_a, center_b, rot_t_a, rot_t_b, ray, ray,
        );

        assert!(!data.is_empty());
        assert_eq!(data.len(), 1);

        data.clear();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);
    }

    #[test]
    fn test_optimal_angular_capacity() {
        let mut triangulator = TriangulatorOptimalAngular::new_with_defaults(5);

        // Initial capacity
        assert!(triangulator.capacity() >= 5);

        // Reserve more
        triangulator.reserve(100);
        assert!(triangulator.capacity() >= 100);
    }
}
