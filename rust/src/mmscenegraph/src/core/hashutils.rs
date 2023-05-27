//
// Copyright (C) 2020, 2021 David Cattermole.
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

use rand::rngs::SmallRng;
use rand::{Rng, SeedableRng};
use rustc_hash::FxHasher;
use std::hash::{Hash, Hasher};
use std::mem;

use crate::constant::HashValue;

pub fn calculate_hash<T: Hash>(t: &T) -> HashValue {
    let mut s = FxHasher::default();
    t.hash(&mut s);
    s.finish()
}

pub fn generate_id_from_name(name: &str) -> HashValue {
    calculate_hash::<&str>(&name)
}

pub fn generate_random_id() -> HashValue {
    // Create small, cheap to initialize and fast RNG with a random seed.
    // The randomness is supplied by the operating system.
    let mut rng = SmallRng::from_entropy();
    rng.gen()
}

// https://stackoverflow.com/questions/39638363/how-can-i-use-a-hashmap-with-f64-as-key-in-rust
fn integer_decode_f64(val: f64) -> (u64, i16, i8) {
    let bits: u64 = unsafe { mem::transmute(val) };
    let sign: i8 = if bits >> 63 == 0 { 1 } else { -1 };
    let mut exponent: i16 = ((bits >> 52) & 0x7ff) as i16;
    let mantissa = if exponent == 0 {
        (bits & 0xfffffffffffff) << 1
    } else {
        (bits & 0xfffffffffffff) | 0x10000000000000
    };

    exponent -= 1023 + 52;
    (mantissa, exponent, sign)
}

/// Returns the mantissa, exponent and sign as integers.
fn integer_decode_f32(val: f32) -> (u64, i16, i8) {
    let bits: u32 = unsafe { mem::transmute(val) };
    let sign: i8 = if bits >> 31 == 0 { 1 } else { -1 };
    let mut exponent: i16 = ((bits >> 23) & 0xff) as i16;
    let mantissa = if exponent == 0 {
        (bits & 0x7fffff) << 1
    } else {
        (bits & 0x7fffff) | 0x800000
    };
    // Exponent bias + mantissa shift
    exponent -= 127 + 23;
    (mantissa as u64, exponent, sign)
}

#[derive(Hash, Eq, PartialEq)]
pub struct HashableF64((u64, i16, i8));

impl HashableF64 {
    pub fn new(val: f64) -> HashableF64 {
        HashableF64(integer_decode_f64(val))
    }
}

#[derive(Hash, Eq, PartialEq)]
pub struct HashableF32((u64, i16, i8));

impl HashableF32 {
    pub fn new(val: f32) -> HashableF32 {
        HashableF32(integer_decode_f32(val))
    }
}
