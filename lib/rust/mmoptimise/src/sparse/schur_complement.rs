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

//! Schur complement elimination for sparse bundle adjustment.
//!
//! This module implements the Schur complement trick for
//! Levenberg-Marquardt bundle adjustment. By exploiting the
//! block-diagonal structure of both H_pp and H_cc, it reduces the
//! normal equations to the smaller of the two variable sets.
//!
//! # Algorithm
//!
//! Given the partitioned normal equations:
//!
//! ```text
//! [H_cc  H_cp] [delta_c]   [g_c]
//! [H_pc  H_pp] [delta_p] = [g_p]
//! ```
//!
//! **Standard direction** (eliminate points, when N_p > N_c):
//!
//! 1. S = H_cc - H_cp * H_pp^{-1} * H_pc  (reduced camera system)
//! 2. r = -g_c + H_cp * H_pp^{-1} * g_p   (reduced RHS)
//! 3. Solve: S * delta_c = r
//! 4. Back-substitute: delta_p = H_pp^{-1} * (-g_p - H_pc * delta_c)
//!
//! **Reverse direction** (eliminate cameras, when N_c > N_p):
//!
//! 1. S = H_pp - H_pc * H_cc^{-1} * H_cp  (reduced point system)
//! 2. r = -g_p + H_pc * H_cc^{-1} * g_c   (reduced RHS)
//! 3. Solve: S * delta_p = r
//! 4. Back-substitute: delta_c = H_cc^{-1} * (-g_c - H_cp * delta_p)

use anyhow::Result;
use mmcholmod::solver::CholmodSolver;
use rayon::prelude::*;

use crate::sparse::SparseOptimisationProblem;

const DEBUG: bool = false;

/// Trait for bundle adjustment problems that provide block-structured
/// Jacobians suitable for Schur complement elimination.
///
/// Problems implementing this trait can be solved with the Schur
/// complement path, which is much faster than the full normal
/// equations when the number of 3D points greatly exceeds the number
/// of cameras.
///
/// Each observation connects exactly one camera to one 3D point,
/// producing 2 residuals (u, v reprojection error) with a
/// `2 x cam_block_size` camera Jacobian block and a
/// `2 x pt_block_size` point Jacobian block.
pub trait SchurStructuredProblem: SparseOptimisationProblem {
    /// Number of cameras in the problem (including locked ones).
    fn num_cameras(&self) -> usize;

    /// Number of 3D points in the problem (including locked ones).
    fn num_points(&self) -> usize;

    /// Number of parameters per camera (typically 6 for
    /// rotation+translation, up to 12 with intrinsics).
    fn camera_block_size(&self) -> usize;

    /// Number of parameters per 3D point (typically 3 for XYZ).
    fn point_block_size(&self) -> usize;

    /// For observation `obs_idx`, returns `(camera_idx, point_idx)`.
    fn observation_structure(&self, obs_idx: usize) -> (usize, usize);

    /// Total number of observations (each produces 2 residuals).
    fn num_observations(&self) -> usize;

    /// Whether the camera at `idx` is unlocked (its parameters are
    /// optimized).
    fn is_camera_unlocked(&self, idx: usize) -> bool;

    /// Whether the 3D point at `idx` is unlocked (its parameters are
    /// optimized).
    fn is_point_unlocked(&self, idx: usize) -> bool;

    /// Compute residuals and per-observation Jacobian blocks.
    ///
    /// # Arguments
    ///
    /// * `parameters` - Current parameter vector (length =
    ///   `parameter_count()`).
    /// * `out_residuals` - Output residuals (length =
    ///   `residual_count()`).
    /// * `out_camera_blocks` - Flat buffer for camera Jacobian
    ///   blocks. Each observation contributes `2 * cam_block_size`
    ///   values stored row-major. Total length = `num_observations()
    ///   * 2 * camera_block_size()`.
    /// * `out_point_blocks` - Flat buffer for point Jacobian blocks.
    ///   Each observation contributes `2 * pt_block_size` values
    ///   stored row-major. Total length = `num_observations() * 2 *
    ///   point_block_size()`.
    fn compute_jacobian_blocks(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
        out_camera_blocks: &mut [f64],
        out_point_blocks: &mut [f64],
    ) -> Result<()>;
}

/// Pre-allocated workspace for Schur complement elimination.
///
/// All buffers are allocated once and reused across LM iterations.
/// The workspace stores the block Hessian sub-matrices, Jacobian
/// blocks, the dense Schur complement matrix, and intermediate
/// results for back-substitution.
pub struct SchurComplementWorkspace {
    // Problem dimensions (immutable after creation).
    pub num_cameras: usize,
    pub num_points: usize,
    pub cam_block_size: usize,
    pub pt_block_size: usize,
    pub num_observations: usize,

    /// Total camera parameters (unlocked cameras only).
    pub total_cam_params: usize,
    /// Total point parameters (unlocked points only).
    pub total_pt_params: usize,

    // --- Block Hessian storage ---
    /// H_pp block diagonal: one `pt_size x pt_size` block per
    /// unlocked point. Flat row-major, length = num_unlocked_points *
    /// pt_size * pt_size.
    pub hpp_blocks: Vec<f64>,

    /// Cached (H_pp)^{-1} blocks. Same layout as `hpp_blocks`.
    pub hpp_inv_blocks: Vec<f64>,

    /// Dense Schur complement / H_cc matrix. Row-major,
    /// `total_cam_params x total_cam_params`.
    pub schur_matrix: Vec<f64>,

    /// H_cp blocks indexed by observation. Each observation
    /// contributes one `cam_size x pt_size` block. Flat row-major,
    /// length = num_observations * cam_size * pt_size.
    pub hcp_blocks: Vec<f64>,

    // --- Gradient vectors ---
    /// Camera gradient g_c. Length = total_cam_params.
    pub gradient_cameras: Vec<f64>,

    /// Point gradient g_p. Length = total_pt_params.
    pub gradient_points: Vec<f64>,

    // --- Solve results ---
    /// Reduced RHS for camera solve. Length = total_cam_params.
    pub rhs_reduced: Vec<f64>,

    /// Camera parameter step. Length = total_cam_params.
    pub delta_cameras: Vec<f64>,

    /// Point parameter step. Length = total_pt_params.
    pub delta_points: Vec<f64>,

    // --- Jacobian block storage ---
    /// Per-observation camera Jacobian blocks. Flat row-major,
    /// length = num_observations * 2 * cam_block_size.
    pub camera_jac_blocks: Vec<f64>,

    /// Per-observation point Jacobian blocks. Flat row-major,
    /// length = num_observations * 2 * pt_block_size.
    pub point_jac_blocks: Vec<f64>,

    // --- Reverse direction (eliminate cameras) storage ---
    /// H_cc block diagonal: one `cam_size x cam_size` block per
    /// unlocked camera. Flat row-major. Used only when eliminating
    /// cameras (reverse direction).
    pub hcc_blocks: Vec<f64>,

    /// Cached (H_cc)^{-1} blocks. Same layout as `hcc_blocks`.
    pub hcc_inv_blocks: Vec<f64>,

    /// Dense Schur complement for reverse direction. Row-major,
    /// `total_pt_params x total_pt_params`. Used when eliminating
    /// cameras.
    pub schur_matrix_reverse: Vec<f64>,

    /// Reduced RHS for reverse direction. Length = total_pt_params.
    pub rhs_reduced_reverse: Vec<f64>,

    // --- Adjacency structure ---
    /// For each point index, the list of observation indices that
    /// see it. Used for Schur complement formation and
    /// back-substitution.
    pub point_to_observations: Vec<Vec<usize>>,

    /// For each camera index, the list of observation indices
    /// involving it. Used for reverse Schur complement.
    pub camera_to_observations: Vec<Vec<usize>>,

    /// Maps camera index -> starting offset in the camera parameter
    /// sub-vector. Locked cameras map to usize::MAX.
    pub camera_param_offset: Vec<usize>,

    /// Maps point index -> starting offset in the point parameter
    /// sub-vector. Locked points map to usize::MAX.
    pub point_param_offset: Vec<usize>,

