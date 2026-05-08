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

//! Synthetic bundle adjustment test problem for validating the Schur
//! complement solver.
//!
//! Provides a self-contained BA problem with pinhole cameras, 3D
//! points, and analytic Jacobians.

use anyhow::Result;

use crate::sparse::schur_complement::SchurStructuredProblem;
use crate::sparse::SparseOptimisationProblem;

/// Camera block size: 6 parameters (rx, ry, rz, tx, ty, tz).
#[allow(dead_code)]
const CAM_BLOCK_SIZE: usize = 6;

/// Point block size: 3 parameters (x, y, z).
#[allow(dead_code)]
const PT_BLOCK_SIZE: usize = 3;

/// Synthetic BA problem with pinhole cameras and 3D points.
///
/// Parameter layout: `[cam0_rx, cam0_ry, cam0_rz, cam0_tx, cam0_ty,
/// cam0_tz, cam1_..., ..., pt0_x, pt0_y, pt0_z, pt1_..., ...]`
///
/// Each observation produces 2 residuals (projected_u - observed_u,
/// projected_v - observed_v).
#[allow(dead_code)]
pub struct SyntheticBAProblem {
    pub num_cameras: usize,
    pub num_points: usize,
    /// (camera_idx, point_idx) per observation.
    pub observations: Vec<(usize, usize)>,
    /// Ground-truth 2D observations (u, v) per observation.
    pub observed_uv: Vec<[f64; 2]>,
    /// Focal length (pixels).
    pub focal_length: f64,
    /// Principal point.
    pub cx: f64,
    pub cy: f64,
    /// Camera lock status.
    pub camera_unlocked: Vec<bool>,
    /// Point lock status.
    pub point_unlocked: Vec<bool>,
}

