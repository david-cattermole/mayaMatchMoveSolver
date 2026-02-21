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

//! SQPnP solver for the Perspective-n-Point (PnP) camera pose problem.
//!
//! Implements: "A Consistently Fast and Globally Optimal Solution to the
//! Perspective-n-Point Problem" by Terzakis and Lourakis (ECCV 2020).
//!
//! The public API uses Maya coordinates (camera looks down -Z). Internally the
//! algorithm uses computer vision conventions (+Z forward), and coordinate
//! conversion is handled automatically.
//!
//! Rotation matrices are stored as 9-element row-major vectors internally.

use anyhow::Result;
use nalgebra as na;
use thiserror::Error;

use super::common::{validate_correspondences, PnPError};
use crate::datatype::conversions::{
    convert_cv_to_maya_rotation, convert_cv_to_maya_translation,
    convert_maya_to_cv_point3,
};
use crate::datatype::{CameraPose, CameraToSceneCorrespondence, UnitValue};

type Vector2 = na::Vector2<f64>;
type Vector3 = na::Vector3<f64>;
type Vector6 = na::Vector6<f64>;
type Vector9 = na::SVector<f64, 9>;
type Matrix3 = na::Matrix3<f64>;
type Matrix6 = na::Matrix6<f64>;
type Matrix9 = na::SMatrix<f64, 9, 9>;
type Matrix9x3 = na::SMatrix<f64, 9, 3>;
type Matrix9x6 = na::SMatrix<f64, 9, 6>;
type Matrix3x9 = na::SMatrix<f64, 3, 9>;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

#[derive(Debug, Error)]
pub enum SqpnpError {
    #[error("Invalid input: points and projections must have the same length and at least 3 elements")]
    InvalidInput,
    #[error("Weights length mismatch")]
    WeightsLengthMismatch,
    #[error("Null space dimension exceeds 6")]
    InvalidNullSpace,
    #[error("Numerical error during computation")]
    NumericalError,
}

/// A 2D point in normalized (undistorted) image coordinates.
///
/// Computed as x = (u - cx) / fx, y = (v - cy) / fy from pixel coordinates
/// (u, v) using focal lengths (fx, fy) and principal point (cx, cy).
#[derive(Debug, Clone, Copy)]
pub struct Projection {
    pub vector: Vector2,
}

impl Projection {
    pub fn new(x: f64, y: f64) -> Self {
        Self {
            vector: Vector2::new(x, y),
        }
    }
}

/// A 3D point in world coordinates.
#[derive(Debug, Clone, Copy)]
pub struct Point {
    pub vector: Vector3,
}

impl Point {
    pub fn new(x: f64, y: f64, z: f64) -> Self {
        Self {
            vector: Vector3::new(x, y, z),
        }
    }
}

/// Method for decomposing the Omega matrix to find rotation candidates.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum OmegaNullspaceMethod {
    /// Rank-Revealing QR with full pivoting (faster, slightly less accurate).
    #[allow(dead_code)]
    Rrqr,
    /// Column-Pivoted Rank-Revealing QR (fastest, potentially less accurate).
    #[allow(dead_code)]
    Cprrqr,
    /// Singular Value Decomposition (slowest, most accurate).
    #[allow(dead_code)]
    Svd,
}

/// Method for projecting a matrix onto the nearest valid rotation matrix.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NearestRotationMethod {
    /// Fast Optimal Attitude Matrix method (faster).
    #[allow(dead_code)]
    Foam,
    /// Singular Value Decomposition (slower, more robust).
    #[allow(dead_code)]
    Svd,
}

/// Tuning parameters for the SQPnP solver.
#[derive(Debug, Clone)]
pub struct SolverParameters {
    /// Tolerance for determining matrix rank.
    pub rank_tolerance: f64,
    /// Convergence tolerance for SQP iterations.
    pub sqp_squared_tolerance: f64,
    /// Determinant threshold above which the nearest rotation is re-projected.
    pub sqp_det_threshold: f64,
    /// Maximum number of SQP iterations.
    pub sqp_max_iteration: i32,
    /// Method for decomposing the Omega matrix.
    pub omega_nullspace_method: OmegaNullspaceMethod,
    /// Method for finding the nearest rotation matrix.
    pub nearest_rotation_method: NearestRotationMethod,
    /// If the orthogonality error of an eigenvector is below this, skip SQP refinement.
    pub orthogonality_squared_error_threshold: f64,
    /// Two rotation vectors are considered equal if their squared difference is below this.
    pub equal_vectors_squared_diff: f64,
    /// Two squared errors are considered equal if their difference is below this.
    pub equal_squared_errors_diff: f64,
    #[allow(dead_code)]
    pub point_variance_threshold: f64,
}

impl Default for SolverParameters {
    fn default() -> Self {
        Self {
            rank_tolerance: 1e-7,
            sqp_squared_tolerance: 1e-10,
            sqp_det_threshold: 1.001,
            sqp_max_iteration: 15,
            omega_nullspace_method: OmegaNullspaceMethod::Svd,
            nearest_rotation_method: NearestRotationMethod::Svd,
            orthogonality_squared_error_threshold: 1e-8,
            equal_vectors_squared_diff: 1e-10,
            equal_squared_errors_diff: 1e-6,
            point_variance_threshold: 1e-5,
        }
    }
}

/// One candidate solution from the SQPnP solver.
///
/// Transforms world points to camera space as: P_camera = R * P_world + t.
#[derive(Debug, Clone)]
pub struct SQPSolution {
    /// Raw rotation as a 9-element row-major vector (may not be perfectly orthogonal).
    pub r: Vector9,
    /// Orthogonalized rotation as a 9-element row-major vector (orthogonal, det=1).
    pub r_hat: Vector9,
    /// Translation vector in camera coordinates.
    pub t: Vector3,
    #[allow(dead_code)]
    pub num_iterations: i32,
    /// Squared reprojection error.
    pub sq_error: f64,
}