    /// Observation camera indices (redundant with problem, cached
    /// for fast iteration).
    pub obs_camera_idx: Vec<usize>,

    /// Observation point indices.
    pub obs_point_idx: Vec<usize>,

    // --- Temp buffers ---
    /// Temporary buffer for E_inv * H_cp^T products.
    /// Length = max_observations_per_point * pt_size * cam_size.
    pub temp_einv_hcp: Vec<f64>,

    // --- CHOLMOD for reduced system ---
    pub cholmod_solver: CholmodSolver,
    pub cholmod_initialized: bool,
}

impl SchurComplementWorkspace {
    /// Create a new workspace for the given problem dimensions.
    ///
    /// # Arguments
    ///
    /// * `num_cameras` - Total cameras (including locked).
    /// * `num_points` - Total 3D points (including locked).
    /// * `cam_block_size` - Parameters per camera.
    /// * `pt_block_size` - Parameters per point.
    /// * `observations` - Slice of `(camera_idx, point_idx)` pairs.
    /// * `camera_unlocked` - Per-camera unlock status.
    /// * `point_unlocked` - Per-point unlock status.
    pub fn new(
        num_cameras: usize,
        num_points: usize,
        cam_block_size: usize,
        pt_block_size: usize,
        observations: &[(usize, usize)],
        camera_unlocked: &[bool],
        point_unlocked: &[bool],
    ) -> Self {
        assert_eq!(camera_unlocked.len(), num_cameras);
        assert_eq!(point_unlocked.len(), num_points);

        let num_observations = observations.len();

        // Build camera/point parameter offsets (only unlocked
        // entities get offsets).
        let mut camera_param_offset = vec![usize::MAX; num_cameras];
        let mut total_cam_params = 0usize;
        for i in 0..num_cameras {
            if camera_unlocked[i] {
                camera_param_offset[i] = total_cam_params;
                total_cam_params += cam_block_size;
            }
        }

        let mut point_param_offset = vec![usize::MAX; num_points];
        let mut total_pt_params = 0usize;
        for i in 0..num_points {
            if point_unlocked[i] {
                point_param_offset[i] = total_pt_params;
                total_pt_params += pt_block_size;
            }
        }

        // Build point-to-observations and camera-to-observations adjacency.
        let mut point_to_observations = vec![Vec::new(); num_points];
        let mut camera_to_observations = vec![Vec::new(); num_cameras];
        let mut obs_camera_idx = Vec::with_capacity(num_observations);
        let mut obs_point_idx = Vec::with_capacity(num_observations);
        for (obs_idx, &(cam_idx, pt_idx)) in observations.iter().enumerate() {
            point_to_observations[pt_idx].push(obs_idx);
            camera_to_observations[cam_idx].push(obs_idx);
            obs_camera_idx.push(cam_idx);
            obs_point_idx.push(pt_idx);
        }

        // Find max observations per point (for temp buffer sizing).
        let max_obs_per_point = point_to_observations
            .iter()
            .map(|v| v.len())
            .max()
            .unwrap_or(0);

        let num_unlocked_cameras =
            camera_unlocked.iter().filter(|&&u| u).count();
        let _ = num_unlocked_cameras;

        SchurComplementWorkspace {
            num_cameras,
            num_points,
            cam_block_size,
            pt_block_size,
            num_observations,
            total_cam_params,
            total_pt_params,

            hpp_blocks: vec![
                0.0;
                (total_pt_params / pt_block_size)
                    * pt_block_size
                    * pt_block_size
            ],
            hpp_inv_blocks: vec![
                0.0;
                (total_pt_params / pt_block_size)
                    * pt_block_size
                    * pt_block_size
            ],
            schur_matrix: vec![0.0; total_cam_params * total_cam_params],
            hcp_blocks: vec![
                0.0;
                num_observations * cam_block_size * pt_block_size
            ],

            gradient_cameras: vec![0.0; total_cam_params],
            gradient_points: vec![0.0; total_pt_params],

            rhs_reduced: vec![0.0; total_cam_params],
            delta_cameras: vec![0.0; total_cam_params],
            delta_points: vec![0.0; total_pt_params],

            camera_jac_blocks: vec![0.0; num_observations * 2 * cam_block_size],
            point_jac_blocks: vec![0.0; num_observations * 2 * pt_block_size],

            hcc_blocks: vec![
                0.0;
                (total_cam_params / cam_block_size.max(1))
                    * cam_block_size
                    * cam_block_size
            ],
            hcc_inv_blocks: vec![
                0.0;
                (total_cam_params / cam_block_size.max(1))
                    * cam_block_size
                    * cam_block_size
            ],
            schur_matrix_reverse: vec![0.0; total_pt_params * total_pt_params],
            rhs_reduced_reverse: vec![0.0; total_pt_params],

            point_to_observations,
            camera_to_observations,
            camera_param_offset,
            point_param_offset,
            obs_camera_idx,
            obs_point_idx,

            temp_einv_hcp: vec![
                0.0;
                max_obs_per_point
                    * pt_block_size
                    * cam_block_size
            ],

            cholmod_solver: CholmodSolver::new()
                .expect("Failed to create CHOLMOD solver"),
            cholmod_initialized: false,
        }
    }

    /// Zero all numeric buffers without deallocating.
    pub fn clear(&mut self) {
        self.hpp_blocks.fill(0.0);
        self.hpp_inv_blocks.fill(0.0);
        self.schur_matrix.fill(0.0);
        self.hcp_blocks.fill(0.0);
        self.gradient_cameras.fill(0.0);
        self.gradient_points.fill(0.0);
        self.rhs_reduced.fill(0.0);
        self.delta_cameras.fill(0.0);
        self.delta_points.fill(0.0);
        self.camera_jac_blocks.fill(0.0);
        self.point_jac_blocks.fill(0.0);
        self.temp_einv_hcp.fill(0.0);
        self.hcc_blocks.fill(0.0);
        self.hcc_inv_blocks.fill(0.0);
        self.schur_matrix_reverse.fill(0.0);
        self.rhs_reduced_reverse.fill(0.0);
    }

    /// Returns true when eliminating cameras (reverse direction)
    /// would produce a smaller reduced system than eliminating points.
    pub fn should_eliminate_cameras(&self) -> bool {
        self.total_cam_params > self.total_pt_params
    }

    /// Number of unlocked cameras.
    pub fn num_unlocked_cameras(&self) -> usize {
        if self.cam_block_size == 0 {
            return 0;
        }
        self.total_cam_params / self.cam_block_size
    }

    /// Number of unlocked points.
    pub fn num_unlocked_points(&self) -> usize {
        if self.pt_block_size == 0 {
            return 0;
        }
        self.total_pt_params / self.pt_block_size
    }

    /// Get the H_pp block for unlocked point at `unlocked_pt_idx`
    /// (0-based among unlocked points).
    pub fn hpp_block(&self, unlocked_pt_idx: usize) -> &[f64] {
        let sz = self.pt_block_size * self.pt_block_size;
        let start = unlocked_pt_idx * sz;
        &self.hpp_blocks[start..start + sz]
    }

    /// Get mutable H_pp block for unlocked point.
    pub fn hpp_block_mut(&mut self, unlocked_pt_idx: usize) -> &mut [f64] {
        let sz = self.pt_block_size * self.pt_block_size;
        let start = unlocked_pt_idx * sz;
        &mut self.hpp_blocks[start..start + sz]
    }

    /// Get the H_pp inverse block for unlocked point.
    pub fn hpp_inv_block(&self, unlocked_pt_idx: usize) -> &[f64] {
        let sz = self.pt_block_size * self.pt_block_size;
        let start = unlocked_pt_idx * sz;
        &self.hpp_inv_blocks[start..start + sz]
    }

    /// Get the H_cp block for observation `obs_idx`.
    pub fn hcp_block(&self, obs_idx: usize) -> &[f64] {
        let sz = self.cam_block_size * self.pt_block_size;
        let start = obs_idx * sz;
        &self.hcp_blocks[start..start + sz]
    }