impl SyntheticBAProblem {
    /// Create a synthetic problem with cameras on a circle looking
    /// at points near the origin.
    ///
    /// Ground-truth cameras are at radius `camera_radius` on the XZ
    /// plane, looking at the origin. Points are random in a unit
    /// cube. Observations are all-to-all (full visibility).
    #[allow(dead_code)]
    pub fn new_circle(
        num_cameras: usize,
        num_points: usize,
        camera_radius: f64,
        seed: u64,
    ) -> (Self, Vec<f64>) {
        let focal_length = 800.0;
        let cx = 320.0;
        let cy = 240.0;

        // Simple deterministic PRNG (xorshift64).
        let mut rng_state = seed;
        let mut rng = || -> f64 {
            rng_state ^= rng_state << 13;
            rng_state ^= rng_state >> 7;
            rng_state ^= rng_state << 17;
            (rng_state as f64 / u64::MAX as f64) * 2.0 - 1.0
        };

        // Generate ground-truth 3D points in [-0.5, 0.5]^3.
        let mut gt_points = Vec::with_capacity(num_points);
        for _ in 0..num_points {
            gt_points.push([rng() * 0.5, rng() * 0.5, rng() * 0.5]);
        }

        // Generate ground-truth cameras on a circle.
        let mut gt_cameras = Vec::with_capacity(num_cameras);
        for i in 0..num_cameras {
            let angle =
                2.0 * std::f64::consts::PI * i as f64 / num_cameras as f64;
            let tx = camera_radius * angle.sin();
            let ty = 0.0;
            let tz = camera_radius * angle.cos();

            // Camera looks at origin:
            // rotation = look_at(pos, origin, up=Y).
            //
            // We use Rodrigues representation.
            //
            // For simplicity, compute rotation matrix then
            // extract Rodrigues.
            let forward = [-tx / camera_radius, 0.0, -tz / camera_radius];
            let up = [0.0, 1.0, 0.0];
            let right = cross(&forward, &up);
            let right_norm = vec_norm(&right);
            let right = if right_norm > 1e-10 {
                [
                    right[0] / right_norm,
                    right[1] / right_norm,
                    right[2] / right_norm,
                ]
            } else {
                [1.0, 0.0, 0.0]
            };
            let up_corrected = cross(&right, &forward);

            // Rotation matrix: columns are right, up, -forward
            // (camera convention: Z points backward).
            let r = [
                [right[0], up_corrected[0], -forward[0]],
                [right[1], up_corrected[1], -forward[1]],
                [right[2], up_corrected[2], -forward[2]],
            ];

            let rodrigues = rotation_matrix_to_rodrigues(&r);
            // t_cam = -R * camera_world_position
            let t_cam = [
                -(r[0][0] * tx + r[0][1] * ty + r[0][2] * tz),
                -(r[1][0] * tx + r[1][1] * ty + r[1][2] * tz),
                -(r[2][0] * tx + r[2][1] * ty + r[2][2] * tz),
            ];
            gt_cameras.push([
                rodrigues[0],
                rodrigues[1],
                rodrigues[2],
                t_cam[0],
                t_cam[1],
                t_cam[2],
            ]);
        }

        // Generate observations and project.
        let mut observations = Vec::new();
        let mut observed_uv = Vec::new();
        for cam_idx in 0..num_cameras {
            let cam = &gt_cameras[cam_idx];
            let r_mat = rodrigues_to_rotation_matrix(&[cam[0], cam[1], cam[2]]);
            let t = [cam[3], cam[4], cam[5]];

            for pt_idx in 0..num_points {
                let pt = &gt_points[pt_idx];
                // Transform: p_cam = R * p_world + t
                //
                // NOTE: For "look at origin" cameras, we use:
                //   p_cam = R^T * (p_world - t)
                //
                // Which is equivalent to:
                //   R_inv * p_world + (-R_inv * t).
                //
                // Actually, the standard BA convention is:
                //   p_cam = R * p_world + t
                // where t is the camera position in cam curds.
                //
                // So we need:
                //   t_cam = -R * camera_position.
                let p_cam = [
                    r_mat[0][0] * pt[0]
                        + r_mat[0][1] * pt[1]
                        + r_mat[0][2] * pt[2]
                        + t[0],
                    r_mat[1][0] * pt[0]
                        + r_mat[1][1] * pt[1]
                        + r_mat[1][2] * pt[2]
                        + t[1],
                    r_mat[2][0] * pt[0]
                        + r_mat[2][1] * pt[1]
                        + r_mat[2][2] * pt[2]
                        + t[2],
                ];

                // Only add if point is in front of camera.
                if p_cam[2] > 0.1 {
                    let u = focal_length * p_cam[0] / p_cam[2] + cx;
                    let v = focal_length * p_cam[1] / p_cam[2] + cy;
                    observations.push((cam_idx, pt_idx));
                    observed_uv.push([u, v]);
                }
            }
        }

        // Build initial parameter vector (ground-truth).
        let n_params =
            num_cameras * CAM_BLOCK_SIZE + num_points * PT_BLOCK_SIZE;
        let mut parameters = vec![0.0; n_params];

        for (i, cam) in gt_cameras.iter().enumerate() {
            let offset = i * CAM_BLOCK_SIZE;
            parameters[offset..offset + 6].copy_from_slice(cam);
        }
        for (i, pt) in gt_points.iter().enumerate() {
            let offset = num_cameras * CAM_BLOCK_SIZE + i * PT_BLOCK_SIZE;
            parameters[offset..offset + 3].copy_from_slice(pt);
        }

        let camera_unlocked = vec![true; num_cameras];
        let point_unlocked = vec![true; num_points];

        let problem = SyntheticBAProblem {
            num_cameras,
            num_points,
            observations,
            observed_uv,
            focal_length,
            cx,
            cy,
            camera_unlocked,
            point_unlocked,
        };

        (problem, parameters)
    }

    /// Add noise to a parameter vector.
    #[allow(dead_code)]
    pub fn add_noise(
        parameters: &mut [f64],
        num_cameras: usize,
        cam_rotation_noise: f64,
        cam_translation_noise: f64,
        point_noise: f64,
        seed: u64,
    ) {
        let mut rng_state = seed;
        let mut rng = || -> f64 {
            rng_state ^= rng_state << 13;
            rng_state ^= rng_state >> 7;
            rng_state ^= rng_state << 17;
            (rng_state as f64 / u64::MAX as f64) * 2.0 - 1.0
        };

        // Add noise to camera rotations.
        for cam in 0..num_cameras {
            let offset = cam * CAM_BLOCK_SIZE;
            for i in 0..3 {
                parameters[offset + i] += rng() * cam_rotation_noise;
            }
            for i in 3..6 {
                parameters[offset + i] += rng() * cam_translation_noise;
            }
        }

        // Add noise to points.
        let pt_start = num_cameras * CAM_BLOCK_SIZE;
        for i in pt_start..parameters.len() {
            parameters[i] += rng() * point_noise;
        }
    }

