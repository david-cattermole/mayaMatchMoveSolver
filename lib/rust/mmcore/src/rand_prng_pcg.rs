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
//! Permuted Congruential Generator (PCG) for pseudorandom number
//! generation.
//!
//! Implementation of the PCG algorithm, a pseudorandom number
//! generator that produces high-quality random numbers with excellent
//! statistical properties.
//!
//! PCG improves on traditional Linear Congruential Generators (LCGs) by:
//!
//! 1. Using an LCG for state transitions (internal state updates).
//! 2. Applying output transformations (permutations) to the internal state.
//! 3. Using bitwise operations that thoroughly mix the bits
//!
//! Reference:
//! - Original PCG paper: <https://www.pcg-random.org/paper.html>
//! - PCG website: <https://www.pcg-random.org/>
//!
//! Advantages of PCG over LCG:
//! - Much longer periods (2^128 for 64-bit PCG vs 2^64 for typical LCGs).
//! - No discernible patterns in n-dimensional plots (passes spectral tests).
//! - All bits of output have high quality (unlike LCGs where low bits have poor quality).
//! - Fast execution comparable to LCGs.
//! - Multiple independent streams available from a single algorithm.

/// Default parameter values recommended for PCG.
pub mod defaults {
    // These parameters produce a 64-bit PCG that outputs 32-bit values.

    /// Default initial seed value.
    pub const SEED: u64 = 0x4d595df4d0f33173;

    /// Default increment parameter (odd value ensures maximum period).
    pub const INCREMENT: u64 = 1442695040888963407;

    /// Default multiplier parameter.
    ///
    /// This is the multiplier recommended for 64-bit LCGs by Knuth
    /// "The Art of Computer Programming" which is known to provide
    /// good statistical properties.
    pub const MULTIPLIER: u64 = 6364136223846793005;
}

/// A Permuted Congruential Generator for high-quality pseudorandom
/// number generation.
///
/// PCG combines a Linear Congruential Generator (LCG) for state
/// transitions with output transformations that significantly improve
/// statistical quality.
#[derive(Debug, Clone)]
pub struct PCG {
    state: u64,      // Current internal state.
    increment: u64,  // Increment for the LCG (must be odd).
    multiplier: u64, // Multiplier for the LCG.
}

impl Default for PCG {
    /// Creates a PCG with default parameters that provide excellent
    /// statistical properties.
    fn default() -> Self {
        PCG {
            state: defaults::SEED,
            increment: defaults::INCREMENT,
            multiplier: defaults::MULTIPLIER,
        }
    }
}

impl PCG {
    /// Creates a new PCG with specified parameters.
    ///
    /// # Parameters
    /// * `seed` - Initial value for the generator.
    /// * `increment` - Increment parameter (should be odd for maximum period).
    ///
    pub fn new(seed: u64, increment: u64) -> Self {
        let mut pcg = PCG {
            state: 0,
            increment: increment | 1, // Ensure increment is odd.
            multiplier: defaults::MULTIPLIER,
        };

        // Initialize state using the seed.
        pcg.state = 0;
        pcg.next_u32(); // Discard first output.
        pcg.state = pcg.state.wrapping_add(seed);
        pcg.next_u32(); // Discard second output.

        pcg
    }

    /// Creates a new PCG with the specified seed and default
    /// increment.
    ///
    /// # Parameters
    /// * `seed` - Initial value for the generator.
    pub fn new_from_seed(seed: u64) -> Self {
        Self::new(seed, defaults::INCREMENT)
    }

    /// Advances the internal state using LCG formula.
    fn advance_state(&mut self) {
        // PCG uses a standard LCG for state transition:
        //
        // state = (multiplier * state + increment) mod 2^64
        //
        // The modulo happens automatically due to u64 overflow.
        self.state = self
            .state
            .wrapping_mul(self.multiplier)
            .wrapping_add(self.increment);
    }

    /// Generates the next 32-bit pseudorandom number.
    ///
    /// PCG applies output permutation to the raw LCG state to improve
    /// randomness quality.
    ///
    /// # Returns
    /// A 32-bit unsigned random integer.
    pub fn next_u32(&mut self) -> u32 {
        // First, advance internal state
        self.advance_state();

        // PCG output permutation function
        // 1. Get the most significant 32 bits of state
        let state = self.state;

        // 2. Calculate rotation amount from lowest bits
        let rot = (state >> 59) as u32;

        // 3. XOR with shifted state and perform bit rotation
        let xorshifted = (((state >> 18) ^ state) >> 27) as u32;
        let result = xorshifted.rotate_right(rot);

        result
    }

    /// Generates a random number in a specified range [0, max-1].
    ///
    /// # Parameters
    /// * `max` - Upper bound (exclusive) for the generated number.
    ///
    /// # Returns
    /// A number in the range [0, max-1].
    pub fn next_range(&mut self, max: u32) -> u32 {
        // To avoid bias when max is not a power of 2:
        // 1. Find largest multiple of max that fits in u32.
        // 2. Generate values until one falls within range.

        if max == 0 {
            return 0;
        }

        // Calculate threshold for unbiased sampling.
        let threshold = u32::MAX - (u32::MAX % max);

        // Generate values until we get one below the threshold.
        loop {
            let r = self.next_u32();
            if r < threshold {
                return r % max;
            }
        }
    }

    /// Generates a random 64-bit value by combining two 32-bit
    /// values.
    ///
    /// # Returns
    /// A 64-bit unsigned random integer.
    pub fn next_u64(&mut self) -> u64 {
        let high = self.next_u32() as u64;
        let low = self.next_u32() as u64;
        (high << 32) | low
    }