impl SQPSolution {
    /// Returns the orthogonalized rotation as a 3x3 matrix.
    pub fn rotation_matrix(&self) -> Matrix3 {
        Matrix3::new(
            self.r_hat[0],
            self.r_hat[1],
            self.r_hat[2],
            self.r_hat[3],
            self.r_hat[4],
            self.r_hat[5],
            self.r_hat[6],
            self.r_hat[7],
            self.r_hat[8],
        )
    }

    pub fn translation(&self) -> &Vector3 {
        &self.t
    }
}

/// Solves the Perspective-n-Point problem using the SQPnP algorithm.
pub struct PnPSolver {
    projections: Vec<Projection>,
    points: Vec<Point>,
    weights: Vec<f64>,
    parameters: SolverParameters,
    omega: Matrix9,
    s: Vector9,
    u: Matrix9,
    p: Matrix3x9,
    point_mean: Vector3,
    num_null_vectors: i32,
    valid: bool,
    solutions: Vec<SQPSolution>,
}

impl PnPSolver {
    const SQRT3: f64 = 1.7320508075688772935274463415059;

    /// Creates a new solver from 3D world points and their 2D normalized image projections.
    ///
    /// `weights` is per-point weighting (None = uniform). `parameters` controls solver
    /// tuning (None = defaults). Requires at least 3 point correspondences.
    pub fn new(
        points_3d: &[Point],
        projections_2d: &[Projection],
        weights: Option<&[f64]>,
        parameters: Option<SolverParameters>,
    ) -> Result<Self, SqpnpError> {
        let n = points_3d.len();

        if n != projections_2d.len() || n < 3 {
            return Err(SqpnpError::InvalidInput);
        }

        let weights = if let Some(w) = weights {
            if w.len() != n {
                return Err(SqpnpError::WeightsLengthMismatch);
            }
            w.to_vec()
        } else {
            vec![1.0; n]
        };

        let parameters = parameters.unwrap_or_default();

        let mut solver = Self {
            projections: projections_2d.to_vec(),
            points: points_3d.to_vec(),
            weights: weights.clone(),
            parameters,
            omega: Matrix9::zeros(),
            s: Vector9::zeros(),
            u: Matrix9::zeros(),
            p: Matrix3x9::zeros(),
            point_mean: Vector3::zeros(),
            num_null_vectors: -1,
            valid: true,
            solutions: Vec::new(),
        };

        solver.build_omega_and_p()?;
        solver.decompose_omega()?;

        Ok(solver)
    }

    fn build_omega_and_p(&mut self) -> Result<(), SqpnpError> {
        let n = self.points.len();
        let mut sum_wx = 0.0;
        let mut sum_wy = 0.0;
        let mut sum_wx2_plus_wy2 = 0.0;
        let mut sum_w = 0.0;
        let mut sum_wx_vec = Vector3::zeros();
        let mut sum_wy_vec = Vector3::zeros();
        let mut sum_wz_vec = Vector3::zeros();

        let mut qa = Matrix3x9::zeros();

        for i in 0..n {
            let w = self.weights[i];
            if w == 0.0 {
                continue;
            }

            let proj = &self.projections[i].vector;
            let pt = &self.points[i].vector;

            let wx = proj[0] * w;
            let wy = proj[1] * w;
            let wsq_norm_m = w * proj.norm_squared();

            sum_wx += wx;
            sum_wy += wy;
            sum_wx2_plus_wy2 += wsq_norm_m;
            sum_w += w;

            let x = pt[0];
            let y = pt[1];
            let z = pt[2];
            let wx_pt = w * x;
            let wy_pt = w * y;
            let wz_pt = w * z;

            sum_wx_vec[0] += wx_pt;
            sum_wy_vec[0] += wy_pt;
            sum_wz_vec[0] += wz_pt;

            // Build Omega matrix blocks.
            let x2 = x * x;
            let xy = x * y;
            let xz = x * z;
            let y2 = y * y;
            let yz = y * z;
            let z2 = z * z;

            // Block (0:2, 0:2).
            self.omega[(0, 0)] += w * x2;
            self.omega[(0, 1)] += w * xy;
            self.omega[(0, 2)] += w * xz;
            self.omega[(1, 1)] += w * y2;
            self.omega[(1, 2)] += w * yz;
            self.omega[(2, 2)] += w * z2;

            // Block (0:2, 6:8).
            self.omega[(0, 6)] -= wx * x2;
            self.omega[(0, 7)] -= wx * xy;
            self.omega[(0, 8)] -= wx * xz;
            self.omega[(1, 7)] -= wx * y2;
            self.omega[(1, 8)] -= wx * yz;
            self.omega[(2, 8)] -= wx * z2;

            // Block (3:5, 6:8).
            self.omega[(3, 6)] -= wy * x2;
            self.omega[(3, 7)] -= wy * xy;
            self.omega[(3, 8)] -= wy * xz;
            self.omega[(4, 7)] -= wy * y2;
            self.omega[(4, 8)] -= wy * yz;
            self.omega[(5, 8)] -= wy * z2;

            // Block (6:8, 6:8).
            self.omega[(6, 6)] += wsq_norm_m * x2;
            self.omega[(6, 7)] += wsq_norm_m * xy;
            self.omega[(6, 8)] += wsq_norm_m * xz;
            self.omega[(7, 7)] += wsq_norm_m * y2;
            self.omega[(7, 8)] += wsq_norm_m * yz;
            self.omega[(8, 8)] += wsq_norm_m * z2;

            // Accumulate QA.
            qa[(0, 0)] += wx_pt;
            qa[(0, 1)] += wy_pt;
            qa[(0, 2)] += wz_pt;
            qa[(0, 6)] -= wx * x;
            qa[(0, 7)] -= wx * y;
            qa[(0, 8)] -= wx * z;
            qa[(1, 6)] -= wy * x;
            qa[(1, 7)] -= wy * y;
            qa[(1, 8)] -= wy * z;
            qa[(2, 6)] += wsq_norm_m * x;
            qa[(2, 7)] += wsq_norm_m * y;
            qa[(2, 8)] += wsq_norm_m * z;
        }

        // Complete QA matrix.
        qa[(1, 3)] = qa[(0, 0)];
        qa[(1, 4)] = qa[(0, 1)];
        qa[(1, 5)] = qa[(0, 2)];
        qa[(2, 0)] = qa[(0, 6)];
        qa[(2, 1)] = qa[(0, 7)];
        qa[(2, 2)] = qa[(0, 8)];
        qa[(2, 3)] = qa[(1, 6)];
        qa[(2, 4)] = qa[(1, 7)];
        qa[(2, 5)] = qa[(1, 8)];

        // Fill symmetric parts of Omega.
        self.complete_omega_symmetry();

        // Build Q matrix.
        let mut q = Matrix3::zeros();
        q[(0, 0)] = sum_w;
        q[(0, 2)] = -sum_wx;
        q[(1, 1)] = sum_w;
        q[(1, 2)] = -sum_wy;
        q[(2, 0)] = -sum_wx;
        q[(2, 1)] = -sum_wy;
        q[(2, 2)] = sum_wx2_plus_wy2;

        // Invert Q.
        let q_inv = Self::invert_symmetric_3x3(&q)?;

        // Compute P = -Q_inv * QA.
        self.p = -q_inv * qa;

        // Complete Omega.
        self.omega += qa.transpose() * self.p;

        // Compute point mean.
        if sum_w > 0.0 {
            let inv_sum_w = 1.0 / sum_w;
            self.point_mean = Vector3::new(
                sum_wx_vec[0] * inv_sum_w,
                sum_wy_vec[0] * inv_sum_w,
                sum_wz_vec[0] * inv_sum_w,
            );
        }

        Ok(())
    }

