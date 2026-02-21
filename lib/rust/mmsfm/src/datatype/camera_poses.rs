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

use mmio::uvtrack_reader::FrameNumber;
use std::collections::BTreeMap;
use std::ops::{Index, IndexMut};

use crate::datatype::camera_pose::CameraPose;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// HashMap-like wrapper for storing camera poses per frame.
///
/// TODO: The underlying data structure should be completely
/// changed to using contiguous memory for both keys and values.
///
/// The aim is to provide a HashMap-like API but backed by a
/// different data structure to avoid the hashing overhead.
///
/// The API should stay the same or similar to the HashMap because
/// we want this to be a (almost) drop-in replacement for the
/// direct HashMap.
#[derive(Clone)]
pub struct CameraPoses {
    data: BTreeMap<FrameNumber, CameraPose>,
}

impl CameraPoses {
    pub fn new() -> CameraPoses {
        CameraPoses {
            data: BTreeMap::new(),
        }
    }

    pub fn insert(&mut self, frame: FrameNumber, camera_pose: CameraPose) {
        self.data.insert(frame, camera_pose);
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

    pub fn get(&self, frame: &FrameNumber) -> Option<&CameraPose> {
        self.data.get(frame)
    }

    pub fn get_mut(&mut self, frame: &FrameNumber) -> Option<&mut CameraPose> {
        self.data.get_mut(frame)
    }

    pub fn keys(&self) -> impl Iterator<Item = &FrameNumber> {
        self.data.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &CameraPose> {
        self.data.values()
    }

    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut CameraPose> {
        self.data.values_mut()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&FrameNumber, &CameraPose)> {
        self.data.iter()
    }

    pub fn iter_mut(
        &mut self,
    ) -> impl Iterator<Item = (&FrameNumber, &mut CameraPose)> {
        self.data.iter_mut()
    }

    pub fn contains_key(&self, frame: &FrameNumber) -> bool {
        self.data.contains_key(frame)
    }

    pub fn generate_sorted_frame_list(&self) -> Vec<FrameNumber> {
        let mut frame_list: Vec<FrameNumber> =
            self.data.keys().copied().collect();
        // TODO: The sorting may not actually be needed.
        frame_list.sort_unstable();
        frame_list
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
        &self.data[frame]
    }
}

// Implement IndexMut trait for mutable indexing
impl IndexMut<&FrameNumber> for CameraPoses {
    fn index_mut(&mut self, frame: &FrameNumber) -> &mut Self::Output {
        self.data.get_mut(frame).expect("Frame not found")
    }
}
