//
// Copyright (C) 2025 David Cattermole.
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

use num_traits::{ToPrimitive, Zero};
use std::ops::{
    Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Rem, RemAssign, Sub,
    SubAssign,
};

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Dual<T> {
    pub real: T,

    pub dual: T,
}

impl<T> Dual<T> {
    pub fn new(real: T, dual: T) -> Self {
        Self { real, dual }
    }
}

impl<T> From<T> for Dual<T>
where
    T: Copy + Default,
{
    fn from(real: T) -> Self {
        Self::new(real, T::default())
    }
}

impl Add for Dual<f64> {
    type Output = Self;
    fn add(self, other: Self) -> Self {
        Self::new(self.real + other.real, self.dual + other.dual)
    }
}

impl Add<f64> for Dual<f64> {
    type Output = Self;
    fn add(self, other: f64) -> Self {
        Self::new(self.real + other, self.dual)
    }
}

impl Sub for Dual<f64> {
    type Output = Self;
    fn sub(self, other: Self) -> Self {
        Self::new(self.real - other.real, self.dual - other.dual)
    }
}

impl Sub<f64> for Dual<f64> {
    type Output = Self;
    fn sub(self, other: f64) -> Self {
        Self::new(self.real - other, self.dual)
    }
}

impl Mul for Dual<f64> {
    type Output = Self;
    fn mul(self, other: Self) -> Self {
        Self::new(
            self.real * other.real,
            self.real * other.dual + self.dual * other.real,
        )
    }
}

impl Mul<f64> for Dual<f64> {
    type Output = Self;
    fn mul(self, other: f64) -> Self {
        Self::new(self.real * other, self.dual * other)
    }
}

impl Div for Dual<f64> {
    type Output = Self;
    fn div(self, other: Self) -> Self {
        Self::new(
            self.real / other.real,
            (self.dual * other.real - self.real * other.dual)
                / (other.real * other.real),
        )
    }
}

impl Div<f64> for Dual<f64> {
    type Output = Self;
    fn div(self, other: f64) -> Self {
        Self::new(self.real / other, self.dual / other)
    }
}

impl AddAssign for Dual<f64> {
    fn add_assign(&mut self, other: Self) {
        self.real += other.real;
        self.dual += other.dual;
    }
}

impl SubAssign for Dual<f64> {
    fn sub_assign(&mut self, other: Self) {
        self.real -= other.real;
        self.dual -= other.dual;
    }
}

impl MulAssign for Dual<f64> {
    fn mul_assign(&mut self, other: Self) {
        *self = *self * other;
    }
}

impl DivAssign for Dual<f64> {
    fn div_assign(&mut self, other: Self) {
        *self = *self / other;
    }
}

impl Rem for Dual<f64> {
    type Output = Self;
    fn rem(self, other: Self) -> Self::Output {
        Self::new(self.real % other.real, 0.0)
    }
}

impl RemAssign for Dual<f64> {
    fn rem_assign(&mut self, other: Self) {
        self.real %= other.real;
        self.dual = 0.0;
    }
}

impl Neg for Dual<f64> {
    type Output = Self;
    fn neg(self) -> Self::Output {
        Self::new(-self.real, -self.dual)
    }
}

impl Zero for Dual<f64> {
    fn zero() -> Self {
        Dual::new(0.0, 0.0)
    }

    fn is_zero(&self) -> bool {
        self.real == 0.0 && self.dual == 0.0
    }
}

impl num_traits::Num for Dual<f64> {
    type FromStrRadixErr = <f64 as num_traits::Num>::FromStrRadixErr;

    fn from_str_radix(
        str: &str,
        radix: u32,
    ) -> Result<Self, Self::FromStrRadixErr> {
        let real = f64::from_str_radix(str, radix)?;
        Ok(Dual::new(real, 0.0))
    }
}

impl num_traits::One for Dual<f64> {
    fn one() -> Self {
        Self::new(1.0, 0.0)
    }

    fn is_one(&self) -> bool {
        self.real == 1.0 && self.dual == 0.0
    }
}

impl num_traits::NumCast for Dual<f64> {
    fn from<T: num_traits::ToPrimitive>(n: T) -> Option<Self> {
        let real = n.to_f64()?;
        Some(Self::new(real, 0.0))
    }
}

impl ToPrimitive for Dual<f64> {
    fn to_i64(&self) -> Option<i64> {
        self.real.to_i64()
    }

    fn to_f64(&self) -> Option<f64> {
        Some(self.real)
    }

    fn to_u64(&self) -> Option<u64> {
        self.real.to_u64()
    }

    // Add other integer and float conversions for a complete implementation
    fn to_i8(&self) -> Option<i8> {
        self.real.to_i8()
    }
    fn to_i16(&self) -> Option<i16> {
        self.real.to_i16()
    }
    fn to_i32(&self) -> Option<i32> {
        self.real.to_i32()
    }
    fn to_isize(&self) -> Option<isize> {
        self.real.to_isize()
    }
    fn to_u8(&self) -> Option<u8> {
        self.real.to_u8()
    }
    fn to_u16(&self) -> Option<u16> {
        self.real.to_u16()
    }
    fn to_u32(&self) -> Option<u32> {
        self.real.to_u32()
    }
    fn to_usize(&self) -> Option<usize> {
        self.real.to_usize()
    }
    fn to_f32(&self) -> Option<f32> {
        self.real.to_f32()
    }
}

pub fn sin(x: Dual<f64>) -> Dual<f64> {
    Dual::new(x.real.sin(), x.dual * x.real.cos())
}

pub fn cos(x: Dual<f64>) -> Dual<f64> {
    Dual::new(x.real.cos(), x.dual * -x.real.sin())
}

pub fn tan(x: Dual<f64>) -> Dual<f64> {
    let tan_real = x.real.tan();
    Dual::new(tan_real, x.dual / x.real.cos().powi(2))
}

pub fn sqrt(x: Dual<f64>) -> Dual<f64> {
    Dual::new(x.real.sqrt(), x.dual / (2.0 * x.real.sqrt()))
}

pub fn exp(x: Dual<f64>) -> Dual<f64> {
    let exp_real = x.real.exp();
    Dual::new(exp_real, x.dual * exp_real)
}

pub fn ln(x: Dual<f64>) -> Dual<f64> {
    Dual::new(x.real.ln(), x.dual / x.real)
}

pub fn pow(x: Dual<f64>, y: f64) -> Dual<f64> {
    Dual::new(x.real.powf(y), x.dual * y * x.real.powf(y - 1.0))
}