    fn complete_omega_symmetry(&mut self) {
        // Fill lower triangle blocks.
        self.omega[(1, 6)] = self.omega[(0, 7)];
        self.omega[(2, 6)] = self.omega[(0, 8)];
        self.omega[(2, 7)] = self.omega[(1, 8)];
        self.omega[(4, 6)] = self.omega[(3, 7)];
        self.omega[(5, 6)] = self.omega[(3, 8)];
        self.omega[(5, 7)] = self.omega[(4, 8)];
        self.omega[(7, 6)] = self.omega[(6, 7)];
        self.omega[(8, 6)] = self.omega[(6, 8)];
        self.omega[(8, 7)] = self.omega[(7, 8)];

        // Fill block (3:5, 3:5) from (0:2, 0:2).
        self.omega[(3, 3)] = self.omega[(0, 0)];
        self.omega[(3, 4)] = self.omega[(0, 1)];
        self.omega[(3, 5)] = self.omega[(0, 2)];
        self.omega[(4, 4)] = self.omega[(1, 1)];
        self.omega[(4, 5)] = self.omega[(1, 2)];
        self.omega[(5, 5)] = self.omega[(2, 2)];

        // Fill remaining lower triangle.
        for i in 0..9 {
            for j in 0..i {
                self.omega[(i, j)] = self.omega[(j, i)];
            }
        }
    }

    fn decompose_omega(&mut self) -> Result<(), SqpnpError> {
        match self.parameters.omega_nullspace_method {
            OmegaNullspaceMethod::Svd => {
                let svd = na::SVD::new(self.omega.clone(), true, false);
                self.u = svd.u.unwrap();
                self.s = svd.singular_values;
            }
            OmegaNullspaceMethod::Rrqr | OmegaNullspaceMethod::Cprrqr => {
                // Use QR decomposition as approximation.
                let qr = na::QR::new(self.omega.clone());
                self.u = qr.q();
                let r = qr.r();
                self.s = r.diagonal().map(|x| x.abs());
            }
        }

        // Find null space dimension.
        self.num_null_vectors = 0;
        while 7 - self.num_null_vectors >= 0
            && self.s[(7 - self.num_null_vectors) as usize]
                < self.parameters.rank_tolerance
        {
            self.num_null_vectors += 1;
        }
        self.num_null_vectors += 1;

        if self.num_null_vectors > 6 {
            return Err(SqpnpError::InvalidNullSpace);
        }

        Ok(())
    }

    /// Runs the solver and returns candidate poses sorted by reprojection error.
    ///
    /// Multiple solutions may be returned due to pose ambiguities.
    pub fn solve(&mut self) -> Result<Vec<SQPSolution>, SqpnpError> {
        if !self.valid {
            return Err(SqpnpError::NumericalError);
        }

        let mut min_sq_error = f64::MAX;
        self.solutions.clear();

        let num_eigen_points = if self.num_null_vectors > 0 {
            self.num_null_vectors
        } else {
            1
        } as usize;

        // Process eigenvectors from the null space.
        for i in (9 - num_eigen_points)..9 {
            let eigenvec = Self::SQRT3 * self.u.column(i).into_owned();
            let orthogonality_sq_error = Self::orthogonality_error(&eigenvec);

            if orthogonality_sq_error
                < self.parameters.orthogonality_squared_error_threshold
            {
                // Eigenvector is already near-orthogonal, just fix the sign.
                let det_e = Self::determinant_9x1(&eigenvec);
                let r_hat = if det_e < 0.0 {
                    -eigenvec.clone()
                } else {
                    eigenvec.clone()
                };

                let mut solution = SQPSolution {
                    r: eigenvec.clone(),
                    r_hat,
                    t: Vector3::zeros(),
                    num_iterations: 0,
                    sq_error: 0.0,
                };
                solution.t = self.p * solution.r_hat;
                self.handle_solution(solution, &mut min_sq_error);
            } else {
                // Refine with SQP using both sign orientations of the eigenvector.
                for sign in [1.0, -1.0] {
                    let initial_rotation = self
                        .nearest_rotation_matrix(&(sign * eigenvec.clone()));
                    let mut solution = self.run_sqp(&initial_rotation)?;
                    solution.t = self.p * solution.r_hat;
                    self.handle_solution(solution, &mut min_sq_error);
                }
            }
        }

        // Also check additional eigenvectors when the error is still high.
        let mut extra_count = 1;
        let mut index = (9 - num_eigen_points - extra_count) as i32;
        while index > 0 && min_sq_error > 3.0 * self.s[index as usize] {
            let eigenvec = self.u.column(index as usize).into_owned();

            for sign in [1.0, -1.0] {
                let initial_rotation =
                    self.nearest_rotation_matrix(&(sign * eigenvec.clone()));
                let mut solution = self.run_sqp(&initial_rotation)?;
                solution.t = self.p * solution.r_hat;
                self.handle_solution(solution, &mut min_sq_error);
            }

            extra_count += 1;
            index = (9 - num_eigen_points - extra_count) as i32;
        }

        Ok(self.solutions.clone())
    }

