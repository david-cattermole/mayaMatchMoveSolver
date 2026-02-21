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

//! Common traits and macros shared across all data types.

pub use num_traits::Zero;
pub use std::fmt;
pub use std::ops::{
    Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign,
};

/// Core trait for unit wrapper types.
///
/// This trait provides the fundamental interface for all unit types,
/// allowing access to the underlying numeric value while maintaining
/// type safety.
pub trait UnitValue<T: Clone> {
    /// Create a new unit value from a raw numeric value.
    fn new(value: T) -> Self;

    /// Get the raw numeric value.
    fn value(&self) -> T;

    /// Get a reference to the raw numeric value.
    fn value_ref(&self) -> &T;

    /// Get a mutable reference to the raw numeric value.
    fn value_mut(&mut self) -> &mut T;
}

/// Implement UnitValue trait for a unit type.
///
/// This macro provides the standard implementation of UnitValue
/// for any unit wrapper type.
#[macro_export]
macro_rules! impl_unit_value {
    ($unit_type:ident) => {
        impl<T: Clone> $crate::datatype::common::UnitValue<T>
            for $unit_type<T>
        {
            fn new(value: T) -> Self {
                $unit_type(value)
            }

            fn value(&self) -> T {
                self.0.clone()
            }

            fn value_ref(&self) -> &T {
                &self.0
            }

            fn value_mut(&mut self) -> &mut T {
                &mut self.0
            }
        }
    };
}

/// Implement arithmetic operations for a unit type.
///
/// This macro provides standard arithmetic operations (Add, Sub, Mul, Div, etc.)
/// for any unit wrapper type. Operations between units of the same type are supported,
/// as well as scalar multiplication and division.
#[macro_export]
macro_rules! impl_arithmetic_ops {
    ($unit_type:ident) => {
        impl<T> $crate::datatype::common::Add for $unit_type<T>
        where
            T: $crate::datatype::common::Add<Output = T>,
        {
            type Output = Self;

            fn add(self, rhs: Self) -> Self::Output {
                $unit_type(self.0 + rhs.0)
            }
        }

        impl<T> $crate::datatype::common::AddAssign for $unit_type<T>
        where
            T: $crate::datatype::common::AddAssign,
        {
            fn add_assign(&mut self, rhs: Self) {
                self.0 += rhs.0;
            }
        }

        impl<T> $crate::datatype::common::Sub for $unit_type<T>
        where
            T: $crate::datatype::common::Sub<Output = T>,
        {
            type Output = Self;

            fn sub(self, rhs: Self) -> Self::Output {
                $unit_type(self.0 - rhs.0)
            }
        }

        impl<T> $crate::datatype::common::SubAssign for $unit_type<T>
        where
            T: $crate::datatype::common::SubAssign,
        {
            fn sub_assign(&mut self, rhs: Self) {
                self.0 -= rhs.0;
            }
        }

        impl<T> $crate::datatype::common::Mul<T> for $unit_type<T>
        where
            T: $crate::datatype::common::Mul<Output = T> + Copy,
        {
            type Output = Self;

            fn mul(self, rhs: T) -> Self::Output {
                $unit_type(self.0 * rhs)
            }
        }

        impl<T> $crate::datatype::common::MulAssign<T> for $unit_type<T>
        where
            T: $crate::datatype::common::MulAssign + Copy,
        {
            fn mul_assign(&mut self, rhs: T) {
                self.0 *= rhs;
            }
        }

        impl<T> $crate::datatype::common::Div<T> for $unit_type<T>
        where
            T: $crate::datatype::common::Div<Output = T> + Copy,
        {
            type Output = Self;

            fn div(self, rhs: T) -> Self::Output {
                $unit_type(self.0 / rhs)
            }
        }

        impl<T> $crate::datatype::common::DivAssign<T> for $unit_type<T>
        where
            T: $crate::datatype::common::DivAssign + Copy,
        {
            fn div_assign(&mut self, rhs: T) {
                self.0 /= rhs;
            }
        }

        impl<T> $crate::datatype::common::Neg for $unit_type<T>
        where
            T: $crate::datatype::common::Neg<Output = T>,
        {
            type Output = Self;

            fn neg(self) -> Self::Output {
                $unit_type(-self.0)
            }
        }

        impl<T> $crate::datatype::common::Zero for $unit_type<T>
        where
            T: $crate::datatype::common::Zero,
        {
            fn zero() -> Self {
                $unit_type(T::zero())
            }

            fn is_zero(&self) -> bool {
                self.0.is_zero()
            }
        }

        impl<T> $crate::datatype::common::fmt::Display for $unit_type<T>
        where
            T: $crate::datatype::common::fmt::Display,
        {
            fn fmt(
                &self,
                f: &mut $crate::datatype::common::fmt::Formatter<'_>,
            ) -> $crate::datatype::common::fmt::Result {
                write!(f, "{}", self.0)
            }
        }
    };
}