    /// Get mutable H_cp block for observation `obs_idx`.
    pub fn hcp_block_mut(&mut self, obs_idx: usize) -> &mut [f64] {
        let sz = self.cam_block_size * self.pt_block_size;
        let start = obs_idx * sz;
        &mut self.hcp_blocks[start..start + sz]
    }

    /// Get the camera Jacobian block for observation `obs_idx`.
    /// Returns a `2 x cam_block_size` slice (row-major).
    pub fn camera_jac_block(&self, obs_idx: usize) -> &[f64] {
        let sz = 2 * self.cam_block_size;
        let start = obs_idx * sz;
        &self.camera_jac_blocks[start..start + sz]
    }

    /// Get the point Jacobian block for observation `obs_idx`.
    /// Returns a `2 x pt_block_size` slice (row-major).
    pub fn point_jac_block(&self, obs_idx: usize) -> &[f64] {
        let sz = 2 * self.pt_block_size;
        let start = obs_idx * sz;
        &self.point_jac_blocks[start..start + sz]
    }

    /// Get the H_cc block for unlocked camera at `unlocked_cam_idx`.
    pub fn hcc_block(&self, unlocked_cam_idx: usize) -> &[f64] {
        let sz = self.cam_block_size * self.cam_block_size;
        let start = unlocked_cam_idx * sz;
        &self.hcc_blocks[start..start + sz]
    }

    /// Get the H_cc inverse block for unlocked camera.
    pub fn hcc_inv_block(&self, unlocked_cam_idx: usize) -> &[f64] {
        let sz = self.cam_block_size * self.cam_block_size;
        let start = unlocked_cam_idx * sz;
        &self.hcc_inv_blocks[start..start + sz]
    }
}

// ====================================================================
// Phase 2: Block Hessian Assembly
// ====================================================================

/// Assemble the block Hessian sub-matrices from per-observation
/// Jacobian blocks.
///
/// Computes H_cc, H_cp, H_pp and gradients g_c, g_p with
/// Levenberg-Marquardt damping applied to the diagonals.
///
/// # Arguments
///
/// * `ws` - Schur complement workspace (must have Jacobian blocks
///   already filled).
/// * `residuals` - Residual vector (length = 2 * num_observations).
/// * `scaling` - Parameter scaling vector (length = total params).
///   Camera params first, then point params.
/// * `lambda` - LM damping factor.
/// * `lambda_regularization` - Additional diagonal regularization.
pub fn assemble_block_hessian(
    ws: &mut SchurComplementWorkspace,
    residuals: &[f64],
    scaling_cameras: &[f64],
    scaling_points: &[f64],
    lambda: f64,
    lambda_regularization: f64,
) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    // Zero the accumulation buffers.
    ws.schur_matrix.fill(0.0);
    ws.hpp_blocks.fill(0.0);
    ws.hcc_blocks.fill(0.0);
    ws.hcp_blocks.fill(0.0);
    ws.gradient_cameras.fill(0.0);
    ws.gradient_points.fill(0.0);

    // Accumulate per-observation contributions.
    // We copy Jacobian blocks to local buffers to avoid borrow
    // checker conflicts (immutable borrow via accessor + mutable
    // borrow for accumulation).
    let mut jc_buf = vec![0.0; 2 * cs];
    let mut jp_buf = vec![0.0; 2 * ps];

    for obs in 0..ws.num_observations {
        let cam_idx = ws.obs_camera_idx[obs];
        let pt_idx = ws.obs_point_idx[obs];

        let cam_offset = ws.camera_param_offset[cam_idx];
        let pt_offset = ws.point_param_offset[pt_idx];

        // Skip observations involving locked entities.
        let cam_unlocked = cam_offset != usize::MAX;
        let pt_unlocked = pt_offset != usize::MAX;
        if !cam_unlocked && !pt_unlocked {
            continue;
        }

        // Residual for this observation (2 values: u, v).
        let r0 = residuals[2 * obs];
        let r1 = residuals[2 * obs + 1];

        // Copy Jacobian blocks to local buffers.
        let jc_start = obs * 2 * cs;
        jc_buf.copy_from_slice(
            &ws.camera_jac_blocks[jc_start..jc_start + 2 * cs],
        );
        let jp_start = obs * 2 * ps;
        jp_buf
            .copy_from_slice(&ws.point_jac_blocks[jp_start..jp_start + 2 * ps]);

        // H_cc[c,c] += J_c^T * J_c  (cs x cs block on diagonal)
        if cam_unlocked {
            let hcc_row_start = cam_offset;
            let n = ws.total_cam_params;
            let cam_block_idx = cam_offset / cs;
            let hcc_diag_start = cam_block_idx * cs * cs;
            for i in 0..cs {
                for j in 0..cs {
                    let val =
                        jc_buf[i] * jc_buf[j] + jc_buf[cs + i] * jc_buf[cs + j];
                    ws.schur_matrix
                        [(hcc_row_start + i) * n + hcc_row_start + j] += val;
                    // Also accumulate block-diagonal H_cc for reverse
                    // Schur direction.
                    ws.hcc_blocks[hcc_diag_start + i * cs + j] += val;
                }
            }

            // g_c[c] += J_c^T * r
            for i in 0..cs {
                ws.gradient_cameras[cam_offset + i] +=
                    jc_buf[i] * r0 + jc_buf[cs + i] * r1;
            }
        }

        // H_pp[p] += J_p^T * J_p  (ps x ps block-diagonal)
        if pt_unlocked {
            let pt_block_idx = pt_offset / ps;
            let hpp_start = pt_block_idx * ps * ps;
            for i in 0..ps {
                for j in 0..ps {
                    let val =
                        jp_buf[i] * jp_buf[j] + jp_buf[ps + i] * jp_buf[ps + j];
                    ws.hpp_blocks[hpp_start + i * ps + j] += val;
                }
            }

            // g_p[p] += J_p^T * r
            for i in 0..ps {
                ws.gradient_points[pt_offset + i] +=
                    jp_buf[i] * r0 + jp_buf[ps + i] * r1;
            }
        }

        // H_cp[obs] = J_c^T * J_p  (cs x ps block)
        if cam_unlocked && pt_unlocked {
            let hcp_start = obs * cs * ps;
            for i in 0..cs {
                for j in 0..ps {
                    let val =
                        jc_buf[i] * jp_buf[j] + jc_buf[cs + i] * jp_buf[ps + j];
                    ws.hcp_blocks[hcp_start + i * ps + j] = val;
                }
            }
        }
    }

    // Add damping to H_cc diagonals.
    {
        let n = ws.total_cam_params;
        for i in 0..n {
            let s = if i < scaling_cameras.len() {
                scaling_cameras[i]
            } else {
                1.0
            };
            let damping = lambda * s * s + lambda_regularization;
            ws.schur_matrix[i * n + i] += damping;
            // Also damp the block-diagonal H_cc.
            let cam_block_idx = i / cs;
            let local_i = i % cs;
            ws.hcc_blocks[cam_block_idx * cs * cs + local_i * cs + local_i] +=
                damping;
        }
    }

    // Add damping to H_pp diagonals.
    {
        let num_unlocked_pts = ws.num_unlocked_points();
        for pt in 0..num_unlocked_pts {
            let hpp_start = pt * ps * ps;
            for i in 0..ps {
                let param_idx = pt * ps + i;
                let s = if param_idx < scaling_points.len() {
                    scaling_points[param_idx]
                } else {
                    1.0
                };
                ws.hpp_blocks[hpp_start + i * ps + i] +=
                    lambda * s * s + lambda_regularization;
            }
        }
    }
}

// ====================================================================
// Phase 3: Schur Complement Formation, Solve, Back-Substitution
// ====================================================================

