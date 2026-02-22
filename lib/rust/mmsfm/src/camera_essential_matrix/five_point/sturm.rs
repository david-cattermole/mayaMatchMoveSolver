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

use super::types::Polynomial;

const CONVERGENCE_TOL: f64 = 1e-12;
const MAX_ITERATIONS: usize = 800;
pub const SMALL_ENOUGH: f64 = 1e-12;
const MAX_POWER: i32 = 32;

/// Sturm chain for polynomial root finding.
pub struct SturmChain {
    polynomials: Vec<Polynomial>,
}

impl SturmChain {
    /// Build a Sturm sequence for the given polynomial
    pub fn new(poly: &Polynomial) -> Self {
        let polynomials = build_sturm_chain(poly);
        SturmChain { polynomials }
    }

    /// Get access to the polynomials in the chain (for testing)
    pub fn polynomials(&self) -> &[Polynomial] {
        &self.polynomials
    }

    /// Count sign changes at a given point
    pub fn num_changes(&self, x: f64) -> usize {
        count_sign_changes(&self.polynomials, x)
    }

    /// Count roots in interval [a, b]
    pub fn num_roots(&self, a: f64, b: f64) -> usize {
        let changes_a = self.num_changes(a);
        let changes_b = self.num_changes(b);
        changes_a.saturating_sub(changes_b)
    }

    /// Count total number of real roots
    pub fn num_real_roots(&self, non_negative: bool) -> (usize, usize, usize) {
        count_real_roots(&self.polynomials, non_negative)
    }
}

/// Build a Sturm chain from a polynomial.
pub fn build_sturm_chain(poly: &Polynomial) -> Vec<Polynomial> {
    let mut chain = Vec::new();
    let mut poly_curr = poly.clone();
    let mut poly_next = poly.derivative();

    // Normalise the derivative by dividing by |leading_coeff * degree|.
    if poly_next.degree() > 0 {
        let f = poly.leading_coefficient().abs() * poly.degree() as f64;
        for coeff in poly_next.coefficients.iter_mut() {
            *coeff /= f;
        }
    }

    chain.push(poly_curr.clone());
    chain.push(poly_next.clone());

    while poly_next.degree() > 0 {
        let (_, mut remainder) = polynomial_division(&poly_curr, &poly_next);

        if remainder.degree() == 0
            && remainder.coefficients[0].abs() < SMALL_ENOUGH
        {
            break;
        }

        // Negate and normalise, but only when degree > 0.
        if remainder.degree() > 0 {
            let factor = -remainder.coefficients[remainder.degree()].abs();
            for coeff in remainder.coefficients.iter_mut() {
                *coeff /= factor;
            }
        }

        chain.push(remainder.clone());
        poly_curr = poly_next;
        poly_next = remainder;
    }

    if let Some(last) = chain.last_mut() {
        if last.coefficients.len() > 0 {
            last.coefficients[0] = -last.coefficients[0];
        }
    }

    chain
}

/// Count sign changes in a polynomial sequence at a given point.
pub fn count_sign_changes(polynomials: &[Polynomial], x: f64) -> usize {
    let mut changes = 0;
    let mut last_sign: Option<f64> = None;

    for poly in polynomials.iter() {
        let val = poly.eval(x);
        let current_sign = val.signum();

        if current_sign == 0.0 {
            continue; // Skip zero values
        }

        if let Some(ls) = last_sign {
            if ls * current_sign < 0.0 {
                changes += 1;
            }
        }
        last_sign = Some(current_sign);
    }
    changes
}

/// Count total number of real roots.
pub fn count_real_roots(
    polynomials: &[Polynomial],
    non_negative: bool,
) -> (usize, usize, usize) {
    let mut at_pos_inf = 0;
    let mut last_sign: Option<f64> = None;

    for poly in polynomials.iter() {
        let current_sign = if poly.leading_coefficient() < 0.0 {
            -1.0
        } else {
            1.0
        };
        if current_sign == 0.0 {
            continue; // Skip zero leading coefficients.
        }

        if let Some(ls) = last_sign {
            if ls * current_sign < 0.0 {
                at_pos_inf += 1;
            }
        }
        last_sign = Some(current_sign);
    }

    let at_neg_inf = if non_negative {
        count_sign_changes(polynomials, 0.0)
    } else {
        let mut changes = 0;
        let mut last_sign: Option<f64> = None;

        for poly in polynomials.iter() {
            let current_sign = if poly.degree() % 2 == 0 {
                if poly.leading_coefficient() < 0.0 {
                    -1.0
                } else {
                    1.0
                }
            } else if poly.leading_coefficient() < 0.0 {
                1.0
            } else {
                -1.0
            };

            if current_sign == 0.0 {
                continue; // Skip zero leading coefficients.
            }

            if let Some(ls) = last_sign {
                if ls * current_sign < 0.0 {
                    changes += 1;
                }
            }
            last_sign = Some(current_sign);
        }
        changes
    };

    (
        at_neg_inf.saturating_sub(at_pos_inf),
        at_neg_inf,
        at_pos_inf,
    )
}