    fn handle_solution(
        &mut self,
        solution: SQPSolution,
        min_sq_error: &mut f64,
    ) {
        if !self.test_positive_depth(&solution)
            && !self.test_positive_majority_depths(&solution)
        {
            return;
        }

        let sq_error = (self.omega * solution.r_hat).dot(&solution.r_hat);
        let solution = SQPSolution {
            sq_error,
            ..solution
        };

        if (*min_sq_error - sq_error).abs()
            > self.parameters.equal_squared_errors_diff
        {
            if *min_sq_error > sq_error {
                *min_sq_error = sq_error;
                self.solutions.clear();
                self.solutions.push(solution);
            }
        } else {
            let mut found = false;
            for existing in &mut self.solutions {
                if (existing.r_hat - solution.r_hat).norm_squared()
                    < self.parameters.equal_vectors_squared_diff
                {
                    if existing.sq_error > sq_error {
                        *existing = solution.clone();
                    }
                    found = true;
                    break;
                }
            }

            if !found {
                self.solutions.push(solution.clone());
            }

            if *min_sq_error > sq_error {
                *min_sq_error = sq_error;
            }
        }
    }

    fn run_sqp(
        &self,
        initial_rotation: &Vector9,
    ) -> Result<SQPSolution, SqpnpError> {
        let mut r = initial_rotation.clone();
        let mut delta_squared_norm = f64::MAX;
        let mut step = 0;

        while delta_squared_norm > self.parameters.sqp_squared_tolerance
            && step < self.parameters.sqp_max_iteration
        {
            let delta = self.solve_sqp_system(&r)?;
            r += delta;
            delta_squared_norm = delta.norm_squared();
            step += 1;
        }

        let mut solution = SQPSolution {
            r: r.clone(),
            r_hat: Vector9::zeros(),
            t: Vector3::zeros(),
            num_iterations: step,
            sq_error: 0.0,
        };

        let mut det_r = Self::determinant_9x1(&r);
        if det_r < 0.0 {
            solution.r = -r;
            det_r = -det_r;
        }

        if det_r > self.parameters.sqp_det_threshold {
            solution.r_hat = self.nearest_rotation_matrix(&solution.r);
        } else {
            solution.r_hat = solution.r.clone();
        }

        Ok(solution)
    }

    fn solve_sqp_system(&self, r: &Vector9) -> Result<Vector9, SqpnpError> {
        let sqnorm_r1 = r[0] * r[0] + r[1] * r[1] + r[2] * r[2];
        let sqnorm_r2 = r[3] * r[3] + r[4] * r[4] + r[5] * r[5];
        let sqnorm_r3 = r[6] * r[6] + r[7] * r[7] + r[8] * r[8];
        let dot_r1r2 = r[0] * r[3] + r[1] * r[4] + r[2] * r[5];
        let dot_r1r3 = r[0] * r[6] + r[1] * r[7] + r[2] * r[8];
        let dot_r2r3 = r[3] * r[6] + r[4] * r[7] + r[5] * r[8];

        let (row_basis, null_basis, jh) = Self::row_and_null_space(r, 0.1)?;

        // Constraint vector: rotation rows must be unit length and mutually orthogonal.
        let g = Vector6::new(
            1.0 - sqnorm_r1,
            1.0 - sqnorm_r2,
            1.0 - sqnorm_r3,
            -dot_r1r2,
            -dot_r2r3,
            -dot_r1r3,
        );

        // Solve (J*H)*x = g by forward substitution (JH is lower triangular).
        let mut x = Vector6::zeros();
        x[0] = g[0] / jh[(0, 0)];
        x[1] = g[1] / jh[(1, 1)];
        x[2] = g[2] / jh[(2, 2)];
        x[3] = (g[3] - jh[(3, 0)] * x[0] - jh[(3, 1)] * x[1]) / jh[(3, 3)];
        x[4] =
            (g[4] - jh[(4, 1)] * x[1] - jh[(4, 2)] * x[2] - jh[(4, 3)] * x[3])
                / jh[(4, 4)];
        x[5] = (g[5]
            - jh[(5, 0)] * x[0]
            - jh[(5, 2)] * x[2]
            - jh[(5, 3)] * x[3]
            - jh[(5, 4)] * x[4])
            / jh[(5, 5)];

        // Row-space component of the update step.
        let mut delta = row_basis * x;

        // Null-space component: solve W * null_coeffs = rhs.
        let nt_omega = null_basis.transpose() * self.omega;
        let w = nt_omega * null_basis;
        let rhs = -(nt_omega * (delta + r));

        let null_coeffs =
            if let Some(w_inv) = Self::invert_symmetric_3x3(&w).ok() {
                w_inv * rhs
            } else {
                // Fall back to pseudo-inverse for near-singular cases.
                w.pseudo_inverse(1e-8).unwrap() * rhs
            };

        delta += null_basis * null_coeffs;

        Ok(delta)
    }

