//
// Copyright (C) 2026 David Cattermole.
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

//! Generic sorted key-value map backed by parallel `Vec`s.
//!
//! [`SortedVecMap`] provides a `HashMap`-like API but stores keys and
//! values in two sorted parallel `Vec`s (SoA layout) for contiguous,
//! cache-friendly storage.  Keys are kept sorted ascending so that
//! binary search gives O(log n) lookups.

use std::ops::{Index, IndexMut};

/// HashMap-like wrapper backed by sorted parallel `Vec`s.
///
/// Keys are kept sorted ascending. Lookups use binary search (O(log n)).
/// Insertions and removals are O(n) due to shifting elements.
#[derive(Clone)]
pub struct SortedVecMap<K: Ord, V> {
    keys: Vec<K>,
    values: Vec<V>,
}

impl<K: Ord, V> SortedVecMap<K, V> {
    pub fn new() -> Self {
        SortedVecMap {
            keys: Vec::new(),
            values: Vec::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> Self {
        SortedVecMap {
            keys: Vec::with_capacity(capacity),
            values: Vec::with_capacity(capacity),
        }
    }

    pub fn reserve(&mut self, additional: usize) {
        self.keys.reserve(additional);
        self.values.reserve(additional);
    }

    pub fn capacity(&self) -> usize {
        self.keys.capacity()
    }

    pub fn len(&self) -> usize {
        self.keys.len()
    }

    pub fn is_empty(&self) -> bool {
        self.keys.is_empty()
    }

    pub fn clear(&mut self) {
        self.keys.clear();
        self.values.clear();
    }

    #[inline]
    fn search(&self, key: &K) -> Result<usize, usize> {
        self.keys.binary_search(key)
    }

    pub fn contains_key(&self, key: &K) -> bool {
        self.search(key).is_ok()
    }

    pub fn get(&self, key: &K) -> Option<&V> {
        self.search(key).ok().map(|i| &self.values[i])
    }

    pub fn get_mut(&mut self, key: &K) -> Option<&mut V> {
        match self.search(key) {
            Ok(i) => Some(&mut self.values[i]),
            Err(_) => None,
        }
    }

    pub fn insert(&mut self, key: K, value: V) -> Option<V> {
        match self.search(&key) {
            Ok(idx) => {
                let old = std::mem::replace(&mut self.values[idx], value);
                Some(old)
            }
            Err(idx) => {
                self.keys.insert(idx, key);
                self.values.insert(idx, value);
                None
            }
        }
    }

    pub fn remove(&mut self, key: &K) -> Option<V> {
        match self.search(key) {
            Ok(idx) => {
                self.keys.remove(idx);
                Some(self.values.remove(idx))
            }
            Err(_) => None,
        }
    }

    pub fn keys(&self) -> impl Iterator<Item = &K> {
        self.keys.iter()
    }

    pub fn values(&self) -> impl Iterator<Item = &V> {
        self.values.iter()
    }

    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut V> {
        self.values.iter_mut()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&K, &V)> {
        self.keys.iter().zip(self.values.iter())
    }

    pub fn iter_mut(&mut self) -> impl Iterator<Item = (&K, &mut V)> {
        self.keys.iter().zip(self.values.iter_mut())
    }
}

impl<K: Ord, V> Default for SortedVecMap<K, V> {
    fn default() -> Self {
        Self::new()
    }
}

impl<K: Ord, V> Index<&K> for SortedVecMap<K, V> {
    type Output = V;

    fn index(&self, key: &K) -> &Self::Output {
        let idx = self.search(key).expect("key not found");
        &self.values[idx]
    }
}

impl<K: Ord, V> IndexMut<&K> for SortedVecMap<K, V> {
    fn index_mut(&mut self, key: &K) -> &mut Self::Output {
        let idx = self.search(key).expect("key not found");
        &mut self.values[idx]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_state() {
        let m: SortedVecMap<u32, f64> = SortedVecMap::new();
        assert!(m.is_empty());
        assert_eq!(m.len(), 0);
    }

    #[test]
    fn test_insert_and_get() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(0u32, 1.0f64);
        assert_eq!(m.len(), 1);
        assert!(m.get(&0).is_some());
        assert!(m.get(&99).is_none());
    }

    #[test]
    fn test_insert_overwrite() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        let old = m.insert(3u32, 1.0f64);
        assert!(old.is_none());
        let old2 = m.insert(3u32, 2.0f64);
        assert!(old2.is_some());
        assert!((old2.unwrap() - 1.0f64).abs() < 1e-10);
        assert_eq!(m.len(), 1);
        assert!((*m.get(&3).unwrap() - 2.0f64).abs() < 1e-10);
    }

    #[test]
    fn test_remove() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(5u32, 5.0f64);
        let removed = m.remove(&5);
        assert!(removed.is_some());
        assert!((removed.unwrap() - 5.0f64).abs() < 1e-10);
        assert!(m.is_empty());
        assert!(m.remove(&5).is_none());
    }

    #[test]
    fn test_contains_key() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(7u32, 7.0f64);
        assert!(m.contains_key(&7));
        assert!(!m.contains_key(&8));
    }

    #[test]
    fn test_sorted_key_order() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        for &k in &[30u32, 10, 20] {
            m.insert(k, k as f64);
        }
        let keys: Vec<u32> = m.keys().copied().collect();
        assert_eq!(keys, vec![10, 20, 30]);
    }

    #[test]
    fn test_iteration() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        for i in 0u32..5 {
            m.insert(i, i as f64);
        }
        let sum: f64 = m.values().sum();
        assert!((sum - 10.0).abs() < 1e-10);
    }

    #[test]
    fn test_index() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(2u32, 42.0f64);
        assert!((m[&2] - 42.0f64).abs() < 1e-10);
    }

    #[test]
    fn test_index_mut() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(2u32, 1.0f64);
        m[&2] = 99.0f64;
        assert!((*m.get(&2).unwrap() - 99.0f64).abs() < 1e-10);
    }

    #[test]
    fn test_clear() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::new();
        m.insert(1u32, 1.0f64);
        m.clear();
        assert!(m.is_empty());
    }

    #[test]
    fn test_with_capacity() {
        let mut m: SortedVecMap<u32, f64> = SortedVecMap::with_capacity(16);
        for i in 0u32..10 {
            m.insert(i, i as f64);
        }
        assert_eq!(m.len(), 10);
        assert!(m.capacity() >= 16);
    }
}