/// Find a root in the interval [a, b] using a modified regula falsi method.
pub fn modrf(poly: &Polynomial, mut a: f64, mut b: f64) -> Option<f64> {
    if a > b {
        std::mem::swap(&mut a, &mut b);
    }

    if b <= 1.0 && a >= -1.0 {
        modrf_internal(poly, a, b, false)
    } else if a >= 1.0 || b <= -1.0 {
        modrf_internal(poly, a, b, true)
    } else {
        // Interval crosses +/-1: split at boundaries.
        let fm1 = poly.eval(-1.0);
        let f1 = poly.eval(1.0);
        let fa = poly.eval(a);
        let fb = poly.eval(b);

        if a < -1.0 && b > 1.0 {
            if fa * fm1 < 0.0 {
                modrf_internal(poly, a, -1.0, true)
            } else if fb * f1 < 0.0 {
                modrf_internal(poly, 1.0, b, true)
            } else {
                modrf_internal(poly, -1.0, 1.0, false)
            }
        } else if a < -1.0 {
            if fa * fm1 < 0.0 {
                modrf_internal(poly, a, -1.0, true)
            } else {
                modrf_internal(poly, -1.0, b, false)
            }
        } else {
            if fb * f1 < 0.0 {
                modrf_internal(poly, 1.0, b, true)
            } else {
                modrf_internal(poly, a, 1.0, false)
            }
        }
    }
}

fn modrf_internal(
    poly: &Polynomial,
    mut a: f64,
    mut b: f64,
    invert: bool,
) -> Option<f64> {
    if invert {
        let temp = a;
        a = 1.0 / b;
        b = 1.0 / temp;
    }

    let mut fa = if invert {
        poly.eval_forward(a)
    } else {
        poly.eval(a)
    };

    let mut fb = if invert {
        poly.eval_forward(b)
    } else {
        poly.eval(b)
    };

    if fa * fb > 0.0 {
        return None;
    }

    if fa.abs() < CONVERGENCE_TOL {
        return Some(if invert { 1.0 / a } else { a });
    }
    if fb.abs() < CONVERGENCE_TOL {
        return Some(if invert { 1.0 / b } else { b });
    }

    let mut last_fx = fa;

    for _its in 0..MAX_ITERATIONS {
        let x = (fb * a - fa * b) / (fb - fa);

        let fx = if invert {
            poly.eval_forward(x)
        } else {
            poly.eval(x)
        };

        if x.abs() > CONVERGENCE_TOL && (fx / x).abs() < CONVERGENCE_TOL {
            return Some(if invert { 1.0 / x } else { x });
        } else if fx.abs() < CONVERGENCE_TOL {
            return Some(if invert { 1.0 / x } else { x });
        }

        // Illinois algorithm: halve the opposite endpoint's value to prevent stagnation.
        if fa * fx < 0.0 {
            b = x;
            fb = fx;
            if last_fx * fx > 0.0 {
                fa /= 2.0;
            }
        } else {
            a = x;
            fa = fx;
            if last_fx * fx > 0.0 {
                fb /= 2.0;
            }
        }

        if (b - a).abs() < CONVERGENCE_TOL * a.abs() {
            return Some(if invert { 1.0 / a } else { a });
        }

        last_fx = fx;
    }

    Some(if invert {
        1.0 / ((a + b) / 2.0)
    } else {
        (a + b) / 2.0
    })
}

