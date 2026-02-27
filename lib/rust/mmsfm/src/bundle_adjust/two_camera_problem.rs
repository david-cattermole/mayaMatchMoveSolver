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

//! Two-camera bundle adjustment with a spherical translation constraint.
//!
//! Camera A is fixed at the origin. Camera B's translation is always unit
//! length, enforced by representing it as two angles (azimuth and elevation).

use std::ops::{Add, Div, Mul, Sub};

use anyhow::Result;
use nalgebra::Matrix3;
use num_traits::{Float, NumCast, Zero};

use mmoptimise::solver::common::{
    OptimisationProblem, SparseJacobianBlocks, SparsityPattern,
};

use crate::bundle_adjust::maths::{
    cartesian_to_spherical, compose_rotation_generic, project_point_generic,
    quaternion_from_vector_f64, quaternion_full_to_rotation_matrix,
    quaternion_multiply, spherical_to_cartesian,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Sparsity pattern for two-camera bundle adjustment.
///
/// Camera 0 (A) is always locked at the origin; camera 1 (B) and all points
/// are always unlocked.
pub struct TwoCameraSparsityPattern {
    pub observation_map: Vec<(usize, usize)>,
    num_points: usize,
}

impl mmoptimise::solver::common::SparsityPattern for TwoCameraSparsityPattern {
    fn observation_to_params(&self, obs_idx: usize) -> (usize, usize) {
        self.observation_map[obs_idx]
    }

    fn num_observations(&self) -> usize {
        self.observation_map.len()
    }

    fn is_camera_unlocked(&self, camera_idx: usize) -> bool {
        camera_idx == 1 // Only Camera B is unlocked
    }

    fn is_point_unlocked(&self, _point_idx: usize) -> bool {
        true // All points unlocked
    }

    fn num_cameras(&self) -> usize {
        2 // Always exactly 2 cameras
    }

    fn num_points(&self) -> usize {
        self.num_points
    }
}

/// Bundle adjustment problem for two cameras where camera A is fixed at the
/// origin and camera B has a unit-length translation constraint.
///
/// Parameter layout: `[rot_x, rot_y, rot_z, theta, phi, pt0_x, pt0_y, pt0_z, ...]`
///
/// Camera B's translation is stored as spherical angles (theta, phi) so that
/// `||t|| = 1` is automatically satisfied.
pub struct TwoCameraBAProblem {
    sparsity_pattern: TwoCameraSparsityPattern,

    /// NDC observations, indexed as `camera_idx * num_points + point_idx`.
    observations_ndc: Vec<(f64, f64)>,

    focal_length_x: f64,
    focal_length_y: f64,
    principal_point: (f64, f64),

    num_bundle_points: usize,
    bundle_points: Vec<[f64; 3]>,

    /// Camera B initial rotation as full quaternion [w, x, y, z].
    camera_b_initial_rotation: [f64; 4],

    /// Camera B initial translation, used to compute initial spherical angles.
    camera_b_initial_translation: [f64; 3],
}

impl TwoCameraBAProblem {
    /// Creates a new two-camera bundle adjustment problem.
    ///
    /// `observations` is a list of `(camera_idx, point_idx, obs_ndc_x, obs_ndc_y)` tuples
    /// where `camera_idx` must be 0 (camera A) or 1 (camera B).
    /// `camera_b_translation` will be normalised to unit length.
    pub fn new(
        observations: Vec<(usize, usize, f64, f64)>,
        focal_length_x: f64,
        focal_length_y: f64,
        principal_point: (f64, f64),
        camera_b_rotation: [f64; 4],
        camera_b_translation: [f64; 3],
        initial_bundle_points: &[[f64; 3]],
    ) -> Self {
        let num_cameras = 2;
        let num_points = initial_bundle_points.len();

        // Validate observations
        for &(cam_idx, pt_idx, _, _) in &observations {
            assert!(
                cam_idx < 2,
                "Camera index must be 0 or 1, got {}",
                cam_idx
            );
            assert!(
                pt_idx < num_points,
                "Point index {} out of bounds (max {})",
                pt_idx,
                num_points
            );
        }

        // Build observation arrays
        let mut observations_ndc =
            vec![(f64::NAN, f64::NAN); num_cameras * num_points];

        for &(camera_idx, point_idx, obs_x, obs_y) in &observations {
            let idx = camera_idx * num_points + point_idx;
            observations_ndc[idx] = (obs_x, obs_y);
        }

        // Compute sparsity structure
        let observation_map: Vec<(usize, usize)> = observations
            .iter()
            .map(|&(cam_idx, pt_idx, _, _)| (cam_idx, pt_idx))
            .collect();

        let sparsity_pattern = TwoCameraSparsityPattern {
            observation_map,
            num_points,
        };

        mm_eprintln_debug!(
            "[TwoCameraBA] Created with {} points, {} observations",
            num_points,
            observations.len()
        );
        if DEBUG {
            let (theta, phi) = cartesian_to_spherical(&camera_b_translation);
            mm_eprintln_debug!(
                "[TwoCameraBA] Initial translation: [{:.4}, {:.4}, {:.4}] -> theta={:.4}, phi={:.4}",
                camera_b_translation[0], camera_b_translation[1], camera_b_translation[2],
                theta, phi
            );
        }

        Self {
            sparsity_pattern,
            observations_ndc,
            focal_length_x,
            focal_length_y,
            principal_point,
            num_bundle_points: num_points,
            bundle_points: initial_bundle_points.to_vec(),
            camera_b_initial_rotation: camera_b_rotation,
            camera_b_initial_translation: camera_b_translation,
        }
    }

    /// Pack initial parameters into `[rot_x, rot_y, rot_z, theta, phi, pt0_x, pt0_y, pt0_z, ...]`.
    ///
    /// Rotation perturbation starts at zero (identity).
    pub fn pack_parameters(&self) -> Vec<f64> {
        let mut params = Vec::with_capacity(self.parameter_count());

        // Rotation perturbation starts at identity.
        params.extend_from_slice(&[0.0, 0.0, 0.0]);

        // Camera B translation as spherical angles
        let (theta, phi) =
            cartesian_to_spherical(&self.camera_b_initial_translation);
        params.push(theta);
        params.push(phi);

        // All points
        for point in &self.bundle_points {
            params.extend_from_slice(point);
        }

        params
    }

    /// Extract the final camera B rotation matrix from the optimized parameter vector.
    pub fn extract_camera_b_rotation_matrix(
        &self,
        parameters: &[f64],
    ) -> Matrix3<f64> {
        let perturbation = [parameters[0], parameters[1], parameters[2]];

        // Compose perturbation with initial rotation
        let perturb_full = quaternion_from_vector_f64(&perturbation);
        let composed =
            quaternion_multiply(&perturb_full, &self.camera_b_initial_rotation);

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

    /// Extract the final camera B translation from the optimized parameter vector.
    pub fn extract_camera_b_translation(&self, parameters: &[f64]) -> [f64; 3] {
        let theta = parameters[3];
        let phi = parameters[4];
        spherical_to_cartesian(theta, phi)
    }

    /// Get point parameters from the parameter vector.
    #[inline]
    fn get_point<T>(&self, parameters: &[T], point_idx: usize) -> [T; 3]
    where
        T: Float + Copy,
    {
        // Points start at index 5 (after 5 camera B params)
        let offset = 5 + point_idx * 3;
        [
            parameters[offset],
            parameters[offset + 1],
            parameters[offset + 2],
        ]
    }

    /// Get number of cameras (always 2).
    pub fn num_cameras(&self) -> usize {
        2
    }

    /// Get number of points.
    pub fn num_points(&self) -> usize {
        self.num_bundle_points
    }
}

impl OptimisationProblem for TwoCameraBAProblem {
    type Sparsity = TwoCameraSparsityPattern;

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

        // Extract camera B parameters
        let perturbation_f64 = [
            NumCast::from(parameters[0]).unwrap(),
            NumCast::from(parameters[1]).unwrap(),
            NumCast::from(parameters[2]).unwrap(),
        ];
        let theta_f64: f64 = NumCast::from(parameters[3]).unwrap();
        let phi_f64: f64 = NumCast::from(parameters[4]).unwrap();

        // Precompute camera B composed rotation (for point Jacobian)
        let camera_b_rotation_f64 = compose_rotation_generic(
            &perturbation_f64,
            &self.camera_b_initial_rotation,
        );

        // Precompute spherical derivatives for camera B translation Jacobian
        let cos_phi = phi_f64.cos();
        let sin_phi = phi_f64.sin();
        let cos_theta = theta_f64.cos();
        let sin_theta = theta_f64.sin();

        // d[tx,ty,tz]/d[theta]
        let dt_dtheta = [
            cos_phi * cos_theta,  // dtx/dtheta
            0.0,                  // dty/dtheta
            -cos_phi * sin_theta, // dtz/dtheta
        ];
        // d[tx,ty,tz]/d[phi]
        let dt_dphi = [
            -sin_phi * sin_theta, // dtx/dphi
            cos_phi,              // dty/dphi
            -sin_phi * cos_theta, // dtz/dphi
        ];

        for (obs_idx, &(cam_idx, point_idx)) in
            self.sparsity_pattern.observation_map.iter().enumerate()
        {
            let residual_idx = obs_idx * 2;

            // Get point (convert T to f64)
            let point_3d = self.get_point(parameters, point_idx);
            let point_3d_f64: [f64; 3] = [
                NumCast::from(point_3d[0]).unwrap(),
                NumCast::from(point_3d[1]).unwrap(),
                NumCast::from(point_3d[2]).unwrap(),
            ];

            if cam_idx == 0 {
                // Camera A is fixed - only point derivatives matter
                // Camera block is all zeros (6x2, but we use 6 for compatibility)
                let camera_block = [[T::zero(); 6]; 2];

                // Compute 2x3 point Jacobian block
                let mut point_block = [[T::zero(); 3]; 2];

                // Camera A is identity
                let cam_a_rot = [1.0, 0.0, 0.0, 0.0];
                let cam_a_trans = [0.0, 0.0, 0.0];

                for param_idx in 0..3 {
                    let mut dual_point = [
                        Dual::new(point_3d_f64[0], 0.0),
                        Dual::new(point_3d_f64[1], 0.0),
                        Dual::new(point_3d_f64[2], 0.0),
                    ];
                    dual_point[param_idx].dual = 1.0;

                    let dual_rot = [
                        Dual::new(cam_a_rot[0], 0.0),
                        Dual::new(cam_a_rot[1], 0.0),
                        Dual::new(cam_a_rot[2], 0.0),
                        Dual::new(cam_a_rot[3], 0.0),
                    ];
                    let dual_trans = [
                        Dual::new(cam_a_trans[0], 0.0),
                        Dual::new(cam_a_trans[1], 0.0),
                        Dual::new(cam_a_trans[2], 0.0),
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

                    point_block[0][param_idx] =
                        NumCast::from(proj_u.dual).unwrap();
                    point_block[1][param_idx] =
                        NumCast::from(proj_v.dual).unwrap();
                    eval_count += 1;
                }

                blocks
                    .blocks
                    .push((residual_idx, camera_block, point_block));
            } else {
                // Camera B - compute full 2x5 camera Jacobian (stored in 2x6 block)
                // Parameters: [rot_x, rot_y, rot_z, theta, phi, (unused)]
                let mut camera_block = [[T::zero(); 6]; 2];

                // Get current translation from spherical
                let translation_f64 =
                    spherical_to_cartesian(theta_f64, phi_f64);

                // Compute derivatives w.r.t. rotation (indices 0-2)
                for param_idx in 0..3 {
                    let mut dual_perturb = [
                        Dual::new(perturbation_f64[0], 0.0),
                        Dual::new(perturbation_f64[1], 0.0),
                        Dual::new(perturbation_f64[2], 0.0),
                    ];
                    dual_perturb[param_idx].dual = 1.0;

                    let dual_rot = compose_rotation_generic(
                        &dual_perturb,
                        &self.camera_b_initial_rotation,
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

                // Compute derivatives w.r.t. theta and phi (indices 3-4)
                // Using chain rule: d(res)/d(theta) = sum over i: d(res)/d(ti) * dti/dtheta
                for param_idx in 0..3 {
                    // Compute d(residual)/d(translation[param_idx])
                    let mut dual_trans = [
                        Dual::new(translation_f64[0], 0.0),
                        Dual::new(translation_f64[1], 0.0),
                        Dual::new(translation_f64[2], 0.0),
                    ];
                    dual_trans[param_idx].dual = 1.0;

                    let dual_rot = [
                        Dual::new(camera_b_rotation_f64[0], 0.0),
                        Dual::new(camera_b_rotation_f64[1], 0.0),
                        Dual::new(camera_b_rotation_f64[2], 0.0),
                        Dual::new(camera_b_rotation_f64[3], 0.0),
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

                    let dres_u_dti = proj_u.dual;
                    let dres_v_dti = proj_v.dual;

                    // Accumulate chain rule for theta (index 3)
                    let dres_u_dtheta: f64 =
                        NumCast::from(camera_block[0][3]).unwrap();
                    let dres_v_dtheta: f64 =
                        NumCast::from(camera_block[1][3]).unwrap();
                    camera_block[0][3] = NumCast::from(
                        dres_u_dtheta + dres_u_dti * dt_dtheta[param_idx],
                    )
                    .unwrap();
                    camera_block[1][3] = NumCast::from(
                        dres_v_dtheta + dres_v_dti * dt_dtheta[param_idx],
                    )
                    .unwrap();

                    // Accumulate chain rule for phi (index 4)
                    let dres_u_dphi: f64 =
                        NumCast::from(camera_block[0][4]).unwrap();
                    let dres_v_dphi: f64 =
                        NumCast::from(camera_block[1][4]).unwrap();
                    camera_block[0][4] = NumCast::from(
                        dres_u_dphi + dres_u_dti * dt_dphi[param_idx],
                    )
                    .unwrap();
                    camera_block[1][4] = NumCast::from(
                        dres_v_dphi + dres_v_dti * dt_dphi[param_idx],
                    )
                    .unwrap();

                    eval_count += 1;
                }

                // Index 5 is unused (we only have 5 camera params, not 6)
                // It remains zero from initialization

                // Compute 2x3 point Jacobian block
                let mut point_block = [[T::zero(); 3]; 2];

                for param_idx in 0..3 {
                    let mut dual_point = [
                        Dual::new(point_3d_f64[0], 0.0),
                        Dual::new(point_3d_f64[1], 0.0),
                        Dual::new(point_3d_f64[2], 0.0),
                    ];
                    dual_point[param_idx].dual = 1.0;

                    let dual_rot = [
                        Dual::new(camera_b_rotation_f64[0], 0.0),
                        Dual::new(camera_b_rotation_f64[1], 0.0),
                        Dual::new(camera_b_rotation_f64[2], 0.0),
                        Dual::new(camera_b_rotation_f64[3], 0.0),
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

                    point_block[0][param_idx] =
                        NumCast::from(proj_u.dual).unwrap();
                    point_block[1][param_idx] =
                        NumCast::from(proj_v.dual).unwrap();
                    eval_count += 1;
                }

                blocks
                    .blocks
                    .push((residual_idx, camera_block, point_block));
            }
        }

        Ok(eval_count)
    }

    fn jacobian_sparsity_pattern(&self) -> Option<&Self::Sparsity> {
        Some(&self.sparsity_pattern)
    }

    fn parameter_count(&self) -> usize {
        // 5 camera B params + 3 per point
        5 + self.num_bundle_points * 3
    }

    fn residual_count(&self) -> usize {
        // 2 residuals per observation
        self.sparsity_pattern.num_observations() * 2
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
        // Extract camera B parameters
        let perturbation = [parameters[0], parameters[1], parameters[2]];
        let theta = parameters[3];
        let phi = parameters[4];

        // Convert camera B perturbation to f64 for compose_rotation_generic
        let perturbation_f64: [f64; 3] = [
            NumCast::from(perturbation[0]).unwrap(),
            NumCast::from(perturbation[1]).unwrap(),
            NumCast::from(perturbation[2]).unwrap(),
        ];

        // Compose camera B rotation
        let camera_b_rotation: [T; 4] = {
            let composed = compose_rotation_generic(
                &perturbation_f64,
                &self.camera_b_initial_rotation,
            );
            [
                NumCast::from(composed[0]).unwrap(),
                NumCast::from(composed[1]).unwrap(),
                NumCast::from(composed[2]).unwrap(),
                NumCast::from(composed[3]).unwrap(),
            ]
        };

        // Convert spherical to Cartesian for camera B translation
        let camera_b_translation = spherical_to_cartesian(theta, phi);

        // Camera A is identity
        let camera_a_rotation: [T; 4] = [
            NumCast::from(1.0).unwrap(),
            NumCast::from(0.0).unwrap(),
            NumCast::from(0.0).unwrap(),
            NumCast::from(0.0).unwrap(),
        ];
        let camera_a_translation: [T; 3] = [
            NumCast::from(0.0).unwrap(),
            NumCast::from(0.0).unwrap(),
            NumCast::from(0.0).unwrap(),
        ];

        // Convert intrinsics
        let focal_length_x: T = NumCast::from(self.focal_length_x).unwrap();
        let focal_length_y: T = NumCast::from(self.focal_length_y).unwrap();
        let principal_point: (T, T) = (
            NumCast::from(self.principal_point.0).unwrap(),
            NumCast::from(self.principal_point.1).unwrap(),
        );

        // Compute residuals for each observation
        for (obs_idx, &(cam_idx, point_idx)) in
            self.sparsity_pattern.observation_map.iter().enumerate()
        {
            let residual_idx = obs_idx * 2;

            // Select camera parameters
            let (rotation, translation) = if cam_idx == 0 {
                (&camera_a_rotation, &camera_a_translation)
            } else {
                (&camera_b_rotation, &camera_b_translation)
            };

            // Get observation
            let obs_array_idx = cam_idx * self.num_bundle_points + point_idx;
            let (obs_ndc_x, obs_ndc_y) = self.observations_ndc[obs_array_idx];

            // Get point
            let point_3d = self.get_point(parameters, point_idx);

            // Project
            let (proj_ndc_x, proj_ndc_y) = project_point_generic(
                &point_3d,
                rotation,
                translation,
                focal_length_x,
                focal_length_y,
                principal_point,
            );

            // Compute residuals
            let obs_ndc_x_t: T = NumCast::from(obs_ndc_x).unwrap();
            let obs_ndc_y_t: T = NumCast::from(obs_ndc_y).unwrap();
            out_residuals[residual_idx] = proj_ndc_x - obs_ndc_x_t;
            out_residuals[residual_idx + 1] = proj_ndc_y - obs_ndc_y_t;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spherical_cartesian_roundtrip() {
        // Test that converting to spherical and back gives original unit vector
        let test_cases = [
            [1.0, 0.0, 0.0],       // +X
            [0.0, 1.0, 0.0],       // +Y (near pole)
            [0.0, 0.0, 1.0],       // +Z
            [-1.0, 0.0, 0.0],      // -X
            [0.0, -1.0, 0.0],      // -Y (near pole)
            [0.0, 0.0, -1.0],      // -Z
            [0.577, 0.577, 0.577], // Diagonal
        ];

        for original in &test_cases {
            let (theta, phi) = cartesian_to_spherical(original);
            let recovered = spherical_to_cartesian::<f64>(theta, phi);

            // Check unit length
            let norm = (recovered[0] * recovered[0]
                + recovered[1] * recovered[1]
                + recovered[2] * recovered[2])
                .sqrt();
            assert!(
                (norm - 1.0).abs() < 1e-10,
                "Recovered vector should be unit length"
            );

            // Normalize original for comparison
            let orig_norm = (original[0] * original[0]
                + original[1] * original[1]
                + original[2] * original[2])
                .sqrt();
            let orig_unit = [
                original[0] / orig_norm,
                original[1] / orig_norm,
                original[2] / orig_norm,
            ];

            // Check direction matches
            for i in 0..3 {
                assert!(
                    (recovered[i] - orig_unit[i]).abs() < 1e-6,
                    "Direction should match: expected {:?}, got {:?}",
                    orig_unit,
                    recovered
                );
            }
        }
    }

    #[test]
    fn test_spherical_always_unit_length() {
        // Test that any spherical angles give unit length
        use std::f64::consts::PI;

        for theta_deg in (-180..=180).step_by(30) {
            for phi_deg in (-90..=90).step_by(30) {
                let theta = (theta_deg as f64) * PI / 180.0;
                let phi = (phi_deg as f64) * PI / 180.0;

                let t = spherical_to_cartesian::<f64>(theta, phi);
                let norm = (t[0] * t[0] + t[1] * t[1] + t[2] * t[2]).sqrt();

                assert!(
                    (norm - 1.0).abs() < 1e-14,
                    "Spherical coords ({}, {}) should give unit vector, got norm {}",
                    theta_deg, phi_deg, norm
                );
            }
        }
    }
}
