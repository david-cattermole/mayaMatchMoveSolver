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

//! Single-camera bundle adjustment with fixed 3D points (PnP refinement).
//!
//! Optimizes one camera pose against fixed 3D points.
//!
//! Parameter layout: `[rot_x, rot_y, rot_z, tx, ty, tz]`

use std::ops::{Add, Div, Mul, Sub};

use anyhow::Result;
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

/// Sparsity pattern for single-camera bundle adjustment.
///
/// Camera 0 is always unlocked; all points are always locked.
pub struct SingleCameraSparsityPattern {
    num_points: usize,
}

impl mmoptimise::solver::common::SparsityPattern
    for SingleCameraSparsityPattern
{
    fn observation_to_params(&self, obs_idx: usize) -> (usize, usize) {
        // Camera index is always 0, point_idx matches obs_idx
        (0, obs_idx)
    }

    fn num_observations(&self) -> usize {
        self.num_points // One observation per point
    }

    fn is_camera_unlocked(&self, _camera_idx: usize) -> bool {
        true // Single camera always unlocked
    }

    fn is_point_unlocked(&self, _point_idx: usize) -> bool {
        false // All points locked (fixed)
    }

    fn num_cameras(&self) -> usize {
        1 // Always exactly 1 camera
    }

    fn num_points(&self) -> usize {
        self.num_points
    }
}

/// Bundle adjustment problem that optimizes a single camera pose against
/// fixed 3D points.
///
/// Parameter layout: `[rot_x, rot_y, rot_z, tx, ty, tz]`
pub struct SingleCameraBAProblem {
    /// Sparsity pattern for solver interface
    sparsity: SingleCameraSparsityPattern,

    /// Observations in NDC coordinates (one per point).
    observations_ndc: Vec<(f64, f64)>,

    /// Camera intrinsics.
    focal_length_x: f64,
    focal_length_y: f64,
    principal_point: (f64, f64),

    /// Fixed 3D points (always locked, not optimized).
    bundle_points: Vec<[f64; 3]>,

    /// Initial camera rotation as full quaternion [w, x, y, z].
    initial_rotation: [f64; 4],

    /// Initial camera translation [tx, ty, tz].
    initial_translation: [f64; 3],
}

impl SingleCameraBAProblem {
    /// Creates a new single-camera bundle adjustment problem.
    ///
    /// `observations` is a list of `(point_idx, obs_ndc_x, obs_ndc_y)` tuples.
    pub fn new(
        observations: &[(usize, f64, f64)],
        focal_length_x: f64,
        focal_length_y: f64,
        principal_point: (f64, f64),
        camera_rotation: [f64; 4],
        camera_translation: [f64; 3],
        bundle_points: &[[f64; 3]],
    ) -> Self {
        let num_points = bundle_points.len();

        // Validate observations
        for &(pt_idx, _, _) in observations {
            assert!(
                pt_idx < num_points,
                "Point index {} out of bounds (max {})",
                pt_idx,
                num_points
            );
        }

        // Build observation arrays indexed by point
        let mut observations_ndc = vec![(f64::NAN, f64::NAN); num_points];

        for &(point_idx, obs_x, obs_y) in observations {
            observations_ndc[point_idx] = (obs_x, obs_y);
        }

        mm_debug_eprintln!(
            "[SingleCameraBA] Created with {} points, {} observations",
            num_points,
            observations.len()
        );

        let sparsity = SingleCameraSparsityPattern { num_points };

        Self {
            sparsity,
            observations_ndc,
            focal_length_x,
            focal_length_y,
            principal_point,
            bundle_points: bundle_points.to_vec(),
            initial_rotation: camera_rotation,
            initial_translation: camera_translation,
        }
    }

    /// Pack initial parameters into `[rot_x, rot_y, rot_z, tx, ty, tz]`.
    ///
    /// Rotation perturbation starts at zero (identity).
    pub fn pack_parameters(&self) -> Vec<f64> {
        vec![
            0.0, // rot_x perturbation
            0.0, // rot_y perturbation
            0.0, // rot_z perturbation
            self.initial_translation[0],
            self.initial_translation[1],
            self.initial_translation[2],
        ]
    }

    /// Extract the final camera rotation matrix from the optimized parameter vector.
    pub fn extract_camera_rotation_matrix(
        &self,
        parameters: &[f64],
    ) -> Matrix3<f64> {
        let perturbation = [parameters[0], parameters[1], parameters[2]];

        // Compose perturbation with initial rotation
        let perturb_full = quaternion_from_vector_f64(&perturbation);
        let composed =
            quaternion_multiply(&perturb_full, &self.initial_rotation);

        // Normalize
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

        quaternion_full_to_rotation_matrix(&normalized)
    }

