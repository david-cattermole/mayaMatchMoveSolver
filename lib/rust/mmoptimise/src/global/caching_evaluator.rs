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

//! Caching wrapper for expensive evaluators.
//!
//! This module provides a thread-safe caching wrapper that prevents
//! redundant evaluations of identical parameter vectors. This is
//! particularly useful for expensive evaluation functions like camera
//! solves where the same parameters may be evaluated multiple times
//! (e.g., when Differential Evolution clamps trial vectors to bounds).
//!
//! # Example
//!
//! ```ignore
//! use mmoptimise::global::{CachingEvaluator, Evaluator};
//!
//! struct ExpensiveEvaluator;
//! impl Evaluator for ExpensiveEvaluator {
//!     fn evaluate(&self, x: &[f64]) -> f64 {
//!         // Expensive computation here...
//!         x.iter().sum()
//!     }
//! }
//!
//! let evaluator = ExpensiveEvaluator;
//! let cached = CachingEvaluator::new(evaluator);
//!
//! // First call computes the result
//! let cost1 = cached.evaluate(&[1.0, 2.0, 3.0]);
//!
//! // Second call with same parameters returns cached result
//! let cost2 = cached.evaluate(&[1.0, 2.0, 3.0]);
//!
//! assert_eq!(cost1, cost2);
//!
//! let (hits, misses) = cached.cache_stats();
//! assert_eq!(hits, 1);
//! assert_eq!(misses, 1);
//! ```

use crate::global::Evaluator;
use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::RwLock;

/// Default precision for discretizing floating-point values.
/// 10 decimal places (1e-10 precision).
const DEFAULT_PRECISION: u32 = 10;

/// Cache key using discretized floating-point values.
///
/// Floating-point values are discretized to i64 to enable reliable
/// hashing and equality comparison. The precision determines how
/// many decimal places are preserved.
#[derive(Hash, Eq, PartialEq, Clone)]
struct CacheKey(Vec<i64>);

impl CacheKey {
    /// Create a cache key from a parameter vector.
    ///
    /// # Arguments
    ///
    /// * `params` - Parameter vector to convert
    /// * `precision` - Number of decimal places to preserve
    ///
    /// # Example
    ///
    /// With precision=3, the value 1.2345 becomes 1235 (rounded).
    #[inline]
    fn from_params(params: &[f64], precision: u32) -> Self {
        let scale = 10f64.powi(precision as i32);
        CacheKey(params.iter().map(|&x| (x * scale).round() as i64).collect())
    }
}

/// Thread-safe caching wrapper for any Evaluator.
///
/// This wrapper caches evaluation results using discretized parameter
/// keys to avoid floating-point comparison issues. The cache uses
/// `RwLock` for thread safety, allowing multiple concurrent reads
/// (cache hits) while serializing writes (cache misses).
///
/// # Thread Safety
///
/// The wrapper is designed for parallel evaluation scenarios like
/// Differential Evolution. Multiple threads can simultaneously:
/// - Check the cache for existing results (read lock)
/// - Compute and store new results (write lock)
///
/// # Memory Management
///
/// The cache grows unbounded during optimization. For long-running
/// optimizations, call `clear_cache()` between runs or generations
/// if memory becomes a concern.
pub struct CachingEvaluator<E> {
    /// The wrapped evaluator.
    inner: E,
    /// Thread-safe cache mapping discretized parameters to costs.
    cache: RwLock<HashMap<CacheKey, f64>>,
    /// Discretization precision (number of decimal places).
    precision: u32,
    /// Number of cache hits (for statistics).
    hits: AtomicUsize,
    /// Number of cache misses (for statistics).
    misses: AtomicUsize,
}

impl<E> CachingEvaluator<E> {
    /// Create a new caching evaluator with default precision.
    ///
    /// Uses 10 decimal places (1e-10 precision) for discretization.
    ///
    /// # Arguments
    ///
    /// * `inner` - The evaluator to wrap
    pub fn new(inner: E) -> Self {
        Self::with_precision(inner, DEFAULT_PRECISION)
    }

