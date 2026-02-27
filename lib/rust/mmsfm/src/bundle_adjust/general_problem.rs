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

use std::ops::{Add, Div, Mul, Sub};

use anyhow::{bail, Result};
use nalgebra::Matrix3;
use num_traits::{Float, NumCast, Zero};

use mmoptimise::solver::common::{OptimisationProblem, SparseJacobianBlocks};

use crate::bundle_adjust::maths::{
    compose_rotation_generic, project_point_generic,
    quaternion_from_vector_f64, quaternion_full_to_rotation_matrix,
    quaternion_multiply,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Sparsity pattern for general bundle adjustment.
///
/// All cameras and points are unlocked (optimizable).
pub struct GeneralBundleAdjustmentSparsityPattern {
    pub observation_map: Vec<(usize, usize)>,
    num_cameras: usize,
    num_points: usize,
}

impl mmoptimise::solver::common::SparsityPattern
    for GeneralBundleAdjustmentSparsityPattern
{
    fn observation_to_params(&self, obs_idx: usize) -> (usize, usize) {
        self.observation_map[obs_idx]
    }

    fn num_observations(&self) -> usize {
        self.observation_map.len()
    }

    fn is_camera_unlocked(&self, _camera_idx: usize) -> bool {
        true
    }

    fn is_point_unlocked(&self, _point_idx: usize) -> bool {
        true // All points unlocked in general BA
    }

    fn num_cameras(&self) -> usize {
        self.num_cameras
    }

    fn num_points(&self) -> usize {
        self.num_points
    }
}

/// Bundle adjustment problem that simultaneously optimizes all camera poses and
/// 3D point positions to minimize reprojection error.
///
/// Each camera has 6 parameters (3 rotation + 3 translation) and each point
/// has 3 parameters (x, y, z). All parameters are optimizable.
pub struct GeneralBundleAdjustmentProblem {
    sparsity_pattern: GeneralBundleAdjustmentSparsityPattern,

    /// NDC observations, indexed as `camera_idx * num_points + point_idx`.
    /// Missing observations are `(NaN, NaN)`.
    observations_ndc: Vec<(f64, f64)>,

    /// Normalized focal length in X: `focal_length_mm / film_back_width_mm`.
    focal_length_x: f64,

    /// Normalized focal length in Y: `focal_length_mm / film_back_height_mm`.
    focal_length_y: f64,

    /// Principal point in NDC coordinates, range [-1, 1], centre at (0, 0).
    principal_point: (f64, f64),

    num_cameras: usize,
    num_points: usize,

    /// Initial camera rotations as full quaternions [w, x, y, z].
    initial_rotations: Vec<[f64; 4]>,

    /// Initial camera translations [tx, ty, tz].
    initial_translations: Vec<[f64; 3]>,

    initial_bundle_points: Vec<[f64; 3]>,
}

impl GeneralBundleAdjustmentProblem {
    /// Creates a new general bundle adjustment problem.
    ///
    /// `observations` is a list of `(camera_idx, point_idx, obs_ndc_x, obs_ndc_y)` tuples.
    /// `initial_camera_poses` is a list of `(quaternion [w,x,y,z], translation)` tuples.
    pub fn new(
        observations: Vec<(usize, usize, f64, f64)>,
        focal_length_x: f64,
        focal_length_y: f64,
        principal_point: (f64, f64),
        initial_camera_poses: &[([f64; 4], [f64; 3])],
        initial_bundle_points: &[[f64; 3]],
    ) -> Self {
        if DEBUG {
            // Validate initial camera poses for NaN/Inf.
            for (i, (quat, trans)) in initial_camera_poses.iter().enumerate() {
                for (j, &v) in quat.iter().chain(trans.iter()).enumerate() {
                    if !v.is_finite() {
                        mm_eprintln_debug!(
                        "ERROR: GeneralBundleAdjustmentProblem::new: Camera {} param {} is NaN/Inf: {}",
                        i, j, v
                    );
                    }
                }
            }

            // Validate initial bundle points for NaN/Inf.
            for (i, point) in initial_bundle_points.iter().enumerate() {
                for (j, &v) in point.iter().enumerate() {
                    if !v.is_finite() {
                        mm_eprintln_debug!(
                        "ERROR: GeneralBundleAdjustmentProblem::new: Point {} coord {} is NaN/Inf: {}",
                        i, j, v
                    );
                    }
                }
            }
        }

        let num_cameras = initial_camera_poses.len();
        let num_points = initial_bundle_points.len();

        // Initialize observation arrays with NaN (missing observations)
        let mut observations_ndc =
            vec![(f64::NAN, f64::NAN); num_cameras * num_points];

        // Populate observations from sparse input
        for &(camera_idx, point_idx, obs_x, obs_y) in &observations {
            let idx = camera_idx * num_points + point_idx;
            observations_ndc[idx] = (obs_x, obs_y);
        }

        // Compute sparsity structure for efficient sparse Jacobian computation
        let observation_map: Vec<(usize, usize)> = observations
            .iter()
            .map(|&(cam_idx, pt_idx, _, _)| (cam_idx, pt_idx))
            .collect();

        let sparsity_pattern = GeneralBundleAdjustmentSparsityPattern {
            observation_map,
            num_cameras,
            num_points,
        };

        // SBA-style rotation parameterization:
        // Store initial rotations as full quaternions [w, x, y, z].
        let initial_rotations: Vec<[f64; 4]> = initial_camera_poses
            .iter()
            .map(|(quaternion, _)| *quaternion)
            .collect();

        if DEBUG {
            for (i, rot) in initial_rotations.iter().enumerate() {
                let norm = (rot[0] * rot[0]
                    + rot[1] * rot[1]
                    + rot[2] * rot[2]
                    + rot[3] * rot[3])
                    .sqrt();
                mm_eprintln_debug!(
                    "[BA_PROBLEM::new] Camera {} initial_rot=[{:.6}, {:.6}, {:.6}, {:.6}], norm={:.6}",
                    i, rot[0], rot[1], rot[2], rot[3], norm
                );
            }
        }
        let initial_translations: Vec<[f64; 3]> = initial_camera_poses
            .iter()
            .map(|(_, translation)| *translation)
            .collect();

        let initial_bundle_points = initial_bundle_points.to_vec();

        Self {
            sparsity_pattern,
            observations_ndc,
            focal_length_x,
            focal_length_y,
            principal_point,
            num_cameras,
            num_points,
            initial_rotations,
            initial_translations,
            initial_bundle_points,
        }
    }

    pub fn num_cameras(&self) -> usize {
        self.num_cameras
    }

    pub fn num_points(&self) -> usize {
        self.num_points
    }

    /// Pack camera poses and 3D points into a flat parameter vector.
    ///
    /// Layout: `[rot_x, rot_y, rot_z, tx, ty, tz, ...]` per camera, then `[x, y, z, ...]` per point.
    /// Rotation perturbation starts at zero (identity).
    pub fn pack_parameters(&self) -> Vec<f64> {
        let mut params = Vec::with_capacity(self.parameter_count());

        // Pack cameras (6 params each).
        for i in 0..self.num_cameras {
            // Initial rotation perturbation is 0
            params.extend_from_slice(&[0.0, 0.0, 0.0]);
            // Initial translation is the current translation
            params.extend_from_slice(&self.initial_translations[i]);
        }

        // Pack points (3 params each).
        for i in 0..self.num_points {
            params.extend_from_slice(&self.initial_bundle_points[i]);
        }

        params
    }

    /// Extract the final rotation matrix for a camera from the optimized parameter vector.
    pub fn extract_camera_rotation_matrix(
        &self,
        parameters: &[f64],
        camera_idx: usize,
    ) -> Matrix3<f64> {
        let (perturbation, _) = self.get_camera(parameters, camera_idx);
        let initial_rot = self.initial_rotations[camera_idx];

        let perturb_full = quaternion_from_vector_f64(&perturbation);
        let composed = quaternion_multiply(&perturb_full, &initial_rot);

        // Normalize to handle accumulated numerical errors
        let norm = (composed[0] * composed[0]
            + composed[1] * composed[1]
            + composed[2] * composed[2]
            + composed[3] * composed[3])
            .sqrt();
        let normalized = [
            composed[0] / norm,
            composed[1] / norm,
            composed[2] / norm,
            composed[3] / norm,
        ];

        mm_eprintln_debug!(
            "[BA_PROBLEM::extract] camera_idx={}, perturb=[{:.6},{:.6},{:.6}] -> full=[{:.6},{:.6},{:.6},{:.6}]",
            camera_idx, perturbation[0], perturbation[1], perturbation[2],
            perturb_full[0], perturb_full[1], perturb_full[2], perturb_full[3]
        );
        mm_eprintln_debug!(
            "[BA_PROBLEM::extract] camera_idx={}, initial=[{:.6},{:.6},{:.6},{:.6}]",
            camera_idx, initial_rot[0], initial_rot[1], initial_rot[2], initial_rot[3]
        );
        mm_eprintln_debug!(
            "[BA_PROBLEM::extract] camera_idx={}, composed=[{:.6},{:.6},{:.6},{:.6}], norm={:.6}",
            camera_idx, normalized[0], normalized[1], normalized[2], normalized[3], norm
        );

        // Convert directly to rotation matrix (no 3-param intermediate).
        quaternion_full_to_rotation_matrix(&normalized)
    }

    /// Get camera parameters (rotation perturbation and translation)
    fn get_camera<T>(
        &self,
        parameters: &[T],
        camera_idx: usize,
    ) -> ([T; 3], [T; 3])
    where
        T: Float + Copy,
    {
        let param_offset = camera_idx * 6;
        let rotation = [
            parameters[param_offset],
            parameters[param_offset + 1],
            parameters[param_offset + 2],
        ];
        let translation = [
            parameters[param_offset + 3],
            parameters[param_offset + 4],
            parameters[param_offset + 5],
        ];
        (rotation, translation)
    }

    /// Get point parameters
    fn get_point<T>(&self, parameters: &[T], point_idx: usize) -> [T; 3]
    where
        T: Float + Copy,
    {
        // Points start after all camera parameters
        let param_offset = (self.num_cameras * 6) + point_idx * 3;
        [
            parameters[param_offset],
            parameters[param_offset + 1],
            parameters[param_offset + 2],
        ]
    }
}

impl OptimisationProblem for GeneralBundleAdjustmentProblem {
    type Sparsity = GeneralBundleAdjustmentSparsityPattern;

    fn sparse_jacobian_blocks<T>(
        &self,
        parameters: &[T],
        blocks: &mut SparseJacobianBlocks<T>,
    ) -> Result<usize>
    where
        T: Float + Copy,
    {
        use mmcore::dual::Dual;

        let mut eval_count = 0;
        blocks.clear();

        for (obs_idx, &(cam_idx, point_idx)) in
            self.sparsity_pattern.observation_map.iter().enumerate()
        {
            let residual_idx = obs_idx * 2;

            let (camera_perturbation, camera_trans) =
                self.get_camera(parameters, cam_idx);
            let point_3d = self.get_point(parameters, point_idx);

            let camera_perturbation_f64 = [
                NumCast::from(camera_perturbation[0]).unwrap(),
                NumCast::from(camera_perturbation[1]).unwrap(),
                NumCast::from(camera_perturbation[2]).unwrap(),
            ];
            let camera_trans_f64 = [
                NumCast::from(camera_trans[0]).unwrap(),
                NumCast::from(camera_trans[1]).unwrap(),
                NumCast::from(camera_trans[2]).unwrap(),
            ];
            let point_3d_f64 = [
                NumCast::from(point_3d[0]).unwrap(),
                NumCast::from(point_3d[1]).unwrap(),
                NumCast::from(point_3d[2]).unwrap(),
            ];

            let initial_rot = self.initial_rotations[cam_idx];

            // 2x6 Camera Block
            let mut camera_block = [[T::zero(); 6]; 2];
            for param_idx in 0..6 {
                let mut dual_cam_perturbation = [
                    Dual::new(camera_perturbation_f64[0], 0.0),
                    Dual::new(camera_perturbation_f64[1], 0.0),
                    Dual::new(camera_perturbation_f64[2], 0.0),
                ];
                let mut dual_cam_trans = [
                    Dual::new(camera_trans_f64[0], 0.0),
                    Dual::new(camera_trans_f64[1], 0.0),
                    Dual::new(camera_trans_f64[2], 0.0),
                ];

                if param_idx < 3 {
                    dual_cam_perturbation[param_idx].dual = 1.0;
                } else {
                    dual_cam_trans[param_idx - 3].dual = 1.0;
                }

                let dual_cam_rot = compose_rotation_generic(
                    &dual_cam_perturbation,
                    &initial_rot,
                );

                let dual_point = [
                    Dual::new(point_3d_f64[0], 0.0),
                    Dual::new(point_3d_f64[1], 0.0),
                    Dual::new(point_3d_f64[2], 0.0),
                ];

                let (proj_u, proj_v) = project_point_generic(
                    &dual_point,
                    &dual_cam_rot,
                    &dual_cam_trans,
                    Dual::new(self.focal_length_x, 0.0),
                    Dual::new(self.focal_length_y, 0.0),
                    (
                        Dual::new(self.principal_point.0, 0.0),
                        Dual::new(self.principal_point.1, 0.0),
                    ),
                );

                camera_block[0][param_idx] =
                    NumCast::from(proj_u.dual).unwrap();
                camera_block[1][param_idx] =
                    NumCast::from(proj_v.dual).unwrap();

                eval_count += 1;
            }

            // 2x3 Point Block
            let mut point_block = [[T::zero(); 3]; 2];
            let composed_rot_f64 = compose_rotation_generic(
                &camera_perturbation_f64,
                &initial_rot,
            );

            for param_idx in 0..3 {
                let mut dual_point = [
                    Dual::new(point_3d_f64[0], 0.0),
                    Dual::new(point_3d_f64[1], 0.0),
                    Dual::new(point_3d_f64[2], 0.0),
                ];
                dual_point[param_idx].dual = 1.0;

                let dual_cam_rot = [
                    Dual::new(composed_rot_f64[0], 0.0),
                    Dual::new(composed_rot_f64[1], 0.0),
                    Dual::new(composed_rot_f64[2], 0.0),
                    Dual::new(composed_rot_f64[3], 0.0),
                ];
                let dual_cam_trans = [
                    Dual::new(camera_trans_f64[0], 0.0),
                    Dual::new(camera_trans_f64[1], 0.0),
                    Dual::new(camera_trans_f64[2], 0.0),
                ];

                let (proj_u, proj_v) = project_point_generic(
                    &dual_point,
                    &dual_cam_rot,
                    &dual_cam_trans,
                    Dual::new(self.focal_length_x, 0.0),
                    Dual::new(self.focal_length_y, 0.0),
                    (
                        Dual::new(self.principal_point.0, 0.0),
                        Dual::new(self.principal_point.1, 0.0),
                    ),
                );

                point_block[0][param_idx] = NumCast::from(proj_u.dual).unwrap();
                point_block[1][param_idx] = NumCast::from(proj_v.dual).unwrap();

                eval_count += 1;
            }

            blocks
                .blocks
                .push((residual_idx, camera_block, point_block));
        }

        Ok(eval_count)
    }

    fn jacobian_sparsity_pattern(&self) -> Option<&Self::Sparsity> {
        Some(&self.sparsity_pattern)
    }

    fn parameter_count(&self) -> usize {
        self.num_cameras * 6 + self.num_points * 3
    }

    fn residual_count(&self) -> usize {
        // Each observation produces 2 residuals (u and v).
        //
        // Count non-NaN observations.
        let mut count = 0;
        for (obs_x, obs_y) in &self.observations_ndc {
            if !obs_x.is_nan() && !obs_y.is_nan() {
                count += 1;
            }
        }
        count * 2
    }

    /// Compute residuals for all observations.
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let focal_length_x = NumCast::from(self.focal_length_x).unwrap();
        let focal_length_y = NumCast::from(self.focal_length_y).unwrap();
        let principal_point = (
            NumCast::from(self.principal_point.0).unwrap(),
            NumCast::from(self.principal_point.1).unwrap(),
        );

        let mut invalid_parameter_count = 0;
        let mut invalid_proj_ndc_count = 0;

        let check_validity = true;
        if check_validity {
            for parameter_value in parameters {
                if !parameter_value.is_finite() {
                    invalid_parameter_count += 1;
                }
            }
        }

        // Iterate over observation_map in the SAME ORDER as Jacobian blocks.
        //
        // This ensures residuals[i] corresponds to jacobian_block[i].
        for (obs_idx, &(cam_idx, point_idx)) in
            self.sparsity_pattern.observation_map.iter().enumerate()
        {
            let residual_idx = obs_idx * 2;

            let (perturbation, translation) =
                self.get_camera(parameters, cam_idx);

            let initial_rot = self.initial_rotations[cam_idx];
            let rotation =
                compose_rotation_generic(&perturbation, &initial_rot);

            let observation_array_idx = cam_idx * self.num_points + point_idx;
            let (obs_ndc_x, obs_ndc_y) =
                self.observations_ndc[observation_array_idx];

            let point_3d = self.get_point(parameters, point_idx);

            let (proj_ndc_x, proj_ndc_y) = project_point_generic(
                &point_3d,
                &rotation,
                &translation,
                focal_length_x,
                focal_length_y,
                principal_point,
            );

            // Check if projection is invalid (sentinel value detected).
            if check_validity {
                if !proj_ndc_x.is_finite() || !proj_ndc_y.is_finite() {
                    invalid_proj_ndc_count += 1;
                }
            }

            // Compute residuals (predicted - observed).
            let obs_ndc_x_t = NumCast::from(obs_ndc_x).unwrap();
            let obs_ndc_y_t = NumCast::from(obs_ndc_y).unwrap();
            out_residuals[residual_idx] = proj_ndc_x - obs_ndc_x_t;
            out_residuals[residual_idx + 1] = proj_ndc_y - obs_ndc_y_t;
        }

        let invalid_parameters = invalid_parameter_count > 0;
        let invalid_proj_ndc = invalid_proj_ndc_count > 0;
        if check_validity && (invalid_parameters || invalid_proj_ndc) {
            bail!(
                "Bundle adjustment residuals contain invalid values: \
                 {} non-finite parameters, {} behind-camera projections",
                invalid_parameter_count,
                invalid_proj_ndc_count
            );
        }

        Ok(())
    }
}

