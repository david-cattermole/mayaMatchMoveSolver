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

use std::convert::TryInto;

use anyhow::{anyhow, Result};
use nalgebra::{DMatrix, Matrix3, Vector3};

use super::{
    polynomial::*,
    sturm::find_real_roots_sturm,
    types::{
        CameraPose, EssentialMatrix, MultivariatePolynomial, Polynomial,
        PolynomialMatrix3x3,
    },
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Linear polynomial in 4 variables: `c[0]*w + c[1]*x + c[2]*y + c[3]`.
#[derive(Clone, Debug, Copy)]
struct Polynomial4Degree1 {
    coeffs: [f64; 4],
}

impl Polynomial4Degree1 {
    fn new(w: f64, x: f64, y: f64, z: f64) -> Self {
        Polynomial4Degree1 {
            coeffs: [w, x, y, z],
        }
    }

    fn zero() -> Self {
        Polynomial4Degree1 {
            coeffs: [0.0, 0.0, 0.0, 0.0],
        }
    }

    /// Evaluate the polynomial at (w, x, y) with z implicitly 1.
    fn eval(&self, w: f64, x: f64, y: f64) -> f64 {
        self.coeffs[0] * w
            + self.coeffs[1] * x
            + self.coeffs[2] * y
            + self.coeffs[3]
    }

    fn get(&self, var_idx: usize) -> f64 {
        self.coeffs[var_idx]
    }
}

/// A 3x3 matrix of linear polynomials spanning the essential matrix nullspace.
type EssentialMatrixSet = [[Polynomial4Degree1; 3]; 3];

/// Estimate camera pose from exactly 5 normalised 2D point correspondences.
///
/// Returns up to 10 candidate camera poses (rotation and translation from camera 1 to camera 2).
pub fn five_point_relative_pose(
    points1: &[[f64; 2]; 5],
    points2: &[[f64; 2]; 5],
) -> Result<Vec<CameraPose>> {
    let mut q1 = Vec::new();
    let mut q2 = Vec::new();

    for i in 0..5 {
        q1.push([points1[i][0], points1[i][1], 1.0]);
        q2.push([points2[i][0], points2[i][1], 1.0]);
    }

    let q1_array: &[[f64; 3]; 5] = q1
        .as_slice()
        .try_into()
        .map_err(|_| anyhow!("Expected exactly 5 points in q1"))?;
    let q2_array: &[[f64; 3]; 5] = q2
        .as_slice()
        .try_into()
        .map_err(|_| anyhow!("Expected exactly 5 points in q2"))?;
    let constraint_matrix = build_constraint_matrix(q1_array, q2_array);

    let e_set = null_space_solve_gaussian(&constraint_matrix)?;
    mm_eprintln_debug!("DEBUG: Gaussian elimination succeeded, E-set created");
    mm_eprintln_debug!("DEBUG: E[0][0] = {:?}", e_set[0][0]);
    mm_eprintln_debug!("DEBUG: E[0][1] = {:?}", e_set[0][1]);
    mm_eprintln_debug!("DEBUG: E[1][1] = {:?}", e_set[1][1]);

    let essential_matrices = solve_polynomial_constraints(&e_set);
    mm_eprintln_debug!(
        "DEBUG: Polynomial solving found {} essential matrices",
        essential_matrices.len()
    );

    let mut poses = Vec::new();
    for e_mat in essential_matrices {
        let mut valid_poses = extract_pose_from_essential(&e_mat, &q1, &q2)?;
        poses.append(&mut valid_poses);
    }

    Ok(poses)
}

/// Estimate camera pose from 5 or more normalised point correspondences.
///
/// Uses SVD to find the nullspace for the overdetermined case.
pub fn five_point_relative_pose_overdetermined(
    points1: &[(f64, f64)],
    points2: &[(f64, f64)],
) -> Result<Vec<CameraPose>> {
    if points1.len() != points2.len() {
        return Err(anyhow!("Point arrays must have the same length"));
    }

    if points1.len() < 5 {
        return Err(anyhow!("Need at least 5 points"));
    }

    let mut q1 = Vec::new();
    let mut q2 = Vec::new();
    for i in 0..points1.len() {
        q1.push([points1[i].0, points1[i].1, 1.0]);
        q2.push([points2[i].0, points2[i].1, 1.0]);
    }

    let constraint_matrix = build_constraint_matrix_overdetermined(&q1, &q2);

    let svd = constraint_matrix.svd(true, true);
    let vt = svd
        .v_t
        .as_ref()
        .ok_or(anyhow!("SVD failed to compute V^T"))?;

    // The last 4 right singular vectors span the 4D nullspace.
    let n = vt.nrows();
    let mut nullspace_basis = DMatrix::zeros(4, 9);
    for i in 0..4 {
        for j in 0..9 {
            nullspace_basis[(i, j)] = vt[(n - 4 + i, j)];
        }
    }

    let e_set =
        convert_nullspace_basis_to_essential_matrix_set(&nullspace_basis)?;

    let essential_matrices = solve_polynomial_constraints(&e_set);

    let mut poses = Vec::new();
    for e_mat in essential_matrices {
        let mut valid_poses = extract_pose_from_essential(&e_mat, &q1, &q2)?;
        poses.append(&mut valid_poses);
    }

    Ok(poses)
}

/// Build the epipolar constraint matrix from point correspondences.
fn build_constraint_matrix(
    q1: &[[f64; 3]; 5],
    q2: &[[f64; 3]; 5],
) -> DMatrix<f64> {
    let mut matrix = DMatrix::zeros(5, 9);

    for i in 0..5 {
        let x1 = q1[i][0];
        let y1 = q1[i][1];
        let z1 = q1[i][2];

        let x2 = q2[i][0];
        let y2 = q2[i][1];
        let z2 = q2[i][2];

        matrix[(i, 0)] = x2 * x1;
        matrix[(i, 1)] = x2 * y1;
        matrix[(i, 2)] = x2 * z1;
        matrix[(i, 3)] = y2 * x1;
        matrix[(i, 4)] = y2 * y1;
        matrix[(i, 5)] = y2 * z1;
        matrix[(i, 6)] = z2 * x1;
        matrix[(i, 7)] = z2 * y1;
        matrix[(i, 8)] = z2 * z1;
    }

    matrix
}

/// Build the epipolar constraint matrix for more than 5 points.
fn build_constraint_matrix_overdetermined(
    q1: &[[f64; 3]],
    q2: &[[f64; 3]],
) -> DMatrix<f64> {
    let n = q1.len();
    let mut matrix = DMatrix::zeros(n, 9);

    for i in 0..n {
        let x1 = q1[i][0];
        let y1 = q1[i][1];
        let z1 = q1[i][2];

        let x2 = q2[i][0];
        let y2 = q2[i][1];
        let z2 = q2[i][2];

        matrix[(i, 0)] = x2 * x1;
        matrix[(i, 1)] = x2 * y1;
        matrix[(i, 2)] = x2 * z1;
        matrix[(i, 3)] = y2 * x1;
        matrix[(i, 4)] = y2 * y1;
        matrix[(i, 5)] = y2 * z1;
        matrix[(i, 6)] = z2 * x1;
        matrix[(i, 7)] = z2 * y1;
        matrix[(i, 8)] = z2 * z1;
    }

    matrix
}

/// Extract the 4D nullspace using Gaussian elimination.
///
/// Produces the basis structure required by the polynomial solver,
/// where the first four elements are pure variables (w, x, y, z).
fn null_space_solve_gaussian(
    matrix: &DMatrix<f64>,
) -> Result<EssentialMatrixSet> {
    let mut a = [[0.0; 9]; 9];
    for i in 0..5 {
        for j in 0..9 {
            a[i][j] = matrix[(i, j)];
        }
    }

    const LASTROW: usize = 4;
    const FIRSTCOL: usize = 4;
    const LASTCOL: usize = 8;

    for col in (FIRSTCOL + 1..=LASTCOL).rev() {
        let row = col - FIRSTCOL;
        let pivot = a[row][col];

        if pivot.abs() < 1e-12 {
            return Err(anyhow!(
                "Singular matrix in nullspace solve: pivot too small"
            ));
        }

        for i in 0..row {
            let fac = a[i][col] / pivot;
            for j in 0..col {
                a[i][j] -= fac * a[row][j];
            }
        }
    }

    for col in FIRSTCOL..LASTCOL {
        let row = col - FIRSTCOL;
        let pivot = a[row][col];

        if pivot.abs() < 1e-12 {
            return Err(anyhow!(
                "Singular matrix in nullspace solve: pivot too small"
            ));
        }

        for i in (row + 1)..=LASTROW {
            let fac = a[i][col] / pivot;
            for j in 0..FIRSTCOL {
                a[i][j] -= fac * a[row][j];
            }
        }
    }

    let mut e = [[Polynomial4Degree1::zero(); 3]; 3];

    // First four elements are the pure nullspace variables w, x, y, z.
    e[0][0] = Polynomial4Degree1::new(1.0, 0.0, 0.0, 0.0); // w
    e[0][1] = Polynomial4Degree1::new(0.0, 1.0, 0.0, 0.0); // x
    e[0][2] = Polynomial4Degree1::new(0.0, 0.0, 1.0, 0.0); // y
    e[1][0] = Polynomial4Degree1::new(0.0, 0.0, 0.0, 1.0); // z

    // Remaining elements are linear combinations from the elimination result.
    let fac = -1.0 / a[0][4];
    e[1][1] = Polynomial4Degree1::new(
        fac * a[0][0],
        fac * a[0][1],
        fac * a[0][2],
        fac * a[0][3],
    );

    let fac = -1.0 / a[1][5];
    e[1][2] = Polynomial4Degree1::new(
        fac * a[1][0],
        fac * a[1][1],
        fac * a[1][2],
        fac * a[1][3],
    );

    let fac = -1.0 / a[2][6];
    e[2][0] = Polynomial4Degree1::new(
        fac * a[2][0],
        fac * a[2][1],
        fac * a[2][2],
        fac * a[2][3],
    );

    let fac = -1.0 / a[3][7];
    e[2][1] = Polynomial4Degree1::new(
        fac * a[3][0],
        fac * a[3][1],
        fac * a[3][2],
        fac * a[3][3],
    );

    let fac = -1.0 / a[4][8];
    e[2][2] = Polynomial4Degree1::new(
        fac * a[4][0],
        fac * a[4][1],
        fac * a[4][2],
        fac * a[4][3],
    );

    Ok(e)
}

/// Convert a 4D SVD nullspace basis into an `EssentialMatrixSet`.
///
/// Finds a linear combination of the 4 basis vectors such that
/// `E[0,0]=w, E[0,1]=x, E[0,2]=y, E[1,0]=z` (pure variables).
fn convert_nullspace_basis_to_essential_matrix_set(
    nullspace_basis: &DMatrix<f64>,
) -> Result<EssentialMatrixSet> {
    // Build a 4x4 system from positions 0,1,2,3 (corresponding to E[0,0..3]) and invert it.
    let mut a = [[0.0; 4]; 4];
    for i in 0..4 {
        for j in 0..4 {
            a[i][j] = nullspace_basis[(j, i)];
        }
    }

    let det = matrix_4x4_determinant(&a);
    if det.abs() < 1e-10 {
        return Err(anyhow!("Singular matrix in nullspace conversion"));
    }

    let inv = matrix_4x4_inverse(&a)?;

    let mut e = [[Polynomial4Degree1::zero(); 3]; 3];

    for row in 0..3 {
        for col in 0..3 {
            let idx = row * 3 + col;
            let mut coeffs = [0.0; 4];

            for i in 0..4 {
                for j in 0..4 {
                    coeffs[i] += inv[i][j] * nullspace_basis[(j, idx)];
                }
            }

            e[row][col] = Polynomial4Degree1::new(
                coeffs[0], coeffs[1], coeffs[2], coeffs[3],
            );
        }
    }

    Ok(e)
}

fn matrix_4x4_determinant(m: &[[f64; 4]; 4]) -> f64 {
    m[0][0]
        * (m[1][1] * (m[2][2] * m[3][3] - m[2][3] * m[3][2])
            - m[1][2] * (m[2][1] * m[3][3] - m[2][3] * m[3][1])
            + m[1][3] * (m[2][1] * m[3][2] - m[2][2] * m[3][1]))
        - m[0][1]
            * (m[1][0] * (m[2][2] * m[3][3] - m[2][3] * m[3][2])
                - m[1][2] * (m[2][0] * m[3][3] - m[2][3] * m[3][0])
                + m[1][3] * (m[2][0] * m[3][2] - m[2][2] * m[3][0]))
        + m[0][2]
            * (m[1][0] * (m[2][1] * m[3][3] - m[2][3] * m[3][1])
                - m[1][1] * (m[2][0] * m[3][3] - m[2][3] * m[3][0])
                + m[1][3] * (m[2][0] * m[3][1] - m[2][1] * m[3][0]))
        - m[0][3]
            * (m[1][0] * (m[2][1] * m[3][2] - m[2][2] * m[3][1])
                - m[1][1] * (m[2][0] * m[3][2] - m[2][2] * m[3][0])
                + m[1][2] * (m[2][0] * m[3][1] - m[2][1] * m[3][0]))
}

fn matrix_4x4_inverse(m: &[[f64; 4]; 4]) -> Result<[[f64; 4]; 4]> {
    let det = matrix_4x4_determinant(m);
    if det.abs() < 1e-10 {
        return Err(anyhow!("Cannot invert singular 4x4 matrix"));
    }

    let inv_det = 1.0 / det;
    let mut inv = [[0.0; 4]; 4];

    for i in 0..4 {
        for j in 0..4 {
            let mut sub = [[0.0; 3]; 3];
            let mut sub_i = 0;
            for si in 0..4 {
                if si == i {
                    continue;
                }
                let mut sub_j = 0;
                for sj in 0..4 {
                    if sj == j {
                        continue;
                    }
                    sub[sub_i][sub_j] = m[si][sj];
                    sub_j += 1;
                }
                sub_i += 1;
            }
            let cofactor = matrix_3x3_determinant(&sub);
            let sign = if (i + j) % 2 == 0 { 1.0 } else { -1.0 };
            inv[j][i] = sign * cofactor * inv_det; // Transposed
        }
    }

    Ok(inv)
}

fn matrix_3x3_determinant(m: &[[f64; 3]; 3]) -> f64 {
    m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
}

/// Extract monomial coefficients from a cubic polynomial into the equation set.
fn mono_coeff(
    poly: &MultivariatePolynomial,
    equations: &mut EquationSet,
    n: usize,
) {
    // Indices for degrees.
    #[allow(dead_code)]
    const W0: usize = 0;
    #[allow(dead_code)]
    const W1: usize = 1;
    #[allow(dead_code)]
    const W2: usize = 2;
    #[allow(dead_code)]
    const W3: usize = 3;

    // Linear variables (indices in Polynomial4Degree1).
    #[allow(dead_code)]
    const W: usize = 0;
    #[allow(dead_code)]
    const X: usize = 1;
    #[allow(dead_code)]
    const Y: usize = 2;
    #[allow(dead_code)]
    const Z: usize = 3;

    // Monomials indices.
    #[allow(dead_code)]
    const XX: usize = 3;
    #[allow(dead_code)]
    const XY: usize = 4;
    #[allow(dead_code)]
    const YY: usize = 5;
    #[allow(dead_code)]
    const XXX: usize = 6;
    #[allow(dead_code)]
    const XXY: usize = 7;
    #[allow(dead_code)]
    const XYY: usize = 8;
    #[allow(dead_code)]
    const YYY: usize = 9;

    // Terms in w^0.
    equations[W0][n][0] = poly.get(0, 0, 0, 3); // z^3
    equations[W0][n][X] = poly.get(0, 1, 0, 2); // x*z^2
    equations[W0][n][Y] = poly.get(0, 0, 1, 2); // y*z^2
    equations[W0][n][XX] = poly.get(0, 2, 0, 1); // x^2*z
    equations[W0][n][YY] = poly.get(0, 0, 2, 1); // y^2*z
    equations[W0][n][XY] = poly.get(0, 1, 1, 1); // x*y*z
    equations[W0][n][XXX] = poly.get(0, 3, 0, 0); // x^3
    equations[W0][n][XXY] = poly.get(0, 2, 1, 0); // x^2*y
    equations[W0][n][XYY] = poly.get(0, 1, 2, 0); // x*y^2
    equations[W0][n][YYY] = poly.get(0, 0, 3, 0); // y^3

    // Terms in w^1
    equations[W1][n][0] = poly.get(1, 0, 0, 2); // w*z^2
    equations[W1][n][X] = poly.get(1, 1, 0, 1); // w*x*z
    equations[W1][n][Y] = poly.get(1, 0, 1, 1); // w*y*z
    equations[W1][n][XX] = poly.get(1, 2, 0, 0); // w*x^2
    equations[W1][n][YY] = poly.get(1, 0, 2, 0); // w*y^2
    equations[W1][n][XY] = poly.get(1, 1, 1, 0); // w*x*y

    // Terms in w^2
    equations[W2][n][0] = poly.get(2, 0, 0, 1); // w^2*z
    equations[W2][n][X] = poly.get(2, 1, 0, 0); // w^2*x
    equations[W2][n][Y] = poly.get(2, 0, 1, 0); // w^2*y

    // Terms in w^3
    equations[W3][n][0] = poly.get(3, 0, 0, 0); // w^3
}

/// Solve the polynomial constraints to find candidate essential matrices.
fn solve_polynomial_constraints(
    e_set: &EssentialMatrixSet,
) -> Vec<EssentialMatrix> {
    let e_poly = build_polynomial_essential_from_essential_matrix_set(e_set);
    mm_eprintln_debug!("DEBUG: Built polynomial essential matrix");

    let mut equations = apply_essential_constraints(&e_poly);
    mm_eprintln_debug!("DEBUG: Applied essential constraints");

    reduce_equation_system(&mut equations);
    mm_eprintln_debug!("DEBUG: Reduced equation system");

    let degree10_poly = extract_determinant_polynomial(&equations);
    mm_eprintln_debug!("DEBUG: Extracted determinant polynomial");

    let roots = find_real_roots_sturm(&degree10_poly, false);
    mm_eprintln_debug!("DEBUG: Polynomial coefficients: {:?}", degree10_poly);
    mm_eprintln_debug!("DEBUG: Found {} real roots", roots.len());

    let mut essential_matrices = Vec::new();

    for &w_root in &roots {
        mm_eprintln_debug!(
            "DEBUG: Trying to recover E matrix for w={}",
            w_root
        );
        if let Ok(e_mat) =
            recover_essential_matrix_from_ematrix_set(w_root, &equations, e_set)
        {
            mm_eprintln_debug!("DEBUG: Successfully recovered E matrix");
            essential_matrices.push(e_mat);
        } else if DEBUG {
            eprintln!("DEBUG: Failed to recover E matrix for w={}", w_root);
        }
    }

    mm_eprintln_debug!(
        "DEBUG: Total essential matrices recovered: {}",
        essential_matrices.len()
    );
    essential_matrices
}

/// Convert an `EssentialMatrixSet` to a polynomial 3x3 matrix representation.
fn build_polynomial_essential_from_essential_matrix_set(
    e_set: &EssentialMatrixSet,
) -> PolynomialMatrix3x3 {
    let mut e_poly = PolynomialMatrix3x3::new(3);

    for i in 0..3 {
        for j in 0..3 {
            let p = &e_set[i][j];

            mm_eprintln_debug!(
                "DEBUG: E[{}][{}] = Polynomial4Degree1({}, {}, {}, {})",
                i,
                j,
                p.get(0),
                p.get(1),
                p.get(2),
                p.get(3)
            );

            e_poly.elements[i][j].set(1, 0, 0, 0, p.get(0)); // w term
            e_poly.elements[i][j].set(0, 1, 0, 0, p.get(1)); // x term
            e_poly.elements[i][j].set(0, 0, 1, 0, p.get(2)); // y term
            e_poly.elements[i][j].set(0, 0, 0, 1, p.get(3)); // z term

            mm_eprintln_debug!(
                "DEBUG: After set, E_poly[{}][{}]: w={}, x={}, y={}, z={}",
                i,
                j,
                e_poly.elements[i][j].get(1, 0, 0, 0),
                e_poly.elements[i][j].get(0, 1, 0, 0),
                e_poly.elements[i][j].get(0, 0, 1, 0),
                e_poly.elements[i][j].get(0, 0, 0, 1)
            );
        }
    }

    e_poly
}

/// Build the polynomial equation set from essential matrix constraints.
///
/// Applies `det(E) = 0` and `2*E*E^T*E - tr(E*E^T)*E = 0`.
fn apply_essential_constraints(e_poly: &PolynomialMatrix3x3) -> EquationSet {
    let mut equations = create_equation_set();

    let trace = compute_trace_eet(e_poly);

    let det_poly = polynomial_matrix_determinant(e_poly);
    mono_coeff(&det_poly, &mut equations, 0);

    let mut eqn = 1;
    for i in 0..3 {
        let mut eee_i = [
            MultivariatePolynomial::new(3),
            MultivariatePolynomial::new(3),
            MultivariatePolynomial::new(3),
        ];

        for q in 0..3 {
            let mut ee_iq = MultivariatePolynomial::new(2);
            for p in 0..3 {
                let prod = multiply_polys(
                    &e_poly.elements[i][p],
                    &e_poly.elements[q][p],
                );
                ee_iq = add_polys(&ee_iq, &prod);
            }

            for j in 0..3 {
                let term = multiply_polys(&ee_iq, &e_poly.elements[q][j]);
                eee_i[j] = add_polys(&eee_i[j], &term);
            }
        }

        for j in 0..3 {
            let mut constraint = scale_poly(&eee_i[j], 2.0);

            mm_eprintln_debug!(
                "DEBUG: Before subtract, 2*EEE[{}] has w^3 = {}",
                eqn,
                constraint.get(3, 0, 0, 0)
            );

            let trace_e = multiply_polys(&trace, &e_poly.elements[i][j]);

            mm_eprintln_debug!(
                "DEBUG: trace*E[{}][{}] has w^3 = {}",
                i,
                j,
                trace_e.get(3, 0, 0, 0)
            );

            constraint = subtract_polys(&constraint, &trace_e);

            mm_eprintln_debug!(
                "DEBUG: Final constraint equation {} has w^3 coefficient = {}",
                eqn,
                constraint.get(3, 0, 0, 0)
            );

            mono_coeff(&constraint, &mut equations, eqn);
            eqn += 1;
        }
    }

    equations
}

fn scale_poly(
    poly: &MultivariatePolynomial,
    factor: f64,
) -> MultivariatePolynomial {
    let mut result = poly.clone();
    for w in 0..result.coefficients.len() {
        for x in 0..result.coefficients[w].len() {
            for y in 0..result.coefficients[w][x].len() {
                for z in 0..result.coefficients[w][x][y].len() {
                    result.coefficients[w][x][y][z] *= factor;
                }
            }
        }
    }
    result
}

/// Compute `trace(E * E^T)` as a quadratic polynomial.
fn compute_trace_eet(e: &PolynomialMatrix3x3) -> MultivariatePolynomial {
    let mut trace = MultivariatePolynomial::new(2);

    for i in 0..3 {
        for j in 0..3 {
            let prod = multiply_polys(&e.elements[i][j], &e.elements[i][j]);
            trace = add_polys(&trace, &prod);
        }
    }

    let e00_squared = multiply_polys(&e.elements[0][0], &e.elements[0][0]);
    mm_eprintln_debug!(
        "DEBUG: E[0][0]*E[0][0] (w*w) = w^2 coefficient: {}",
        e00_squared.get(2, 0, 0, 0)
    );

    let e00_cubed = multiply_polys(&e00_squared, &e.elements[0][0]);
    mm_eprintln_debug!(
        "DEBUG: (w^2)*w = w^3 coefficient: {}",
        e00_cubed.get(3, 0, 0, 0)
    );

    mm_eprintln_debug!("DEBUG: trace(E*E^T) has w^2={}, w*x={}, w*y={}, w*z={}, x^2={}, y^2={}, z^2={}",
             trace.get(2, 0, 0, 0),
             trace.get(1, 1, 0, 0),
             trace.get(1, 0, 1, 0),
             trace.get(1, 0, 0, 1),
             trace.get(0, 2, 0, 0),
             trace.get(0, 0, 2, 0),
             trace.get(0, 0, 0, 2));

    trace
}

/// Equation system: `[degree][equation][coefficient]`.
type EquationSet = [[[f64; 10]; 10]; 5];

fn create_equation_set() -> EquationSet {
    [[[0.0; 10]; 10]; 5]
}

fn sweep_up(
    equations: &mut EquationSet,
    row: usize,
    col: usize,
    degree: usize,
) {
    const NUM1: usize = 6; // nonzero columns in degree 1
    const NUM2: usize = 3; // nonzero columns in degree 2
    const NUM3: usize = 1; // nonzero columns in degree 3

    let pivot = equations[degree][row][col];
    if pivot.abs() < 1e-10 {
        return;
    }

    for i in 0..row {
        let fac = equations[degree][i][col] / pivot;

        // Constant terms
        for j in 0..=col {
            equations[0][i][j] -= fac * equations[0][row][j];
        }

        // Degree 1 terms
        for j in 0..NUM1 {
            equations[1][i][j] -= fac * equations[1][row][j];
        }

        // Degree 2 terms
        for j in 0..NUM2 {
            equations[2][i][j] -= fac * equations[2][row][j];
        }

        // Degree 3 terms
        for j in 0..NUM3 {
            equations[3][i][j] -= fac * equations[3][row][j];
        }
    }
}

fn sweep_down(
    equations: &mut EquationSet,
    row: usize,
    col: usize,
    degree: usize,
    lastrow: usize,
) {
    const NUM1: usize = 6;
    const NUM2: usize = 3;
    const NUM3: usize = 1;

    let pivot = equations[degree][row][col];
    if pivot.abs() < 1e-10 {
        return;
    }

    for i in (row + 1)..=lastrow {
        let fac = equations[degree][i][col] / pivot;

        // Constant terms
        for j in 0..=col {
            equations[0][i][j] -= fac * equations[0][row][j];
        }

        // Degree 1 terms
        for j in 0..NUM1 {
            equations[1][i][j] -= fac * equations[1][row][j];
        }

        // Degree 2 terms
        for j in 0..NUM2 {
            equations[2][i][j] -= fac * equations[2][row][j];
        }

        // Degree 3 terms
        for j in 0..NUM3 {
            equations[3][i][j] -= fac * equations[3][row][j];
        }
    }
}

/// Improve pivot conditioning by adding the row with the largest column element.
fn pivot(equations: &mut EquationSet, col: usize, deg: usize, lastrow: usize) {
    const NUM1: usize = 6;
    const NUM2: usize = 3;
    const NUM3: usize = 1;

    let mut maxval = -1.0;
    let mut row = 0;
    for i in 0..=lastrow {
        if i != col && equations[deg][i][col].abs() > maxval {
            row = i;
            maxval = equations[deg][i][col].abs();
        }
    }

    if maxval < 1e-10 {
        return;
    }

    let fac = if equations[deg][row][col] * equations[deg][col][col] < 0.0 {
        -1.0
    } else {
        1.0
    };

    for j in 0..=col {
        equations[0][col][j] += fac * equations[0][row][j];
    }

    for j in 0..NUM1 {
        equations[1][col][j] += fac * equations[1][row][j];
    }

    for j in 0..NUM2 {
        equations[2][col][j] += fac * equations[2][row][j];
    }

    for j in 0..NUM3 {
        equations[3][col][j] += fac * equations[3][row][j];
    }
}

/// Reduce the 10x10 equation system to a 3x3 system via Gaussian elimination.
fn reduce_equation_system(equations: &mut EquationSet) {
    pivot(equations, 9, 0, 8);
    sweep_up(equations, 9, 9, 0);
    pivot(equations, 8, 0, 7);
    sweep_up(equations, 8, 8, 0);
    pivot(equations, 7, 0, 6);
    sweep_up(equations, 7, 7, 0);
    pivot(equations, 6, 0, 5);
    sweep_up(equations, 6, 6, 0);

    pivot(equations, 5, 0, 4);
    sweep_up(equations, 5, 5, 0);
    pivot(equations, 4, 0, 3);
    sweep_up(equations, 4, 4, 0);
    pivot(equations, 3, 0, 2);
    sweep_up(equations, 3, 3, 0);

    let lastrow = 5;
    sweep_down(equations, 3, 3, 0, lastrow);
    sweep_down(equations, 4, 4, 0, lastrow);

    sweep_up(equations, 2, 5, 1);
    sweep_up(equations, 1, 4, 1);

    sweep_down(equations, 0, 3, 1, lastrow);
    sweep_down(equations, 1, 4, 1, lastrow);
    sweep_down(equations, 2, 5, 1, lastrow);

    for i in 0..3 {
        let numerator = equations[1][i][3 + i];
        let denominator = equations[0][3 + i][3 + i];
        let fac = numerator / denominator;

        mm_eprintln_debug!(
            "DEBUG: i={}, numerator={}, denominator={}, fac={}",
            i,
            numerator,
            denominator,
            fac
        );
        mm_eprintln_debug!(
            "DEBUG: equations[3][{}][0] = {}",
            i + 3,
            equations[3][i + 3][0]
        );

        equations[4][i][0] = -equations[3][i + 3][0] * fac;
        mm_eprintln_debug!(
            "DEBUG: equations[4][{}][0] = {}",
            i,
            equations[4][i][0]
        );

        for j in 0..3 {
            equations[3][i][j] -= equations[2][i + 3][j] * fac;
            equations[2][i][j] -= equations[1][i + 3][j] * fac;
            equations[1][i][j] -= equations[0][i + 3][j] * fac;
        }
    }

    mm_eprintln_debug!(
        "DEBUG: After reduction, equations[4][0][0] = {}",
        equations[4][0][0]
    );
    mm_eprintln_debug!(
        "DEBUG: After reduction, equations[4][1][0] = {}",
        equations[4][1][0]
    );
    mm_eprintln_debug!(
        "DEBUG: After reduction, equations[4][2][0] = {}",
        equations[4][2][0]
    );
}

fn one_cofactor(
    equations: &EquationSet,
    poly: &mut [f64; 11],
    r0: usize,
    r1: usize,
    r2: usize,
) {
    let mut two = [0.0; 7];

    for i in 0..=3 {
        for j in 0..=3 {
            two[i + j] += equations[i][r1][1] * equations[j][r2][2]
                - equations[i][r2][1] * equations[j][r1][2];
        }
    }

    for i in 0..=6 {
        for j in 0..=4 {
            poly[i + j] += equations[j][r0][0] * two[i];
        }
    }
}

/// Extract the 10th-degree determinant polynomial from the reduced 3x3 system.
fn extract_determinant_polynomial(equations: &EquationSet) -> Polynomial {
    let mut poly = [0.0; 11];

    one_cofactor(equations, &mut poly, 0, 1, 2);
    one_cofactor(equations, &mut poly, 1, 2, 0);
    one_cofactor(equations, &mut poly, 2, 0, 1);

    Polynomial::new(poly.to_vec())
}

/// Solve for the null space of a 3x3 matrix, returning (x, y) such that `A * [x, y, 1]^T = 0`.
fn null_space_solve_3x3(a: &[[f64; 3]; 3]) -> Result<(f64, f64)> {
    let f0 = a[0][2].abs();
    let f1 = a[1][2].abs();
    let f2 = a[2][2].abs();

    let p1 = if f0 > f1 {
        if f0 > f2 {
            0
        } else {
            2
        }
    } else if f1 > f2 {
        1
    } else {
        2
    };

    let r1 = (p1 + 1) % 3;
    let r2 = (p1 + 2) % 3;

    let mut m = *a;

    let pivot1 = m[p1][2];
    if pivot1.abs() < 1e-10 {
        return Err(anyhow!("Singular matrix in null space solve"));
    }

    let fac1 = m[r1][2] / pivot1;
    m[r1][0] -= fac1 * m[p1][0];
    m[r1][1] -= fac1 * m[p1][1];

    let fac2 = m[r2][2] / pivot1;
    m[r2][0] -= fac2 * m[p1][0];
    m[r2][1] -= fac2 * m[p1][1];

    let p2 = if m[r1][1].abs() > m[r2][1].abs() {
        r1
    } else {
        r2
    };

    let pivot2 = m[p2][1];
    if pivot2.abs() < 1e-10 {
        return Err(anyhow!("Singular matrix in null space solve"));
    }

    let x = -m[p2][0] / pivot2;
    let y = -(m[p1][0] + m[p1][1] * x) / pivot1;

    Ok((x, y))
}

/// Recover an essential matrix from a single root value.
fn recover_essential_matrix_from_ematrix_set(
    w_root: f64,
    equations: &EquationSet,
    e_set: &EssentialMatrixSet,
) -> Result<EssentialMatrix> {
    let w2 = w_root * w_root;
    let w3 = w2 * w_root;
    let w4 = w3 * w_root;

    let mut m = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = equations[0][i][j]
                + w_root * equations[1][i][j]
                + w2 * equations[2][i][j]
                + w3 * equations[3][i][j];
        }
        // Only the first column has degree-4 terms.
        m[i][0] += w4 * equations[4][i][0];
    }

    let (x, y) = null_space_solve_3x3(&m)?;

    let mut e = Matrix3::zeros();
    for i in 0..3 {
        for j in 0..3 {
            e[(i, j)] = e_set[i][j].eval(w_root, x, y);
        }
    }

    Ok(EssentialMatrix { matrix: e })
}