    /// Number of camera parameters total (including locked).
    fn total_cam_params(&self) -> usize {
        self.num_cameras * CAM_BLOCK_SIZE
    }

    /// Project a 3D point through a camera, returning (u, v) and
    /// the intermediate `p_cam` for Jacobian computation.
    fn project(
        &self,
        cam_params: &[f64],
        point: &[f64],
    ) -> ([f64; 2], [f64; 3]) {
        let r_mat = rodrigues_to_rotation_matrix(&[
            cam_params[0],
            cam_params[1],
            cam_params[2],
        ]);
        let t = [cam_params[3], cam_params[4], cam_params[5]];

        let p_cam = [
            r_mat[0][0] * point[0]
                + r_mat[0][1] * point[1]
                + r_mat[0][2] * point[2]
                + t[0],
            r_mat[1][0] * point[0]
                + r_mat[1][1] * point[1]
                + r_mat[1][2] * point[2]
                + t[1],
            r_mat[2][0] * point[0]
                + r_mat[2][1] * point[1]
                + r_mat[2][2] * point[2]
                + t[2],
        ];

        let inv_z = 1.0 / p_cam[2];
        let u = self.focal_length * p_cam[0] * inv_z + self.cx;
        let v = self.focal_length * p_cam[1] * inv_z + self.cy;

        ([u, v], p_cam)
    }

    /// Compute analytic Jacobian blocks for one observation.
    ///
    /// Returns (J_camera: 2x6 row-major, J_point: 2x3 row-major).
    fn compute_jacobian_for_observation(
        &self,
        cam_params: &[f64],
        point: &[f64],
    ) -> ([f64; 12], [f64; 6]) {
        let rodrigues = [cam_params[0], cam_params[1], cam_params[2]];
        let r_mat = rodrigues_to_rotation_matrix(&rodrigues);
        let t = [cam_params[3], cam_params[4], cam_params[5]];

        let p_cam = [
            r_mat[0][0] * point[0]
                + r_mat[0][1] * point[1]
                + r_mat[0][2] * point[2]
                + t[0],
            r_mat[1][0] * point[0]
                + r_mat[1][1] * point[1]
                + r_mat[1][2] * point[2]
                + t[1],
            r_mat[2][0] * point[0]
                + r_mat[2][1] * point[1]
                + r_mat[2][2] * point[2]
                + t[2],
        ];

        let f = self.focal_length;
        let inv_z = 1.0 / p_cam[2];
        let inv_z2 = inv_z * inv_z;

        // d(u)/d(p_cam) = f * [1/z, 0, -x/z^2]
        // d(v)/d(p_cam) = f * [0, 1/z, -y/z^2]
        let du_dpc = [f * inv_z, 0.0, -f * p_cam[0] * inv_z2];
        let dv_dpc = [0.0, f * inv_z, -f * p_cam[1] * inv_z2];

        // d(p_cam)/d(translation) = I (3x3)
        // So d(u)/d(t) = du_dpc, d(v)/d(t) = dv_dpc

        // d(p_cam)/d(rodrigues): use numerical differentiation
        // of the rotation for robustness.
        let eps = 1e-7;
        let mut dr_dp_cam = [[0.0; 3]; 3]; // dr_dp_cam[rot_idx][cam_coord]
        for ri in 0..3 {
            let mut rod_plus = rodrigues;
            rod_plus[ri] += eps;
            let r_plus = rodrigues_to_rotation_matrix(&rod_plus);

            let mut rod_minus = rodrigues;
            rod_minus[ri] -= eps;
            let r_minus = rodrigues_to_rotation_matrix(&rod_minus);

            for ci in 0..3 {
                let p_plus = r_plus[ci][0] * point[0]
                    + r_plus[ci][1] * point[1]
                    + r_plus[ci][2] * point[2]
                    + t[ci];
                let p_minus = r_minus[ci][0] * point[0]
                    + r_minus[ci][1] * point[1]
                    + r_minus[ci][2] * point[2]
                    + t[ci];
                dr_dp_cam[ri][ci] = (p_plus - p_minus) / (2.0 * eps);
            }
        }

        // J_camera (2x6 row-major): [du/dr0, du/dr1, du/dr2,
        // du/dt0, du/dt1, du/dt2; dv/dr0, ...]
        let mut jc = [0.0; 12];
        for ri in 0..3 {
            // du/d(rod_ri) = du_dpc . dr_dp_cam[ri]
            jc[ri] = du_dpc[0] * dr_dp_cam[ri][0]
                + du_dpc[1] * dr_dp_cam[ri][1]
                + du_dpc[2] * dr_dp_cam[ri][2];
            // dv/d(rod_ri)
            jc[6 + ri] = dv_dpc[0] * dr_dp_cam[ri][0]
                + dv_dpc[1] * dr_dp_cam[ri][1]
                + dv_dpc[2] * dr_dp_cam[ri][2];
        }
        // du/d(t0..t2)
        jc[3] = du_dpc[0]; // du/dtx
        jc[4] = du_dpc[1]; // du/dty
        jc[5] = du_dpc[2]; // du/dtz
                           // dv/d(t0..t2)
        jc[9] = dv_dpc[0];
        jc[10] = dv_dpc[1];
        jc[11] = dv_dpc[2];

        // J_point (2x3 row-major):
        // d(p_cam)/d(point) = R (3x3)
        // du/d(point) = du_dpc * R
        // dv/d(point) = dv_dpc * R
        let mut jp = [0.0; 6];
        for ci in 0..3 {
            jp[ci] = du_dpc[0] * r_mat[0][ci]
                + du_dpc[1] * r_mat[1][ci]
                + du_dpc[2] * r_mat[2][ci];
            jp[3 + ci] = dv_dpc[0] * r_mat[0][ci]
                + dv_dpc[1] * r_mat[1][ci]
                + dv_dpc[2] * r_mat[2][ci];
        }

        (jc, jp)
    }
}