    /// Create a new caching evaluator with custom precision.
    ///
    /// # Arguments
    ///
    /// * `inner` - The evaluator to wrap
    /// * `precision` - Number of decimal places for discretization
    ///
    /// # Precision Guidelines
    ///
    /// - High precision (10-15): More cache misses, fewer false hits
    /// - Low precision (3-6): More cache hits, risk of false hits
    /// - Default (10): Good balance for most optimization problems
    pub fn with_precision(inner: E, precision: u32) -> Self {
        Self {
            inner,
            cache: RwLock::new(HashMap::new()),
            precision,
            hits: AtomicUsize::new(0),
            misses: AtomicUsize::new(0),
        }
    }

    /// Clear the cache.
    ///
    /// Call this between optimization runs to free memory and
    /// reset the cache state.
    pub fn clear_cache(&self) {
        self.cache.write().unwrap().clear();
    }

    /// Get cache statistics.
    ///
    /// # Returns
    ///
    /// A tuple of (hits, misses) counts.
    pub fn cache_stats(&self) -> (usize, usize) {
        (
            self.hits.load(Ordering::Relaxed),
            self.misses.load(Ordering::Relaxed),
        )
    }

    /// Get the current cache size.
    ///
    /// # Returns
    ///
    /// Number of unique parameter vectors cached.
    pub fn cache_size(&self) -> usize {
        self.cache.read().unwrap().len()
    }

    /// Reset the cache statistics counters.
    pub fn reset_stats(&self) {
        self.hits.store(0, Ordering::Relaxed);
        self.misses.store(0, Ordering::Relaxed);
    }
}