impl num_traits::Float for Dual<f64> {
    fn nan() -> Self {
        Self::new(f64::nan(), f64::nan())
    }
    fn infinity() -> Self {
        Self::new(f64::infinity(), f64::nan())
    }
    fn neg_infinity() -> Self {
        Self::new(f64::neg_infinity(), f64::nan())
    }
    fn neg_zero() -> Self {
        Self::new(f64::neg_zero(), 0.0)
    }
    fn min_value() -> Self {
        Self::new(f64::min_value(), f64::nan())
    }
    fn min_positive_value() -> Self {
        Self::new(f64::min_positive_value(), f64::nan())
    }
    fn max_value() -> Self {
        Self::new(f64::max_value(), f64::nan())
    }
    fn is_nan(self) -> bool {
        self.real.is_nan() || self.dual.is_nan()
    }
    fn is_infinite(self) -> bool {
        self.real.is_infinite()
    }
    fn is_finite(self) -> bool {
        self.real.is_finite() && self.dual.is_finite()
    }
    fn is_normal(self) -> bool {
        self.real.is_normal() && self.dual.is_normal()
    }
    fn classify(self) -> std::num::FpCategory {
        self.real.classify()
    }
    fn floor(self) -> Self {
        Self::new(self.real.floor(), self.dual)
    }
    fn ceil(self) -> Self {
        Self::new(self.real.ceil(), self.dual)
    }
    fn round(self) -> Self {
        Self::new(self.real.round(), self.dual)
    }
    fn trunc(self) -> Self {
        Self::new(self.real.trunc(), self.dual)
    }
    fn fract(self) -> Self {
        Self::new(self.real.fract(), self.dual)
    }
    fn abs(self) -> Self {
        if self.real >= 0.0 {
            self
        } else {
            -self
        }
    }
    fn signum(self) -> Self {
        Self::new(self.real.signum(), self.dual)
    }
    fn is_sign_positive(self) -> bool {
        self.real.is_sign_positive()
    }
    fn is_sign_negative(self) -> bool {
        self.real.is_sign_negative()
    }
    fn mul_add(self, a: Self, b: Self) -> Self {
        self * a + b
    }
    fn recip(self) -> Self {
        Self::new(1.0 / self.real, -self.dual / (self.real * self.real))
    }
    fn powi(self, n: i32) -> Self {
        self.powf(Self::new(n as f64, 0.0))
    }
    fn powf(self, n: Self) -> Self {
        pow(self, n.real)
    }
    fn sqrt(self) -> Self {
        sqrt(self)
    }
    fn exp(self) -> Self {
        exp(self)
    }
    fn exp2(self) -> Self {
        Self::new(
            self.real.exp2(),
            self.dual * 2.0_f64.ln() * self.real.exp2(),
        )
    }
    fn ln(self) -> Self {
        ln(self)
    }
    fn log(self, base: Self) -> Self {
        ln(self) / ln(base)
    }
    fn log2(self) -> Self {
        ln(self) / Self::new(2.0_f64.ln(), 0.0)
    }
    fn log10(self) -> Self {
        ln(self) / Self::new(10.0_f64.ln(), 0.0)
    }
    fn cbrt(self) -> Self {
        let real_cbrt = self.real.cbrt();
        Self::new(real_cbrt, self.dual / (3.0 * real_cbrt * real_cbrt))
    }
    fn hypot(self, other: Self) -> Self {
        let res_real = self.real.hypot(other.real);
        let res_dual =
            (self.real * self.dual + other.real * other.dual) / res_real;
        Self::new(res_real, res_dual)
    }
    fn sin(self) -> Self {
        sin(self)
    }
    fn cos(self) -> Self {
        cos(self)
    }
    fn tan(self) -> Self {
        tan(self)
    }

    fn asin(self) -> Self {
        let real = self.real.asin();
        let dual = self.dual / (1.0 - self.real.powi(2)).sqrt();
        Self::new(real, dual)
    }

    fn acos(self) -> Self {
        let real = self.real.acos();
        let dual = -self.dual / (1.0 - self.real.powi(2)).sqrt();
        Self::new(real, dual)
    }

    fn atan(self) -> Self {
        let real = self.real.atan();
        let dual = self.dual / (1.0 + self.real.powi(2));
        Self::new(real, dual)
    }

