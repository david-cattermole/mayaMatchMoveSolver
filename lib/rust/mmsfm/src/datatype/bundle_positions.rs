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

use nalgebra::Point3;
use std::collections::BTreeMap;
use std::ops::{Index, IndexMut};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// The index of a marker.
pub type MarkerIndex = usize;

#[derive(Clone)]
pub struct BundlePositions {
    // TODO: The underlying data structure should be completely
    // changed to using contiguous memory for both keys and values.
    //
    // The aim is to provide a HashMap-like API but backed by a
    // different data structure to avoid the hashing overhead.
    //
    // The API should stay the same or similar to the HashMap because
    // we want this to be a (almost) drop-in replacement for the
    // direct HashMap.
    data: BTreeMap<MarkerIndex, Point3<f64>>,
    // TODO: Could this struct also combine the "marker_indices"
    // variable that is often used through-out the code?
}

impl BundlePositions {
    pub fn new() -> BundlePositions {
        BundlePositions {
            data: BTreeMap::new(),
        }
    }

    pub fn keys(
        &self,
    ) -> std::collections::btree_map::Keys<'_, MarkerIndex, Point3<f64>> {
        self.data.keys()
    }

    pub fn values(
        &self,
    ) -> std::collections::btree_map::Values<'_, MarkerIndex, Point3<f64>> {
        self.data.values()
    }

    pub fn values_mut(
        &mut self,
    ) -> std::collections::btree_map::ValuesMut<'_, MarkerIndex, Point3<f64>>
    {
        self.data.values_mut()
    }

    pub fn iter(
        &self,
    ) -> std::collections::btree_map::Iter<'_, MarkerIndex, Point3<f64>> {
        self.data.iter()
    }

    pub fn iter_mut(
        &mut self,
    ) -> std::collections::btree_map::IterMut<'_, MarkerIndex, Point3<f64>>
    {
        self.data.iter_mut()
    }

    pub fn insert(
        &mut self,
        marker_index: MarkerIndex,
        bundle_position: Point3<f64>,
    ) -> Option<Point3<f64>> {
        self.data.insert(marker_index, bundle_position)
    }

    pub fn remove(
        &mut self,
        marker_index: &MarkerIndex,
    ) -> Option<Point3<f64>> {
        self.data.remove(marker_index)
    }

    pub fn get(&self, marker_index: &MarkerIndex) -> Option<&Point3<f64>> {
        self.data.get(marker_index)
    }

    pub fn get_mut(
        &mut self,
        marker_index: &MarkerIndex,
    ) -> Option<&mut Point3<f64>> {
        self.data.get_mut(marker_index)
    }

    pub fn get_point_at_index(
        &self,
        marker_index: &MarkerIndex,
    ) -> Point3<f64> {
        self.data[marker_index]
    }

    pub fn contains_key(&self, marker_index: &MarkerIndex) -> bool {
        self.data.contains_key(marker_index)
    }

    pub fn clear(&mut self) {
        self.data.clear();
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
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
        &self.data[marker_index]
    }
}

impl IndexMut<&MarkerIndex> for BundlePositions {
    fn index_mut(&mut self, marker_index: &MarkerIndex) -> &mut Self::Output {
        self.data
            .get_mut(marker_index)
            .expect("marker index not found")
    }
}
