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
// Essential matrix estimation from 5 normalized bearing vector correspondences.
//
// This implementation follows the algorithm described in:
// - Nister, D. (2004). "An efficient solution to the five-point relative pose problem"
//   IEEE Transactions on Pattern Analysis and Machine Intelligence, 26(6), 756-770.
// - Stewenius, H., Engels, C., & Nister, D. (2006). "Recent developments on direct
//   relative orientation" ISPRS Journal of Photogrammetry and Remote Sensing, 60(4), 284-294.
//
// The algorithm uses Grobner basis techniques to solve the minimal 5-point relative
// pose problem, which can return up to 10 essential matrix solutions.
//

use nalgebra::{Matrix3, Vector3};

use super::sturm::SMALL_ENOUGH;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// The essential matrix encodes the geometric relationship between two camera views.
#[derive(Debug, Clone)]
pub struct EssentialMatrix {
    pub matrix: Matrix3<f64>,
}

// TODO: This type should be renamed because it conflicts with the
// existing CameraPose type.
#[derive(Debug, Clone)]
pub struct CameraPose {
    pub rotation: Matrix3<f64>,
    pub translation: Vector3<f64>,
}

/// Polynomial with coefficients stored lowest-degree first.
#[derive(Debug, Clone)]
pub struct Polynomial {
    pub coefficients: Vec<f64>,
}

impl Polynomial {
    pub fn new(coefficients: Vec<f64>) -> Self {
        Polynomial { coefficients }.trim_trailing_zeros()
    }

    fn trim_trailing_zeros(mut self) -> Self {
        while self.coefficients.len() > 1
            && self.coefficients.last().unwrap().abs() < SMALL_ENOUGH
        {
            self.coefficients.pop();
        }
        self
    }

    pub fn degree(&self) -> usize {
        self.coefficients.len().saturating_sub(1)
    }

    pub fn eval(&self, x: f64) -> f64 {
        let mut result = 0.0;
        for &coeff in self.coefficients.iter().rev() {
            result = result * x + coeff;
        }
        result
    }

    pub fn derivative(&self) -> Polynomial {
        if self.degree() == 0 {
            mm_debug_eprintln!(
                "DEBUG_POLY: Derivative of constant/zero polynomial: {:?}",
                self.coefficients
            );
            return Polynomial::new(vec![0.0]);
        }

        let mut deriv_coeffs = Vec::with_capacity(self.coefficients.len() - 1);
        for i in 1..self.coefficients.len() {
            deriv_coeffs.push(self.coefficients[i] * i as f64);
        }
        let derivative = Polynomial::new(deriv_coeffs);
        mm_debug_eprintln!(
            "DEBUG_POLY: Original: {:?}, Derivative: {:?}",
            self.coefficients,
            derivative.coefficients
        );
        derivative
    }

    pub fn leading_coefficient(&self) -> f64 {
        *self.coefficients.last().unwrap_or(&0.0)
    }

    /// Normalize polynomial so leading coefficient is 1.
    pub fn normalize(&self) -> Polynomial {
        let lead = self.leading_coefficient();
        if lead.abs() < f64::EPSILON {
            return self.clone();
        }

        let coeffs: Vec<f64> =
            self.coefficients.iter().map(|&c| c / lead).collect();
        Polynomial::new(coeffs)
    }

    /// Evaluate the polynomial using forward coefficient iteration.
    pub fn eval_forward(&self, x: f64) -> f64 {
        let mut result = 0.0;
        for &coeff in self.coefficients.iter() {
            result = result * x + coeff;
        }
        result
    }

    /// Evaluate the polynomial with an inverted variable for numerical stability.
    pub fn eval_inverted(&self, x: f64) -> f64 {
        let mut result = self.coefficients[0];
        for &coeff in &self.coefficients[1..] {
            result = result * x + coeff;
        }
        result
    }
}

/// A polynomial in multiple variables (w, x, y, z).
#[derive(Debug, Clone)]
pub struct MultivariatePolynomial {
    /// Coefficients indexed by powers of (w, x, y, z).
    pub coefficients: Vec<Vec<Vec<Vec<f64>>>>,
}

impl MultivariatePolynomial {
    pub fn new(max_degree: usize) -> Self {
        let size = max_degree + 1;
        let coefficients = vec![vec![vec![vec![0.0; size]; size]; size]; size];
        MultivariatePolynomial { coefficients }
    }

    pub fn get(&self, w: usize, x: usize, y: usize, z: usize) -> f64 {
        if w < self.coefficients.len()
            && x < self.coefficients[w].len()
            && y < self.coefficients[w][x].len()
            && z < self.coefficients[w][x][y].len()
        {
            self.coefficients[w][x][y][z]
        } else {
            0.0
        }
    }

    pub fn set(&mut self, w: usize, x: usize, y: usize, z: usize, value: f64) {
        if w < self.coefficients.len()
            && x < self.coefficients[w].len()
            && y < self.coefficients[w][x].len()
            && z < self.coefficients[w][x][y].len()
        {
            self.coefficients[w][x][y][z] = value;
        }
    }
}

/// A 3x3 matrix of multivariate polynomials.
#[derive(Debug, Clone)]
pub struct PolynomialMatrix3x3 {
    pub elements: [[MultivariatePolynomial; 3]; 3],
}

impl PolynomialMatrix3x3 {
    pub fn new(max_degree: usize) -> Self {
        let elements = core::array::from_fn(|_| {
            core::array::from_fn(|_| MultivariatePolynomial::new(max_degree))
        });
        PolynomialMatrix3x3 { elements }
    }
}