    fn row_and_null_space(
        r: &Vector9,
        norm_threshold: f64,
    ) -> Result<(Matrix9x6, Matrix9x3, Matrix6), SqpnpError> {
        let mut row_basis = Matrix9x6::zeros();
        let mut jh = Matrix6::zeros();

        // Gram-Schmidt orthogonalization of the constraint Jacobian rows.
        // Step 1: q1.
        let norm_r1 = (r[0] * r[0] + r[1] * r[1] + r[2] * r[2]).sqrt();
        let inv_norm_r1 = if norm_r1 > 1e-5 { 1.0 / norm_r1 } else { 0.0 };
        row_basis[(0, 0)] = r[0] * inv_norm_r1;
        row_basis[(1, 0)] = r[1] * inv_norm_r1;
        row_basis[(2, 0)] = r[2] * inv_norm_r1;
        jh[(0, 0)] = 2.0 * norm_r1;

        // Step 2: q2.
        let norm_r2 = (r[3] * r[3] + r[4] * r[4] + r[5] * r[5]).sqrt();
        let inv_norm_r2 = 1.0 / norm_r2;
        row_basis[(3, 1)] = r[3] * inv_norm_r2;
        row_basis[(4, 1)] = r[4] * inv_norm_r2;
        row_basis[(5, 1)] = r[5] * inv_norm_r2;
        jh[(1, 1)] = 2.0 * norm_r2;

        // Step 3: q3.
        let norm_r3 = (r[6] * r[6] + r[7] * r[7] + r[8] * r[8]).sqrt();
        let inv_norm_r3 = 1.0 / norm_r3;
        row_basis[(6, 2)] = r[6] * inv_norm_r3;
        row_basis[(7, 2)] = r[7] * inv_norm_r3;
        row_basis[(8, 2)] = r[8] * inv_norm_r3;
        jh[(2, 2)] = 2.0 * norm_r3;

        // Step 4: q4.
        let dot_j4q1 = r[3] * row_basis[(0, 0)]
            + r[4] * row_basis[(1, 0)]
            + r[5] * row_basis[(2, 0)];
        let dot_j4q2 = r[0] * row_basis[(3, 1)]
            + r[1] * row_basis[(4, 1)]
            + r[2] * row_basis[(5, 1)];

        row_basis[(0, 3)] = r[3] - dot_j4q1 * row_basis[(0, 0)];
        row_basis[(1, 3)] = r[4] - dot_j4q1 * row_basis[(1, 0)];
        row_basis[(2, 3)] = r[5] - dot_j4q1 * row_basis[(2, 0)];
        row_basis[(3, 3)] = r[0] - dot_j4q2 * row_basis[(3, 1)];
        row_basis[(4, 3)] = r[1] - dot_j4q2 * row_basis[(4, 1)];
        row_basis[(5, 3)] = r[2] - dot_j4q2 * row_basis[(5, 1)];

        let norm_j4 = (row_basis[(0, 3)] * row_basis[(0, 3)]
            + row_basis[(1, 3)] * row_basis[(1, 3)]
            + row_basis[(2, 3)] * row_basis[(2, 3)]
            + row_basis[(3, 3)] * row_basis[(3, 3)]
            + row_basis[(4, 3)] * row_basis[(4, 3)]
            + row_basis[(5, 3)] * row_basis[(5, 3)])
            .sqrt();
        let inv_norm_j4 = 1.0 / norm_j4;

        for i in 0..6 {
            row_basis[(i, 3)] *= inv_norm_j4;
        }

        jh[(3, 0)] = r[3] * row_basis[(0, 0)]
            + r[4] * row_basis[(1, 0)]
            + r[5] * row_basis[(2, 0)];
        jh[(3, 1)] = r[0] * row_basis[(3, 1)]
            + r[1] * row_basis[(4, 1)]
            + r[2] * row_basis[(5, 1)];
        jh[(3, 2)] = 0.0;
        jh[(3, 3)] = r[3] * row_basis[(0, 3)]
            + r[4] * row_basis[(1, 3)]
            + r[5] * row_basis[(2, 3)]
            + r[0] * row_basis[(3, 3)]
            + r[1] * row_basis[(4, 3)]
            + r[2] * row_basis[(5, 3)];

        // Step 5: q5.
        let dot_j5q2 = r[6] * row_basis[(3, 1)]
            + r[7] * row_basis[(4, 1)]
            + r[8] * row_basis[(5, 1)];
        let dot_j5q3 = r[3] * row_basis[(6, 2)]
            + r[4] * row_basis[(7, 2)]
            + r[5] * row_basis[(8, 2)];
        let dot_j5q4 = r[6] * row_basis[(3, 3)]
            + r[7] * row_basis[(4, 3)]
            + r[8] * row_basis[(5, 3)];

        row_basis[(0, 4)] = -dot_j5q4 * row_basis[(0, 3)];
        row_basis[(1, 4)] = -dot_j5q4 * row_basis[(1, 3)];
        row_basis[(2, 4)] = -dot_j5q4 * row_basis[(2, 3)];
        row_basis[(3, 4)] =
            r[6] - dot_j5q2 * row_basis[(3, 1)] - dot_j5q4 * row_basis[(3, 3)];
        row_basis[(4, 4)] =
            r[7] - dot_j5q2 * row_basis[(4, 1)] - dot_j5q4 * row_basis[(4, 3)];
        row_basis[(5, 4)] =
            r[8] - dot_j5q2 * row_basis[(5, 1)] - dot_j5q4 * row_basis[(5, 3)];
        row_basis[(6, 4)] = r[3] - dot_j5q3 * row_basis[(6, 2)];
        row_basis[(7, 4)] = r[4] - dot_j5q3 * row_basis[(7, 2)];
        row_basis[(8, 4)] = r[5] - dot_j5q3 * row_basis[(8, 2)];

        let norm_j5 = row_basis.column(4).norm();
        let inv_norm_j5 = 1.0 / norm_j5;
        for i in 0..9 {
            row_basis[(i, 4)] *= inv_norm_j5;
        }

        jh[(4, 0)] = 0.0;
        jh[(4, 1)] = r[6] * row_basis[(3, 1)]
            + r[7] * row_basis[(4, 1)]
            + r[8] * row_basis[(5, 1)];
        jh[(4, 2)] = r[3] * row_basis[(6, 2)]
            + r[4] * row_basis[(7, 2)]
            + r[5] * row_basis[(8, 2)];
        jh[(4, 3)] = r[6] * row_basis[(3, 3)]
            + r[7] * row_basis[(4, 3)]
            + r[8] * row_basis[(5, 3)];
        jh[(4, 4)] = r[6] * row_basis[(3, 4)]
            + r[7] * row_basis[(4, 4)]
            + r[8] * row_basis[(5, 4)]
            + r[3] * row_basis[(6, 4)]
            + r[4] * row_basis[(7, 4)]
            + r[5] * row_basis[(8, 4)];

        // Step 6: q6.
        let dot_j6q1 = r[6] * row_basis[(0, 0)]
            + r[7] * row_basis[(1, 0)]
            + r[8] * row_basis[(2, 0)];
        let dot_j6q3 = r[0] * row_basis[(6, 2)]
            + r[1] * row_basis[(7, 2)]
            + r[2] * row_basis[(8, 2)];
        let dot_j6q4 = r[6] * row_basis[(0, 3)]
            + r[7] * row_basis[(1, 3)]
            + r[8] * row_basis[(2, 3)];
        let dot_j6q5 = r[0] * row_basis[(6, 4)]
            + r[1] * row_basis[(7, 4)]
            + r[2] * row_basis[(8, 4)]
            + r[6] * row_basis[(0, 4)]
            + r[7] * row_basis[(1, 4)]
            + r[8] * row_basis[(2, 4)];

        row_basis[(0, 5)] = r[6]
            - dot_j6q1 * row_basis[(0, 0)]
            - dot_j6q4 * row_basis[(0, 3)]
            - dot_j6q5 * row_basis[(0, 4)];
        row_basis[(1, 5)] = r[7]
            - dot_j6q1 * row_basis[(1, 0)]
            - dot_j6q4 * row_basis[(1, 3)]
            - dot_j6q5 * row_basis[(1, 4)];
        row_basis[(2, 5)] = r[8]
            - dot_j6q1 * row_basis[(2, 0)]
            - dot_j6q4 * row_basis[(2, 3)]
            - dot_j6q5 * row_basis[(2, 4)];

        row_basis[(3, 5)] =
            -dot_j6q5 * row_basis[(3, 4)] - dot_j6q4 * row_basis[(3, 3)];
        row_basis[(4, 5)] =
            -dot_j6q5 * row_basis[(4, 4)] - dot_j6q4 * row_basis[(4, 3)];
        row_basis[(5, 5)] =
            -dot_j6q5 * row_basis[(5, 4)] - dot_j6q4 * row_basis[(5, 3)];

        row_basis[(6, 5)] =
            r[0] - dot_j6q3 * row_basis[(6, 2)] - dot_j6q5 * row_basis[(6, 4)];
        row_basis[(7, 5)] =
            r[1] - dot_j6q3 * row_basis[(7, 2)] - dot_j6q5 * row_basis[(7, 4)];
        row_basis[(8, 5)] =
            r[2] - dot_j6q3 * row_basis[(8, 2)] - dot_j6q5 * row_basis[(8, 4)];

        let norm_j6 = row_basis.column(5).norm();
        let inv_norm_j6 = 1.0 / norm_j6;
        for i in 0..9 {
            row_basis[(i, 5)] *= inv_norm_j6;
        }

        jh[(5, 0)] = r[6] * row_basis[(0, 0)]
            + r[7] * row_basis[(1, 0)]
            + r[8] * row_basis[(2, 0)];
        jh[(5, 1)] = 0.0;
        jh[(5, 2)] = r[0] * row_basis[(6, 2)]
            + r[1] * row_basis[(7, 2)]
            + r[2] * row_basis[(8, 2)];
        jh[(5, 3)] = r[6] * row_basis[(0, 3)]
            + r[7] * row_basis[(1, 3)]
            + r[8] * row_basis[(2, 3)];
        jh[(5, 4)] = r[6] * row_basis[(0, 4)]
            + r[7] * row_basis[(1, 4)]
            + r[8] * row_basis[(2, 4)]
            + r[0] * row_basis[(6, 4)]
            + r[1] * row_basis[(7, 4)]
            + r[2] * row_basis[(8, 4)];
        jh[(5, 5)] = r[6] * row_basis[(0, 5)]
            + r[7] * row_basis[(1, 5)]
            + r[8] * row_basis[(2, 5)]
            + r[0] * row_basis[(6, 5)]
            + r[1] * row_basis[(7, 5)]
            + r[2] * row_basis[(8, 5)];

        // Build the orthonormal null space basis from the projector P_n = I - H*H^T.
        let identity = Matrix9::identity();
        let pn = identity - row_basis * row_basis.transpose();

        let mut col_norms = [0.0; 9];
        for i in 0..9 {
            col_norms[i] = pn.column(i).norm();
        }

        let mut indices = [0usize; 3];
        let mut used = [false; 9];

        // Pick the column with the largest norm.
        let mut max_norm = 0.0;
        for i in 0..9 {
            if col_norms[i] > max_norm && col_norms[i] >= norm_threshold {
                max_norm = col_norms[i];
                indices[0] = i;
            }
        }
        used[indices[0]] = true;

        // Pick the second column most orthogonal to the first.
        let v1 = pn.column(indices[0]);
        let mut min_dot = f64::MAX;
        for i in 0..9 {
            if !used[i] && col_norms[i] >= norm_threshold {
                let cos_angle = (pn.column(i).dot(&v1) / col_norms[i]).abs();
                if cos_angle < min_dot {
                    min_dot = cos_angle;
                    indices[1] = i;
                }
            }
        }
        used[indices[1]] = true;

        // Pick the third column most orthogonal to both.
        let v2 = pn.column(indices[1]);
        let mut min_sum = f64::MAX;
        for i in 0..9 {
            if !used[i] && col_norms[i] >= norm_threshold {
                let inv_norm = 1.0 / col_norms[i];
                let cos1 = (pn.column(i).dot(&v1) * inv_norm).abs();
                let cos2 = (pn.column(i).dot(&v2) * inv_norm).abs();
                let sum = cos1 + cos2;
                if sum < min_sum {
                    min_sum = sum;
                    indices[2] = i;
                }
            }
        }

        // Orthonormalize the three selected columns via Gram-Schmidt.
        let mut null_basis = Matrix9x3::zeros();
        null_basis.set_column(0, &(pn.column(indices[0]).normalize()));

        let mut col1 = pn.column(indices[1]).into_owned();
        col1 -=
            col1.dot(&null_basis.column(0)) * null_basis.column(0).into_owned();
        null_basis.set_column(1, &col1.normalize());

        let mut col2 = pn.column(indices[2]).into_owned();
        col2 -=
            col2.dot(&null_basis.column(0)) * null_basis.column(0).into_owned();
        col2 -=
            col2.dot(&null_basis.column(1)) * null_basis.column(1).into_owned();
        null_basis.set_column(2, &col2.normalize());

        Ok((row_basis, null_basis, jh))
    }