impl SparseOptimisationProblem for SyntheticBAProblem {
    fn parameter_count(&self) -> usize {
        self.num_cameras * CAM_BLOCK_SIZE + self.num_points * PT_BLOCK_SIZE
    }

    fn residual_count(&self) -> usize {
        self.observations.len() * 2
    }

    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let num_obs = self.observations.len();
        let mut row_indices = Vec::with_capacity(num_obs * 18);
        let mut col_indices = Vec::with_capacity(num_obs * 18);
        let mut values = Vec::with_capacity(num_obs * 18);

        for (obs_idx, &(cam_idx, pt_idx)) in
            self.observations.iter().enumerate()
        {
            let cam_offset = cam_idx * CAM_BLOCK_SIZE;
            let pt_offset = self.total_cam_params() + pt_idx * PT_BLOCK_SIZE;

            let cam_params = &parameters[cam_offset..cam_offset + 6];
            let point = &parameters[pt_offset..pt_offset + 3];

            let (uv, _) = self.project(cam_params, point);

            let res_idx = obs_idx * 2;
            out_residuals[res_idx] = uv[0] - self.observed_uv[obs_idx][0];
            out_residuals[res_idx + 1] = uv[1] - self.observed_uv[obs_idx][1];

            let (jc, jp) =
                self.compute_jacobian_for_observation(cam_params, point);

            // Camera block: 2 rows x 6 cols.
            if self.camera_unlocked[cam_idx] {
                for row in 0..2 {
                    for col in 0..CAM_BLOCK_SIZE {
                        let val = jc[row * CAM_BLOCK_SIZE + col];
                        if val.abs() > 1e-20 {
                            row_indices.push(res_idx + row);
                            col_indices.push(cam_offset + col);
                            values.push(val);
                        }
                    }
                }
            }

            // Point block: 2 rows x 3 cols.
            if self.point_unlocked[pt_idx] {
                for row in 0..2 {
                    for col in 0..PT_BLOCK_SIZE {
                        let val = jp[row * PT_BLOCK_SIZE + col];
                        if val.abs() > 1e-20 {
                            row_indices.push(res_idx + row);
                            col_indices.push(pt_offset + col);
                            values.push(val);
                        }
                    }
                }
            }
        }

        Ok((row_indices, col_indices, values))
    }
}

