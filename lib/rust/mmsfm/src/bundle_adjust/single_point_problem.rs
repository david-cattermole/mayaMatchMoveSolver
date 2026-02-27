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

//! Single-point bundle adjustment with fixed cameras.
//!
//! Optimizes one 3D point position against fixed camera poses.
//!
//! Parameter layout: `[px, py, pz]`

use std::ops::{Add, Div, Mul, Sub};

use anyhow::Result;
use num_traits::{Float, NumCast, Zero};

use mmoptimise::solver::common::{OptimisationProblem, SparseJacobianBlocks};

use crate::bundle_adjust::maths::project_point_generic;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Sparsity pattern for single-point bundle adjustment.
///
/// All cameras are always locked; point 0 is always unlocked.
pub struct SinglePointSparsityPattern {
    num_cameras: usize,
}

impl mmoptimise::solver::common::SparsityPattern
    for SinglePointSparsityPattern
{
    fn observation_to_params(&self, obs_idx: usize) -> (usize, usize) {
        // Camera index matches obs_idx, point_idx is always 0
        (obs_idx, 0)
    }

    fn num_observations(&self) -> usize {
        self.num_cameras // One observation per camera
    }

    fn is_camera_unlocked(&self, _camera_idx: usize) -> bool {
        false // All cameras locked (fixed)
    }

    fn is_point_unlocked(&self, _point_idx: usize) -> bool {
        true // Single point always unlocked
    }

    fn num_cameras(&self) -> usize {
        self.num_cameras
    }

    fn num_points(&self) -> usize {
        1 // Always exactly 1 point
    }
}

/// Bundle adjustment problem that optimizes a single 3D point position
/// against fixed camera poses.
///
/// Parameter layout: `[px, py, pz]`
pub struct SinglePointBAProblem {
    /// Sparsity pattern for solver interface
    sparsity: SinglePointSparsityPattern,

    /// Observations in NDC coordinates (one per camera).
    /// Index matches camera index.
    observations_ndc: Vec<(f64, f64)>,

    /// Camera intrinsics.
    focal_length_x: f64,
    focal_length_y: f64,
    principal_point: (f64, f64),

    /// Fixed camera rotations as full quaternions [w, x, y, z].
    camera_rotations: Vec<[f64; 4]>,

    /// Fixed camera translations [tx, ty, tz].
    camera_translations: Vec<[f64; 3]>,

    /// Initial 3D point position [px, py, pz].
    initial_point: [f64; 3],
}

impl SinglePointBAProblem {
    /// Creates a new single-point bundle adjustment problem.
    ///
    /// `observations` is a list of `(camera_idx, obs_ndc_x, obs_ndc_y)` tuples.
    pub fn new(
        observations: Vec<(usize, f64, f64)>,
        focal_length_x: f64,
        focal_length_y: f64,
        principal_point: (f64, f64),
        camera_rotations: &[[f64; 4]],
        camera_translations: &[[f64; 3]],
        initial_point: [f64; 3],
    ) -> Self {
        let num_cameras = camera_rotations.len();
        assert_eq!(
            camera_rotations.len(),
            camera_translations.len(),
            "Camera rotations and translations must have same length"
        );

        // Validate observations
        for &(cam_idx, _, _) in &observations {
            assert!(
                cam_idx < num_cameras,
                "Camera index {} out of bounds (max {})",
                cam_idx,
                num_cameras
            );
        }

        // Build observation arrays indexed by camera
        let mut observations_ndc = vec![(f64::NAN, f64::NAN); num_cameras];

        for &(camera_idx, obs_x, obs_y) in &observations {
            observations_ndc[camera_idx] = (obs_x, obs_y);
        }

        mm_eprintln_debug!(
            "[SinglePointBA] Created with {} cameras, {} observations",
            num_cameras,
            observations.len()
        );

        let sparsity = SinglePointSparsityPattern { num_cameras };

        Self {
            sparsity,
            observations_ndc,
            focal_length_x,
            focal_length_y,
            principal_point,
            camera_rotations: camera_rotations.to_vec(),
            camera_translations: camera_translations.to_vec(),
            initial_point,
        }
    }

    /// Pack initial parameters into `[px, py, pz]`.
    pub fn pack_parameters(&self) -> Vec<f64> {
        vec![
            self.initial_point[0],
            self.initial_point[1],
            self.initial_point[2],
        ]
    }

    /// Extract the final 3D point position from the optimized parameter vector.
    pub fn extract_point(&self, parameters: &[f64]) -> [f64; 3] {
        [parameters[0], parameters[1], parameters[2]]
    }

    /// Get number of cameras (observations).
    pub fn num_cameras(&self) -> usize {
        self.camera_rotations.len()
    }

    /// Get a fixed camera rotation by index.
    #[inline]
    fn get_camera_rotation(&self, camera_idx: usize) -> [f64; 4] {
        self.camera_rotations[camera_idx]
    }

    /// Get a fixed camera translation by index.
    #[inline]
    fn get_camera_translation(&self, camera_idx: usize) -> [f64; 3] {
        self.camera_translations[camera_idx]
    }
}

impl OptimisationProblem for SinglePointBAProblem {
    type Sparsity = SinglePointSparsityPattern;

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