    fn test_positive_depth(&self, solution: &SQPSolution) -> bool {
        let r = &solution.r_hat;
        let t = &solution.t;
        let m = &self.point_mean;

        r[6] * m[0] + r[7] * m[1] + r[8] * m[2] + t[2] > 0.0
    }

    fn test_positive_majority_depths(&self, solution: &SQPSolution) -> bool {
        let r = &solution.r_hat;
        let t = &solution.t;
        let mut points_in_front = 0;
        let mut points_behind = 0;

        for i in 0..self.points.len() {
            if self.weights[i] == 0.0 {
                continue;
            }
            let m = &self.points[i].vector;
            if r[6] * m[0] + r[7] * m[1] + r[8] * m[2] + t[2] > 0.0 {
                points_in_front += 1;
            } else {
                points_behind += 1;
            }
        }

        points_in_front >= points_behind
    }

    fn nearest_rotation_matrix(&self, e: &Vector9) -> Vector9 {
        match self.parameters.nearest_rotation_method {
            NearestRotationMethod::Svd => Self::nearest_rotation_matrix_svd(e),
            NearestRotationMethod::Foam => {
                Self::nearest_rotation_matrix_foam(e)
            }
        }
    }

    fn nearest_rotation_matrix_svd(e: &Vector9) -> Vector9 {
        let mat =
            Matrix3::new(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8]);

