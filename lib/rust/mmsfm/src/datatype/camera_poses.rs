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

//! Per-frame Camera Pose data structure.

use mmcore::collections::SortedVecMap;
use mmio::uvtrack_reader::FrameNumber;
use std::ops::{Index, IndexMut};

use crate::datatype::camera_pose::CameraPose;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// HashMap-like wrapper for storing camera poses per frame.
///
/// Backed by a `SortedVecMap` for contiguous, cache-friendly storage.
///
/// Frame numbers are kept sorted ascending so that binary search
/// gives O(log n) lookups and `generate_sorted_frame_list` is a free
/// clone with no extra sort.
#[derive(Clone)]
pub struct CameraPoses {
    inner: SortedVecMap<FrameNumber, CameraPose>,
}

impl CameraPoses {
    pub fn new() -> CameraPoses {
        CameraPoses {
            inner: SortedVecMap::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> CameraPoses {
        CameraPoses {
            inner: SortedVecMap::with_capacity(capacity),
        }
    }

    pub fn insert(&mut self, frame: FrameNumber, camera_pose: CameraPose) {
        self.inner.insert(frame, camera_pose);
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

    pub fn get(&self, frame: &FrameNumber) -> Option<&CameraPose> {
        self.inner.get(frame)
    }

    pub fn get_mut(&mut self, frame: &FrameNumber) -> Option<&mut CameraPose> {
        self.inner.get_mut(frame)
    }

    pub fn keys(&self) -> impl Iterator<Item = &FrameNumber> {
        self.inner.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &CameraPose> {
        self.inner.values()
    }

    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut CameraPose> {
        self.inner.values_mut()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&FrameNumber, &CameraPose)> {
        self.inner.iter()
    }

    pub fn iter_mut(
        &mut self,
    ) -> impl Iterator<Item = (&FrameNumber, &mut CameraPose)> {
        self.inner.iter_mut()
    }

    pub fn contains_key(&self, frame: &FrameNumber) -> bool {
        self.inner.contains_key(frame)
    }

    pub fn generate_sorted_frame_list(&self) -> Vec<FrameNumber> {
        // Already sorted - just clone.
        self.inner.keys().copied().collect()
    }
}

impl Default for CameraPoses {
    fn default() -> Self {
        Self::new()
    }
}

// Implement Index trait for camera_poses[&frame] syntax
impl Index<&FrameNumber> for CameraPoses {
    type Output = CameraPose;

    fn index(&self, frame: &FrameNumber) -> &Self::Output {
        &self.inner[frame]
    }
}

// Implement IndexMut trait for mutable indexing
impl IndexMut<&FrameNumber> for CameraPoses {
    fn index_mut(&mut self, frame: &FrameNumber) -> &mut Self::Output {
        &mut self.inner[frame]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::{Matrix3, Point3};

    fn make_pose(v: f64) -> CameraPose {
        CameraPose::new(Matrix3::identity(), Point3::new(v, v, v))
    }

    #[test]
    fn test_generate_sorted_frame_list() {
        let mut poses = CameraPoses::new();
        for &f in &[5u32, 3, 1, 4, 2] {
            poses.insert(f, make_pose(f as f64));
        }
        let list = poses.generate_sorted_frame_list();
        assert_eq!(list, vec![1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_index() {
        let mut poses = CameraPoses::new();
        poses.insert(10, make_pose(42.0));
        assert_eq!(poses[&10].center().x, 42.0);
    }

    #[test]
    fn test_index_mut() {
        let mut poses = CameraPoses::new();
        poses.insert(10, make_pose(1.0));
        *poses[&10].center_mut() = Point3::new(99.0, 0.0, 0.0);
        assert_eq!(poses.get(&10).unwrap().center().x, 99.0);
    }
}