/// Invert all H_pp blocks (block-diagonal). For pt_block_size == 3,
/// uses the analytic 3x3 inverse. Otherwise falls back to LU.
///
/// Uses rayon to parallelize across points when there are enough
/// blocks to benefit. Near-singular blocks are regularized before
/// inversion.
pub fn invert_hpp_blocks(ws: &mut SchurComplementWorkspace) -> Result<()> {
    let ps = ws.pt_block_size;
    let num_pts = ws.num_unlocked_points();
    let block_sz = ps * ps;
    let epsilon = 1e-12;

    // Parallel inversion using rayon. We borrow hpp_blocks
    // immutably and hpp_inv_blocks mutably via index-based chunks.
    let hpp_blocks = &ws.hpp_blocks;
    ws.hpp_inv_blocks
        .par_chunks_mut(block_sz)
        .take(num_pts)
        .enumerate()
        .for_each(|(pt, dst)| {
            let start = pt * block_sz;
            let src = &hpp_blocks[start..start + block_sz];
            if ps == 3 {
                invert_3x3_block(src, dst, epsilon);
            } else {
                invert_general_block(src, dst, ps, epsilon);
            }
        });

    Ok(())
}

/// Invert a 3x3 block using the analytic cofactor formula.
fn invert_3x3_block(src: &[f64], dst: &mut [f64], epsilon: f64) {
    let a = src[0];
    let b = src[1];
    let c = src[2];
    let d = src[3];
    let e = src[4];
    let f = src[5];
    let g = src[6];
    let h = src[7];
    let k = src[8];

    let det = a * (e * k - f * h) - b * (d * k - f * g) + c * (d * h - e * g);

    let inv_det = if det.abs() < epsilon {
        let trace = a + e + k;
        1.0 / trace.abs().max(epsilon)
    } else {
        1.0 / det
    };

    dst[0] = (e * k - f * h) * inv_det;
    dst[1] = (c * h - b * k) * inv_det;
    dst[2] = (b * f - c * e) * inv_det;
    dst[3] = (f * g - d * k) * inv_det;
    dst[4] = (a * k - c * g) * inv_det;
    dst[5] = (c * d - a * f) * inv_det;
    dst[6] = (d * h - e * g) * inv_det;
    dst[7] = (b * g - a * h) * inv_det;
    dst[8] = (a * e - b * d) * inv_det;
}

/// Invert a general NxN block using nalgebra LU.
fn invert_general_block(src: &[f64], dst: &mut [f64], ps: usize, epsilon: f64) {
    let mat = nalgebra::DMatrix::from_row_slice(ps, ps, src);
    let inv = match mat.clone().try_inverse() {
        Some(inv) => inv,
        None => {
            let mut reg_mat = mat;
            for i in 0..ps {
                reg_mat[(i, i)] += epsilon;
            }
            reg_mat
                .try_inverse()
                .unwrap_or_else(|| nalgebra::DMatrix::identity(ps, ps))
        }
    };
    for i in 0..ps {
        for j in 0..ps {
            dst[i * ps + j] = inv[(i, j)];
        }
    }
}

/// Form the Schur complement matrix:
///   S = H_cc - H_cp * H_pp^{-1} * H_pc
///
/// Requires `invert_hpp_blocks()` to have been called first.
pub fn form_schur_complement(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;
    let n = ws.total_cam_params;

    // S starts as H_cc (already accumulated in schur_matrix).
    // Now subtract H_cp * H_pp^{-1} * H_pc for each point.

    for pt_idx in 0..ws.num_points {
        let pt_offset = ws.point_param_offset[pt_idx];
        if pt_offset == usize::MAX {
            continue; // locked point
        }
        let unlocked_pt = pt_offset / ps;

        let obs_list = &ws.point_to_observations[pt_idx];
        if obs_list.is_empty() {
            continue;
        }

        // Get E_inv = H_pp^{-1}[pt] (ps x ps, row-major).
        let einv_start = unlocked_pt * ps * ps;

        // For each pair of observations (k_i, k_j) seeing this
        // point, compute:
        //   S[c_i, c_j] -= H_cp[k_i] * E_inv * H_cp[k_j]^T
        for &obs_i in obs_list.iter() {
            let cam_i = ws.obs_camera_idx[obs_i];
            let cam_i_offset = ws.camera_param_offset[cam_i];
            if cam_i_offset == usize::MAX {
                continue; // locked camera
            }

            // Compute temp = H_cp[obs_i] * E_inv  (cs x ps)
            let hcp_i_start = obs_i * cs * ps;
            // temp is cs x ps, stored in a small stack buffer.
            let mut temp = vec![0.0; cs * ps];
            for r in 0..cs {
                for c in 0..ps {
                    let mut sum = 0.0;
                    for k in 0..ps {
                        sum += ws.hcp_blocks[hcp_i_start + r * ps + k]
                            * ws.hpp_inv_blocks[einv_start + k * ps + c];
                    }
                    temp[r * ps + c] = sum;
                }
            }

            for &obs_j in obs_list.iter() {
                let cam_j = ws.obs_camera_idx[obs_j];
                let cam_j_offset = ws.camera_param_offset[cam_j];
                if cam_j_offset == usize::MAX {
                    continue; // locked camera
                }

                // Only compute upper triangle + diagonal for
                // symmetry, then mirror.
                if cam_j_offset < cam_i_offset {
                    continue;
                }

                // S[c_i, c_j] -= temp * H_cp[obs_j]^T
                // temp is cs x ps, H_cp[obs_j] is cs x ps
                // result is cs x cs
                let hcp_j_start = obs_j * cs * ps;
                for r in 0..cs {
                    for c in 0..cs {
                        let mut sum = 0.0;
                        for k in 0..ps {
                            sum += temp[r * ps + k]
                                * ws.hcp_blocks[hcp_j_start + c * ps + k];
                        }
                        ws.schur_matrix
                            [(cam_i_offset + r) * n + cam_j_offset + c] -= sum;
                        // Mirror for lower triangle.
                        if cam_i_offset != cam_j_offset {
                            ws.schur_matrix
                                [(cam_j_offset + c) * n + cam_i_offset + r] -=
                                sum;
                        }
                    }
                }
            }
        }
    }
}

/// Form the reduced RHS for the normal equations:
///   rhs = -g_c + H_cp * H_pp^{-1} * g_p
///
/// This follows from the normal equations `H * delta = -g` after
/// Schur complement elimination of the point variables.
///
/// Requires `invert_hpp_blocks()` to have been called first.
pub fn form_reduced_rhs(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    // Start with -g_c.
    for i in 0..ws.total_cam_params {
        ws.rhs_reduced[i] = -ws.gradient_cameras[i];
    }

    // Add H_cp * H_pp^{-1} * g_p for each point.
    for pt_idx in 0..ws.num_points {
        let pt_offset = ws.point_param_offset[pt_idx];
        if pt_offset == usize::MAX {
            continue;
        }
        let unlocked_pt = pt_offset / ps;
        let einv_start = unlocked_pt * ps * ps;

        // temp = E_inv * g_p[pt] (ps x 1)
        let mut temp = [0.0; 16]; // enough for pt_size <= 16
        for i in 0..ps {
            let mut sum = 0.0;
            for k in 0..ps {
                sum += ws.hpp_inv_blocks[einv_start + i * ps + k]
                    * ws.gradient_points[pt_offset + k];
            }
            temp[i] = sum;
        }

        // For each observation seeing this point:
        let obs_list = &ws.point_to_observations[pt_idx];
        for &obs in obs_list.iter() {
            let cam_idx = ws.obs_camera_idx[obs];
            let cam_offset = ws.camera_param_offset[cam_idx];
            if cam_offset == usize::MAX {
                continue;
            }

            // rhs[c] += H_cp[obs] * temp
            let hcp_start = obs * cs * ps;
            for i in 0..cs {
                let mut sum = 0.0;
                for k in 0..ps {
                    sum += ws.hcp_blocks[hcp_start + i * ps + k] * temp[k];
                }
                ws.rhs_reduced[cam_offset + i] += sum;
            }
        }
    }
}