/// Isolate roots in [min, max] using Sturm sequences and bisection.
pub fn sturm_bisect(
    chain: &SturmChain,
    poly: &Polynomial,
    mut min: f64,
    mut max: f64,
    mut at_min: usize,
    mut at_max: usize,
) -> Vec<f64> {
    let n_roots = at_min.saturating_sub(at_max);

    if n_roots == 0 {
        return vec![];
    }

    if n_roots == 1 {
        if let Some(root) = modrf(poly, min, max) {
            return vec![root];
        }

        for _its in 0..MAX_ITERATIONS {
            let mid = (min + max) / 2.0;
            let at_mid = chain.num_changes(mid);

            if mid.abs() > CONVERGENCE_TOL {
                if ((max - min) / mid).abs() < CONVERGENCE_TOL {
                    return vec![mid];
                }
            } else if (max - min).abs() < CONVERGENCE_TOL {
                return vec![mid];
            }

            if at_min.saturating_sub(at_mid) == 0 {
                min = mid;
            } else {
                max = mid;
            }
        }

        return vec![(min + max) / 2.0];
    }

    for _its in 0..MAX_ITERATIONS {
        let mid = (min + max) / 2.0;
        let at_mid = chain.num_changes(mid);

        let n1 = at_min.saturating_sub(at_mid);
        let n2 = at_mid.saturating_sub(at_max);

        if n1 != 0 && n2 != 0 {
            let mut roots = sturm_bisect(chain, poly, min, mid, at_min, at_mid);
            let mut roots2 =
                sturm_bisect(chain, poly, mid, max, at_mid, at_max);
            roots.append(&mut roots2);
            return roots;
        }

        if n1 == 0 {
            min = mid;
            at_min = at_mid;
        } else {
            max = mid;
            at_max = at_mid;
        }
    }

    vec![(min + max) / 2.0; n_roots]
}

/// Find all real roots of a polynomial using Sturm sequences.
pub fn find_real_roots_sturm(
    poly: &Polynomial,
    non_negative: bool,
) -> Vec<f64> {
    if poly.degree() == 0 {
        return vec![];
    }

    // Make polynomial monic.
    let mut normalized = poly.clone();
    let leading = normalized.leading_coefficient();
    for coeff in normalized.coefficients.iter_mut() {
        *coeff /= leading;
    }

    // Scale if constant term is large, for numerical stability.
    let val0 = normalized.coefficients[0].abs();
    let scale_factor = if val0 > 10.0 {
        let fac = val0.powf(-1.0 / poly.degree() as f64);
        let mut mult = fac;
        for i in (0..poly.degree()).rev() {
            normalized.coefficients[i] *= mult;
            mult *= fac;
        }
        fac
    } else {
        1.0
    };

    let chain = SturmChain::new(&normalized);
    let (n_roots, at_min, at_max) = chain.num_real_roots(non_negative);

    if n_roots == 0 {
        return vec![];
    }

    let min = if non_negative {
        0.0
    } else {
        let mut min = -1.0;
        let mut n_changes = chain.num_changes(min);
        let mut pow = 0;

        while n_changes != at_min && pow < MAX_POWER {
            min *= 10.0;
            n_changes = chain.num_changes(min);
            pow += 1;
        }
        min
    };

    let mut max = 1.0;
    let mut n_changes = chain.num_changes(max);
    let mut pow = 0;

    while n_changes != at_max && pow < MAX_POWER {
        max *= 10.0;
        n_changes = chain.num_changes(max);
        pow += 1;
    }

    let mut roots = sturm_bisect(
        &chain,
        &normalized,
        min,
        max,
        chain.num_changes(min),
        chain.num_changes(max),
    );

    for root in &mut roots {
        *root /= scale_factor;
    }

    roots.sort_by(|a, b| a.partial_cmp(b).unwrap());
    roots
}

/// Divide two polynomials, returning (quotient, remainder).
pub fn polynomial_division(
    dividend: &Polynomial,
    divisor: &Polynomial,
) -> (Polynomial, Polynomial) {
    if divisor.degree() == 0 && divisor.coefficients[0].abs() < SMALL_ENOUGH {
        panic!("Division by zero polynomial");
    }

    let mut remainder = dividend.coefficients.clone();
    let mut quotient = Vec::new();

    let divisor_lead = divisor.coefficients[divisor.degree()];

    while remainder.len() > divisor.degree() {
        let coeff = remainder.last().unwrap() / divisor_lead;
        quotient.push(coeff);

        let n = remainder.len();
        for i in 0..=divisor.degree() {
            remainder[n - 1 - divisor.degree() + i] -=
                coeff * divisor.coefficients[i];
            if remainder[n - 1 - divisor.degree() + i].abs() < SMALL_ENOUGH {
                remainder[n - 1 - divisor.degree() + i] = 0.0;
            }
        }
        remainder.pop();
    }

    quotient.reverse();

    while remainder.len() > 1 && remainder.last().unwrap().abs() < SMALL_ENOUGH
    {
        remainder.pop();
    }

    (Polynomial::new(quotient), Polynomial::new(remainder))
}