// Implementation of SparseOptimisationProblem trait for sparse solvers.
impl mmoptimise::sparse::SparseOptimisationProblem
    for GeneralBundleAdjustmentProblem
{
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        self.residuals(parameters, out_residuals)?;

        let num_observations = self.sparsity_pattern.observation_map.len();
        let max_nonzeros = num_observations * 2 * (6 + 3);
        let mut row_indices = Vec::with_capacity(max_nonzeros);
        let mut col_indices = Vec::with_capacity(max_nonzeros);
        let mut values = Vec::with_capacity(max_nonzeros);

        let mut jacobian_blocks = SparseJacobianBlocks::<f64>::new();
        self.sparse_jacobian_blocks(parameters, &mut jacobian_blocks)?;

        for &(residual_idx, camera_block, point_block) in
            &jacobian_blocks.blocks
        {
            let residual_row_base = residual_idx;
            let obs_idx = residual_idx / 2;
            let (camera_idx, point_idx) =
                self.sparsity_pattern.observation_map[obs_idx];

            // Camera block: 2x6
            let camera_col_base = camera_idx * 6;
            for row in 0..2 {
                for col in 0..6 {
                    let value = camera_block[row][col];
                    if value.abs() > 1e-20 {
                        row_indices.push(residual_row_base + row);
                        col_indices.push(camera_col_base + col);
                        values.push(value);
                    }
                }
            }

            // Point block: 2x3
            let point_col_base = (self.num_cameras * 6) + point_idx * 3;
            for row in 0..2 {
                for col in 0..3 {
                    let value = point_block[row][col];
                    if value.abs() > 1e-20 {
                        row_indices.push(residual_row_base + row);
                        col_indices.push(point_col_base + col);
                        values.push(value);
                    }
                }
            }
        }

        Ok((row_indices, col_indices, values))
    }

    fn parameter_count(&self) -> usize {
        self.num_cameras * 6 + self.num_points * 3
    }

    fn residual_count(&self) -> usize {
        self.sparsity_pattern.observation_map.len() * 2
    }
}