        let svd = na::SVD::new(mat, true, true);
        let u = svd.u.unwrap();
        let v_t = svd.v_t.unwrap();

        let det_uv = u.determinant() * v_t.transpose().determinant();
        let diag = Matrix3::from_diagonal(&Vector3::new(1.0, 1.0, det_uv));
        let r = u * diag * v_t;

        Vector9::from([
            r[(0, 0)],
            r[(0, 1)],
            r[(0, 2)],
            r[(1, 0)],
            r[(1, 1)],
            r[(1, 2)],
            r[(2, 0)],
            r[(2, 1)],
            r[(2, 2)],
        ])
    }

    fn nearest_rotation_matrix_foam(e: &Vector9) -> Vector9 {
        let b = e.as_slice();

        let det_b = (b[0] * b[4] * b[8]
            - b[0] * b[5] * b[7]
            - b[1] * b[3] * b[8])
            + (b[2] * b[3] * b[7] + b[1] * b[6] * b[5] - b[2] * b[6] * b[4]);

        if det_b.abs() < 1e-4 {
            return Self::nearest_rotation_matrix_svd(e);
        }

        // Adjugate (transpose of cofactor matrix) of b.
        let mut adjugate = [0.0; 9];
        adjugate[0] = b[4] * b[8] - b[5] * b[7];
        adjugate[1] = b[2] * b[7] - b[1] * b[8];
        adjugate[2] = b[1] * b[5] - b[2] * b[4];
        adjugate[3] = b[5] * b[6] - b[3] * b[8];
        adjugate[4] = b[0] * b[8] - b[2] * b[6];
        adjugate[5] = b[2] * b[3] - b[0] * b[5];
        adjugate[6] = b[3] * b[7] - b[4] * b[6];
        adjugate[7] = b[1] * b[6] - b[0] * b[7];
        adjugate[8] = b[0] * b[4] - b[1] * b[3];

        let b_norm_sq = b.iter().map(|x| x * x).sum::<f64>();
        let adjugate_norm_sq = adjugate.iter().map(|x| x * x).sum::<f64>();

        // Newton-Raphson iteration for the FOAM scalar lambda.
        let mut lambda = 0.5 * (b_norm_sq + 3.0);
        if det_b < 0.0 {
            lambda = -lambda;
        }

        let mut lambda_prev = 0.0;
        for _ in 0..15 {
            let tmp = lambda * lambda - b_norm_sq;
            let p = tmp * tmp - 8.0 * lambda * det_b - 4.0 * adjugate_norm_sq;
            let pp = 8.0 * (0.5 * tmp * lambda - det_b);

            if (lambda - lambda_prev).abs() <= 1e-12 * lambda_prev.abs() {
                break;
            }

            lambda_prev = lambda;
            lambda -= p / pp;
        }

        // B * B^T.
        let mut b_times_bt = Matrix3::zeros();
        b_times_bt[(0, 0)] = b[0] * b[0] + b[1] * b[1] + b[2] * b[2];
        b_times_bt[(0, 1)] = b[0] * b[3] + b[1] * b[4] + b[2] * b[5];
        b_times_bt[(0, 2)] = b[0] * b[6] + b[1] * b[7] + b[2] * b[8];
        b_times_bt[(1, 0)] = b_times_bt[(0, 1)];
        b_times_bt[(1, 1)] = b[3] * b[3] + b[4] * b[4] + b[5] * b[5];
        b_times_bt[(1, 2)] = b[3] * b[6] + b[4] * b[7] + b[5] * b[8];
        b_times_bt[(2, 0)] = b_times_bt[(0, 2)];
        b_times_bt[(2, 1)] = b_times_bt[(1, 2)];
        b_times_bt[(2, 2)] = b[6] * b[6] + b[7] * b[7] + b[8] * b[8];

        let b_mat =
            Matrix3::new(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8]);
        let bbt_times_b = b_times_bt * b_mat;

        let a = lambda * lambda + b_norm_sq;
        let denom =
            1.0 / (lambda * (lambda * lambda - b_norm_sq) - 2.0 * det_b);

        let mut r = Vector9::zeros();
        r[0] = (a * b[0] + 2.0 * (lambda * adjugate[0] - bbt_times_b[(0, 0)]))
            * denom;
        r[1] = (a * b[1] + 2.0 * (lambda * adjugate[3] - bbt_times_b[(0, 1)]))
            * denom;
        r[2] = (a * b[2] + 2.0 * (lambda * adjugate[6] - bbt_times_b[(0, 2)]))
            * denom;
        r[3] = (a * b[3] + 2.0 * (lambda * adjugate[1] - bbt_times_b[(1, 0)]))
            * denom;
        r[4] = (a * b[4] + 2.0 * (lambda * adjugate[4] - bbt_times_b[(1, 1)]))
            * denom;
        r[5] = (a * b[5] + 2.0 * (lambda * adjugate[7] - bbt_times_b[(1, 2)]))
            * denom;
        r[6] = (a * b[6] + 2.0 * (lambda * adjugate[2] - bbt_times_b[(2, 0)]))
            * denom;
        r[7] = (a * b[7] + 2.0 * (lambda * adjugate[5] - bbt_times_b[(2, 1)]))
            * denom;
        r[8] = (a * b[8] + 2.0 * (lambda * adjugate[8] - bbt_times_b[(2, 2)]))
            * denom;

        r
    }

    fn orthogonality_error(a: &Vector9) -> f64 {
        let sq_norm_a1 = a[0] * a[0] + a[1] * a[1] + a[2] * a[2];
        let sq_norm_a2 = a[3] * a[3] + a[4] * a[4] + a[5] * a[5];
        let sq_norm_a3 = a[6] * a[6] + a[7] * a[7] + a[8] * a[8];
        let dot_a1a2 = a[0] * a[3] + a[1] * a[4] + a[2] * a[5];
        let dot_a1a3 = a[0] * a[6] + a[1] * a[7] + a[2] * a[8];
        let dot_a2a3 = a[3] * a[6] + a[4] * a[7] + a[5] * a[8];

        (sq_norm_a1 - 1.0).powi(2)
            + (sq_norm_a2 - 1.0).powi(2)
            + (sq_norm_a3 - 1.0).powi(2)
            + 2.0 * (dot_a1a2.powi(2) + dot_a1a3.powi(2) + dot_a2a3.powi(2))
    }

    fn determinant_9x1(r: &Vector9) -> f64 {
        r[0] * r[4] * r[8] + r[1] * r[5] * r[6] + r[2] * r[3] * r[7]
            - r[6] * r[4] * r[2]
            - r[7] * r[5] * r[0]
            - r[8] * r[3] * r[1]
    }

    fn invert_symmetric_3x3(q: &Matrix3) -> Result<Matrix3, SqpnpError> {
        let det = q.determinant();

        if det.abs() < 1e-10 {
            // Use pseudo-inverse for singular matrices.
            q.pseudo_inverse(1e-10)
                .map_err(|_| SqpnpError::NumericalError)
        } else {
            // Direct inversion for non-singular symmetric matrices.
            q.try_inverse().ok_or(SqpnpError::NumericalError)
        }
    }
}