impl<E: Evaluator + Sync> Evaluator for CachingEvaluator<E> {
    /// Evaluate with caching.
    ///
    /// Checks the cache first (read lock). On cache miss, computes
    /// the result using the wrapped evaluator and stores it (write lock).
    ///
    /// # Arguments
    ///
    /// * `x` - Parameter vector to evaluate
    ///
    /// # Returns
    ///
    /// The cost for the given parameters (cached or newly computed).
    fn evaluate(&self, x: &[f64]) -> f64 {
        let key = CacheKey::from_params(x, self.precision);

        // Fast path: check cache with read lock
        if let Some(&cost) = self.cache.read().unwrap().get(&key) {
            self.hits.fetch_add(1, Ordering::Relaxed);
            return cost;
        }

        // Cache miss: compute result
        self.misses.fetch_add(1, Ordering::Relaxed);
        let cost = self.inner.evaluate(x);

        // Store result with write lock
        self.cache.write().unwrap().insert(key, cost);

        cost
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicUsize;
    use std::sync::Arc;

    /// Test evaluator that counts how many times it's called.
    struct CountingEvaluator {
        call_count: AtomicUsize,
    }

    impl CountingEvaluator {
        fn new() -> Self {
            Self {
                call_count: AtomicUsize::new(0),
            }
        }

        fn count(&self) -> usize {
            self.call_count.load(Ordering::Relaxed)
        }
    }

    impl Evaluator for CountingEvaluator {
        fn evaluate(&self, x: &[f64]) -> f64 {
            self.call_count.fetch_add(1, Ordering::Relaxed);
            x.iter().map(|v| v * v).sum()
        }
    }

    #[test]
    fn test_cache_prevents_duplicate_evaluations() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        // First evaluation
        let cost1 = cached.evaluate(&[1.0, 2.0, 3.0]);
        assert_eq!(cached.inner.count(), 1);

        // Same parameters - should use cache
        let cost2 = cached.evaluate(&[1.0, 2.0, 3.0]);
        assert_eq!(cached.inner.count(), 1); // Still 1!
        assert_eq!(cost1, cost2);

        // Different parameters - should evaluate
        let _cost3 = cached.evaluate(&[4.0, 5.0, 6.0]);
        assert_eq!(cached.inner.count(), 2);

        // Check stats
        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 1);
        assert_eq!(misses, 2);
    }

    #[test]
    fn test_cache_stats() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        // Initial stats
        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 0);
        assert_eq!(misses, 0);

        // First eval - miss
        cached.evaluate(&[1.0]);
        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 0);
        assert_eq!(misses, 1);

        // Same params - hit
        cached.evaluate(&[1.0]);
        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 1);
        assert_eq!(misses, 1);

        // Different params - miss
        cached.evaluate(&[2.0]);
        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 1);
        assert_eq!(misses, 2);
    }

    #[test]
    fn test_cache_size() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        assert_eq!(cached.cache_size(), 0);

        cached.evaluate(&[1.0]);
        assert_eq!(cached.cache_size(), 1);

        cached.evaluate(&[1.0]); // Duplicate
        assert_eq!(cached.cache_size(), 1);

        cached.evaluate(&[2.0]);
        assert_eq!(cached.cache_size(), 2);
    }

    #[test]
    fn test_cache_clear() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        cached.evaluate(&[1.0]);
        cached.evaluate(&[2.0]);
        assert_eq!(cached.cache_size(), 2);

        cached.clear_cache();
        assert_eq!(cached.cache_size(), 0);

        // After clear, same params should miss
        cached.evaluate(&[1.0]);
        assert_eq!(cached.inner.count(), 3); // New evaluation
    }

    #[test]
    fn test_reset_stats() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        cached.evaluate(&[1.0]);
        cached.evaluate(&[1.0]);

        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 1);
        assert_eq!(misses, 1);

        cached.reset_stats();

        let (hits, misses) = cached.cache_stats();
        assert_eq!(hits, 0);
        assert_eq!(misses, 0);
    }

    #[test]
    fn test_precision_affects_caching() {
        let inner = CountingEvaluator::new();
        // Low precision - 2 decimal places
        let cached = CachingEvaluator::with_precision(inner, 2);

        // These should be considered the same with precision=2
        cached.evaluate(&[1.001]);
        cached.evaluate(&[1.002]);

        // With precision=2, 1.001 -> 100, 1.002 -> 100 (both round to same)
        assert_eq!(cached.inner.count(), 1);

        // This should be different
        cached.evaluate(&[1.01]);
        assert_eq!(cached.inner.count(), 2);
    }

    #[test]
    fn test_concurrent_access() {
        use std::thread;

        let inner = CountingEvaluator::new();
        let cached = Arc::new(CachingEvaluator::new(inner));

        let mut handles = vec![];

        // Spawn multiple threads evaluating the same parameters
        for _ in 0..10 {
            let cached_clone = Arc::clone(&cached);
            handles.push(thread::spawn(move || {
                for i in 0..100 {
                    let params = vec![i as f64];
                    cached_clone.evaluate(&params);
                }
            }));
        }

        for handle in handles {
            handle.join().unwrap();
        }

        // Should have exactly 100 unique evaluations
        assert_eq!(cached.inner.count(), 100);
        assert_eq!(cached.cache_size(), 100);

        // Total calls = 10 threads * 100 params = 1000
        // Unique = 100, so hits = 900
        let (hits, misses) = cached.cache_stats();
        assert_eq!(misses, 100);
        assert_eq!(hits, 900);
    }

    #[test]
    fn test_negative_and_zero_values() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        cached.evaluate(&[-1.0, 0.0, 1.0]);
        cached.evaluate(&[-1.0, 0.0, 1.0]);

        assert_eq!(cached.inner.count(), 1);

        cached.evaluate(&[0.0, 0.0, 0.0]);
        assert_eq!(cached.inner.count(), 2);
    }

    #[test]
    fn test_empty_params() {
        let inner = CountingEvaluator::new();
        let cached = CachingEvaluator::new(inner);

        cached.evaluate(&[]);
        cached.evaluate(&[]);

        assert_eq!(cached.inner.count(), 1);
    }
}
