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

//! Bundle Position data structure.

use mmcore::collections::SortedVecMap;
use nalgebra::Point3;
use std::ops::{Index, IndexMut};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// The index of a marker.
pub type MarkerIndex = usize;

/// HashMap-like wrapper for storing 3-D bundle positions keyed by marker index.
///
/// Backed by a `SortedVecMap` for contiguous, cache-friendly storage.
#[derive(Clone)]
pub struct BundlePositions {
    inner: SortedVecMap<MarkerIndex, Point3<f64>>,
}

impl BundlePositions {
    pub fn new() -> BundlePositions {
        BundlePositions {
            inner: SortedVecMap::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> BundlePositions {
        BundlePositions {
            inner: SortedVecMap::with_capacity(capacity),
        }
    }

    pub fn reserve(&mut self, additional: usize) {
        self.inner.reserve(additional);
    }

    pub fn capacity(&self) -> usize {
        self.inner.capacity()
    }

    pub fn keys(&self) -> impl Iterator<Item = &MarkerIndex> {
        self.inner.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &Point3<f64>> {
        self.inner.values()
    }

    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut Point3<f64>> {
        self.inner.values_mut()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&MarkerIndex, &Point3<f64>)> {
        self.inner.iter()
    }

    pub fn iter_mut(
        &mut self,
    ) -> impl Iterator<Item = (&MarkerIndex, &mut Point3<f64>)> {
        self.inner.iter_mut()
    }

    pub fn insert(
        &mut self,
        marker_index: MarkerIndex,
        bundle_position: Point3<f64>,
    ) -> Option<Point3<f64>> {
        self.inner.insert(marker_index, bundle_position)
    }

    pub fn remove(
        &mut self,
        marker_index: &MarkerIndex,
    ) -> Option<Point3<f64>> {
        self.inner.remove(marker_index)
    }

    pub fn get(&self, marker_index: &MarkerIndex) -> Option<&Point3<f64>> {
        self.inner.get(marker_index)
    }

    pub fn get_mut(
        &mut self,
        marker_index: &MarkerIndex,
    ) -> Option<&mut Point3<f64>> {
        self.inner.get_mut(marker_index)
    }

    pub fn get_point_at_index(
        &self,
        marker_index: &MarkerIndex,
    ) -> Point3<f64> {
        self.inner[marker_index]
    }

    pub fn contains_key(&self, marker_index: &MarkerIndex) -> bool {
        self.inner.contains_key(marker_index)
    }

    pub fn clear(&mut self) {
        self.inner.clear();
    }

    pub fn len(&self) -> usize {
        self.inner.len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}

impl Default for BundlePositions {
    fn default() -> Self {
        Self::new()
    }
}

impl Index<&MarkerIndex> for BundlePositions {
    type Output = Point3<f64>;

    fn index(&self, marker_index: &MarkerIndex) -> &Self::Output {
        &self.inner[marker_index]
    }
}

impl IndexMut<&MarkerIndex> for BundlePositions {
    fn index_mut(&mut self, marker_index: &MarkerIndex) -> &mut Self::Output {
        &mut self.inner[marker_index]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::Point3;

    fn pt(v: f64) -> Point3<f64> {
        Point3::new(v, v * 2.0, v * 3.0)
    }

    #[test]
    fn test_sorted_key_order() {
        let mut b = BundlePositions::new();
        for &k in &[30usize, 10, 20] {
            b.insert(k, pt(k as f64));
        }
        let keys: Vec<usize> = b.keys().copied().collect();
        assert_eq!(keys, vec![10, 20, 30]);
    }

    #[test]
    fn test_get_point_at_index() {
        let mut b = BundlePositions::new();
        b.insert(4, pt(4.0));
        let p = b.get_point_at_index(&4);
        assert_eq!(p.x, 4.0);
    }
}