/// Extract camera poses from an essential matrix using SVD decomposition.
fn extract_pose_from_essential(
    e_mat: &EssentialMatrix,
    q1: &[[f64; 3]],
    q2: &[[f64; 3]],
) -> Result<Vec<CameraPose>> {
    let e = &e_mat.matrix;

    let svd = e.svd(true, true);
    let u = svd.u.ok_or(anyhow!("SVD failed to compute U"))?;
    let vt = svd.v_t.ok_or(anyhow!("SVD failed to compute V^T"))?;

    let mut u_fixed = u;
    let mut vt_fixed = vt;

    if u_fixed.determinant() < 0.0 {
        u_fixed.column_mut(2).scale_mut(-1.0);
    }
    if vt_fixed.determinant() < 0.0 {
        vt_fixed.row_mut(2).scale_mut(-1.0);
    }

    let w = Matrix3::new(0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0);

    let r1 = u_fixed * w * vt_fixed;
    let r2 = u_fixed * w.transpose() * vt_fixed;
    let t = u_fixed.column(2).normalize();

    let solutions = vec![
        CameraPose {
            rotation: r1,
            translation: t,
        },
        CameraPose {
            rotation: r1,
            translation: -t,
        },
        CameraPose {
            rotation: r2,
            translation: t,
        },
        CameraPose {
            rotation: r2,
            translation: -t,
        },
    ];

    let mut valid_solutions = Vec::new();

    for solution in solutions {
        if check_cheirality(&solution, &q1[0], &q2[0]) {
            valid_solutions.push(solution);
        }
    }

    Ok(valid_solutions)
}

/// Returns true if the point is in front of both cameras (positive depth).
fn check_cheirality(pose: &CameraPose, q1: &[f64; 3], q2: &[f64; 3]) -> bool {
    let p1 = Vector3::new(q1[0], q1[1], q1[2]);
    let _p2 = Vector3::new(q2[0], q2[1], q2[2]);

    let r = &pose.rotation;
    let t = &pose.translation;

    let depth1 = p1[2];
    let p2_transformed = r * p1 + t;
    let depth2 = p2_transformed[2];

    depth1 > 0.0 && depth2 > 0.0
}