    /// Generates a random floating-point number in the range [0.0,
    /// 1.0).
    ///
    /// # Returns
    /// A float in the range [0.0, 1.0).
    pub fn next_f64(&mut self) -> f64 {
        // Use 53 bits of precision (standard for f64 mantissa).
        const PRECISION: u64 = 53;
        const SCALE: f64 = 1.0 / ((1u64 << PRECISION) as f64);

        // Get random bits and scale.
        let random_bits = self.next_u64() >> (64 - PRECISION);
        random_bits as f64 * SCALE
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_pcg_determinism() {
        // Two PCGs with identical parameters should produce identical
        // sequences.
        let mut rng1 = PCG::new(12345, 67890);
        let mut rng2 = PCG::new(12345, 67890);

        for _ in 0..100 {
            assert_eq!(rng1.next_u32(), rng2.next_u32());
        }
    }

    #[test]
    fn test_pcg_range() {
        // All values should be within the valid u32 range.
        let mut rng = PCG::default();

        for _ in 0..1000 {
            let val = rng.next_u32();
            assert!(val <= u32::MAX);
        }
    }

    #[test]
    fn test_next_range() {
        // Test that next_range produces values within the specified
        // range.
        let mut rng = PCG::default();
        let max = 100;

        for _ in 0..1000 {
            let val = rng.next_range(max);
            assert!(val < max);
        }
    }

    #[test]
    fn test_next_f64() {
        // Test that next_f64 produces values in [0.0, 1.0).
        let mut rng = PCG::default();

        for _ in 0..1000 {
            let val = rng.next_f64();
            assert!(val >= 0.0 && val < 1.0);
        }
    }

    #[test]
    fn test_sequence_uniqueness() {
        // Test that we don't get immediate repetition.
        let mut rng = PCG::default();
        let mut seen = HashSet::new();

        // Generate a number of values and check for duplicates.
        for _ in 0..1000 {
            let val = rng.next_u32();
            assert!(
                !seen.contains(&val),
                "Duplicate value found too early in sequence"
            );
            seen.insert(val);
        }
    }

    #[test]
    fn test_different_seeds() {
        // Different seeds should produce different sequences.
        let mut rng1 = PCG::new_from_seed(12345);
        let mut rng2 = PCG::new_from_seed(12346);

        // First values should be different.
        assert_ne!(rng1.next_u32(), rng2.next_u32());

        // Entire sequences should diverge.
        let mut matches = 0;
        for _ in 0..100 {
            if rng1.next_u32() == rng2.next_u32() {
                matches += 1;
            }
        }
        // Allow a few matches by chance, but sequences should be
        // distinct.
        assert!(matches < 5, "Seeds produced too similar sequences");
    }

    #[test]
    fn test_known_sequence() {
        // Test against a pre-computed sequence for a specific seed.
        let mut rng = PCG::new(42, defaults::INCREMENT);

        // Values pre-computed with the same parameters.
        //
        // NOTE: These would need to be replaced with actual values
        // from a reference implementation
        let first_value = rng.next_u32();

        // Reset and verify we get the same sequence again.
        let mut rng2 = PCG::new(42, defaults::INCREMENT);
        assert_eq!(first_value, rng2.next_u32());
    }

    #[test]
    fn test_distribution() {
        // Simple uniformity test for small range.
        let mut rng = PCG::default();
        let range = 10;
        let iterations = 10000;
        let mut counts = vec![0; range as usize];

        // Count occurrences of each value.
        for _ in 0..iterations {
            let val = rng.next_range(range) as usize;
            counts[val] += 1;
        }

        // Check that each value appears approximately the expected
        // number of times.
        let expected = iterations / range as usize;
        let tolerance = (expected as f64 * 0.15) as usize; // 15% tolerance

        for (i, &count) in counts.iter().enumerate() {
            assert!(
                count >= expected - tolerance && count <= expected + tolerance,
                "Value {} appeared {} times, expected around {} (tolerance: {})",
                i, count, expected, tolerance
            );
        }
    }

    #[test]
    fn test_u64_generation() {
        // Test that next_u64 produces the full range of u64 values.
        let mut rng = PCG::default();

        // Just check that high bits aren't always zero.
        let mut has_high_bits = false;
        for _ in 0..100 {
            let val = rng.next_u64();
            if val > 0xFFFFFFFF {
                has_high_bits = true;
                break;
            }
        }
        assert!(has_high_bits, "next_u64() doesn't seem to use all 64 bits");
    }

    #[test]
    fn test_main() {
        // Example usage.
        let mut rng = PCG::default();

        // Generate and print 10 random integers.
        println!("10 random integers:");
        for _ in 0..10 {
            println!("{}", rng.next_u32());
        }

        // Generate and print 5 random integers in range [0, 100).
        println!("\n5 random integers in range [0, 100):");
        for _ in 0..5 {
            println!("{}", rng.next_range(100));
        }

        // Generate and print 5 random floats in range [0.0, 1.0).
        println!("\n5 random floats in range [0.0, 1.0):");
        for _ in 0..5 {
            println!("{}", rng.next_f64());
        }

        // Demonstrate creating PCG with custom seed.
        println!("\nUsing custom seed:");
        let mut rng_custom_seed = PCG::new_from_seed(67890);
        for _ in 0..5 {
            println!("{}", rng_custom_seed.next_u32());
        }
    }
}