impl SchurStructuredProblem for SyntheticBAProblem {
    fn num_cameras(&self) -> usize {
        self.num_cameras
    }
    fn num_points(&self) -> usize {
        self.num_points
    }
    fn camera_block_size(&self) -> usize {
        CAM_BLOCK_SIZE
    }
    fn point_block_size(&self) -> usize {
        PT_BLOCK_SIZE
    }
    fn observation_structure(&self, obs_idx: usize) -> (usize, usize) {
        self.observations[obs_idx]
    }
    fn num_observations(&self) -> usize {
        self.observations.len()
    }
    fn is_camera_unlocked(&self, idx: usize) -> bool {
        self.camera_unlocked[idx]
    }
    fn is_point_unlocked(&self, idx: usize) -> bool {
        self.point_unlocked[idx]
    }

    fn compute_jacobian_blocks(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
        out_camera_blocks: &mut [f64],
        out_point_blocks: &mut [f64],
    ) -> Result<()> {
        for (obs_idx, &(cam_idx, pt_idx)) in
            self.observations.iter().enumerate()
        {
            let cam_offset = cam_idx * CAM_BLOCK_SIZE;
            let pt_offset = self.total_cam_params() + pt_idx * PT_BLOCK_SIZE;

            let cam_params = &parameters[cam_offset..cam_offset + 6];
            let point = &parameters[pt_offset..pt_offset + 3];

            let (uv, _) = self.project(cam_params, point);

            let res_idx = obs_idx * 2;
            out_residuals[res_idx] = uv[0] - self.observed_uv[obs_idx][0];
            out_residuals[res_idx + 1] = uv[1] - self.observed_uv[obs_idx][1];

            let (jc, jp) =
                self.compute_jacobian_for_observation(cam_params, point);

            // Write camera block (2x6 row-major).
            let jc_start = obs_idx * 2 * CAM_BLOCK_SIZE;
            out_camera_blocks[jc_start..jc_start + 12].copy_from_slice(&jc);

            // Write point block (2x3 row-major).
            let jp_start = obs_idx * 2 * PT_BLOCK_SIZE;
            out_point_blocks[jp_start..jp_start + 6].copy_from_slice(&jp);
        }

        Ok(())
    }
}

// ====================================================================
// Rotation helpers
// ====================================================================