/// Solve the reduced camera system: S * delta_c = rhs_reduced.
///
/// Uses nalgebra dense Cholesky for small systems
/// (total_cam_params <= 100), CHOLMOD for larger.
pub fn solve_reduced_system(ws: &mut SchurComplementWorkspace) -> Result<()> {
    let n = ws.total_cam_params;
    if n == 0 {
        return Ok(());
    }

    // Use nalgebra dense Cholesky.
    // Build a symmetric matrix from row-major schur_matrix.
    let mat =
        nalgebra::DMatrix::from_fn(n, n, |i, j| ws.schur_matrix[i * n + j]);

    let rhs = nalgebra::DVector::from_column_slice(&ws.rhs_reduced);

    match mat.clone().cholesky() {
        Some(chol) => {
            let sol = chol.solve(&rhs);
            for i in 0..n {
                ws.delta_cameras[i] = sol[i];
            }
            Ok(())
        }
        None => {
            if DEBUG {
                eprintln!(
                    "[Schur] Cholesky failed on reduced system, trying LU"
                );
            }
            // Fallback to LU.
            let lu = mat.lu();
            let sol = lu.solve(&rhs).ok_or_else(|| {
                anyhow::anyhow!("Schur reduced system is singular")
            })?;
            for i in 0..n {
                ws.delta_cameras[i] = sol[i];
            }
            Ok(())
        }
    }
}

/// Back-substitute to recover point parameter updates:
///   delta_p[p] = H_pp^{-1} * (-g_p[p] - H_pc * delta_c)
///
/// Uses rayon to parallelize across points.
/// Requires `solve_reduced_system()` to have been called.
pub fn back_substitute(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    // Collect unlocked point info for parallel iteration.
    let unlocked_pts: Vec<(usize, usize)> = (0..ws.num_points)
        .filter_map(|pt_idx| {
            let pt_offset = ws.point_param_offset[pt_idx];
            if pt_offset == usize::MAX {
                None
            } else {
                Some((pt_idx, pt_offset))
            }
        })
        .collect();

    // Borrow shared data immutably.
    let gradient_points = &ws.gradient_points;
    let point_to_observations = &ws.point_to_observations;
    let obs_camera_idx = &ws.obs_camera_idx;
    let camera_param_offset = &ws.camera_param_offset;
    let hcp_blocks = &ws.hcp_blocks;
    let delta_cameras = &ws.delta_cameras;
    let hpp_inv_blocks = &ws.hpp_inv_blocks;

    // Parallel back-substitution per point.
    let results: Vec<(usize, Vec<f64>)> = unlocked_pts
        .par_iter()
        .map(|&(pt_idx, pt_offset)| {
            let unlocked_pt = pt_offset / ps;
            let einv_start = unlocked_pt * ps * ps;

            // sum = -g_p[p]
            let mut sum = vec![0.0; ps];
            for i in 0..ps {
                sum[i] = -gradient_points[pt_offset + i];
            }

            // sum -= H_pc * delta_c
            let obs_list = &point_to_observations[pt_idx];
            for &obs in obs_list.iter() {
                let cam_idx = obs_camera_idx[obs];
                let cam_offset = camera_param_offset[cam_idx];
                if cam_offset == usize::MAX {
                    continue;
                }
                let hcp_start = obs * cs * ps;
                for i in 0..ps {
                    let mut dot = 0.0;
                    for k in 0..cs {
                        dot += hcp_blocks[hcp_start + k * ps + i]
                            * delta_cameras[cam_offset + k];
                    }
                    sum[i] -= dot;
                }
            }

            // delta_p = E_inv * sum
            let mut delta = vec![0.0; ps];
            for i in 0..ps {
                let mut val = 0.0;
                for k in 0..ps {
                    val += hpp_inv_blocks[einv_start + i * ps + k] * sum[k];
                }
                delta[i] = val;
            }

            (pt_offset, delta)
        })
        .collect();

    // Write results back.
    ws.delta_points.fill(0.0);
    for (pt_offset, delta) in results {
        for i in 0..ps {
            ws.delta_points[pt_offset + i] = delta[i];
        }
    }
}

/// Assemble the full parameter step vector from camera and point
/// deltas.
///
/// The output `step` vector has the same layout as the problem's
/// parameter vector: camera parameters first (all cameras in order),
/// then point parameters.
///
/// # Arguments
///
/// * `ws` - Workspace with computed delta_cameras and delta_points.
/// * `step` - Output step vector (length = parameter_count).
/// * `num_cam_params_total` - Total camera parameter slots in the
///   full parameter vector (including locked cameras).
pub fn assemble_full_step(
    ws: &SchurComplementWorkspace,
    step: &mut [f64],
    num_cam_params_total: usize,
) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    step.fill(0.0);

    // Camera parameters.
    for cam_idx in 0..ws.num_cameras {
        let offset = ws.camera_param_offset[cam_idx];
        if offset == usize::MAX {
            continue;
        }
        let full_offset = cam_idx * cs;
        for i in 0..cs {
            step[full_offset + i] = ws.delta_cameras[offset + i];
        }
    }

    // Point parameters.
    for pt_idx in 0..ws.num_points {
        let offset = ws.point_param_offset[pt_idx];
        if offset == usize::MAX {
            continue;
        }
        let full_offset = num_cam_params_total + pt_idx * ps;
        for i in 0..ps {
            step[full_offset + i] = ws.delta_points[offset + i];
        }
    }
}

/// Compute predicted reduction using block Jacobian:
///   pred_red = -step^T * gradient - 0.5 * ||J * step||^2
///
/// The ||J * step||^2 term is computed per-observation from blocks:
///   ||J_c * delta_c + J_p * delta_p||^2
pub fn compute_predicted_reduction(
    ws: &SchurComplementWorkspace,
    gradient: &[f64],
    step: &[f64],
) -> f64 {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    // -step^T * gradient
    let linear_term: f64 =
        step.iter().zip(gradient.iter()).map(|(s, g)| s * g).sum();

    // 0.5 * ||J * step||^2 computed per-observation.
    let mut j_step_norm_sq = 0.0;
    for obs in 0..ws.num_observations {
        let cam_idx = ws.obs_camera_idx[obs];
        let pt_idx = ws.obs_point_idx[obs];
        let cam_offset = ws.camera_param_offset[cam_idx];
        let pt_offset = ws.point_param_offset[pt_idx];

        let jc = ws.camera_jac_block(obs);
        let jp = ws.point_jac_block(obs);

        // Compute J_c * delta_c + J_p * delta_p for both residual
        // rows.
        for row in 0..2 {
            let mut val = 0.0;
            if cam_offset != usize::MAX {
                for k in 0..cs {
                    val += jc[row * cs + k] * ws.delta_cameras[cam_offset + k];
                }
            }
            if pt_offset != usize::MAX {
                for k in 0..ps {
                    val += jp[row * ps + k] * ws.delta_points[pt_offset + k];
                }
            }
            j_step_norm_sq += val * val;
        }
    }

    -linear_term - 0.5 * j_step_norm_sq
}

// ====================================================================
// Reverse direction: eliminate cameras (when N_c > N_p)
// ====================================================================

/// Invert all H_cc blocks (block-diagonal). Uses the general NxN
/// inverse since camera blocks are typically 6x6.
///
/// Uses rayon to parallelize across cameras.
pub fn invert_hcc_blocks(ws: &mut SchurComplementWorkspace) -> Result<()> {
    let cs = ws.cam_block_size;
    let num_cams = ws.num_unlocked_cameras();
    let block_sz = cs * cs;
    let epsilon = 1e-12;

    let hcc_blocks = &ws.hcc_blocks;
    ws.hcc_inv_blocks
        .par_chunks_mut(block_sz)
        .take(num_cams)
        .enumerate()
        .for_each(|(cam, dst)| {
            let start = cam * block_sz;
            let src = &hcc_blocks[start..start + block_sz];
            invert_general_block(src, dst, cs, epsilon);
        });

    Ok(())
}