    fn atan2(self, other: Self) -> Self {
        let real = self.real.atan2(other.real);
        let dual = (other.real * self.dual - self.real * other.dual)
            / (self.real.powi(2) + other.real.powi(2));
        Self::new(real, dual)
    }
    fn sin_cos(self) -> (Self, Self) {
        (self.sin(), self.cos())
    }
    fn sinh(self) -> Self {
        let real = self.real.sinh();
        let dual = self.dual * self.real.cosh();
        Self::new(real, dual)
    }
    fn cosh(self) -> Self {
        let real = self.real.cosh();
        let dual = self.dual * self.real.sinh();
        Self::new(real, dual)
    }
    fn tanh(self) -> Self {
        let real = self.real.tanh();
        let dual = self.dual / self.real.cosh().powi(2);
        Self::new(real, dual)
    }
    fn asinh(self) -> Self {
        let real = self.real.asinh();
        let dual = self.dual / (self.real.powi(2) + 1.0).sqrt();
        Self::new(real, dual)
    }
    fn acosh(self) -> Self {
        let real = self.real.acosh();
        let dual = self.dual / (self.real.powi(2) - 1.0).sqrt();
        Self::new(real, dual)
    }
    fn atanh(self) -> Self {
        let real = self.real.atanh();
        let dual = self.dual / (1.0 - self.real.powi(2));
        Self::new(real, dual)
    }
    fn integer_decode(self) -> (u64, i16, i8) {
        self.real.integer_decode()
    }
    fn max(self, other: Self) -> Self {
        Self::new(self.real.max(other.real), self.dual.max(other.dual))
    }
    fn min(self, other: Self) -> Self {
        Self::new(self.real.min(other.real), self.dual.min(other.dual))
    }
    fn abs_sub(self, other: Self) -> Self {
        (self - other).abs()
    }
    fn exp_m1(self) -> Self {
        let real = self.real.exp_m1();
        let dual = self.dual * self.real.exp();
        Self::new(real, dual)
    }
    fn ln_1p(self) -> Self {
        let real = self.real.ln_1p();
        let dual = self.dual / (1.0 + self.real);
        Self::new(real, dual)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use num_traits::{Float, Num, NumCast, One, Zero};

    const EPSILON: f64 = 1e-12;

    // Helper function to assert dual numbers are approximately equal.
    fn assert_dual_eq(a: Dual<f64>, b: Dual<f64>, tolerance: f64) {
        assert!(
            (a.real - b.real).abs() < tolerance,
            "Real parts differ: {} vs {}, diff: {}",
            a.real,
            b.real,
            (a.real - b.real).abs()
        );
        assert!(
            (a.dual - b.dual).abs() < tolerance,
            "Dual parts differ: {} vs {}, diff: {}",
            a.dual,
            b.dual,
            (a.dual - b.dual).abs()
        );
    }

    #[test]
    fn test_constructor_and_conversions() {
        // Test basic constructor.
        let d = Dual::new(3.0, 2.0);
        assert_eq!(d.real, 3.0);
        assert_eq!(d.dual, 2.0);

        // Test From<f64> conversion.
        let d2: Dual<f64> = 5.0.into();
        assert_eq!(d2.real, 5.0);
        assert_eq!(d2.dual, 0.0);

        // Test From trait.
        let d3: Dual<f64> = 7.0.into();
        assert_eq!(d3.real, 7.0);
        assert_eq!(d3.dual, 0.0);
    }

    #[test]
    fn test_zero_and_one_traits() {
        // Test Zero trait.
        let zero = Dual::<f64>::zero();
        assert_eq!(zero.real, 0.0);
        assert_eq!(zero.dual, 0.0);
        assert!(zero.is_zero());

        let non_zero = Dual::new(1.0, 0.0);
        assert!(!non_zero.is_zero());

        // Test One trait.
        let one = Dual::<f64>::one();
        assert_eq!(one.real, 1.0);
        assert_eq!(one.dual, 0.0);
        assert!(one.is_one());

        let non_one = Dual::new(2.0, 0.0);
        assert!(!non_one.is_one());
    }

    #[test]
    fn test_basic_arithmetic() {
        let a = Dual::new(3.0, 1.0);
        let b = Dual::new(2.0, 1.0);

        // Addition: (a + b)' = a' + b'
        let sum = a + b;
        assert_eq!(sum.real, 5.0);
        assert_eq!(sum.dual, 2.0);

        // Addition with scalar.
        let sum_scalar = a + 4.0;
        assert_eq!(sum_scalar.real, 7.0);
        assert_eq!(sum_scalar.dual, 1.0);

        // Subtraction: (a - b)' = a' - b'
        let diff = a - b;
        assert_eq!(diff.real, 1.0);
        assert_eq!(diff.dual, 0.0);

        // Subtraction with scalar.
        let diff_scalar = a - 1.0;
        assert_eq!(diff_scalar.real, 2.0);
        assert_eq!(diff_scalar.dual, 1.0);

        // Multiplication: (ab)' = a'b + ab'
        let prod = a * b;
        assert_eq!(prod.real, 6.0);
        assert_eq!(prod.dual, 5.0); // 1*2 + 3*1 = 5

        // Multiplication with scalar.
        let prod_scalar = a * 3.0;
        assert_eq!(prod_scalar.real, 9.0);
        assert_eq!(prod_scalar.dual, 3.0);

        // Division: (a/b)' = (a'b - ab') / b^2
        let quot = a / b;
        assert_eq!(quot.real, 1.5);
        assert_eq!(quot.dual, -0.25); // (1*2 - 3*1) / (2*2) = (2-3)/4 = -1/4 = -0.25

        // Division with scalar.
        let quot_scalar = a / 2.0;
        assert_eq!(quot_scalar.real, 1.5);
        assert_eq!(quot_scalar.dual, 0.5);
    }

    #[test]
    fn test_assignment_operators() {
        let mut d = Dual::new(3.0, 1.0);
        let other = Dual::new(2.0, 1.0);

        // Test +=
        d += other;
        assert_eq!(d.real, 5.0);
        assert_eq!(d.dual, 2.0);

        // Test -=
        d -= other;
        assert_eq!(d.real, 3.0);
        assert_eq!(d.dual, 1.0);

        // Test *=
        d *= other;
        assert_eq!(d.real, 6.0);
        assert_eq!(d.dual, 5.0); // 1*2 + 3*1 = 5

        // Test /=
        d /= other;
        assert_eq!(d.real, 3.0);
        assert_eq!(d.dual, 1.0); // Back to original.
    }

    #[test]
    fn test_negation() {
        let d = Dual::new(3.0, 2.0);
        let neg_d = -d;
        assert_eq!(neg_d.real, -3.0);
        assert_eq!(neg_d.dual, -2.0);
    }

    #[test]
    fn test_remainder() {
        let a = Dual::new(7.0, 1.0);
        let b = Dual::new(3.0, 1.0);

        let rem = a % b;
        assert_eq!(rem.real, 1.0); // 7 % 3 = 1
        assert_eq!(rem.dual, 0.0); // Derivative is set to 0 for remainder.

        let mut a_mut = a;
        a_mut %= b;
        assert_eq!(a_mut.real, 1.0);
        assert_eq!(a_mut.dual, 0.0);
    }

    #[test]
    fn test_trigonometric_functions() {
        let x = Dual::new(std::f64::consts::PI / 4.0, 1.0); // 45 degrees.

        // Test sin:
        // d/dx(sin(x)) = cos(x)
        let sin_x = sin(x);
        assert_dual_eq(
            sin_x,
            Dual::new(
                (std::f64::consts::PI / 4.0).sin(),
                (std::f64::consts::PI / 4.0).cos(),
            ),
            EPSILON,
        );

        // Test cos:
        // d/dx(cos(x)) = -sin(x)
        let cos_x = cos(x);
        assert_dual_eq(
            cos_x,
            Dual::new(
                (std::f64::consts::PI / 4.0).cos(),
                -(std::f64::consts::PI / 4.0).sin(),
            ),
            EPSILON,
        );

        // Test tan:
        // d/dx(tan(x)) = sec^2(x) = 1/cos^2(x)
        let tan_x = tan(x);
        let expected_tan_derivative =
            1.0 / (std::f64::consts::PI / 4.0).cos().powi(2);
        assert_dual_eq(
            tan_x,
            Dual::new(
                (std::f64::consts::PI / 4.0).tan(),
                expected_tan_derivative,
            ),
            EPSILON,
        );

        // Test Float trait methods.
        let sin_x_trait = x.sin();
        assert_dual_eq(sin_x_trait, sin_x, EPSILON);

        let cos_x_trait = x.cos();
        assert_dual_eq(cos_x_trait, cos_x, EPSILON);

        let tan_x_trait = x.tan();
        assert_dual_eq(tan_x_trait, tan_x, EPSILON);
    }

    #[test]
    fn test_inverse_trigonometric_functions() {
        let x = Dual::new(0.5, 1.0);

        // Test asin:
        // d/dx(asin(x)) = 1/sqrt(1-x^2)
        let asin_x = x.asin();
        let expected_asin_derivative = 1.0 / (1.0 - 0.5 * 0.5).sqrt();
        assert_dual_eq(
            asin_x,
            Dual::new(0.5.asin(), expected_asin_derivative),
            EPSILON,
        );

        // Test acos:
        // d/dx(acos(x)) = -1/sqrt(1-x^2)
        let acos_x = x.acos();
        let expected_acos_derivative = -1.0 / (1.0 - 0.5 * 0.5).sqrt();
        assert_dual_eq(
            acos_x,
            Dual::new(0.5.acos(), expected_acos_derivative),
            EPSILON,
        );

        // Test atan:
        // d/dx(atan(x)) = 1/(1+x^2)
        let atan_x = x.atan();
        let expected_atan_derivative = 1.0 / (1.0 + 0.5 * 0.5);
        assert_dual_eq(
            atan_x,
            Dual::new(0.5.atan(), expected_atan_derivative),
            EPSILON,
        );

        // Test atan2.
        let y = Dual::new(1.0, 1.0);
        let atan2_result = y.atan2(x);
        let expected_atan2_derivative =
            (0.5 * 1.0 - 1.0 * 1.0) / (1.0 * 1.0 + 0.5 * 0.5);
        assert_dual_eq(
            atan2_result,
            Dual::new(1.0.atan2(0.5), expected_atan2_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_hyperbolic_functions() {
        let x = Dual::new(1.0, 1.0);

        // Test sinh:
        // d/dx(sinh(x)) = cosh(x)
        let sinh_x = x.sinh();
        assert_dual_eq(sinh_x, Dual::new(1.0.sinh(), 1.0.cosh()), EPSILON);

        // Test cosh:
        // d/dx(cosh(x)) = sinh(x)
        let cosh_x = x.cosh();
        assert_dual_eq(cosh_x, Dual::new(1.0.cosh(), 1.0.sinh()), EPSILON);

        // Test tanh:
        // d/dx(tanh(x)) = sech^2(x) = 1/cosh^2(x)
        let tanh_x = x.tanh();
        let expected_tanh_derivative = 1.0 / 1.0.cosh().powi(2);
        assert_dual_eq(
            tanh_x,
            Dual::new(1.0.tanh(), expected_tanh_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_inverse_hyperbolic_functions() {
        let x = Dual::new(2.0, 1.0);

        // Test asinh:
        // d/dx(asinh(x)) = 1/sqrt(x^2+1)
        let asinh_x = x.asinh();
        let expected_asinh_derivative = 1.0 / (2.0 * 2.0 + 1.0).sqrt();
        assert_dual_eq(
            asinh_x,
            Dual::new(2.0.asinh(), expected_asinh_derivative),
            EPSILON,
        );

        // Test acosh:
        // d/dx(acosh(x)) = 1/sqrt(x^2-1)
        let acosh_x = x.acosh();
        let expected_acosh_derivative = 1.0 / (2.0 * 2.0 - 1.0).sqrt();
        assert_dual_eq(
            acosh_x,
            Dual::new(2.0.acosh(), expected_acosh_derivative),
            EPSILON,
        );

        // Test atanh for x in (-1, 1).
        let y = Dual::new(0.5, 1.0);
        let atanh_y = y.atanh();
        let expected_atanh_derivative = 1.0 / (1.0 - 0.5 * 0.5);
        assert_dual_eq(
            atanh_y,
            Dual::new(0.5.atanh(), expected_atanh_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_exponential_and_logarithmic_functions() {
        let x = Dual::new(2.0, 1.0);

        // Test exp:
        // d/dx(e^x) = e^x
        let exp_x = exp(x);
        assert_dual_eq(exp_x, Dual::new(2.0.exp(), 2.0.exp()), EPSILON);

        let exp_x_trait = x.exp();
        assert_dual_eq(exp_x_trait, exp_x, EPSILON);

        // Test exp2:
        // d/dx(2^x) = 2^x * ln(2)
        let exp2_x = x.exp2();
        let expected_exp2_derivative = 2.0_f64.powf(2.0) * 2.0_f64.ln();
        assert_dual_eq(
            exp2_x,
            Dual::new(2.0_f64.exp2(), expected_exp2_derivative),
            EPSILON,
        );

        // Test ln:
        // d/dx(ln(x)) = 1/x
        let ln_x = ln(x);
        assert_dual_eq(ln_x, Dual::new(2.0.ln(), 0.5), EPSILON);

        let ln_x_trait = x.ln();
        assert_dual_eq(ln_x_trait, ln_x, EPSILON);

        // Test log2:
        // d/dx(log₂(x)) = 1/(x * ln(2))
        let log2_x = x.log2();
        let expected_log2_derivative = 1.0 / (2.0 * 2.0_f64.ln());
        assert_dual_eq(
            log2_x,
            Dual::new(2.0.log2(), expected_log2_derivative),
            EPSILON,
        );

        // Test log10:
        // d/dx(log₁₀(x)) = 1/(x * ln(10))
        let log10_x = x.log10();
        let expected_log10_derivative = 1.0 / (2.0 * 10.0_f64.ln());
        assert_dual_eq(
            log10_x,
            Dual::new(2.0.log10(), expected_log10_derivative),
            EPSILON,
        );

        // Test exp_m1:
        // d/dx(e^x - 1) = e^x
        let exp_m1_x = x.exp_m1();
        assert_dual_eq(exp_m1_x, Dual::new(2.0.exp_m1(), 2.0.exp()), EPSILON);

        // Test ln_1p:
        // d/dx(ln(1 + x)) = 1/(1 + x)
        let ln_1p_x = x.ln_1p();
        let expected_ln_1p_derivative = 1.0 / (1.0 + 2.0);
        assert_dual_eq(
            ln_1p_x,
            Dual::new(2.0.ln_1p(), expected_ln_1p_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_power_functions() {
        let x = Dual::new(4.0, 1.0);

        // Test sqrt:
        // d/dx(sqrt(x)) = 1/(2sqrt(x))
        let sqrt_x = sqrt(x);
        let expected_sqrt_derivative = 1.0 / (2.0 * 4.0.sqrt());
        assert_dual_eq(
            sqrt_x,
            Dual::new(4.0.sqrt(), expected_sqrt_derivative),
            EPSILON,
        );

        let sqrt_x_trait = x.sqrt();
        assert_dual_eq(sqrt_x_trait, sqrt_x, EPSILON);

        // Test cbrt (Cube Root):
        // d/dx(cbrt(x)) = 1/(3cbrt(x^2))
        let cbrt_x = x.cbrt();
        let expected_cbrt_derivative = 1.0 / (3.0 * 4.0.cbrt().powi(2));
        assert_dual_eq(
            cbrt_x,
            Dual::new(4.0.cbrt(), expected_cbrt_derivative),
            EPSILON,
        );

        // Test pow:
        // d/dx(x^n) = n * x^(n-1)
        let pow_x = pow(x, 3.0);
        let expected_pow_derivative = 3.0 * 4.0_f64.powf(2.0);
        assert_dual_eq(
            pow_x,
            Dual::new(4.0_f64.powf(3.0), expected_pow_derivative),
            EPSILON,
        );

        // Test powi.
        let powi_x = x.powi(3);
        assert_dual_eq(powi_x, pow_x, EPSILON);

        // Test powf with dual exponent.
        let base = Dual::new(2.0, 1.0);
        let exponent = Dual::new(3.0, 0.0);
        let powf_result = base.powf(exponent);
        assert_dual_eq(powf_result, Dual::new(8.0, 12.0), EPSILON); // d/dx(2^3) = 3*2^2 = 12
    }

    #[test]
    fn test_other_mathematical_functions() {
        let x = Dual::new(-2.5, 1.0);

        // Test abs.
        let abs_x = x.abs();
        assert_eq!(abs_x.real, 2.5);
        assert_eq!(abs_x.dual, -1.0); // Derivative of abs(x) = sign(x) * x'

        let positive_x = Dual::new(2.5, 1.0);
        let abs_pos = positive_x.abs();
        assert_eq!(abs_pos.real, 2.5);
        assert_eq!(abs_pos.dual, 1.0);

        // Test floor, ceil, round, trunc, fract.
        let y = Dual::new(2.7, 1.0);

        let floor_y = y.floor();
        assert_eq!(floor_y.real, 2.0);
        assert_eq!(floor_y.dual, 1.0); // Derivative preserved.

        let ceil_y = y.ceil();
        assert_eq!(ceil_y.real, 3.0);
        assert_eq!(ceil_y.dual, 1.0);

        let round_y = y.round();
        assert_eq!(round_y.real, 3.0);
        assert_eq!(round_y.dual, 1.0);

        let trunc_y = y.trunc();
        assert_eq!(trunc_y.real, 2.0);
        assert_eq!(trunc_y.dual, 1.0);

        let fract_y = y.fract();
        assert!((fract_y.real - 0.7).abs() < 1e-10); // Account for floating point precision.
        assert_eq!(fract_y.dual, 1.0);

        // Test signum.
        let signum_pos = positive_x.signum();
        assert_eq!(signum_pos.real, 1.0);
        assert_eq!(signum_pos.dual, 1.0);

        let signum_neg = x.signum();
        assert_eq!(signum_neg.real, -1.0);
        assert_eq!(signum_neg.dual, 1.0);

        // Test recip:
        // d/dx(1/x) = -1/x^2
        let z = Dual::new(2.0, 1.0);
        let recip_z = z.recip();
        let expected_recip_derivative = -1.0 / (2.0 * 2.0);
        assert_dual_eq(
            recip_z,
            Dual::new(0.5, expected_recip_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_hypot_function() {
        let x = Dual::new(3.0, 1.0);
        let y = Dual::new(4.0, 1.0);

        // Test hypot:
        // sqrt(x^2 + y^2)
        // d/dx(hypot(x,y)) = x/hypot(x,y)
        // d/dy(hypot(x,y)) = y/hypot(x,y)
        //
        // Combined:
        // (x*dx + y*dy)/hypot(x,y)
        let hypot_result = x.hypot(y);
        let expected_real = (3.0 * 3.0 + 4.0 * 4.0).sqrt(); // 5.0
        let expected_dual = (3.0 * 1.0 + 4.0 * 1.0) / 5.0; // 7.0/5.0 = 1.4
        assert_dual_eq(
            hypot_result,
            Dual::new(expected_real, expected_dual),
            EPSILON,
        );
    }

    #[test]
    fn test_mul_add_function() {
        let a = Dual::new(2.0, 1.0);
        let b = Dual::new(3.0, 1.0);
        let c = Dual::new(4.0, 1.0);

        // Test mul_add:
        // a * b + c
        let mul_add_result = a.mul_add(b, c);
        let expected = a * b + c;
        assert_dual_eq(mul_add_result, expected, EPSILON);
    }

    #[test]
    fn test_special_values_and_edge_cases() {
        // Test with zero.
        let zero = Dual::new(0.0, 1.0);
        let two = Dual::new(2.0, 1.0);

        // Zero operations.
        assert_eq!((zero + two).real, 2.0);
        assert_eq!((zero * two).real, 0.0);
        assert_eq!((zero * two).dual, 2.0); // d/dx(0*2x) = 2

        // Test with infinity.
        let inf = Dual::new(f64::INFINITY, 1.0);
        assert!(inf.is_infinite());
        assert!(!inf.is_finite());
        assert!(!inf.is_normal());

        // Test with NaN.
        let nan = Dual::new(f64::NAN, 1.0);
        assert!(nan.is_nan());
        assert!(!nan.is_finite());
        assert!(!nan.is_normal());

        let dual_nan = Dual::new(1.0, f64::NAN);
        assert!(dual_nan.is_nan()); // Should be true if either part is NaN.

        // Test Float trait special values.
        let dual_inf = Dual::<f64>::infinity();
        assert!(dual_inf.is_infinite());

        let dual_neg_inf = Dual::<f64>::neg_infinity();
        assert_eq!(dual_neg_inf.real, f64::NEG_INFINITY);

        let dual_nan_trait = Dual::<f64>::nan();
        assert!(dual_nan_trait.is_nan());

        let dual_neg_zero = Dual::<f64>::neg_zero();
        assert_eq!(dual_neg_zero.real, -0.0);

        // Test min/max values.
        let min_val = Dual::<f64>::min_value();
        let max_val = Dual::<f64>::max_value();
        let min_pos = Dual::<f64>::min_positive_value();

        assert_eq!(min_val.real, f64::MIN);
        assert_eq!(max_val.real, f64::MAX);
        assert_eq!(min_pos.real, f64::MIN_POSITIVE);
    }

    #[test]
    fn test_classification_functions() {
        let normal = Dual::new(1.0, 1.0);
        let zero = Dual::new(0.0, 1.0);
        let inf = Dual::new(f64::INFINITY, 1.0);
        let nan = Dual::new(f64::NAN, 1.0);

        // Test is_normal.
        assert!(normal.is_normal());
        assert!(!zero.is_normal());
        assert!(!inf.is_normal());
        assert!(!nan.is_normal());

        // Test is_finite.
        assert!(normal.is_finite());
        assert!(zero.is_finite());
        assert!(!inf.is_finite());
        assert!(!nan.is_finite());

        // Test classify.
        use std::num::FpCategory;
        assert_eq!(normal.classify(), FpCategory::Normal);
        assert_eq!(zero.classify(), FpCategory::Zero);
        assert_eq!(inf.classify(), FpCategory::Infinite);
        assert_eq!(nan.classify(), FpCategory::Nan);

        // Test sign functions.
        let pos = Dual::new(1.0, 1.0);
        let neg = Dual::new(-1.0, 1.0);

        assert!(pos.is_sign_positive());
        assert!(!pos.is_sign_negative());
        assert!(!neg.is_sign_positive());
        assert!(neg.is_sign_negative());
    }

    #[test]
    fn test_min_max_abs_sub() {
        let a = Dual::new(3.0, 1.0);
        let b = Dual::new(2.0, 2.0);

        // Test max - note: this implementation takes max of both real
        // and dual parts.
        let max_result = a.max(b);
        assert_eq!(max_result.real, 3.0);
        assert_eq!(max_result.dual, 2.0); // max(1.0, 2.0) = 2.0

        // Test min - note: this implementation takes min of both real
        // and dual parts.
        let min_result = a.min(b);
        assert_eq!(min_result.real, 2.0);
        assert_eq!(min_result.dual, 1.0); // min(1.0, 2.0) = 1.0

        // Test abs_sub - (a - b).abs() where a > b
        let abs_sub_result = a.abs_sub(b);

        // |3-2| = 1.
        assert_eq!(abs_sub_result.real, 1.0);

        // (3-2).dual = 1-2 = -1, and since 3>2, abs preserves the sign.
        assert_eq!(abs_sub_result.dual, -1.0);
    }

    #[test]
    fn test_num_cast_and_primitive_conversions() {
        let d = Dual::new(3.5, 1.0);

        // Test NumCast.
        let from_int: Option<Dual<f64>> = NumCast::from(42i32);
        assert!(from_int.is_some());
        let converted = from_int.unwrap();
        assert_eq!(converted.real, 42.0);
        assert_eq!(converted.dual, 0.0);

        // Test ToPrimitive conversions.
        assert_eq!(d.to_f64(), Some(3.5));
        assert_eq!(d.to_i32(), Some(3));
        assert_eq!(d.to_u32(), Some(3));
        assert_eq!(d.to_f32(), Some(3.5_f32));

        // Test edge cases for conversions.
        let large_dual = Dual::new(f64::MAX, 1.0);
        assert_eq!(large_dual.to_f64(), Some(f64::MAX));

        let neg_dual = Dual::new(-3.7, 1.0);
        assert_eq!(neg_dual.to_i32(), Some(-3));
    }

    #[test]
    fn test_from_str_radix() {
        // Test Num trait from_str_radix.
        let result = Dual::<f64>::from_str_radix("42", 10);
        assert!(result.is_ok());
        let dual_val = result.unwrap();
        assert_eq!(dual_val.real, 42.0);
        assert_eq!(dual_val.dual, 0.0);

        // Test with different radix.
        let hex_result = Dual::<f64>::from_str_radix("A", 16);
        assert!(hex_result.is_ok());
        let hex_dual = hex_result.unwrap();
        assert_eq!(hex_dual.real, 10.0);
        assert_eq!(hex_dual.dual, 0.0);

        // Test invalid input.
        let invalid_result = Dual::<f64>::from_str_radix("invalid", 10);
        assert!(invalid_result.is_err());
    }

    #[test]
    fn test_sin_cos_combined() {
        let x = Dual::new(std::f64::consts::PI / 3.0, 1.0); // 60 degrees.

        let (sin_result, cos_result) = x.sin_cos();
        let expected_sin = x.sin();
        let expected_cos = x.cos();

        assert_dual_eq(sin_result, expected_sin, EPSILON);
        assert_dual_eq(cos_result, expected_cos, EPSILON);
    }

    #[test]
    fn test_log_with_base() {
        let x = Dual::new(8.0, 1.0);
        let base = Dual::new(2.0, 0.0);

        // log_2(8) = 3, d/dx(log_2(x)) = 1/(x * ln(2))
        let log_result = x.log(base);
        let expected_derivative = 1.0 / (8.0 * 2.0_f64.ln());
        assert_dual_eq(
            log_result,
            Dual::new(3.0, expected_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_integer_decode() {
        let d = Dual::new(3.5, 1.0);
        let (mantissa, exponent, sign) = d.integer_decode();
        let (expected_mantissa, expected_exponent, expected_sign) =
            3.5_f64.integer_decode();

        assert_eq!(mantissa, expected_mantissa);
        assert_eq!(exponent, expected_exponent);
        assert_eq!(sign, expected_sign);
    }

    // Property-based tests to verify mathematical laws.
    #[test]
    fn test_linearity_property() {
        // Test linearity:
        // d/dx(af + bg) = a*f' + b*g'
        let x = Dual::new(2.0, 1.0);
        let a = 3.0;
        let b = 4.0;

        // f(x) = x^2
        let f = x * x;

        // g(x) = x^3
        let g = x * x * x;

        // af + bg
        let a_dual: Dual<f64> = a.into();
        let b_dual: Dual<f64> = b.into();
        let combined = a_dual * f + b_dual * g;

        // Expected:
        // a * 2x + b * 3x^2 = 3 * 2*2 + 4 * 3*4 = 12 + 48 = 60
        assert_eq!(combined.dual, 60.0);

        // Verify the function value:
        // 3*4 + 4*8 = 12 + 32 = 44
        assert_eq!(combined.real, 44.0);
    }

    #[test]
    fn test_product_rule() {
        // Test product rule:
        // d/dx(fg) = f'g + fg'
        let x = Dual::new(3.0, 1.0);

        // f(x) = x^2
        let f = x * x; // f = 9, f' = 6

        // g(x) = x^3
        let g = x * x * x; // g = 27, g' = 27

        let product = f * g;

        // Product rule:
        // f'g + fg' = 6*27 + 9*27 = 162 + 243 = 405
        assert_eq!(product.dual, 405.0);

        // Function value:
        // f*g = 9*27 = 243
        assert_eq!(product.real, 243.0);
    }

    #[test]
    fn test_quotient_rule() {
        // Test quotient rule:
        // d/dx(f/g) = (f'g - fg') / g^2
        let x = Dual::new(2.0, 1.0);

        // f(x) = x^3 + 1
        let one_dual: Dual<f64> = 1.0.into();
        let f = x * x * x + one_dual; // f = 9, f' = 12

        // g(x) = x^2
        let g = x * x; // g = 4, g' = 4

        let quotient = f / g;

        // Quotient rule:
        // (f'g - fg') / g^2 = (12*4 - 9*4) / 16 = (48 - 36) / 16 = 0.75
        assert_eq!(quotient.dual, 0.75);

        // Function value:
        // f/g = 9/4 = 2.25
        assert_eq!(quotient.real, 2.25);
    }

    #[test]
    fn test_chain_rule() {
        // Test chain rule:
        // d/dx(f(g(x))) = f'(g(x)) * g'(x)
        let x = Dual::new(2.0, 1.0);

        // g(x) = x^2
        let g = x * x; // g = 4, g' = 4

        // f(g) = sin(g) = sin(x^2)
        let composite = sin(g);

        // Chain rule:
        // f'(g) * g' = cos(4) * 4
        let expected_derivative = 4.0_f64.cos() * 4.0;
        assert_dual_eq(
            composite,
            Dual::new(4.0_f64.sin(), expected_derivative),
            EPSILON,
        );

        // Test more complex composition:
        // exp(sin(x^2))
        let complex_composite = exp(sin(g));
        let sin_g = 4.0_f64.sin();
        let expected_complex_derivative = sin_g.exp() * 4.0_f64.cos() * 4.0;
        assert_dual_eq(
            complex_composite,
            Dual::new(sin_g.exp(), expected_complex_derivative),
            EPSILON,
        );
    }

    #[test]
    fn test_power_rule_generalized() {
        // Test general power rule:
        // d/dx(x^n) = n * x^(n-1)
        let test_cases = vec![
            (2.0, 1.0, 1.0),                      // x^1 = x, derivative = 1
            (2.0, 2.0, 4.0),                      // x^2, derivative = 2x = 4
            (2.0, 3.0, 12.0),                     // x^3, derivative = 3x^2 = 12
            (3.0, 0.5, 0.5 * 3.0_f64.powf(-0.5)), // x^0.5, derivative = 0.5 * x^(-0.5)
        ];

        for (x_val, n, expected_derivative) in test_cases {
            let x = Dual::new(x_val, 1.0);
            let result = pow(x, n);
            let expected_real = x_val.powf(n);

            assert_dual_eq(
                result,
                Dual::new(expected_real, expected_derivative),
                EPSILON,
            );
        }

        // Test x^0 separately since it has special behaviour.
        let x = Dual::new(2.0, 1.0);
        let result = pow(x, 0.0);
        assert_eq!(result.real, 1.0); // 2^0 = 1.
        assert_eq!(result.dual, 0.0); // derivative of constant is 0.
    }

    #[test]
    fn test_inverse_function_derivatives() {
        // Test that inverse functions have reciprocal derivatives.
        let x = Dual::new(0.5, 1.0);

        // sin and arcsin.
        let sin_x = sin(x);
        let asin_sin_x = sin_x.asin();

        // Should recover original value.
        assert_dual_eq(asin_sin_x, x, EPSILON);

        // Test that d/dx(asin(sin(x))) = 1
        //
        // (by chain rule cancellation)
        assert!((asin_sin_x.dual - 1.0).abs() < EPSILON);

        // exp and ln.
        let y = Dual::new(2.0, 1.0);
        let exp_y = exp(y);
        let ln_exp_y = ln(exp_y);

        // Should recover original value.
        assert_dual_eq(ln_exp_y, y, EPSILON);

        // Test that d/dx(ln(exp(x))) = 1
        //
        // (by chain rule cancellation)
        assert!((ln_exp_y.dual - 1.0).abs() < EPSILON);
    }

    #[test]
    fn test_trigonometric_identities() {
        let x = Dual::new(1.5, 1.0);

        // Test sin^2 + cos^2 = 1
        //
        // (derivatives should also satisfy this relationship)
        let sin_x = sin(x);
        let cos_x = cos(x);
        let identity = sin_x * sin_x + cos_x * cos_x;

        // Real part should be 1
        assert!((identity.real - 1.0).abs() < EPSILON);

        // Derivative should be 0:
        // d/dx(sin^2x + cos^2x) = 2sin(x)cos(x) + 2cos(x)(-sin(x)) = 0
        assert!(identity.dual.abs() < EPSILON);

        // Test tan = sin/cos
        let tan_x = tan(x);
        let tan_from_ratio = sin(x) / cos(x);
        assert_dual_eq(tan_x, tan_from_ratio, EPSILON);
    }

    #[test]
    fn test_exponential_properties() {
        let x = Dual::new(1.0, 1.0);
        let y = Dual::new(2.0, 1.0);

        // Test e^(x+y) = e^x * e^y
        let exp_sum = exp(x + y);
        let exp_product = exp(x) * exp(y);
        assert_dual_eq(exp_sum, exp_product, EPSILON);

        // Test ln(xy) = ln(x) + ln(y)
        let ln_product = ln(x * y);
        let ln_sum = ln(x) + ln(y);
        assert_dual_eq(ln_product, ln_sum, EPSILON);
    }

    #[test]
    fn test_derivative_consistency_with_finite_differences() {
        // Test various functions against finite differences to ensure
        // derivative accuracy.
        let x_val = 2.5;
        let h = 1e-8;

        // Test x^2.
        let x_dual = Dual::new(x_val, 1.0);
        let dual_result = x_dual * x_dual;
        let dual_derivative = dual_result.dual;

        let f_x = x_val * x_val;
        let f_x_plus_h = (x_val + h) * (x_val + h);
        let finite_diff_derivative = (f_x_plus_h - f_x) / h;

        let error = (dual_derivative - finite_diff_derivative).abs();
        assert!(
            error < 1e-6,
            "Function x^2: Dual derivative {} vs finite diff {} (error: {})",
            dual_derivative,
            finite_diff_derivative,
            error
        );

        // Test sin(x).
        let dual_result = sin(x_dual);
        let dual_derivative = dual_result.dual;

        let f_x = x_val.sin();
        let f_x_plus_h = (x_val + h).sin();
        let finite_diff_derivative = (f_x_plus_h - f_x) / h;

        let error = (dual_derivative - finite_diff_derivative).abs();
        assert!(
            error < 1e-6,
            "Function sin(x): Dual derivative {} vs finite diff {} (error: {})",
            dual_derivative,
            finite_diff_derivative,
            error
        );
    }

    #[test]
    fn test_polynomial_accuracy_comprehensive() {
        // Test against the polynomial from existing accuracy tests
        // but more comprehensively.
        let test_points = vec![0.5, 1.0, 1.5, 2.0, 2.5, 3.0];

        for x_val in test_points {
            // Test function:
            // f(x) = x^3 + 2x^2 + 3x + 4
            //
            // Analytical derivative:
            // f'(x) = 3x^2 + 4x + 3
            let exact_derivative = 3.0 * x_val * x_val + 4.0 * x_val + 3.0;

            let x_dual = Dual::new(x_val, 1.0);
            let result = x_dual * x_dual * x_dual
                + Into::<Dual<f64>>::into(2.0) * x_dual * x_dual
                + Into::<Dual<f64>>::into(3.0) * x_dual
                + Into::<Dual<f64>>::into(4.0);

            let dual_derivative = result.dual;

            // Dual numbers should be exact for polynomial functions.
            let error = (dual_derivative - exact_derivative).abs();
            assert!(
                error < 1e-15,
                "Polynomial derivative error at x={}: {} vs {} (error: {})",
                x_val,
                dual_derivative,
                exact_derivative,
                error
            );
        }
    }

    #[test]
    fn test_complex_composite_functions() {
        // Test derivatives of complex composite functions.
        let x = Dual::new(1.0, 1.0);

        // Test f(x) = exp(sin(x^2))
        let x_squared = x * x;
        let sin_x_squared = sin(x_squared);
        let result = exp(sin_x_squared);

        // Analytical derivative using chain rule:
        // d/dx[exp(sin(x^2))] = exp(sin(x^2)) * cos(x^2) * 2x
        let x_val = 1.0;
        let expected_derivative =
            (x_val * x_val).sin().exp() * (x_val * x_val).cos() * 2.0 * x_val;

        assert_dual_eq(
            result,
            Dual::new((x_val * x_val).sin().exp(), expected_derivative),
            EPSILON,
        );

        // Test f(x) = ln(sqrt(x^2 + 1))
        let x2 = Dual::new(2.0, 1.0);
        let one_dual: Dual<f64> = 1.0.into();
        let sqrt_arg = x2 * x2 + one_dual;
        let sqrt_result = sqrt(sqrt_arg);
        let ln_result = ln(sqrt_result);

        // This is equivalent to ln(sqrt(x^2 + 1)) = 0.5 * ln(x^2 + 1)
        //
        // Derivative:
        // d/dx[0.5 * ln(x^2 + 1)] = 0.5 * 2x/(x^2 + 1) = x/(x^2 + 1)
        let x2_val = 2.0;
        let expected_derivative_2 = x2_val / (x2_val * x2_val + 1.0);
        let expected_real = 0.5 * (x2_val * x2_val + 1.0).ln();

        assert_dual_eq(
            ln_result,
            Dual::new(expected_real, expected_derivative_2),
            EPSILON,
        );
    }

    #[test]
    fn test_multivariate_partial_derivatives() {
        // Test partial derivatives for functions of the form f(x,y)
        // by setting one variable's derivative to 1.

        // f(x,y) = x^2y + xy^2
        // df/dx = 2xy + y^2, df/dy = x^2 + 2xy
        let x_val = 2.0;
        let y_val = 3.0;

        // Test df/dx (set dx = 1, dy = 0)
        let x_dual = Dual::new(x_val, 1.0);
        let y_const = Dual::new(y_val, 0.0);
        let result_dx = x_dual * x_dual * y_const + x_dual * y_const * y_const;

        let expected_partial_x = 2.0 * x_val * y_val + y_val * y_val; // 2*2*3 + 3^2 = 12 + 9 = 21
        assert_eq!(result_dx.dual, expected_partial_x);

        // Test df/dy (set dx = 0, dy = 1)
        let x_const = Dual::new(x_val, 0.0);
        let y_dual = Dual::new(y_val, 1.0);
        let result_dy = x_const * x_const * y_dual + x_const * y_dual * y_dual;

        let expected_partial_y = x_val * x_val + 2.0 * x_val * y_val; // 2^2 + 2*2*3 = 4 + 12 = 16
        assert_eq!(result_dy.dual, expected_partial_y);
    }

    #[test]
    fn test_higher_order_approximation() {
        // While dual numbers only compute first derivatives exactly,
        // test that they maintain accuracy for functions where second
        // derivatives matter.

        let h = 1e-10; // Very small step for finite differences.

        // Test x^4
        let x_val = 1.5;
        let x_dual = Dual::new(x_val, 1.0);
        let dual_result = x_dual * x_dual * x_dual * x_dual;
        let dual_derivative = dual_result.dual;

        let f_x = x_val.powi(4);
        let f_x_plus_h = (x_val + h).powi(4);
        let finite_diff_derivative = (f_x_plus_h - f_x) / h;

        let error = (dual_derivative - finite_diff_derivative).abs();
        assert!(
            error < 1e-5, // More relaxed tolerance for very small step size.
            "Higher-order function x^4: Dual derivative {} vs finite diff {} (error: {})",
            dual_derivative, finite_diff_derivative, error
        );

        // Test e^(x^2)
        let x_val = 0.5;
        let x_dual = Dual::new(x_val, 1.0);
        let dual_result = exp(x_dual * x_dual);
        let dual_derivative = dual_result.dual;

        let f_x = (x_val * x_val).exp();
        let f_x_plus_h = ((x_val + h) * (x_val + h)).exp();
        let finite_diff_derivative = (f_x_plus_h - f_x) / h;

        let error = (dual_derivative - finite_diff_derivative).abs();
        assert!(
            error < 1e-6, // Relaxed tolerance for numerical precision.
            "Higher-order function e^(x^2): Dual derivative {} vs finite diff {} (error: {})",
            dual_derivative, finite_diff_derivative, error
        );
    }

    #[test]
    fn test_comparative_accuracy_vs_existing_tests() {
        // Replicate and extend the accuracy test.
        let x_val = 2.5;

        // Test function:
        // f(x) = x^3 + 2x^2 + 3x + 4
        //
        // Exact derivative:
        // 3x^2 + 4x + 3
        let exact_derivative = 3.0 * x_val * x_val + 4.0 * x_val + 3.0;

        // Dual numbers derivative.
        let x_dual = Dual::new(x_val, 1.0);
        let result_dual = x_dual * x_dual * x_dual
            + Into::<Dual<f64>>::into(2.0) * x_dual * x_dual
            + Into::<Dual<f64>>::into(3.0) * x_dual
            + Into::<Dual<f64>>::into(4.0);
        let dual_derivative = result_dual.dual;

        // Test against various finite difference step sizes.
        let h_values = vec![1e-4, 1e-6, 1e-8, 1e-10, 1e-12];

        for h in h_values {
            let f_x = |x: f64| x * x * x + 2.0 * x * x + 3.0 * x + 4.0;
            let f_x_val = f_x(x_val);
            let f_x_plus_h = f_x(x_val + h);
            let finite_diff_derivative = (f_x_plus_h - f_x_val) / h;

            let dual_error = (dual_derivative - exact_derivative).abs();
            let finite_diff_error =
                (finite_diff_derivative - exact_derivative).abs();

            // Dual numbers should be exact (within machine precision).
            assert!(dual_error < 1e-15, "Dual error too large: {}", dual_error);

            // Dual numbers should be more accurate than finite
            // differences.
            if finite_diff_error > 1e-14 {
                // Only compare when finite diff has meaningful error.
                assert!(dual_error < finite_diff_error,
                    "Dual numbers should be more accurate than finite differences (h={}): dual_error={}, finite_diff_error={}",
                    h, dual_error, finite_diff_error);
            }
        }
    }

    fn test_function_f64(x: f64) -> f64 {
        x * x * x + 2.0 * x * x + 3.0 * x + 4.0
    }

    fn test_function_dual(x: Dual<f64>) -> Dual<f64> {
        x * x * x
            + Into::<Dual<f64>>::into(2.0) * x * x
            + Into::<Dual<f64>>::into(3.0) * x
            + Into::<Dual<f64>>::into(4.0)
    }

    #[test]
    fn test_dual_vs_finite_diff_accuracy() {
        let x_val = 2.5;

        // Exact derivative:
        // 3x^2 + 4x + 3
        let exact_derivative = 3.0 * x_val * x_val + 4.0 * x_val + 3.0;

        // Dual numbers derivative.
        let x_dual = Dual::new(x_val, 1.0);
        let result_dual = test_function_dual(x_dual);
        let dual_derivative = result_dual.dual;

        // Finite differences derivative (h = 1e-8).
        let h = 1e-8;
        let f_x = test_function_f64(x_val);
        let f_x_plus_h = test_function_f64(x_val + h);
        let finite_diff_derivative = (f_x_plus_h - f_x) / h;

        println!("x = {}", x_val);
        println!("Exact derivative:      {:.12}", exact_derivative);
        println!("Dual derivative:       {:.12}", dual_derivative);
        println!("Finite diff derivative: {:.12}", finite_diff_derivative);
        println!(
            "Dual error:            {:.2e}",
            (dual_derivative - exact_derivative).abs()
        );
        println!(
            "Finite diff error:     {:.2e}",
            (finite_diff_derivative - exact_derivative).abs()
        );

        // Dual numbers should be exact for polynomial functions.
        assert!((dual_derivative - exact_derivative).abs() < 1e-15);

        // Finite differences should be close but not exact.
        assert!((finite_diff_derivative - exact_derivative).abs() < 1e-6);
    }
}