        // Extract point parameters
        let point_f64 = [
            NumCast::from(parameters[0]).unwrap(),
            NumCast::from(parameters[1]).unwrap(),
            NumCast::from(parameters[2]).unwrap(),
        ];

        for camera_idx in 0..self.camera_rotations.len() {
            // Skip cameras without observations
            if self.observations_ndc[camera_idx].0.is_nan() {
                continue;
            }

            let residual_idx = camera_idx * 2;

            // Camera is fixed, so camera block is all zeros
            let camera_block = [[T::zero(); 6]; 2];

            // Compute 2x3 point Jacobian block
            let mut point_block = [[T::zero(); 3]; 2];

            let cam_rot = self.get_camera_rotation(camera_idx);
            let cam_trans = self.get_camera_translation(camera_idx);

            // Derivatives w.r.t. point position (indices 0-2)
            for param_idx in 0..3 {
                let mut dual_point = [
                    Dual::new(point_f64[0], 0.0),
                    Dual::new(point_f64[1], 0.0),
                    Dual::new(point_f64[2], 0.0),
                ];
                dual_point[param_idx].dual = 1.0;

                let dual_rot = [
                    Dual::new(cam_rot[0], 0.0),
                    Dual::new(cam_rot[1], 0.0),
                    Dual::new(cam_rot[2], 0.0),
                    Dual::new(cam_rot[3], 0.0),
                ];
                let dual_trans = [
                    Dual::new(cam_trans[0], 0.0),
                    Dual::new(cam_trans[1], 0.0),
                    Dual::new(cam_trans[2], 0.0),
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
        Some(&self.sparsity)
    }

    fn parameter_count(&self) -> usize {
        // 3 point params (x, y, z).
        3
    }

    fn residual_count(&self) -> usize {
        // 2 residuals per observed camera.
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
        // Extract point parameters.
        let point_3d = [parameters[0], parameters[1], parameters[2]];

        // Convert intrinsics.
        let focal_length_x: T = NumCast::from(self.focal_length_x).unwrap();
        let focal_length_y: T = NumCast::from(self.focal_length_y).unwrap();
        let principal_point: (T, T) = (
            NumCast::from(self.principal_point.0).unwrap(),
            NumCast::from(self.principal_point.1).unwrap(),
        );

        // Compute residuals for each observation.
        let mut residual_idx = 0;
        for camera_idx in 0..self.camera_rotations.len() {
            let (obs_ndc_x, obs_ndc_y) = self.observations_ndc[camera_idx];
            if obs_ndc_x.is_nan() {
                continue;
            }

            // Get fixed camera pose.
            let cam_rot = self.get_camera_rotation(camera_idx);
            let cam_trans = self.get_camera_translation(camera_idx);

            let rotation: [T; 4] = [
                NumCast::from(cam_rot[0]).unwrap(),
                NumCast::from(cam_rot[1]).unwrap(),
                NumCast::from(cam_rot[2]).unwrap(),
                NumCast::from(cam_rot[3]).unwrap(),
            ];
            let translation: [T; 3] = [
                NumCast::from(cam_trans[0]).unwrap(),
                NumCast::from(cam_trans[1]).unwrap(),
                NumCast::from(cam_trans[2]).unwrap(),
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
        let rotations = [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]];
        let translations = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]];
        let problem = SinglePointBAProblem::new(
            observations,
            1.0, // focal_length_x
            1.0, // focal_length_y
            (0.0, 0.0),
            &rotations,
            &translations,
            [0.0, 0.0, -5.0], // initial point
        );

        assert_eq!(problem.parameter_count(), 3);
    }

    #[test]
    fn test_residual_count() {
        let observations = vec![(0, 0.0, 0.0), (1, 0.1, 0.1)];
        let rotations = [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]];
        let translations = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]];
        let problem = SinglePointBAProblem::new(
            observations,
            1.0,
            1.0,
            (0.0, 0.0),
            &rotations,
            &translations,
            [0.0, 0.0, -5.0],
        );

        // 2 observations * 2 residuals each = 4
        assert_eq!(problem.residual_count(), 4);
    }

    #[test]
    fn test_pack_parameters() {
        let observations = vec![(0, 0.0, 0.0)];
        let rotations = [[1.0, 0.0, 0.0, 0.0]];
        let translations = [[0.0, 0.0, 0.0]];
        let problem = SinglePointBAProblem::new(
            observations,
            1.0,
            1.0,
            (0.0, 0.0),
            &rotations,
            &translations,
            [1.0, 2.0, -5.0], // initial point
        );

        let params = problem.pack_parameters();
        assert_eq!(params.len(), 3);
        assert_eq!(params[0], 1.0);
        assert_eq!(params[1], 2.0);
        assert_eq!(params[2], -5.0);
    }

    #[test]
    fn test_extract_point() {
        let observations = vec![(0, 0.0, 0.0)];
        let rotations = [[1.0, 0.0, 0.0, 0.0]];
        let translations = [[0.0, 0.0, 0.0]];
        let problem = SinglePointBAProblem::new(
            observations,
            1.0,
            1.0,
            (0.0, 0.0),
            &rotations,
            &translations,
            [0.0, 0.0, -5.0],
        );

        let params = vec![3.0, 4.0, -10.0];
        let point = problem.extract_point(&params);
        assert_eq!(point, [3.0, 4.0, -10.0]);
    }
}