/// Form the reverse Schur complement matrix:
///   S = H_pp - H_pc * H_cc^{-1} * H_cp
///
/// Requires `invert_hcc_blocks()` to have been called first.
/// Result is stored in `ws.schur_matrix_reverse`.
pub fn form_schur_complement_reverse(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;
    let n = ws.total_pt_params;

    // S starts as H_pp (copy block-diagonal into dense matrix).
    ws.schur_matrix_reverse.fill(0.0);
    let num_pts = ws.num_unlocked_points();
    for pt in 0..num_pts {
        let hpp_start = pt * ps * ps;
        let row_base = pt * ps;
        for i in 0..ps {
            for j in 0..ps {
                ws.schur_matrix_reverse[(row_base + i) * n + row_base + j] =
                    ws.hpp_blocks[hpp_start + i * ps + j];
            }
        }
    }

    // Subtract H_pc * H_cc^{-1} * H_cp for each camera.
    // H_pc[obs] = H_cp[obs]^T  (ps x cs), H_cp[obs] is (cs x ps).
    for cam_idx in 0..ws.num_cameras {
        let cam_offset = ws.camera_param_offset[cam_idx];
        if cam_offset == usize::MAX {
            continue; // locked camera
        }
        let unlocked_cam = cam_offset / cs;

        let obs_list = &ws.camera_to_observations[cam_idx];
        if obs_list.is_empty() {
            continue;
        }

        let einv_start = unlocked_cam * cs * cs;

        for &obs_i in obs_list.iter() {
            let pt_i = ws.obs_point_idx[obs_i];
            let pt_i_offset = ws.point_param_offset[pt_i];
            if pt_i_offset == usize::MAX {
                continue;
            }

            // Compute temp = H_pc[obs_i] * H_cc^{-1}  (ps x cs)
            // H_pc[obs_i] = H_cp[obs_i]^T, which is ps x cs.
            let hcp_i_start = obs_i * cs * ps;
            let mut temp = vec![0.0; ps * cs];
            for r in 0..ps {
                for c in 0..cs {
                    let mut sum = 0.0;
                    for k in 0..cs {
                        // H_pc[r,k] = H_cp[k,r] (transposed)
                        sum += ws.hcp_blocks[hcp_i_start + k * ps + r]
                            * ws.hcc_inv_blocks[einv_start + k * cs + c];
                    }
                    temp[r * cs + c] = sum;
                }
            }

            for &obs_j in obs_list.iter() {
                let pt_j = ws.obs_point_idx[obs_j];
                let pt_j_offset = ws.point_param_offset[pt_j];
                if pt_j_offset == usize::MAX {
                    continue;
                }

                // Only upper triangle + diagonal.
                if pt_j_offset < pt_i_offset {
                    continue;
                }

                // S[p_i, p_j] -= temp * H_cp[obs_j]
                // temp is ps x cs, H_cp[obs_j] is cs x ps
                // result is ps x ps
                let hcp_j_start = obs_j * cs * ps;
                for r in 0..ps {
                    for c in 0..ps {
                        let mut sum = 0.0;
                        for k in 0..cs {
                            sum += temp[r * cs + k]
                                * ws.hcp_blocks[hcp_j_start + k * ps + c];
                        }
                        ws.schur_matrix_reverse
                            [(pt_i_offset + r) * n + pt_j_offset + c] -= sum;
                        // Mirror for lower triangle.
                        if pt_i_offset != pt_j_offset {
                            ws.schur_matrix_reverse
                                [(pt_j_offset + c) * n + pt_i_offset + r] -=
                                sum;
                        }
                    }
                }
            }
        }
    }
}

/// Form the reduced RHS for reverse direction:
///   rhs = -g_p + H_pc * H_cc^{-1} * g_c
///
/// Requires `invert_hcc_blocks()` to have been called first.
pub fn form_reduced_rhs_reverse(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    // Start with -g_p.
    for i in 0..ws.total_pt_params {
        ws.rhs_reduced_reverse[i] = -ws.gradient_points[i];
    }

    // Add H_pc * H_cc^{-1} * g_c for each camera.
    for cam_idx in 0..ws.num_cameras {
        let cam_offset = ws.camera_param_offset[cam_idx];
        if cam_offset == usize::MAX {
            continue;
        }
        let unlocked_cam = cam_offset / cs;
        let einv_start = unlocked_cam * cs * cs;

        // temp = H_cc^{-1} * g_c[cam] (cs x 1)
        let mut temp = [0.0; 16]; // enough for cam_size <= 16
        for i in 0..cs {
            let mut sum = 0.0;
            for k in 0..cs {
                sum += ws.hcc_inv_blocks[einv_start + i * cs + k]
                    * ws.gradient_cameras[cam_offset + k];
            }
            temp[i] = sum;
        }

        // For each observation involving this camera:
        let obs_list = &ws.camera_to_observations[cam_idx];
        for &obs in obs_list.iter() {
            let pt_idx = ws.obs_point_idx[obs];
            let pt_offset = ws.point_param_offset[pt_idx];
            if pt_offset == usize::MAX {
                continue;
            }

            // rhs[p] += H_pc[obs] * temp
            // H_pc[obs] = H_cp[obs]^T (ps x cs)
            let hcp_start = obs * cs * ps;
            for i in 0..ps {
                let mut sum = 0.0;
                for k in 0..cs {
                    // H_pc[i,k] = H_cp[k,i]
                    sum += ws.hcp_blocks[hcp_start + k * ps + i] * temp[k];
                }
                ws.rhs_reduced_reverse[pt_offset + i] += sum;
            }
        }
    }
}

/// Solve the reduced point system: S * delta_p = rhs.
///
/// Uses nalgebra dense Cholesky, falling back to LU.
pub fn solve_reduced_system_reverse(
    ws: &mut SchurComplementWorkspace,
) -> Result<()> {
    let n = ws.total_pt_params;
    if n == 0 {
        return Ok(());
    }

    let mat = nalgebra::DMatrix::from_fn(n, n, |i, j| {
        ws.schur_matrix_reverse[i * n + j]
    });

    let rhs =
        nalgebra::DVector::from_column_slice(&ws.rhs_reduced_reverse[..n]);

    match mat.clone().cholesky() {
        Some(chol) => {
            let sol = chol.solve(&rhs);
            for i in 0..n {
                ws.delta_points[i] = sol[i];
            }
            Ok(())
        }
        None => {
            if DEBUG {
                eprintln!("[Schur-R] Cholesky failed, trying LU");
            }
            let lu = mat.lu();
            let sol = lu.solve(&rhs).ok_or_else(|| {
                anyhow::anyhow!("Reverse Schur reduced system is singular")
            })?;
            for i in 0..n {
                ws.delta_points[i] = sol[i];
            }
            Ok(())
        }
    }
}

/// Back-substitute to recover camera parameter updates (reverse):
///   delta_c[c] = H_cc^{-1} * (-g_c[c] - H_cp * delta_p)
///
/// Uses rayon to parallelize across cameras.
pub fn back_substitute_reverse(ws: &mut SchurComplementWorkspace) {
    let cs = ws.cam_block_size;
    let ps = ws.pt_block_size;

    let unlocked_cams: Vec<(usize, usize)> = (0..ws.num_cameras)
        .filter_map(|cam_idx| {
            let cam_offset = ws.camera_param_offset[cam_idx];
            if cam_offset == usize::MAX {
                None
            } else {
                Some((cam_idx, cam_offset))
            }
        })
        .collect();

    let gradient_cameras = &ws.gradient_cameras;
    let camera_to_observations = &ws.camera_to_observations;
    let obs_point_idx = &ws.obs_point_idx;
    let point_param_offset = &ws.point_param_offset;
    let hcp_blocks = &ws.hcp_blocks;
    let delta_points = &ws.delta_points;
    let hcc_inv_blocks = &ws.hcc_inv_blocks;

    let results: Vec<(usize, Vec<f64>)> = unlocked_cams
        .par_iter()
        .map(|&(cam_idx, cam_offset)| {
            let unlocked_cam = cam_offset / cs;
            let einv_start = unlocked_cam * cs * cs;

            // sum = -g_c[c]
            let mut sum = vec![0.0; cs];
            for i in 0..cs {
                sum[i] = -gradient_cameras[cam_offset + i];
            }

            // sum -= H_cp * delta_p
            let obs_list = &camera_to_observations[cam_idx];
            for &obs in obs_list.iter() {
                let pt_idx = obs_point_idx[obs];
                let pt_offset = point_param_offset[pt_idx];
                if pt_offset == usize::MAX {
                    continue;
                }
                let hcp_start = obs * cs * ps;
                for i in 0..cs {
                    let mut dot = 0.0;
                    for k in 0..ps {
                        dot += hcp_blocks[hcp_start + i * ps + k]
                            * delta_points[pt_offset + k];
                    }
                    sum[i] -= dot;
                }
            }

            // delta_c = H_cc^{-1} * sum
            let mut delta = vec![0.0; cs];
            for i in 0..cs {
                let mut val = 0.0;
                for k in 0..cs {
                    val += hcc_inv_blocks[einv_start + i * cs + k] * sum[k];
                }
                delta[i] = val;
            }

            (cam_offset, delta)
        })
        .collect();

    ws.delta_cameras.fill(0.0);
    for (cam_offset, delta) in results {
        for i in 0..cs {
            ws.delta_cameras[cam_offset + i] = delta[i];
        }
    }
}

