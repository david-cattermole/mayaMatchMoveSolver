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

use super::types::{MultivariatePolynomial, PolynomialMatrix3x3};

/// Compute the determinant of a polynomial 3x3 matrix
pub fn polynomial_matrix_determinant(
    mat: &PolynomialMatrix3x3,
) -> MultivariatePolynomial {
    // Use expansion by minors.
    // det = e00 * (e11*e22 - e12*e21) - e01 * (e10*e22 - e12*e20) + e02 * (e10*e21 - e11*e20)

    let mut det = MultivariatePolynomial::new(3);

    // First compute the 2x2 minors.
    let minor00 = multiply_polys(&mat.elements[1][1], &mat.elements[2][2]);
    let temp = multiply_polys(&mat.elements[1][2], &mat.elements[2][1]);
    let minor00 = subtract_polys(&minor00, &temp);

    let minor01 = multiply_polys(&mat.elements[1][0], &mat.elements[2][2]);
    let temp = multiply_polys(&mat.elements[1][2], &mat.elements[2][0]);
    let minor01 = subtract_polys(&minor01, &temp);

    let minor02 = multiply_polys(&mat.elements[1][0], &mat.elements[2][1]);
    let temp = multiply_polys(&mat.elements[1][1], &mat.elements[2][0]);
    let minor02 = subtract_polys(&minor02, &temp);

    // Now multiply by the first row and combine.
    let term1 = multiply_polys(&mat.elements[0][0], &minor00);
    let term2 = multiply_polys(&mat.elements[0][1], &minor01);
    let term3 = multiply_polys(&mat.elements[0][2], &minor02);

    det = add_polys(&det, &term1);
    det = subtract_polys(&det, &term2);
    det = add_polys(&det, &term3);

    det
}

/// Multiply two multivariate polynomials
pub fn multiply_polys(
    p1: &MultivariatePolynomial,
    p2: &MultivariatePolynomial,
) -> MultivariatePolynomial {
    let max_degree = 6; // Conservative upper bound.
    let mut result = MultivariatePolynomial::new(max_degree);

    for w1 in 0..p1.coefficients.len() {
        for x1 in 0..p1.coefficients[w1].len() {
            for y1 in 0..p1.coefficients[w1][x1].len() {
                for z1 in 0..p1.coefficients[w1][x1][y1].len() {
                    let coeff1 = p1.get(w1, x1, y1, z1);
                    if coeff1.abs() < 1e-10 {
                        continue;
                    }

                    for w2 in 0..p2.coefficients.len() {
                        for x2 in 0..p2.coefficients[w2].len() {
                            for y2 in 0..p2.coefficients[w2][x2].len() {
                                for z2 in 0..p2.coefficients[w2][x2][y2].len() {
                                    let coeff2 = p2.get(w2, x2, y2, z2);
                                    if coeff2.abs() < 1e-10 {
                                        continue;
                                    }

                                    let w = w1 + w2;
                                    let x = x1 + x2;
                                    let y = y1 + y2;
                                    let z = z1 + z2;

                                    if w <= max_degree
                                        && x <= max_degree
                                        && y <= max_degree
                                        && z <= max_degree
                                    {
                                        result.set(
                                            w,
                                            x,
                                            y,
                                            z,
                                            result.get(w, x, y, z)
                                                + coeff1 * coeff2,
                                        );
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    result
}

/// Add two multivariate polynomials.
pub fn add_polys(
    p1: &MultivariatePolynomial,
    p2: &MultivariatePolynomial,
) -> MultivariatePolynomial {
    let max_len = p1.coefficients.len().max(p2.coefficients.len());
    let mut result = MultivariatePolynomial::new(max_len - 1);

    for w in 0..max_len {
        for x in 0..max_len {
            for y in 0..max_len {
                for z in 0..max_len {
                    let val = p1.get(w, x, y, z) + p2.get(w, x, y, z);
                    result.set(w, x, y, z, val);
                }
            }
        }
    }

    result
}

/// Subtract two multivariate polynomials.
pub fn subtract_polys(
    p1: &MultivariatePolynomial,
    p2: &MultivariatePolynomial,
) -> MultivariatePolynomial {
    let max_len = p1.coefficients.len().max(p2.coefficients.len());
    let mut result = MultivariatePolynomial::new(max_len - 1);

    for w in 0..max_len {
        for x in 0..max_len {
            for y in 0..max_len {
                for z in 0..max_len {
                    let val = p1.get(w, x, y, z) - p2.get(w, x, y, z);
                    result.set(w, x, y, z, val);
                }
            }
        }
    }

    result
}