fn cross(a: &[f64; 3], b: &[f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

fn vec_norm(v: &[f64; 3]) -> f64 {
    (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt()
}

/// Convert Rodrigues vector to 3x3 rotation matrix.
fn rodrigues_to_rotation_matrix(rod: &[f64; 3]) -> [[f64; 3]; 3] {
    let theta = vec_norm(rod);
    if theta < 1e-10 {
        // Near-zero rotation: return identity + skew.
        return [
            [1.0, -rod[2], rod[1]],
            [rod[2], 1.0, -rod[0]],
            [-rod[1], rod[0], 1.0],
        ];
    }

    let inv_theta = 1.0 / theta;
    let k = [rod[0] * inv_theta, rod[1] * inv_theta, rod[2] * inv_theta];
    let c = theta.cos();
    let s = theta.sin();
    let t = 1.0 - c;

    [
        [
            c + k[0] * k[0] * t,
            k[0] * k[1] * t - k[2] * s,
            k[0] * k[2] * t + k[1] * s,
        ],
        [
            k[1] * k[0] * t + k[2] * s,
            c + k[1] * k[1] * t,
            k[1] * k[2] * t - k[0] * s,
        ],
        [
            k[2] * k[0] * t - k[1] * s,
            k[2] * k[1] * t + k[0] * s,
            c + k[2] * k[2] * t,
        ],
    ]
}

/// Convert 3x3 rotation matrix to Rodrigues vector.
fn rotation_matrix_to_rodrigues(r: &[[f64; 3]; 3]) -> [f64; 3] {
    let trace = r[0][0] + r[1][1] + r[2][2];
    let cos_theta = ((trace - 1.0) / 2.0).clamp(-1.0, 1.0);
    let theta = cos_theta.acos();

    if theta < 1e-10 {
        // Near identity.
        return [
            (r[2][1] - r[1][2]) / 2.0,
            (r[0][2] - r[2][0]) / 2.0,
            (r[1][0] - r[0][1]) / 2.0,
        ];
    }

    let sin_theta = theta.sin();
    if sin_theta.abs() < 1e-10 {
        // theta near pi.
        // Use the column of (R + I) with largest norm.
        let mut best_col = 0;
        let mut best_norm = 0.0;
        for col in 0..3 {
            let mut norm_sq = 0.0;
            for row in 0..3 {
                let val = r[row][col] + if row == col { 1.0 } else { 0.0 };
                norm_sq += val * val;
            }
            if norm_sq > best_norm {
                best_norm = norm_sq;
                best_col = col;
            }
        }
        let norm = best_norm.sqrt();
        let mut axis = [0.0; 3];
        for row in 0..3 {
            axis[row] = (r[row][best_col]
                + if row == best_col { 1.0 } else { 0.0 })
                / norm;
        }
        return [axis[0] * theta, axis[1] * theta, axis[2] * theta];
    }

    let factor = theta / (2.0 * sin_theta);
    [
        (r[2][1] - r[1][2]) * factor,
        (r[0][2] - r[2][0]) * factor,
        (r[1][0] - r[0][1]) * factor,
    ]
}

// ====================================================================
// Tests
// ====================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sparse::schur_complement::SchurComplementWorkspace;
    use crate::sparse::{
        SparseLevenbergMarquardtConfig, SparseLevenbergMarquardtSolver,
        SparseLevenbergMarquardtWorkspace,
    };

    #[test]
    fn test_synthetic_ba_ground_truth_zero_residuals() {
        // At ground-truth parameters, residuals should be ~zero.
        let (problem, gt_params) =
            SyntheticBAProblem::new_circle(3, 10, 5.0, 42);

        let num_residuals = problem.residual_count();
        let mut residuals = vec![0.0; num_residuals];
        let _ = problem
            .compute_sparse_jacobian(&gt_params, &mut residuals)
            .unwrap();

        let cost: f64 = residuals.iter().map(|r| r * r).sum::<f64>() * 0.5;
        assert!(
            cost < 1e-10,
            "Ground-truth cost should be ~0, got {:.3e}",
            cost
        );
    }

    #[test]
    fn test_schur_solver_converges_ba() {
        // Create problem, add noise, solve with Schur complement.
        let (problem, gt_params) =
            SyntheticBAProblem::new_circle(3, 20, 5.0, 123);

        assert!(
            problem.residual_count() >= problem.parameter_count(),
            "Need residuals({}) >= params({}), obs={}",
            problem.residual_count(),
            problem.parameter_count(),
            problem.observations.len()
        );

        let mut noisy_params = gt_params.clone();
        SyntheticBAProblem::add_noise(
            &mut noisy_params,
            problem.num_cameras,
            0.005, // very small rotation noise
            0.02,  // small translation noise
            0.02,  // small point noise
            456,
        );

        let config = SparseLevenbergMarquardtConfig {
            max_iterations: 100,
            ..Default::default()
        };
        let solver = SparseLevenbergMarquardtSolver::new(config);

        let mut workspace =
            SparseLevenbergMarquardtWorkspace::new(&problem, &noisy_params)
                .unwrap();

        let mut schur_ws = SchurComplementWorkspace::new(
            problem.num_cameras,
            problem.num_points,
            CAM_BLOCK_SIZE,
            PT_BLOCK_SIZE,
            &problem.observations,
            &problem.camera_unlocked,
            &problem.point_unlocked,
        );

        let result = solver
            .solve_problem_schur(&problem, &mut workspace, &mut schur_ws)
            .unwrap();

        println!(
            "Schur BA: status={:?}, cost={:.3e}, iters={}",
            result.status, result.cost, result.iterations
        );

        // Also test the full solve for comparison.
        let mut ws_full =
            SparseLevenbergMarquardtWorkspace::new(&problem, &noisy_params)
                .unwrap();
        let result_full = solver.solve_problem(&problem, &mut ws_full).unwrap();
        println!(
            "Full BA:  status={:?}, cost={:.3e}, iters={}",
            result_full.status, result_full.cost, result_full.iterations
        );

        assert!(
            result.cost < 1e-4,
            "Schur solver should converge, cost={:.3e} (full={:.3e})",
            result.cost,
            result_full.cost
        );
    }

    #[test]
    fn test_schur_vs_full_solve_same_result() {
        // Both solve paths should produce similar results.
        let (problem, gt_params) =
            SyntheticBAProblem::new_circle(3, 20, 5.0, 789);

        let mut noisy_params = gt_params.clone();
        SyntheticBAProblem::add_noise(
            &mut noisy_params,
            problem.num_cameras,
            0.01,
            0.05,
            0.05,
            101,
        );

        let config = SparseLevenbergMarquardtConfig {
            max_iterations: 50,
            ..Default::default()
        };

        // Full solve path.
        let solver = SparseLevenbergMarquardtSolver::new(config);
        let mut ws_full =
            SparseLevenbergMarquardtWorkspace::new(&problem, &noisy_params)
                .unwrap();
        let result_full = solver.solve_problem(&problem, &mut ws_full).unwrap();

        // Schur solve path.
        let mut ws_schur =
            SparseLevenbergMarquardtWorkspace::new(&problem, &noisy_params)
                .unwrap();
        let mut schur_ws = SchurComplementWorkspace::new(
            problem.num_cameras,
            problem.num_points,
            CAM_BLOCK_SIZE,
            PT_BLOCK_SIZE,
            &problem.observations,
            &problem.camera_unlocked,
            &problem.point_unlocked,
        );
        let result_schur = solver
            .solve_problem_schur(&problem, &mut ws_schur, &mut schur_ws)
            .unwrap();

        println!(
            "Full:  cost={:.3e}, iters={}",
            result_full.cost, result_full.iterations
        );
        println!(
            "Schur: cost={:.3e}, iters={}",
            result_schur.cost, result_schur.iterations
        );

        // Both should converge to low cost.
        assert!(
            result_full.cost < 1e-4,
            "Full solve cost={:.3e}",
            result_full.cost
        );
        assert!(
            result_schur.cost < 1e-4,
            "Schur solve cost={:.3e}",
            result_schur.cost
        );

        // Final costs should be similar (within an order of
        // magnitude, since convergence paths may differ slightly).
        let ratio = result_schur.cost / result_full.cost.max(1e-20);
        assert!(
            ratio < 100.0 && ratio > 0.01,
            "Cost ratio too different: full={:.3e}, schur={:.3e}",
            result_full.cost,
            result_schur.cost
        );
    }

    #[test]
    fn test_ba_locked_camera() {
        // Lock camera 0, solve only cameras 1,2 + all points.
        let (mut problem, gt_params) =
            SyntheticBAProblem::new_circle(3, 20, 5.0, 333);
        problem.camera_unlocked = vec![false, true, true];

        let mut noisy_params = gt_params.clone();
        SyntheticBAProblem::add_noise(
            &mut noisy_params,
            problem.num_cameras,
            0.01,
            0.05,
            0.05,
            444,
        );
        // Restore camera 0 to ground truth (it's locked).
        for i in 0..CAM_BLOCK_SIZE {
            noisy_params[i] = gt_params[i];
        }

        let config = SparseLevenbergMarquardtConfig {
            max_iterations: 100,
            ..Default::default()
        };
        let solver = SparseLevenbergMarquardtSolver::new(config);

        let mut workspace =
            SparseLevenbergMarquardtWorkspace::new(&problem, &noisy_params)
                .unwrap();
        let mut schur_ws = SchurComplementWorkspace::new(
            problem.num_cameras,
            problem.num_points,
            CAM_BLOCK_SIZE,
            PT_BLOCK_SIZE,
            &problem.observations,
            &problem.camera_unlocked,
            &problem.point_unlocked,
        );

        let result = solver
            .solve_problem_schur(&problem, &mut workspace, &mut schur_ws)
            .unwrap();

        println!(
            "Locked cam BA: cost={:.3e}, iters={}",
            result.cost, result.iterations
        );
        assert!(
            result.cost < 1e-4,
            "Should converge with locked camera, cost={:.3e}",
            result.cost
        );

        // Camera 0 parameters should be unchanged.
        for i in 0..CAM_BLOCK_SIZE {
            assert!(
                (result.parameters[i] - gt_params[i]).abs() < 1e-10,
                "Locked camera param {} changed: {:.10} vs {:.10}",
                i,
                result.parameters[i],
                gt_params[i]
            );
        }
    }
}