// ====================================================================
// Tests
// ====================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_workspace_creation_dimensions() {
        // 2 cameras (both unlocked), 5 points (all unlocked),
        // 10 observations.
        let cam_block_size = 6;
        let pt_block_size = 3;
        let num_cameras = 2;
        let num_points = 5;
        let observations: Vec<(usize, usize)> = vec![
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
        ];
        let camera_unlocked = vec![true, true];
        let point_unlocked = vec![true, true, true, true, true];

        let ws = SchurComplementWorkspace::new(
            num_cameras,
            num_points,
            cam_block_size,
            pt_block_size,
            &observations,
            &camera_unlocked,
            &point_unlocked,
        );

        assert_eq!(ws.total_cam_params, 12); // 2 * 6
        assert_eq!(ws.total_pt_params, 15); // 5 * 3
        assert_eq!(ws.num_unlocked_cameras(), 2);
        assert_eq!(ws.num_unlocked_points(), 5);

        // Buffer sizes.
        assert_eq!(ws.hpp_blocks.len(), 5 * 9); // 5 * 3*3
        assert_eq!(ws.hpp_inv_blocks.len(), 5 * 9);
        assert_eq!(ws.schur_matrix.len(), 12 * 12);
        assert_eq!(ws.hcp_blocks.len(), 10 * 6 * 3);
        assert_eq!(ws.gradient_cameras.len(), 12);
        assert_eq!(ws.gradient_points.len(), 15);
        assert_eq!(ws.camera_jac_blocks.len(), 10 * 2 * 6);
        assert_eq!(ws.point_jac_blocks.len(), 10 * 2 * 3);

        // Adjacency: each point has 2 observations.
        for pt in 0..5 {
            assert_eq!(ws.point_to_observations[pt].len(), 2);
        }

        // Offsets.
        assert_eq!(ws.camera_param_offset[0], 0);
        assert_eq!(ws.camera_param_offset[1], 6);
        assert_eq!(ws.point_param_offset[0], 0);
        assert_eq!(ws.point_param_offset[4], 12);
    }

    #[test]
    fn test_workspace_with_locked_entities() {
        // 3 cameras (cam 0 locked), 4 points (point 2 locked).
        let observations =
            vec![(0, 0), (0, 1), (1, 0), (1, 1), (1, 3), (2, 0), (2, 3)];
        let camera_unlocked = vec![false, true, true];
        let point_unlocked = vec![true, true, false, true];

        let ws = SchurComplementWorkspace::new(
            3,
            4,
            6,
            3,
            &observations,
            &camera_unlocked,
            &point_unlocked,
        );

        assert_eq!(ws.total_cam_params, 12); // 2 unlocked * 6
        assert_eq!(ws.total_pt_params, 9); // 3 unlocked * 3

        assert_eq!(ws.camera_param_offset[0], usize::MAX);
        assert_eq!(ws.camera_param_offset[1], 0);
        assert_eq!(ws.camera_param_offset[2], 6);

        assert_eq!(ws.point_param_offset[0], 0);
        assert_eq!(ws.point_param_offset[1], 3);
        assert_eq!(ws.point_param_offset[2], usize::MAX);
        assert_eq!(ws.point_param_offset[3], 6);
    }

    #[test]
    fn test_workspace_clear() {
        let observations = vec![(0, 0), (1, 0)];
        let mut ws = SchurComplementWorkspace::new(
            2,
            1,
            6,
            3,
            &observations,
            &[true, true],
            &[true],
        );

        // Fill some data.
        ws.schur_matrix[0] = 42.0;
        ws.hpp_blocks[0] = 99.0;
        ws.gradient_cameras[0] = 7.0;

        ws.clear();

        assert_eq!(ws.schur_matrix[0], 0.0);
        assert_eq!(ws.hpp_blocks[0], 0.0);
        assert_eq!(ws.gradient_cameras[0], 0.0);

        // Adjacency should be preserved.
        assert_eq!(ws.point_to_observations[0].len(), 2);
    }

    #[test]
    fn test_assemble_block_hessian_simple() {
        // Minimal: 1 camera, 1 point, 1 observation.
        // cam_block_size=2, pt_block_size=2 for easy manual calc.
        let observations = vec![(0, 0)];
        let mut ws = SchurComplementWorkspace::new(
            1,
            1,
            2,
            2,
            &observations,
            &[true],
            &[true],
        );

        // Set Jacobian blocks:
        // J_c = [[1, 2], [3, 4]]  (2x2, row-major in camera_jac_blocks)
        ws.camera_jac_blocks[0] = 1.0;
        ws.camera_jac_blocks[1] = 2.0;
        ws.camera_jac_blocks[2] = 3.0;
        ws.camera_jac_blocks[3] = 4.0;

        // J_p = [[5, 6], [7, 8]]
        ws.point_jac_blocks[0] = 5.0;
        ws.point_jac_blocks[1] = 6.0;
        ws.point_jac_blocks[2] = 7.0;
        ws.point_jac_blocks[3] = 8.0;

        let residuals = [0.1, 0.2];
        let scaling_cam = [1.0, 1.0];
        let scaling_pt = [1.0, 1.0];

        assemble_block_hessian(
            &mut ws,
            &residuals,
            &scaling_cam,
            &scaling_pt,
            0.0, // no damping
            0.0,
        );

        // H_cc = J_c^T * J_c = [[1,3],[2,4]]^T * [[1,2],[3,4]]
        //                     = [[1*1+3*3, 1*2+3*4],[2*1+4*3, 2*2+4*4]]
        //                     = [[10, 14],[14, 20]]
        assert!((ws.schur_matrix[0] - 10.0).abs() < 1e-10);
        assert!((ws.schur_matrix[1] - 14.0).abs() < 1e-10);
        assert!((ws.schur_matrix[2] - 14.0).abs() < 1e-10);
        assert!((ws.schur_matrix[3] - 20.0).abs() < 1e-10);

        // H_pp = J_p^T * J_p = [[5,7],[6,8]]^T * [[5,6],[7,8]]
        //                     = [[74, 86],[86, 100]]
        assert!((ws.hpp_blocks[0] - 74.0).abs() < 1e-10);
        assert!((ws.hpp_blocks[1] - 86.0).abs() < 1e-10);
        assert!((ws.hpp_blocks[2] - 86.0).abs() < 1e-10);
        assert!((ws.hpp_blocks[3] - 100.0).abs() < 1e-10);

        // H_cp = J_c^T * J_p = [[1*5+3*7, 1*6+3*8],[2*5+4*7, 2*6+4*8]]
        //                    = [[26, 30],[38, 44]]
        assert!((ws.hcp_blocks[0] - 26.0).abs() < 1e-10);
        assert!((ws.hcp_blocks[1] - 30.0).abs() < 1e-10);
        assert!((ws.hcp_blocks[2] - 38.0).abs() < 1e-10);
        assert!((ws.hcp_blocks[3] - 44.0).abs() < 1e-10);

        // g_c = J_c^T * r = [[1*0.1+3*0.2],[2*0.1+4*0.2]] = [0.7, 1.0]
        assert!((ws.gradient_cameras[0] - 0.7).abs() < 1e-10);
        assert!((ws.gradient_cameras[1] - 1.0).abs() < 1e-10);

        // g_p = J_p^T * r = [[5*0.1+7*0.2],[6*0.1+8*0.2]] = [1.9, 2.2]
        assert!((ws.gradient_points[0] - 1.9).abs() < 1e-10);
        assert!((ws.gradient_points[1] - 2.2).abs() < 1e-10);
    }

    #[test]
    fn test_invert_hpp_3x3() {
        // Single 3x3 identity block.
        let observations = vec![(0, 0)];
        let mut ws = SchurComplementWorkspace::new(
            1,
            1,
            6,
            3,
            &observations,
            &[true],
            &[true],
        );

        // Set H_pp to identity.
        ws.hpp_blocks[0] = 1.0;
        ws.hpp_blocks[4] = 1.0;
        ws.hpp_blocks[8] = 1.0;

        invert_hpp_blocks(&mut ws).unwrap();

        // Inverse of identity is identity.
        for i in 0..3 {
            for j in 0..3 {
                let expected = if i == j { 1.0 } else { 0.0 };
                assert!(
                    (ws.hpp_inv_blocks[i * 3 + j] - expected).abs() < 1e-10,
                    "hpp_inv[{},{}] = {}, expected {}",
                    i,
                    j,
                    ws.hpp_inv_blocks[i * 3 + j],
                    expected
                );
            }
        }
    }

    #[test]
    fn test_invert_hpp_3x3_nontrivial() {
        let observations = vec![(0, 0)];
        let mut ws = SchurComplementWorkspace::new(
            1,
            1,
            6,
            3,
            &observations,
            &[true],
            &[true],
        );

        // H_pp = [[2, 1, 0], [1, 3, 1], [0, 1, 2]]
        ws.hpp_blocks[0] = 2.0;
        ws.hpp_blocks[1] = 1.0;
        ws.hpp_blocks[2] = 0.0;
        ws.hpp_blocks[3] = 1.0;
        ws.hpp_blocks[4] = 3.0;
        ws.hpp_blocks[5] = 1.0;
        ws.hpp_blocks[6] = 0.0;
        ws.hpp_blocks[7] = 1.0;
        ws.hpp_blocks[8] = 2.0;

        invert_hpp_blocks(&mut ws).unwrap();

        // Verify A * A^{-1} = I.
        for i in 0..3 {
            for j in 0..3 {
                let mut sum = 0.0;
                for k in 0..3 {
                    sum +=
                        ws.hpp_blocks[i * 3 + k] * ws.hpp_inv_blocks[k * 3 + j];
                }
                let expected = if i == j { 1.0 } else { 0.0 };
                assert!(
                    (sum - expected).abs() < 1e-10,
                    "A*A_inv[{},{}] = {}, expected {}",
                    i,
                    j,
                    sum,
                    expected
                );
            }
        }
    }

    #[test]
    fn test_schur_complement_matches_full_solve() {
        // 2 cameras (both unlocked), 1 point, 2 observations.
        // cam_block_size=2, pt_block_size=2 for tractable manual
        // comparison.
        //
        // Full system: H * delta = g
        // where H = [[H_cc, H_cp], [H_pc, H_pp]]
        //
        // We set up blocks, assemble the full 6x6 system, solve,
        // then compare with Schur complement path.

        let observations = vec![(0, 0), (1, 0)];
        let mut ws = SchurComplementWorkspace::new(
            2,
            1,
            2,
            2,
            &observations,
            &[true, true],
            &[true],
        );

        // Observation 0: cam 0, point 0.
        // J_c0 = [[1, 0], [0, 1]]
        ws.camera_jac_blocks[0] = 1.0;
        ws.camera_jac_blocks[1] = 0.0;
        ws.camera_jac_blocks[2] = 0.0;
        ws.camera_jac_blocks[3] = 1.0;

        // J_p0 = [[2, 0], [0, 2]]
        ws.point_jac_blocks[0] = 2.0;
        ws.point_jac_blocks[1] = 0.0;
        ws.point_jac_blocks[2] = 0.0;
        ws.point_jac_blocks[3] = 2.0;

        // Observation 1: cam 1, point 0.
        // J_c1 = [[0.5, 0], [0, 0.5]]
        ws.camera_jac_blocks[4] = 0.5;
        ws.camera_jac_blocks[5] = 0.0;
        ws.camera_jac_blocks[6] = 0.0;
        ws.camera_jac_blocks[7] = 0.5;

        // J_p1 = [[1, 0], [0, 1]]
        ws.point_jac_blocks[4] = 1.0;
        ws.point_jac_blocks[5] = 0.0;
        ws.point_jac_blocks[6] = 0.0;
        ws.point_jac_blocks[7] = 1.0;

        let residuals = [1.0, 2.0, 0.5, 1.0];
        let scaling_cam = [1.0; 4];
        let scaling_pt = [1.0; 2];
        let lambda = 0.1;

        assemble_block_hessian(
            &mut ws,
            &residuals,
            &scaling_cam,
            &scaling_pt,
            lambda,
            0.0,
        );

        // Now build the full 6x6 system manually for comparison.
        // Parameters: [cam0_0, cam0_1, cam1_0, cam1_1, pt0_0, pt0_1]
        // Full Jacobian (4 x 6):
        // obs0: [1, 0, 0, 0, 2, 0]
        //       [0, 1, 0, 0, 0, 2]
        // obs1: [0, 0, 0.5, 0, 1, 0]
        //       [0, 0, 0, 0.5, 0, 1]
        let j_full: Vec<Vec<f64>> = vec![
            vec![1.0, 0.0, 0.0, 0.0, 2.0, 0.0],
            vec![0.0, 1.0, 0.0, 0.0, 0.0, 2.0],
            vec![0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
            vec![0.0, 0.0, 0.0, 0.5, 0.0, 1.0],
        ];

        // H_full = J^T J + lambda * I
        let mut h_full = vec![vec![0.0; 6]; 6];
        for row in &j_full {
            for i in 0..6 {
                for j in 0..6 {
                    h_full[i][j] += row[i] * row[j];
                }
            }
        }
        for i in 0..6 {
            h_full[i][i] += lambda;
        }

        // g_full = J^T * r
        let r_full = [1.0, 2.0, 0.5, 1.0];
        let mut g_full = [0.0; 6];
        for (row_idx, row) in j_full.iter().enumerate() {
            for i in 0..6 {
                g_full[i] += row[i] * r_full[row_idx];
            }
        }

        // Solve full system with nalgebra.
        // Normal equations: H * step = -g (descent direction).
        let h_mat = nalgebra::DMatrix::from_fn(6, 6, |i, j| h_full[i][j]);
        let neg_g: Vec<f64> = g_full.iter().map(|v| -v).collect();
        let neg_g_vec = nalgebra::DVector::from_column_slice(&neg_g);
        let full_solution = h_mat.cholesky().unwrap().solve(&neg_g_vec);

        // Schur complement path.
        invert_hpp_blocks(&mut ws).unwrap();
        form_schur_complement(&mut ws);
        form_reduced_rhs(&mut ws);
        solve_reduced_system(&mut ws).unwrap();
        back_substitute(&mut ws);

        // Assemble full step.
        let mut schur_step = vec![0.0; 6];
        // cam0 params at [0,1], cam1 at [2,3], pt0 at [4,5]
        schur_step[0] = ws.delta_cameras[0];
        schur_step[1] = ws.delta_cameras[1];
        schur_step[2] = ws.delta_cameras[2];
        schur_step[3] = ws.delta_cameras[3];
        schur_step[4] = ws.delta_points[0];
        schur_step[5] = ws.delta_points[1];

        // Compare.
        for i in 0..6 {
            assert!(
                (schur_step[i] - full_solution[i]).abs() < 1e-8,
                "step[{}]: schur={:.10}, full={:.10}",
                i,
                schur_step[i],
                full_solution[i]
            );
        }
    }
}