    /// Extract the final camera translation from the optimized parameter vector.
    pub fn extract_camera_translation(&self, parameters: &[f64]) -> [f64; 3] {
        [parameters[3], parameters[4], parameters[5]]
    }

    /// Get number of fixed 3D points.
    pub fn num_points(&self) -> usize {
        self.bundle_points.len()
    }

    /// Get a fixed point by index.
    #[inline]
    fn get_point(&self, point_idx: usize) -> [f64; 3] {
        self.bundle_points[point_idx]
    }
}

impl OptimisationProblem for SingleCameraBAProblem {
    type Sparsity = SingleCameraSparsityPattern;

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

        // Extract camera parameters
        let perturbation_f64 = [
            NumCast::from(parameters[0]).unwrap(),
            NumCast::from(parameters[1]).unwrap(),
            NumCast::from(parameters[2]).unwrap(),
        ];
        let translation_f64 = [
            NumCast::from(parameters[3]).unwrap(),
            NumCast::from(parameters[4]).unwrap(),
            NumCast::from(parameters[5]).unwrap(),
        ];

        // Precompute composed rotation for camera
        let camera_rotation_f64 =
            compose_rotation_generic(&perturbation_f64, &self.initial_rotation);

        for point_idx in 0..self.bundle_points.len() {
            // Skip points without observations
            if self.observations_ndc[point_idx].0.is_nan() {
                continue;
            }

            let residual_idx = point_idx * 2;
            let point_3d_f64 = self.get_point(point_idx);

            // Compute 2x6 camera Jacobian block
            let mut camera_block = [[T::zero(); 6]; 2];

            // Derivatives w.r.t. rotation (indices 0-2)
            for param_idx in 0..3 {
                let mut dual_perturb = [
                    Dual::new(perturbation_f64[0], 0.0),
                    Dual::new(perturbation_f64[1], 0.0),
                    Dual::new(perturbation_f64[2], 0.0),
                ];
                dual_perturb[param_idx].dual = 1.0;

                let dual_rot = compose_rotation_generic(
                    &dual_perturb,
                    &self.initial_rotation,
                );

                let dual_point = [
                    Dual::new(point_3d_f64[0], 0.0),
                    Dual::new(point_3d_f64[1], 0.0),
                    Dual::new(point_3d_f64[2], 0.0),
                ];
                let dual_trans = [
                    Dual::new(translation_f64[0], 0.0),
                    Dual::new(translation_f64[1], 0.0),
                    Dual::new(translation_f64[2], 0.0),
                ];

                let (proj_u, proj_v) = project_point_generic(
                    &dual_point,
                    &dual_rot,
                    &dual_trans,
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

            // Derivatives w.r.t. translation (indices 3-5)
            for param_idx in 0..3 {
                let mut dual_trans = [
                    Dual::new(translation_f64[0], 0.0),
                    Dual::new(translation_f64[1], 0.0),
                    Dual::new(translation_f64[2], 0.0),
                ];
                dual_trans[param_idx].dual = 1.0;

                let dual_rot = [
                    Dual::new(camera_rotation_f64[0], 0.0),
                    Dual::new(camera_rotation_f64[1], 0.0),
                    Dual::new(camera_rotation_f64[2], 0.0),
                    Dual::new(camera_rotation_f64[3], 0.0),
                ];
                let dual_point = [
                    Dual::new(point_3d_f64[0], 0.0),
                    Dual::new(point_3d_f64[1], 0.0),
                    Dual::new(point_3d_f64[2], 0.0),
                ];

                let (proj_u, proj_v) = project_point_generic(
                    &dual_point,
                    &dual_rot,
                    &dual_trans,
                    Dual::new(self.focal_length_x, 0.0),
                    Dual::new(self.focal_length_y, 0.0),
                    (
                        Dual::new(self.principal_point.0, 0.0),
                        Dual::new(self.principal_point.1, 0.0),
                    ),
                );

                camera_block[0][param_idx + 3] =
                    NumCast::from(proj_u.dual).unwrap();
                camera_block[1][param_idx + 3] =
                    NumCast::from(proj_v.dual).unwrap();
                eval_count += 1;
            }

            // Point block is all zeros (points are fixed)
            let point_block = [[T::zero(); 3]; 2];

            blocks
                .blocks
                .push((residual_idx, camera_block, point_block));
        }

        Ok(eval_count)
    }

    fn jacobian_sparsity_pattern(&self) -> Option<&Self::Sparsity> {
        Some(&self.sparsity)
    }

    fn parameter_count(&self) -> usize {
        // 6 camera params (3 rotation + 3 translation).
        6
    }

    fn residual_count(&self) -> usize {
        // 2 residuals per observed point.
        //
        // Count non-NaN observations.
        self.observations_ndc
            .iter()
            .filter(|(x, _)| !x.is_nan())
            .count()
            * 2
    }

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
        // Extract camera parameters.
        let perturbation = [parameters[0], parameters[1], parameters[2]];
        let translation = [parameters[3], parameters[4], parameters[5]];

        // Convert perturbation to f64 for compose_rotation_generic.
        let perturbation_f64: [f64; 3] = [
            NumCast::from(perturbation[0]).unwrap(),
            NumCast::from(perturbation[1]).unwrap(),
            NumCast::from(perturbation[2]).unwrap(),
        ];

        // Compose camera rotation.
        let rotation: [T; 4] = {
            let composed = compose_rotation_generic(
                &perturbation_f64,
                &self.initial_rotation,
            );
            [
                NumCast::from(composed[0]).unwrap(),
                NumCast::from(composed[1]).unwrap(),
                NumCast::from(composed[2]).unwrap(),
                NumCast::from(composed[3]).unwrap(),
            ]
        };

        // Convert intrinsics.
        let focal_length_x: T = NumCast::from(self.focal_length_x).unwrap();
        let focal_length_y: T = NumCast::from(self.focal_length_y).unwrap();
        let principal_point: (T, T) = (
            NumCast::from(self.principal_point.0).unwrap(),
            NumCast::from(self.principal_point.1).unwrap(),
        );

        // Compute residuals for each observation.
        let mut residual_idx = 0;
        for point_idx in 0..self.bundle_points.len() {
            let (obs_ndc_x, obs_ndc_y) = self.observations_ndc[point_idx];
            if obs_ndc_x.is_nan() {
                continue;
            }

            // Get fixed point.
            let point_f64 = self.get_point(point_idx);
            let point_3d: [T; 3] = [
                NumCast::from(point_f64[0]).unwrap(),
                NumCast::from(point_f64[1]).unwrap(),
                NumCast::from(point_f64[2]).unwrap(),
            ];

            let (proj_ndc_x, proj_ndc_y) = project_point_generic(
                &point_3d,
                &rotation,
                &translation,
                focal_length_x,
                focal_length_y,
                principal_point,
            );

            // Compute residuals.
            let obs_ndc_x_t: T = NumCast::from(obs_ndc_x).unwrap();
            let obs_ndc_y_t: T = NumCast::from(obs_ndc_y).unwrap();
            out_residuals[residual_idx] = proj_ndc_x - obs_ndc_x_t;
            out_residuals[residual_idx + 1] = proj_ndc_y - obs_ndc_y_t;
            residual_idx += 2;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parameter_count() {
        let observations = vec![(0, 0.0, 0.0), (1, 0.1, 0.1)];
        let points = [[0.0, 0.0, -5.0], [1.0, 0.0, -5.0]];
        let problem = SingleCameraBAProblem::new(
            &observations,
            1.0, // focal_length_x
            1.0, // focal_length_y
            (0.0, 0.0),
            [1.0, 0.0, 0.0, 0.0], // identity quaternion
            [0.0, 0.0, 0.0],
            &points,
        );

        assert_eq!(problem.parameter_count(), 6);
    }

    #[test]
    fn test_residual_count() {
        let observations = vec![(0, 0.0, 0.0), (1, 0.1, 0.1)];
        let points = [[0.0, 0.0, -5.0], [1.0, 0.0, -5.0]];
        let problem = SingleCameraBAProblem::new(
            &observations,
            1.0,
            1.0,
            (0.0, 0.0),
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            &points,
        );

        // 2 observations * 2 residuals each = 4
        assert_eq!(problem.residual_count(), 4);
    }

    #[test]
    fn test_pack_parameters() {
        let observations = vec![(0, 0.0, 0.0)];
        let points = [[0.0, 0.0, -5.0]];
        let problem = SingleCameraBAProblem::new(
            &observations,
            1.0,
            1.0,
            (0.0, 0.0),
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 2.0, 3.0], // initial translation
            &points,
        );

        let params = problem.pack_parameters();
        assert_eq!(params.len(), 6);
        // Rotation perturbation should be zero
        assert_eq!(params[0], 0.0);
        assert_eq!(params[1], 0.0);
        assert_eq!(params[2], 0.0);
        // Translation should match initial
        assert_eq!(params[3], 1.0);
        assert_eq!(params[4], 2.0);
        assert_eq!(params[5], 3.0);
    }
}