/// Computes camera poses from 2D-3D point correspondences using the SQPnP algorithm.
///
/// Requires at least 3 correspondences. Returns candidate poses sorted by reprojection
/// error (best first). Multiple poses may be returned due to pose ambiguities.
///
/// Inputs and outputs use Maya coordinates (camera looks down -Z). The 2D camera points
/// must be in normalized image coordinates (not pixels).
pub fn compute_sqpnp_poses(
    correspondences: &[CameraToSceneCorrespondence<f64>],
) -> Result<Vec<CameraPose>, PnPError> {
    validate_correspondences(correspondences)?;
    if correspondences.len() < 3 {
        return Err(PnPError::InsufficientPoints {
            min_points: 3,
            actual_points: correspondences.len(),
        });
    }

    // SQPnP uses CV convention (+Z forward), so convert 3D points from Maya to CV.
    // TODO: Avoid this conversion step.
    let mut points_3d = Vec::new();
    let mut projections_2d = Vec::new();

    for corr in correspondences {
        let maya_point = na::Point3::new(
            corr.scene_point.coords.x.value(),
            corr.scene_point.coords.y.value(),
            corr.scene_point.coords.z.value(),
        );
        let cv_point = convert_maya_to_cv_point3(maya_point);
        let pt_3d = Point::new(cv_point.x, cv_point.y, cv_point.z);
        points_3d.push(pt_3d);

        let pt_2d = Projection::new(
            corr.camera_point.coords.x.value(),
            corr.camera_point.coords.y.value(),
        );
        projections_2d.push(pt_2d);
    }

    let mut solver = PnPSolver::new(&points_3d, &projections_2d, None, None)
        .map_err(|e| match e {
            SqpnpError::InvalidInput => PnPError::InsufficientPoints {
                min_points: 3,
                actual_points: correspondences.len(),
            },
            SqpnpError::InvalidNullSpace => PnPError::SingularConfiguration,
            SqpnpError::WeightsLengthMismatch => {
                PnPError::SingularConfiguration
            }
            SqpnpError::NumericalError => PnPError::SingularConfiguration,
        })?;

    let solutions = solver.solve().map_err(|_| PnPError::NoSolution)?;

    if solutions.is_empty() {
        return Err(PnPError::NoSolution);
    }

    // Convert from CV coordinates back to Maya coordinates.
    let mut poses = Vec::new();
    for solution in &solutions {
        let cv_rotation = solution.rotation_matrix();
        let cv_translation = solution.translation();

        let maya_rotation = convert_cv_to_maya_rotation(cv_rotation);
        let maya_translation = convert_cv_to_maya_translation(*cv_translation);

        // SQPnP gives P_camera = R * P_world + t.
        // CameraPose stores the camera center: center = -R^T * t.
        let center = -maya_rotation.transpose() * maya_translation;

        poses.push(CameraPose::new(maya_rotation, center.into()));
    }

    Ok(poses)
}
